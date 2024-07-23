#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""This module contains functions to save solving results of models.
"""

import logging
import argparse

import numpy as np
import xarray as xr
import pandas as pd

from prepshot.logs import timer
from prepshot.utils import cartesian_product


def create_data_array(
    data : dict, dims : list, unit : str, model : object
) -> xr.DataArray:
    """Create a xarray DataArray with specified data, dimensions, coordinates 
    and units.

    Parameters
    ----------
    data : dict
        The data to be included in the DataArray.
    dims : list
        The list of dimentions of the data.
    unit : str
        The unit of the data.
    model : object
        The model object.

    Returns
    -------
    xr.DataArray
        A DataArray with the specified data, dimensions, coordinates and units.
    """
    coords = {dim:getattr(model, dim) for dim in dims}
    index_tuple = cartesian_product(*coords.values())
    if len(dims) == 1:
        index_tuple = [i[0] for i in index_tuple]
    data_values = data.map(model.get_value)
    data = np.array(
        [data_values[tuple_] for tuple_ in index_tuple]
    ).reshape([len(coord) for coord in coords.values()])
    return xr.DataArray(data=data,
                        dims=dims,
                        coords=coords,
                        attrs={'unit': unit})


@timer
def extract_results_non_hydro(model : object) -> xr.Dataset:
    """Extracts results for non-hydro models.

    Parameters
    ----------
    model : object
        Model object sloved already.

    Returns
    -------
    xr.Dataset
        A Dataset containing DataArrays for each attribute of the model.
    """
    model.zone1 = model.zone
    model.zone2 = model.zone

    data_vars = {}
    data_vars['trans_export'] = create_data_array(
        model.trans_export, ['hour', 'month', 'year', 'zone1', 'zone2'],
        'TWh', 
        model)
    data_vars['gen'] = create_data_array(
        model.gen, ['hour', 'month', 'year', 'zone', 'tech'], 'TWh', model)
    data_vars['install'] = create_data_array(
        model.cap_existing, ['year', 'zone', 'tech'], 'MW', model
    )
    data_vars['carbon'] = create_data_array(
        model.carbon, ['year'], 'Ton', model
    )
    data_vars['charge'] = create_data_array(
        model.charge, ['hour', 'month', 'year', 'zone', 'tech'], 'MWh', model
    )
    data_vars['cost_var_breakdown'] = create_data_array(
        model.cost_var_tech_breakdown, ['year', 'zone', 'tech'],
        'dollar', model
    )
    data_vars['cost_fix_breakdown'] = create_data_array(
        model.cost_fix_tech_breakdown, ['year', 'zone', 'tech'],
        'dollar', model
    )
    data_vars['cost_newtech_breakdown'] = create_data_array(
        model.cost_newtech_breakdown, ['year', 'zone', 'tech'],
        'dollar', model
    )
    data_vars['cost_newline_breakdown'] = create_data_array(
        model.cost_newline_breakdown, ['year', 'zone1', 'zone2'],
        'dollar', model
    )
    data_vars['carbon_breakdown'] = create_data_array(
        model.carbon_breakdown, ['year', 'zone', 'tech'], 'Ton', model)
    data_vars['cost_var'] = xr.DataArray(model.get_value(model.cost_var))
    data_vars['cost_fix'] = xr.DataArray(model.get_value(model.cost_fix))
    data_vars['cost_newtech'] = xr.DataArray(
        data=model.get_value(model.cost_newtech)
    )
    data_vars['cost_newline'] = xr.DataArray(
        data=model.get_value(model.cost_newline)
    )
    data_vars['income'] = xr.DataArray(
        data=model.get_value(model.income)
    )
    data_vars['cost'] = xr.DataArray(
        data = model.get_value(model.cost)
    )

    return xr.Dataset(data_vars)

@timer
def extract_results_hydro(model : object) -> xr.Dataset:
    """Extracts results for hydro models.

    Parameters
    ----------
    model : object
        Model solved already.

    Returns
    -------
    xr.Dataset
        A Dataset containing DataArrays for each attribute of the model.
    """
    ds = extract_results_non_hydro(model)
    data_vars = {}
    data_vars['genflow'] = create_data_array(
        model.genflow, ['station', 'hour', 'month', 'year'], 'm**3s**-1',
        model
    )

    data_vars['spillflow'] = create_data_array(
        model.spillflow, ['station', 'hour', 'month', 'year'], 'm**3s**-1',
        model
    )

    return ds.assign(data_vars)

@timer
def save_to_excel(
    ds : xr.Dataset,
    output_filename : str
) -> None:
    """Save the results to an Excel file.

    Parameters
    ----------
    ds : xr.Dataset
        Dataset containing the results.
    output_filename : str
        The name of the output file.
    """
    # pylint: disable=abstract-class-instantiated
    with pd.ExcelWriter(
        f'{output_filename}.xlsx', engine='xlsxwriter'
    ) as writer:
        for key in ds.data_vars:
            if len(ds[key].shape) == 0:
                df = pd.DataFrame([ds[key].values.max()], columns=[key])
            else:
                df = ds[key].to_dataframe()
            df.to_excel(writer, sheet_name=key, merge_cells=False)


def save_result(model : object) -> None:
    """Extracts results from the provided model.

    Parameters
    ----------
    model : object
        The model object to extract results from and save.
    """
    isinflow = model.params['isinflow']
    args = model.params['command_line_args']
    output_filename = model.params['output_filename']
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


def update_output_filename(
    output_filename : str, args : argparse.Namespace
) -> str:
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
