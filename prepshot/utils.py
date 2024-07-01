#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module contains utility functions for the model.
"""
import datetime
import logging
import numpy as np
import pandas as pd
import xarray as xr
from scipy import interpolate
import pyoptinterface as poi

from prepshot.logs import timer

def update_output_filename(output_filename, args):
    """Update the output filename based on the arguments.

    Parameters
    ----------
    output_filename : str
        The name of the output file.
    args : argparse.Namespace
        Arguments parsed by argparse.

    Returns
    -------
    str
        The updated output filename.
    """
    output_filename = output_filename + '_'.join(
        f'{key}_{value}' for key, value in vars(args).items() 
        if value is not None
    )
    return output_filename

def validate_values(*values):
    """Validate that all values are greater than 0, otherwise raise a 
    ValueError.
    
    Parameters
    ----------
    values : int or float
        Values to be validated.

    Raises
    ------
    ValueError
        If any of the values are less than or equal to 0.
    """
    for value in values:
        if value <= 0:
            raise ValueError("All arguments must be greater than 0.")

def inv_cost_factor(
    dep_period, interest_rate, year_built, discount_rate, year_min, year_max
):
    """Calculate the investment cost factor.

    Parameters
    ----------
    dep_period : int
        Depreciation period.
    interest_rate : float
        Interest rate.
    year_built : int
        Year of construction.
    discount_rate : float
        Discount rate.
    year_min : int
        Minimum year.
    year_max : int
        Maximum year.

    Returns
    -------
    float
        The investment cost factor.

    Raises
    ------
    ValueError
        If year_max is less than or equal to year_min, 
        or year_max is less than year_built,
        or year_built is less than year_min. 
    """
    validate_values(
        dep_period, interest_rate, year_built, year_min, year_max
    )
    if (year_max <= year_min) or (year_max < year_built)                      \
        or (year_built < year_min):
        raise ValueError("Invalid year values.")

    years_since_min = year_built - year_min
    years_to_max = year_max - year_built + 1
    return (interest_rate / (1 - (1 + interest_rate) ** (-dep_period))
             * (1 - (1 + discount_rate) ** (-min(dep_period, years_to_max)))
             / (discount_rate * (1 + discount_rate) ** years_since_min))

def cost_factor(discount_rate, modeled_year, year_min, next_modeled_year):
    """Calculate the cost factor.

    Parameters
    ----------
    discount_rate : float
        Discount rate.
    modeled_year : int
        Modeled year.
    year_min : int
        Minimum year.
    next_modeled_year : int
        Next modeled year.

    Returns
    -------
    float
        The cost factor.

    Raises
    ------
    ValueError
        if next_modeled_year is less than modeled_year.
    """
    validate_values(discount_rate, modeled_year, year_min, next_modeled_year)
    if next_modeled_year < modeled_year:
        raise ValueError(
            "Next modeled year must be greater than or" 
            + "equal to the current modeled year."
        )

    years_since_min = modeled_year - year_min
    years_to_next = next_modeled_year - modeled_year
    return (1 - (1 + discount_rate) ** (-years_to_next))                      \
        / (discount_rate * (1 + discount_rate) ** (years_since_min - 1))

def read_data(
    filename, index_cols, header_rows, unstack_levels=None, 
    first_col_only=False, dropna=True
):
    """Read data from the input Excel file into a pandas.DataFrame.

    Parameters
    ----------
    filename : str
        The name of the input Excel file.
    index_cols : list
        List of column names to be used as index.
    header_rows : list
        List of rows to be used as header.
    unstack_levels : list, optional
        List of levels to be unstacked, by default None
    first_col_only : bool, optional
        Whether to keep only the first column, by default False
    dropna : bool, optional
        Whether to drop rows with NaN values, by default True

    Returns
    -------
    pandas.DataFrame
        A DataFrame containing the data from the input Excel file.
    """
    df = pd.read_excel(io=filename, index_col=index_cols, header=header_rows)

    if unstack_levels:
        df = df.unstack(level=unstack_levels)

    if first_col_only:
        df = df.iloc[:, 0]

    if dropna:
        df = df.dropna().to_dict()

    return df

def interpolate_z_by_q_or_s(name, qs, zqv):
    """Interpolate Z by Q or S.

    Parameters
    ----------
    name : str
        Name of the hydropower station.
    qs : numpy.ndarray
        Array of Q or S values.
    zqv : pandas.DataFrame
        DataFrame of ZQ or ZV values.

    Returns
    -------
    scipy.interpolate.interp1d
        Array of interpolated values.
    """
    try:
        zqv_temp = zqv[(zqv.name == int(name)) | (zqv.name == str(name))]
    except Exception:
        zqv_temp = zqv[zqv.name == str(name)]
    try:
        x = zqv_temp.Q
    except Exception:
        x = zqv_temp.V
    f_zqv = interpolate.interp1d(x, zqv_temp.Z, fill_value='extrapolate')
    return f_zqv(qs)

def initialize_waterhead(stations, year, month, hour, para):
    """Initialize water head.

    Parameters
    ----------
    stations : list
        List of stations.
    year : list
        List of years.
    month : list
        List of months.
    hour : list
        List of hours.
    para : dict
        Dictionary of parameters for the model.

    Returns
    -------
    tuple
        A tuple of two pandas.DataFrame objects, the first one is 
        the old water head, the second one is the new water head.
    """
    old_waterhead = pd.DataFrame(
        index=stations,
        columns=pd.MultiIndex.from_product(
            [year, month, hour], names=['year', 'month', 'hour']
        )
    )
    new_waterhead = old_waterhead.copy(deep=True)

    for s in stations:
        old_waterhead.loc[s, :] = [
            para['reservoir_characteristics']['head', s]
        ] * (len(hour) * len(month) * len(year))
    return old_waterhead, new_waterhead

def compute_error(old_waterhead, new_waterhead):
    """Calculate the error of the water head.

    Parameters
    ----------
    old_waterhead : pandas.DataFrame
        The water head before the solution.
    new_waterhead : pandas.DataFrame
        The water head after the solution.

    Returns
    -------
    float
        The error of the water head.
    """
    new_waterhead[new_waterhead <= 0] = 1
    error = (
        abs(new_waterhead - old_waterhead)
        / new_waterhead
    ).mean(axis='columns').mean()
    return error

def process_model_solution(
    model, stations, year, month, hour, para, old_waterhead, new_waterhead
):
    """Process the solution of the model, updating the water head data.

    Parameters
    ----------
    model : pyoptinterface._src.mosek.Model
        Model to be solved.
    stations : list
        List of hydropower stations.
    year : list
        List of years.
    month : list
        List of months.
    hour : list
        List of hours.
    para : dict
        Dictionary of parameters for the model.
    old_waterhead : pandas.DataFrame
        The water head before the solution.
    new_waterhead : pandas.DataFrame
        The water head after the solution.

    Returns
    -------
    bool
        True if the model is solved, False otherwise.
    """
    idx = pd.IndexSlice
    for s, h, m, y in model.station_hour_month_year_tuples:
        efficiency = para['reservoir_characteristics']['coeff', s]
        model.set_normalized_coefficient(
            model.output_calc_cons[s, h, m, y],
            model.genflow[s, h, m, y],
            - efficiency * 1e-3 * old_waterhead.loc[s, idx[y, m, h]]
        )
    # Solve the model and check the solution status.
    model.set_model_attribute(poi.ModelAttribute.Silent, False)
    model.optimize() # add log into log file
    status = model.get_model_attribute(poi.ModelAttribute.TerminationStatus)
    if status != poi.TerminationStatusCode.OPTIMAL:
        return False
    if para['iteration_number'] <= 1:
        # If fixed head is True, do not update water head.
        new_waterhead = old_waterhead
        return True
    # Iterate over each station to update water head data.
    for stcd in stations:
        outflow = np.array([[
            [model.get_value(model.outflow[int(stcd), h, m, y]) for h in hour]
            for m in month] for y in year]
        )
        storage = np.array([[
            [model.get_value(model.storage_reservoir[int(stcd), h, m, y])
            for h in model.hour_p] for m in month] for y in year]
        )

        tail = interpolate_z_by_q_or_s(
            str(stcd), outflow,
            para['reservoir_tailrace_level_discharge_function']
        )
        storage = interpolate_z_by_q_or_s(
            str(stcd), storage, para['reservoir_forebay_level_volume_function']
        )

        # Calculate the new water head.
        fore = (storage[:, :, :hour[-1]] + storage[:, :, 1:]) / 2
        h = np.maximum(fore - tail, 0)
        new_waterhead.loc[int(stcd), :] = h.ravel()
    return True

def run_model_iteration(
    model, para, error_threshold=0.001, max_iterations=5
):
    """Run the model iteratively.

    Parameters
    ----------
    model : pyoptinterface._src.mosek.Model
        Model to be solved.
    para : dict
        Dictionary of parameters for the model.
    error_threshold : float, optional
        The error threshold, by default 0.001
    max_iterations : int, optional
        The maximum number of iterations, by default 5

    Returns
    -------
    bool
        True if the model is solved, False otherwise.
    """
    logging.info(
        'Starting iteration recorded at %s.', 
        datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

    # Initialize water head.
    stations, years, months, hours =                                          \
        para['stcd'], para['year'], para['month'], para['hour']
    old_waterhead, new_waterhead = initialize_waterhead(
        stations, years, months, hours, para
    )

    # Variables for iteration.
    error = 1
    errors = []
    # Perform water head iteration.
    for iteration in range(1, max_iterations+1):
        alpha = 1 / iteration
        success = process_model_solution(
            model, stations, years, months, hours, para,
            old_waterhead, new_waterhead
        )
        if not success:
            return False

        # Calculate error.
        if  max_iterations <= 1:
            logging.warning(
                "Maximum iteration is set to 1 and " 
                + "the model will be solved with fixed head."
            )
            error = 0
        else:
            error = compute_error(old_waterhead, new_waterhead)
        errors.append(error)
        logging.info('Water head error: %.2f%%', error)
        if error < error_threshold:
            return True

        # Update old water head for next iteration.
        old_waterhead += alpha * (new_waterhead - old_waterhead)

    logging.warning(
        "Ending iteration recorded at %s."
        + "Failed to converge. Maximum iteration exceeded.",
        datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    return True

def create_data_array(data, dims, coords, unit):
    """Create a xarray DataArray with specified data, dimensions, coordinates 
    and units.

    Parameters
    ----------
    data : list
        The data to be included in the DataArray.
    dims : list
        The dimensions of the data.
    coords : dict
        The coordinates of the data.
    unit : str
        The unit of the data.

    Returns
    -------
    xr.DataArray
        A DataArray with the specified data, dimensions, coordinates and units.
    """
    return xr.DataArray(data=data,
                        dims=dims,
                        coords=coords,
                        attrs={'unit': unit})

@timer
def solve_model(model, parameters):
    """Solve the model.

    Parameters
    ----------
    model : pyoptinterface._src.mosek.Model
        Model to be solved.
    parameters : dict
        Dictionary of parameters for the model.

    Returns
    -------
    bool
        True if the model is solved, False otherwise.
    """
    if parameters['isinflow']:
        error_threshold = parameters['error_threshold']
        iteration_number = parameters['iteration_number']
        return run_model_iteration(
            model, parameters, error_threshold, iteration_number
        )
    model.optimize()
    status = model.get_model_attribute(poi.ModelAttribute.TerminationStatus)
    if status != poi.TerminationStatusCode.OPTIMAL:
        return False
    return True

@timer
def extract_results_non_hydro(model):
    """Extracts results for non-hydro models.

    Parameters
    ----------
    model : pyoptinterface._src.mosek.Model
        Model to be solved.

    Returns
    -------
    xr.Dataset
        A Dataset containing DataArrays for each attribute of 
        the model.
    """
    # Extract attributes and values from model.
    hour = model.hour
    month = model.month
    year = model.year
    zone = model.zone
    tech = model.tech

    # Extract values from model.
    cost_var_values = model.get_value(model.cost_var)
    cost_fix_values = model.get_value(model.cost_fix)
    cost_newtech_values = model.get_value(model.cost_newtech)
    cost_newline_values = model.get_value(model.cost_newline)
    income_values = model.get_value(model.income)

    # Create DataArrays for each result set.
    trans_import_v = create_data_array(
        [[[[[model.get_value(model.trans_import[h, m, y, z1, z2]) / 1e6
            if (h, m, y, z1, z2) in model.hour_month_year_zone_zone_tuples
            else np.nan for h in hour] for m in month]
            for y in year] for z1 in zone] for z2 in zone],
        ['zone2', 'zone1', 'year', 'month', 'hour'],
        {
            'month': month, 'hour': hour, 'year': year, 
            'zone1': zone, 'zone2': zone
        }, 
        'TWh'
    )

    trans_export_v = create_data_array(
        [[[[[model.get_value(model.trans_export[h, m, y, z1, z2]) / 1e6
            if (h, m, y, z1, z2) in model.hour_month_year_zone_zone_tuples
            else np.nan
            for h in hour] for m in month]
            for y in year] for z2 in zone] for z1 in zone],
        ['zone2', 'zone1', 'year', 'month', 'hour'],
        {
            'month': month, 'hour': hour, 'year': year, 
            'zone1': zone, 'zone2': zone
        },
        'TWh'
    )

    gen_v = create_data_array(
        [[[[[model.get_value(model.gen[h, m, y, z, te]) / 1e6
            for h in hour] for m in month] for y in year]
            for z in zone] for te in tech],
        ['tech', 'zone', 'year', 'month', 'hour'],
        {
            'month': month, 'hour': hour, 'year': year, 
            'zone': zone, 'tech': tech
        },
        'TWh'
    )

    install_v = create_data_array(
        [[[model.get_value(model.cap_existing[y, z, te]) for y in year]
            for z in zone] for te in tech],
        ['tech', 'zone', 'year'],
        {'zone': zone, 'tech': tech, 'year': year},
        'MW'
    )

    carbon_v = create_data_array(
        [model.get_value(model.carbon[y]) for y in year],
        ['year'], 
        {'year': year}, 'Ton')

    charge_v = create_data_array(
        [[[[[model.get_value(model.charge[h, m, y, z, te]) for h in hour]
            for m in month] for y in year] for z in zone] for te in tech],
        ['tech', 'zone', 'year', 'month', 'hour'],
        {
            'tech': tech, 'zone': zone, 'year': year, 
            'month': month, 'hour': hour
        },
        'MW'
    )
    # year_zone_tech_tuples
    cost_var_breakdown_v = create_data_array(
        [[[model.get_value(model.cost_var_breakdown[y, z, te])
            for y in year] for z in zone] for te in tech],
        ['tech', 'zone', 'year'],
        {'tech': tech, 'zone': zone, 'year': year},
        'dollar'
    )
    cost_fix_breakdown_v = create_data_array(
        [[[model.get_value(model.cost_fix_breakdown[y, z, te])
            for y in year] for z in zone] for te in tech],
        ['tech', 'zone', 'year'],
        {'tech': tech, 'zone': zone, 'year': year}, 'dollar')
    cost_newtech_breakdown_v = create_data_array(
        [[[model.get_value(model.cost_newtech_breakdown[y, z, te])
            for y in year] for z in zone] for te in tech],
        ['tech', 'zone', 'year'],
        {'tech': tech, 'zone': zone, 'year': year}, 'dollar')
    cost_newline_breakdown_v = create_data_array(
        [[[model.get_value(model.cost_newline_breakdown[y, z1, z])
            if (y, z1, z) in model.year_zone_zone_tuples 
            else np.nan for y in year] for z1 in zone] for z in zone],
        ['zone2', 'zone1', 'year'],
        {'zone2': zone, 'zone1': zone, 'year': year}, 'dollar')
    carbon_breakdown_v = create_data_array(
        [[[model.get_value(model.carbon_breakdown[y, z, te])
            for y in year] for z in zone] for te in tech],
        ['tech', 'zone', 'year'],
        {'tech': tech, 'zone': zone, 'year': year}, 'ton')

    # Calculate total cost and income and create DataArray for each cost
    # component.
    cost_v = xr.DataArray(
        data = cost_var_values
        + cost_fix_values
        + cost_newtech_values
        + cost_newline_values
        - income_values
    )
    cost_var_v = xr.DataArray(data=cost_var_values)
    cost_fix_v = xr.DataArray(data=cost_fix_values)
    cost_newtech_v = xr.DataArray(data=cost_newtech_values)
    cost_newline_v = xr.DataArray(data=cost_newline_values)
    income_v = xr.DataArray(data=income_values)

    # Combine all DataArrays into a Dataset.
    ds = xr.Dataset(data_vars={
        'trans_import': trans_import_v,
        'trans_export': trans_export_v,
        'gen': gen_v,
        'carbon': carbon_v,
        'install': install_v,
        'cost': cost_v,
        'cost_var': cost_var_v,
        'cost_var_breakdown': cost_var_breakdown_v,
        'cost_fix_breakdown': cost_fix_breakdown_v,
        'cost_newtech_breakdown': cost_newtech_breakdown_v,
        'cost_newline_breakdown': cost_newline_breakdown_v,
        'carbon_breakdown': carbon_breakdown_v,
        'cost_fix': cost_fix_v,
        'charge': charge_v,
        'cost_newtech': cost_newtech_v,
        'cost_newline': cost_newline_v,
        'income': income_v
    })
    return ds

@timer
def extract_results_hydro(model):
    """Extracts results for hydro models.

    Parameters
    ----------
    model : pyoptinterface._src.mosek.Model
        Model to be solved.

    Returns
    -------
    xr.Dataset
        A Dataset containing DataArrays for each attribute 
        of the model.
    """
    ds = extract_results_non_hydro(model)

    # Extract additional attributes specific to hydro models.
    stations = model.station
    # genflow_values = model.genflow.extract_values()
    # spillflow_values = model.spillflow.extract_values()
    hour = model.hour
    month = model.month
    year = model.year

    # Create additional DataArrays specific to hydro models.
    genflow_v = create_data_array(
        [[[[model.get_value(model.genflow[s, h, m, y])
            for h in hour] for m in month] for y in year] for s in stations],
        ['station', 'year', 'month', 'hour'],
        {'station': stations, 'year': year, 'month': month, 'hour': hour}, 
        'm**3s**-1'
    )

    spillflow_v = create_data_array(
        [[[[model.get_value(model.spillflow[s, h, m, y]) for h in hour]
            for m in month] for y in year] for s in stations], 
        ['station', 'year', 'month', 'hour'], 
        {'station': stations, 'year': year, 'month': month, 'hour': hour}, 
        'm**3s**-1'
    )

    # Add these DataArrays to the existing non-hydro Dataset.
    ds = ds.assign({'genflow': genflow_v, 'spillflow': spillflow_v})

    return ds

@timer
def save_to_excel(ds, output_filename):
    """Save the results to an Excel file.

    Parameters
    ----------
    ds : xr.Dataset
        Dataset containing the results.
    output_filename : str
        The name of the output file.
    """
    with pd.ExcelWriter(f'{output_filename}.xlsx') as writer:
        for key in ds.data_vars:
            if len(ds[key].shape) == 0:
                df = pd.DataFrame([ds[key].values.max()], columns=[key])
            else:
                df = ds[key].to_dataframe()
            df.to_excel(writer, sheet_name=key, merge_cells=False)

def extract_result(model, isinflow=True):
    """Extracts results from the provided model.

    Parameters
    ----------
    model : pyoptinterface._src.mosek.Model
        Model to be solved.
    isinflow : bool, optional
        Whether the model should consider hydrological constraints. 
        Defaults to True., by default True

    Returns
    -------
    xr.Dataset
        A Dataset containing DataArrays for each attribute 
        of the model.
    """
    if isinflow:
        return extract_results_hydro(model)
    return extract_results_non_hydro(model)
