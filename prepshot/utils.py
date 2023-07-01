import datetime
import logging
import numpy as np
import pandas as pd
import xarray as xr
from pyomo.opt import SolverStatus, TerminationCondition
from scipy import interpolate

def update_output_filename(output_filename, args):
    """
    Update the output filename based on the arguments.

    Args:
        output_filename (str): The name of the output file.
        args (argparse.Namespace): Arguments parsed by argparse.

    Returns:
        str: The updated output filename.
    """
    output_filename = output_filename + '_'.join(f'{key}_{value}' for key, value in vars(args).items() if value is not None)
    return output_filename


def validate_values(*values):
    """
    Validate that all values are greater than 0, otherwise raise a ValueError.

    Args:
        *values (int or float): Values to be validated.

    Returns:
        None
    """
    for value in values:
        if value <= 0:
            raise ValueError("All arguments must be greater than 0.")
            

def inv_cost_factor(dep_period, interest_rate, year_built, discount_rate, year_min, year_max):
    """
    Calculate the investment cost factor.

    Args:
        dep_period (int): Depreciation period.
        interest_rate (float): Interest rate.
        year_built (int): Year of construction.
        discount_rate (float): Discount rate.
        year_min (int): Minimum year.
        year_max (int): Maximum year.

    Returns:
        float: The investment cost factor.
    """
    validate_values(dep_period, interest_rate, year_built, year_min, year_max)
    if (year_max <= year_min) or (year_max < year_built) or (year_built < year_min):
        raise ValueError("Invalid year values.")
        
    years_since_min = year_built - year_min
    years_to_max = year_max - year_built + 1
    return (interest_rate / (1 - (1 + interest_rate) ** (-dep_period)) * 
            (1 - (1 + discount_rate) ** (-min(dep_period, years_to_max))) / 
            (discount_rate * (1 + discount_rate) ** years_since_min))


def cost_factor(discount_rate, modeled_year, year_min, next_modeled_year):
    """
    Calculate the cost factor.

    Args:
        discount_rate (float): Discount rate.
        modeled_year (int): Modeled year.
        year_min (int): Minimum year.
        next_modeled_year (int): Next modeled year.

    Returns:
        float: The cost factor.
    """
    validate_values(discount_rate, modeled_year, year_min, next_modeled_year)
    if next_modeled_year < modeled_year:
        raise ValueError("Next modeled year must be greater than or equal to the current modeled year.")

    years_since_min = modeled_year - year_min
    years_to_next = next_modeled_year - modeled_year
    return (1 - (1 + discount_rate) ** (-years_to_next)) / (discount_rate * (1 + discount_rate) ** (years_since_min - 1))


def read_data(filename, index_cols, header_rows, unstack_levels=None, first_col_only=False, dropna=True):
    """
    Read data from the input Excel file into a pandas.DataFrame.

    Args:
        filename (str): The name of the input Excel file.
        index_cols (list): List of column names to be used as index.
        header_rows (list): List of rows to be used as header.
        unstack_levels (list, optional): List of levels to be unstacked. Defaults to None.
        first_col_only (bool, optional): Whether to keep only the first column. Defaults to False.
        dropna (bool, optional): Whether to drop rows with NaN values. Defaults to True.

    Returns:
        pandas.DataFrame: A DataFrame containing the data from the input Excel file.
    """
    df = pd.read_excel(io=filename, index_col=index_cols, header=header_rows)
    
    if unstack_levels:
        df = df.unstack(level=unstack_levels)
        
    if first_col_only:
        df = df.iloc[:, 0]

    if dropna:
        df = df.dropna().to_dict()

    return df


