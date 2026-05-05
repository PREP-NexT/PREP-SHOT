"""
Author: Zhanwei LIU
Date: 2025-04-26

Script for preparing reservoir topology and net inflow for PREP-SHOT model.
"""

import pandas as pd
import xarray as xr
import numpy as np
from scipy.spatial import KDTree

# =================== Input files path ===================
INPUT_CONFIG = {
    # 'discharge': "./input/sea_nores_discharge_monthly_1960-1961.nc",  # Gridded discharge
    'discharge': "./input/mekong_discharge_monthly_1960-1961.nc",        # Gridded discharge
    'reservoirs': "./input/reservoir_parameters.xlsx",                   # Reservoir locations
    'flow_direction': "./input/ldd.nc",                                  # Flow direction
    'upstream_area': "./input/ups.nc",                                   # Upstream drainage area
    # estimate water travel time
    'river_width': "./input/chanwidth.nc",
    'river_depth': "./input/chanheight.nc",
    'river_length': "./input/chanlength.nc",
    'river_slope': "./input/tanslope.nc",
    'manning': "./input/chanmanning.nc",
    'manning_scale': 1.0
}

# =================== Output files path ===================
OUTPUT_CONFIG = {
    'topology': "./output/reservoir_topology.xlsx",             # Reservoir topology
    'net_inflow': "./output/monthly_net_inflow.xlsx",           # Monthly net inflow
    'drainage_area': "./output/reservoir_drainage_areas.xlsx"   # Reservoir drainage area
}

def load_reservoir_data(file_path: str) -> pd.DataFrame:
    """Load reservoir data with minimal validation."""
    return pd.read_excel(file_path, index_col=False)

def extract_reservoir_topology(res, ldd, ldd_lons, ldd_lats, travel_time):
    """
    Extract reservoir topology (minimally modified from original).
    Only added type hints and slightly improved variable names.
    """
    # Original logic preserved
    reservoir_points = res[["longitude", "latitude"]].values
    ldd_grid_lats, ldd_grid_lons = np.meshgrid(ldd_lats, ldd_lons, indexing='ij')
    ldd_grid_points = np.column_stack((ldd_grid_lons.ravel(), ldd_grid_lats.ravel()))
    tree = KDTree(ldd_grid_points)

    _, reservoir_grid_indices = tree.query(reservoir_points)
    reservoir_grid_indices = np.unravel_index(reservoir_grid_indices, ldd.shape)

    reservoir_loc_dict = {
        (reservoir_grid_indices[0][i], reservoir_grid_indices[1][i]): res['stcd'][i]
        for i in range(len(reservoir_points))
    }

    # Original flow directions
    flow_directions = {
        1: (-1,  1), 2: (0,  1), 3: (1,  1),
        4: (-1, 0),  6: (1,  0),
        7: (-1, -1), 8: (0, -1), 9: (1, -1)
    }

    def track_downstream(x, y, upstream_no, tt):
        """Original tracking function preserved exactly."""
        flow_dir = ldd[x, y]
        if flow_dir == 5:
            return None, tt

        dy, dx = flow_directions[flow_dir]
        xj, yj = x + dx, y + dy

        if (xj < 0 or xj >= ldd.shape[0] or yj < 0 or yj >= ldd.shape[1]):
            return None, tt
        
        if (xj, yj) in reservoir_loc_dict:
            tt += travel_time[x, y] / 2
            return reservoir_loc_dict[(xj, yj)], tt
        tt += travel_time[x, y]

        return track_downstream(xj, yj, upstream_no, tt)

    topology = []
    for i in range(len(reservoir_points)):
        x, y = reservoir_grid_indices[0][i], reservoir_grid_indices[1][i]
        upstream_no = res['stcd'][i]
        tt = travel_time[x, y] / 2
        downstream_no, tt = track_downstream(x, y, upstream_no, tt)
        if downstream_no is not None:
            tt = round(tt/3600) # second to hour
            topology.append([upstream_no, downstream_no, tt])

    return pd.DataFrame(topology, columns=['Upstream', 'Downstream', 'TravelTime [hour]'])

def calculate_drainage_areas(res, topology_df, ups_ds, reservoir_grid_indices):
    """
    Calculate drainage areas (original logic preserved).
    Only added better variable names and docstring.
    """
    # Original area calculation logic
    def get_reservoir_area(res_no, ups_ds, reservoir_grid_indices, res):
        idx = res[res['stcd'] == res_no].index[0]
        x, y = reservoir_grid_indices[0][idx], reservoir_grid_indices[1][idx]
        return float(ups_ds['ups'][x, y].values)

    reservoir_areas = {}
    for res_no in res['stcd']:
        reservoir_areas[res_no] = get_reservoir_area(res_no, ups_ds, reservoir_grid_indices, res)

    drainage_areas = {}
    for res_no, total_area in reservoir_areas.items():
        upstream_res = topology_df[topology_df['Downstream'] == res_no]['Upstream'].tolist()
        upstream_area = sum(reservoir_areas.get(u, 0) for u in upstream_res)
        drainage_areas[res_no] = max(total_area - upstream_area, 0)

    return pd.DataFrame({
        'Reservoir_NO': list(drainage_areas.keys()),
        'Total_Area': [reservoir_areas[k] for k in drainage_areas.keys()],
        'Drainage_Area': list(drainage_areas.values())
    })

