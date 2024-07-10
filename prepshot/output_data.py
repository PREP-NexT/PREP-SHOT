#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module contains utility functions to save solving results of model.
"""

import logging
import numpy as np
import xarray as xr
import pandas as pd
from prepshot.logs import timer


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
    cost_var_breakdown_v = create_data_array(
        [[[model.get_value(model.cost_var_tech_breakdown[y, z, te])
            for y in year] for z in zone] for te in tech],
        ['tech', 'zone', 'year'],
        {'tech': tech, 'zone': zone, 'year': year},
        'dollar'
    )
    cost_fix_breakdown_v = create_data_array(
        [[[model.get_value(model.cost_fix_tech_breakdown[y, z, te])
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


def save_result(model):
    """Extracts results from the provided model.

    Parameters
    ----------
    model : pyoptinterface._src.mosek.Model
        Model to be solved.
    """
    isinflow = model.para['isinflow']
    args = model.para['command_line_args']
    output_filename = model.para['output_filename']
    output_filename = update_output_filename(output_filename, args)

    if isinflow:
        ds = extract_results_hydro(model)
    else:
        ds = extract_results_non_hydro(model)
    ds.to_netcdf(f'{output_filename}.nc')
    logging.info(
            "Results are written to %s.nc", output_filename
    )
    save_to_excel(ds, output_filename)
    logging.info("Results are written to separate excel files")


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