def interpolate_Z_by_Q_or_S(name, QS, ZQV):
    """
    Interpolate Z by Q or S.

    Args:
        name (str): Name of the station.
        QS (numpy.ndarray): Array of Q or S values.
        ZQV (pandas.DataFrame): DataFrame of ZQ or ZV values.

    Returns:
        scipy.interpolate.interp1d: Array of interpolated values.
    """
    try:
        ZQV_temp = ZQV[(ZQV.name == int(name)) | (ZQV.name == str(name))]  
    except:
        ZQV_temp = ZQV[ZQV.name == str(name)]
    try:
        x = ZQV_temp.Q
    except:
        x = ZQV_temp.V
    f_ZQV = interpolate.interp1d(x, ZQV_temp.Z, fill_value='extrapolate')
    return f_ZQV(QS)


def initialize_waterhead(stations, year, month, hour, para):
    """
    Initialize water head.

    Args:
        stations (list): List of stations.
        year (list): List of years.
        month (list): List of months.
        hour (list): List of hours.
        para (dict): Dictionary of parameters for the model.

    Returns:
        tuple: A tuple of two pandas.DataFrame objects, the first one is the old water head, the second one is the new water head.
    """
    old_waterhead = pd.DataFrame(index=stations, columns=pd.MultiIndex.from_product([year, month, hour], names=['year', 'month', 'hour']))
    new_waterhead = old_waterhead.copy(deep=True)

    for s in stations:
        old_waterhead.loc[s, :] = [para['static']['head', s]] * (len(hour) * len(month) * len(year))
    return old_waterhead, new_waterhead


def compute_error(old_waterhead, new_waterhead):
    """
    Calculate the error of the water head.

    Args:
        old_waterhead (pandas.DataFrame): The water head before the solution.
        new_waterhead (pandas.DataFrame): The water head after the solution.

    Returns:
        float: The error of the water head.
    """
    new_waterhead[new_waterhead <= 0] = 1
    error = (abs(new_waterhead - old_waterhead) / new_waterhead).mean(axis='columns').mean()
    return error


def process_model_solution(model, solver, stations, year, month, hour, para, old_waterhead, new_waterhead):
    """
    Process the solution of the model, updating the water head data.

    Args:
        model (pyomo.core.base.PyomoModel.ConcreteModel): Model to be solved.
        solver (pyomo.solvers.plugins.solvers): Solver for the model.
        stations (list): List of stations.
        year (list): List of years.
        month (list): List of months.
        hour (list): List of hours.
        para (dict): Dictionary of parameters for the model.
        old_waterhead (pandas.DataFrame): The water head before the solution.
        new_waterhead (pandas.DataFrame): The water head after the solution.

    Returns:
        bool: True if the model is solved, False otherwise.
    """
    idx = pd.IndexSlice
    for s, h, m, y in model.station_hour_month_year_tuples:
        model.head_para[s, h, m, y] = old_waterhead.loc[s, idx[y, m, h]]

    # Solve the model and check the solution status.
    results = solver.solve(model, tee=True)
    if not (results.solver.status == SolverStatus.ok and results.solver.termination_condition == TerminationCondition.optimal):
        return False

    outflow_values = model.outflow.extract_values()
    storage_values = model.storage_hydro.extract_values()

    # Iterate over each station to update water head data.
    for stcd in stations:
        tail = np.array([[[outflow_values[int(stcd), h, m, y] for h in hour] for m in month] for y in year])
        storage = np.array([[[storage_values[int(stcd), h, m, y] for h in model.hour_p] for m in month] for y in year])

        tail = interpolate_Z_by_Q_or_S(str(stcd), tail, para['zq'])
        storage = interpolate_Z_by_Q_or_S(str(stcd), storage, para['zv'])
        
        # Calculate the new water head.
        fore = (storage[:, :, :hour[-1]] + storage[:, :, 1:]) / 2
        H = np.maximum(fore - tail, 0)
        new_waterhead.loc[int(stcd), :] = H.ravel()
    return True