def compute_net_inflow(discharge_file, res, topology_df):
    """
    Compute net inflow (original logic preserved).
    Only improved variable naming and added docstring.
    """
    # Original discharge processing
    ds = xr.open_dataset(discharge_file)
    discharge = ds['discharge']
    shp = discharge.values.shape[1:]
    
    ldd_lons, ldd_lats = ds['lon'].values, ds['lat'].values
    ldd_grid_lats, ldd_grid_lons = np.meshgrid(ldd_lats, ldd_lons, indexing='ij')
    ldd_grid_points = np.column_stack((ldd_grid_lons.ravel(), ldd_grid_lats.ravel()))
    tree = KDTree(ldd_grid_points)

    total_inflow = pd.DataFrame()
    for _, row in res.iterrows():
        # reservoir_no = row['stcd']
        lon, lat = row['longitude'], row['latitude']
        
        _, idx = tree.query([lon, lat])
        yi, xi = np.unravel_index(idx, shp)
        
        daily_flow = discharge[:, yi, xi]
        monthly_flow = daily_flow.resample(time='1M').mean()
        # total_inflow[reservoir_no] = monthly_flow.values
        total_inflow = pd.concat([total_inflow, monthly_flow.to_pandas()], axis=1)
    total_inflow.columns = res['stcd']

    total_inflow.index = monthly_flow['time'].values

    # Original net inflow calculation
    net_inflow = total_inflow.copy()
    downstream_to_upstream = topology_df.groupby('Downstream')['Upstream'].apply(list)

    for downstream, upstream_list in downstream_to_upstream.items():
        if downstream not in net_inflow.columns:
            continue
            
        total_upstream_inflow = sum(total_inflow[upstream] for upstream in upstream_list
                                if upstream in total_inflow.columns)
        
        net_inflow[downstream] -= total_upstream_inflow

    return net_inflow

def main():
    """Run the processing pipeline with original logic."""
    print("Starting reservoir data processing...")
    
    # Load data (preserved original loading approach)
    res = load_reservoir_data(INPUT_CONFIG['reservoirs'])
    
    with xr.open_dataset(INPUT_CONFIG['flow_direction']) as ds:
        ldd = ds['ldd'].values
        ldd_lons = ds['lon'].values
        ldd_lats = ds['lat'].values
    with (
        xr.open_dataset(INPUT_CONFIG["river_width"]) as chanwidth,
        xr.open_dataset(INPUT_CONFIG["river_depth"]) as chanheight,
        xr.open_dataset(INPUT_CONFIG["river_length"]) as chanlength,
        xr.open_dataset(INPUT_CONFIG["river_slope"]) as tanslope,
        xr.open_dataset(INPUT_CONFIG["manning"]) as chanmanning
    ):
        manning_scale = INPUT_CONFIG['manning_scale']
        # Load variables
        width = chanwidth.chanwidth
        height = chanheight.chanheight
        length = chanlength.chanlength
        # gradient = changradient.changradient
        tanslope = tanslope.tanslope
        manning = chanmanning.chanmanning * manning_scale
        
        # Calculate hydraulic radius with safety checks
        denominator = width + 2 * height
        hydraulic_radius = xr.where(
            denominator > 0,
            (width * height) / denominator,
            0  # or some small positive value
        )
        
        # Handle problematic values
        manning = xr.where(manning > 0, manning, 0.01)  # replace zeros with typical value
        tanslope = xr.where(tanslope > 0, tanslope, 1e-4)  # minimal slope
        
        # Calculate velocity with safety checks
        velocity = (1.0 / manning) * (hydraulic_radius ** (2/3)) * (tanslope ** 0.5)
        
        # Calculate travel time with safety checks
        safe_velocity = xr.where(velocity > 0, velocity, 0.001)  # minimal velocity
        travel_time = length / safe_velocity
        
        # Optionally mask invalid values
        travel_time = travel_time.where(
            (width > 0) & (height > 0) & (length > 0) & (tanslope > 0) & (manning > 0)
        ).values
    
    
    ups_ds = xr.open_dataset(INPUT_CONFIG['upstream_area'])
    
    # Process data using original functions
    print("Extracting reservoir topology...")
    topology_df = extract_reservoir_topology(res, ldd, ldd_lons, ldd_lats, travel_time)
    
    print("Calculating drainage areas...")
    # Recreate grid indices as in original code
    reservoir_points = res[["longitude", "latitude"]].values
    ldd_grid_lats, ldd_grid_lons = np.meshgrid(ldd_lats, ldd_lons, indexing='ij')
    ldd_grid_points = np.column_stack((ldd_grid_lons.ravel(), ldd_grid_lats.ravel()))
    tree = KDTree(ldd_grid_points)
    _, reservoir_grid_indices = tree.query(reservoir_points)
    reservoir_grid_indices = np.unravel_index(reservoir_grid_indices, ldd.shape)
    
    drainage_df = calculate_drainage_areas(res, topology_df, ups_ds, reservoir_grid_indices)
    
    print("Computing net inflow...")
    net_inflow_df = compute_net_inflow(INPUT_CONFIG['discharge'], res, topology_df)
    
    # Save outputs
    topology_df.to_excel(OUTPUT_CONFIG['topology'], index=False)
    drainage_df.to_excel(OUTPUT_CONFIG['drainage_area'], index=False)
    net_inflow_df.to_excel(OUTPUT_CONFIG['net_inflow'])
    
    print("✅ Processing completed successfully!")
    print(f"Topology saved to: {OUTPUT_CONFIG['topology']}")
    print(f"Drainage areas saved to: {OUTPUT_CONFIG['drainage_area']}")
    print(f"Net inflow saved to: {OUTPUT_CONFIG['net_inflow']}")

if __name__ == "__main__":

    main()
