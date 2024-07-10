#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" 
This module contains functions for loading data from json and xlsx files.
"""
import json
import sys
import logging
from os import path
import pandas as pd
from prepshot.utils import inv_cost_factor, cost_factor


def load_json(file):
    """Load data from a json file.

    Parameters
    ----------
    file : str
        Path to the json file.

    Returns
    -------
    dict
        Dictionary containing data from the json file.
    """
    with open(file, "r", encoding="utf-8") as f:
        return json.load(f)


def get_required_config_data(config_data):
    """Get required data from loaded configuration data.

    Parameters
    ----------
    config_data : dict
        Configuration data for the model.

    Returns
    -------
    dict
        Dictionary containing required data from the loaded 
        configuration data.
    """
    # Extract general parameters and solver parameters from configuration file.
    hour = int(config_data['general_parameters']['hour'])
    month = int(config_data['general_parameters']['month'])
    dt = int(config_data['general_parameters']['dt'])
    hours_in_year = int(config_data['general_parameters']['hours_in_year'])
    price = float(config_data['general_parameters']['price'])
    includes_hydrological_constraints =                                       \
        config_data['hydro_parameters']['isinflow']
    error_threshold = float(
        config_data['hydro_parameters']['error_threshold']
    )
    iteration_number = int(
        config_data['hydro_parameters']['iteration_number']
    )

    # Create dictionary containing required data from configuration file.
    required_config_data = {
        'dt': dt,
        'price': price,
        'weight': (month * hour * dt) / hours_in_year,
        'solver': config_data['solver_parameters'],
        'isinflow': includes_hydrological_constraints,
        'error_threshold': error_threshold,
        'iteration_number': iteration_number
    }

    return required_config_data


def load_input_params(input_filepath, params_data, para):
    """Load excel input data.
    
    Parameters
    ----------
    input_filepath : str
        Path to the input folder.
    params_data : dict
        Dictionary containing parameter name and their dimension information.
    para : dict
        Dictionary to store input data of parameters.
    """
    # Load input data into parameters dictionary.
    try:
        for key, value in params_data.items():
            filename = path.join(input_filepath, f"{value['file_name']}.xlsx")
            para[key] = read_data(
                filename,
                value["index_cols"],
                value["header_rows"],
                value["unstack_levels"],
                value["first_col_only"],
                value["drop_na"]
            )
    except FileNotFoundError as e:
        logging.error("Error loading %s data: %s", value["file_name"], e)
        sys.exit(1)


def get_sets(para):
    """Extract simple sets from parameters.
    
    Parameters
    ----------
    para : dict
        Dictionary containing parameters.
    """
    para["year"] = sorted(list(para["discount_factor"].keys()))
    if "reservoir_characteristics" in para.keys():
        para["stcd"] = list({
            i[1] for i in para["reservoir_characteristics"].keys()
        })
    para["hour"] = sorted({
        i[3] for i in para["demand"].keys() if isinstance(i[3], int)
    })
    para["month"] = sorted({
        i[2] for i in para["demand"].keys() if isinstance(i[2], int)
    })
    para["zone"] = list({i[0] for i in para["demand"].keys()})
    para["tech"] = list(para["technology_type"].keys())


def calculate_cost_factors(para):
    """Calculate cost factors for transmission investment, investment, 
        fixed and variable costs.

    Parameters
    ----------
    para : dict
        Dictionary containing parameters.
    """
    # Initialize dictionaries for computed cost factors.
    para["trans_inv_factor"] = {}
    para["inv_factor"] = {}
    para["fix_factor"] = {}
    para["var_factor"] = {}

    # Initialize parameters for cost factor calculations.
    trans_line_lifetime = max(para["transmission_line_lifetime"].values())
    lifetime = para["lifetime"]
    y_min, y_max = min(para["year"]), max(para["year"])

    # Calculate cost factors
    for tech in para["tech"]:
        for year in para["year"]:
            discount_rate = para["discount_factor"][year]
            next_year = year+1 if year == y_max                               \
                else para["year"][para["year"].index(year) + 1]
            para["trans_inv_factor"][year] = inv_cost_factor(
                trans_line_lifetime, discount_rate, year, discount_rate,
                y_min, y_max
            )
            para["inv_factor"][tech, year] = inv_cost_factor(
                lifetime[tech, year], discount_rate, year, discount_rate,
                y_min, y_max
            )
            para["fix_factor"][year] = cost_factor(
                discount_rate, year, y_min, next_year
            )
            para["var_factor"][year] = cost_factor(
                discount_rate, year, y_min, next_year
            )


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


def load_data(params_data, input_filepath):
    """ Loads data from provided file path and processes it according to 
        parameters from params.json.

    Parameters
    ----------
    params_data : dict
        Dictionary containing parameters data.
    input_filepath : str
        Path to the input folder.
            
    Returns
    -------
    dict
        Dictionary containing processed parameters.
    """
    para = {}
    load_input_params(input_filepath, params_data, para)
    get_sets(para)
    calculate_cost_factors(para)

    return para