def run_model_iteration(model, solver, para, error_threshold=0.001, max_iterations=5):
    """
    Run the model iteratively.

    Args:
        model (pyomo.core.base.PyomoModel.ConcreteModel): Model to be solved.
        solver (pyomo.solvers.plugins.solvers): Solver for the model.
        para (dict): Dictionary of parameters for the model.
        error_threshold (float, optional): The error threshold. Defaults to 0.001.
        max_iterations (int, optional): The maximum number of iterations. Defaults to 5.

    Returns:
        bool: True if the model is solved, False otherwise.
    """
    logging.info('Starting iteration recorded at %s.' %(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

    # Initialize water head.
    stations, years, months, hours = para['stcd'], para['year'], para['month'], para['hour']
    old_waterhead, new_waterhead = initialize_waterhead(stations, years, months, hours, para)

    # Variables for iteration.
    error = 1
    errors = []

    # Perform water head iteration.
    for iteration in range(1, max_iterations+1):
        alpha = 1 / iteration
        success = process_model_solution(model, solver, stations, years, months, hours, para, old_waterhead, new_waterhead)
        if not success:
            return False

        # Calculate error.
        error = compute_error(old_waterhead, new_waterhead)
        errors.append(error)
        logging.info('Water head error: {:.2%}'.format(error))
        if error < error_threshold:
            return True

        # Update old water head for next iteration.
        old_waterhead += alpha * (new_waterhead - old_waterhead)

    logging.warning('Ending iteration recorded at %s. Failed to converge. Maximum iteration exceeded.' % 
                    (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    return True


def create_data_array(data, dims, coords, unit):
    """
    Create a xarray DataArray with specified data, dimensions, coordinates and units.

    Args:
        data (list): The data to be included in the DataArray.
        dims (list): The dimensions of the data.
        coords (dict): The coordinates of the data.
        unit (str): The unit of the data.

    Returns:
        xr.DataArray: A DataArray with the specified data, dimensions, coordinates and units.
    """
    return xr.DataArray(data=data,
                        dims=dims,
                        coords=coords,
                        attrs={'unit': unit})


def extract_results_non_hydro(model):
    """
    Extracts results for non-hydro models.

    Args:
        model (pyomo.core.base.PyomoModel.ConcreteModel): Model to be solved.

    Returns:
        xr.Dataset: A Dataset containing DataArrays for each attribute of the model.
    """
    # Extract attributes and values from model.
    hour = model.hour
    month = model.month
    year = model.year
    zone = model.zone
    tech = model.tech

    # Extract values from model.
    trans_import_values = model.trans_import.extract_values()
    trans_export_values = model.trans_export.extract_values()
    gen_values = model.gen.extract_values()
    carbon_values = model.carbon.extract_values()
    cap_existing_values = model.cap_existing.extract_values()
    cost_var_values = model.cost_var.extract_values()[None]
    cost_fix_values = model.cost_fix.extract_values()[None]
    cost_newtech_values = model.cost_newtech.extract_values()[None]
    cost_newline_values = model.cost_newline.extract_values()[None]
    income_values = model.income.extract_values()[None]
    charge_values = model.charge.extract_values()

    # Create DataArrays for each result set.
    trans_import_v = create_data_array(
        [[[[[trans_import_values[h, m, y, z1, z2] / 1e6 
             if (h, m, y, z1, z2) in model.hour_month_year_zone_zone_tuples else np.nan for h in hour] for m in month] 
             for y in year] for z1 in zone] for z2 in zone], 
        ['zone2', 'zone1', 'year', 'month', 'hour'], 
        {'month': month, 'hour': hour, 'year': year, 'zone1': zone, 'zone2': zone}, 'TWh')

    trans_export_v = create_data_array(
        [[[[[trans_export_values[h, m, y, z1, z2] / 1e6
            if (h, m, y, z1, z2) in model.hour_month_year_zone_zone_tuples else np.nan
            for h in hour] for m in month] for y in year] for z2 in zone] for z1 in zone],
        ['zone2', 'zone1', 'year', 'month', 'hour'],
        {'month': month, 'hour': hour, 'year': year, 'zone1': zone, 'zone2': zone}, 'TWh')

    gen_v = create_data_array(
        [[[[[gen_values[h, m, y, z, te] / 1e6 
             for h in hour] for m in month] for y in year] for z in zone] for te in tech], 
        ['tech', 'zone', 'year', 'month', 'hour'], 
        {'month': month, 'hour': hour, 'year': year, 'zone': zone, 'tech': tech}, 'TWh')

    install_v = create_data_array(
        [[[cap_existing_values[y, z, te] for y in year] for z in zone] for te in tech], 
        ['tech', 'zone', 'year'], 
        {'zone': zone, 'tech': tech, 'year': year}, 'MW')

    carbon_v = create_data_array(
        [carbon_values[y] for y in year], 
        ['year'], 
        {'year': year}, 'Ton')

    charge_v = create_data_array(
        [[[[[charge_values[h, m, y, z, te] for h in hour] for m in month] for y in year] for z in zone] for te in tech], 
        ['tech', 'zone', 'year', 'month', 'hour'], 
        {'tech': tech, 'zone': zone, 'year': year, 'month': month, 'hour': hour}, 'MW')
    
    # Calculate total cost and income and create DataArray for each cost component.
    cost_v = xr.DataArray(data=cost_var_values + cost_fix_values + cost_newtech_values + cost_newline_values - income_values)
    cost_var_v = xr.DataArray(data=cost_var_values)
    cost_fix_v = xr.DataArray(data=cost_fix_values)
    cost_newtech_v = xr.DataArray(data=cost_newtech_values)
    cost_newline_v = xr.DataArray(data=cost_newline_values)
    income_v = xr.DataArray(data=income_values)
    
    # Combine all DataArrays into a Dataset.
    ds = xr.Dataset(data_vars={'trans_import_v': trans_import_v,
                               'trans_export_v': trans_export_v,
                               'gen_v': gen_v,
                               'carbon_v': carbon_v,
                               'install_v': install_v,
                               'carbon_v': carbon_v,
                               'cost_v': cost_v,
                               'cost_var_v': cost_var_v,
                               'cost_fix_v': cost_fix_v,
                               'charge_v': charge_v,
                               'cost_newtech_v': cost_newtech_v,
                               'cost_newline_v': cost_newline_v,
                               'income_v': income_v})
    return ds


def extract_results_hydro(model):
    """
    Extracts results for hydro models.

    Args:
        model (pyomo.core.base.PyomoModel.ConcreteModel): Model to be solved.

    Returns:
        xr.Dataset: A Dataset containing DataArrays for each attribute of the model.
    """
    ds = extract_results_non_hydro(model)

    # Extract additional attributes specific to hydro models.
    stations = model.station
    genflow_values = model.genflow.extract_values()
    spillflow_values = model.spillflow.extract_values()
    hour = model.hour
    month = model.month
    year = model.year

    # Create additional DataArrays specific to hydro models.
    genflow_v = create_data_array(
        [[[[genflow_values[s, h, m, y] for h in hour] for m in month] for y in year] for s in stations], 
        ['station', 'year', 'month', 'hour'], 
        {'station': stations, 'year': year, 'month': month, 'hour': hour}, 'm**3s**-1')
    
    spillflow_v = create_data_array(
        [[[[spillflow_values[s, h, m, y] for h in hour] for m in month] for y in year] for s in stations], 
        ['station', 'year', 'month', 'hour'], 
        {'station': stations, 'year': year, 'month': month, 'hour': hour}, 'm**3s**-1')

    # Add these DataArrays to the existing non-hydro Dataset.
    ds = ds.assign({'genflow_v': genflow_v, 'spillflow_v': spillflow_v})

    return ds


def extract_result(model, ishydro=True):
    """
    Extracts results from the provided model.

    Args:
        model (pyomo.core.base.PyomoModel.ConcreteModel): Model to be solved.
        ishydro (bool, optional): Whether the model should consider hydrological constraints. Defaults to True.

    Returns:
        xr.Dataset: A Dataset containing DataArrays for each attribute of the model.
    """
    if ishydro:
        return extract_results_hydro(model)
    else:
        return extract_results_non_hydro(model)
