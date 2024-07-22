#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""This module contains functions for loading and processing data from JSON
and Excel files.
"""

import json
import sys
import logging
from os import path

import pandas as pd

from prepshot.utils import calc_inv_cost_factor, calc_cost_factor


def load_json(file_path : str) -> dict:
    """Load data from a JSON file.

    Parameters
    ----------
    file_path : str
        Path to the JSON file.

    Returns
    -------
    dict
        Dictionary containing data from the JSON file.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def extract_config_data(config_data : dict) -> dict:
    """Extract necessary data from configuration settings.

    Parameters
    ----------
    config_data : dict
        Configuration data for the model.

    Returns
    -------
    dict
        Dictionary containing necessary configuration data.
    """
    # Extract parameters from configuration data.
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

    # Create dictionary with necessary configuration data.
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


def load_excel_data(
    input_folder : str, params_info : dict, data_store : dict
) -> None:
    """Load data from Excel files based on the provided parameters.

    Parameters
    ----------
    input_folder : str
        Path to the input folder.
    params_info : dict
        Dictionary containing parameter names and their corresponding file
        information.
    data_store : dict
        Dictionary to store loaded data.
    """
    try:
        for key, value in params_info.items():
            filename = path.join(input_folder, f"{value['file_name']}.xlsx")
            data_store[key] = read_excel(
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


def extract_sets(data_store : dict) -> None:
    """Extract simple sets from loaded parameters.
    
    Parameters
    ----------
    data_store : dict
        Dictionary containing loaded parameters.
    """
    data_store["year"] = sorted(list(data_store["discount_factor"].keys()))
    if "reservoir_characteristics" in data_store.keys():
        data_store["stcd"] = list({
            i[1] for i in data_store["reservoir_characteristics"].keys()
        })
    data_store["hour"] = sorted({
        i[3] for i in data_store["demand"].keys() if isinstance(i[3], int)
    })
    data_store["month"] = sorted({
        i[2] for i in data_store["demand"].keys() if isinstance(i[2], int)
    })
    data_store["zone"] = list({i[0] for i in data_store["demand"].keys()})
    data_store["tech"] = list(data_store["technology_type"].keys())


def compute_cost_factors(data_store : dict) -> None:
    """Calculate cost factors for various transmission investment and 
    operational costs.

    Parameters
    ----------
    data_store : dict
        Dictionary containing loaded parameters.
    """
    # Initialize dictionaries for computed cost factors.
    data_store["trans_inv_factor"] = {}
    data_store["inv_factor"] = {}
    data_store["fix_factor"] = {}
    data_store["var_factor"] = {}

    # Initialize parameters for cost factor calculations.
    trans_line_lifetime = max(data_store["transmission_line_lifetime"].values())
    lifetime = data_store["lifetime"]
    y_min, y_max = min(data_store["year"]), max(data_store["year"])

    # Calculate cost factors
    for tech in data_store["tech"]:
        for year in data_store["year"]:
            discount_rate = data_store["discount_factor"][year]
            next_year = year+1 if year == y_max                               \
                else data_store["year"][data_store["year"].index(year) + 1]
            data_store["trans_inv_factor"][year] = calc_inv_cost_factor(
                trans_line_lifetime, discount_rate, year, discount_rate,
                y_min, y_max
            )
            data_store["inv_factor"][tech, year] = calc_inv_cost_factor(
                lifetime[tech, year], discount_rate, year, discount_rate,
                y_min, y_max
            )
            data_store["fix_factor"][year] = calc_cost_factor(
                discount_rate, year, y_min, next_year
            )
            data_store["var_factor"][year] = calc_cost_factor(
                discount_rate, year, y_min, next_year
            )


def read_excel(
    filename, index_cols, header_rows, unstack_levels=None,
    first_col_only=False, dropna=True
) -> pd.DataFrame:
    """Read data from an Excel file into a pandas DataFrame.

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
        A DataFrame containing the data from the Excel file.
    """
    df = pd.read_excel(io=filename, index_col=index_cols, header=header_rows)

    if unstack_levels:
        df = df.unstack(level=unstack_levels)

    if first_col_only:
        df = df.iloc[:, 0]

    if dropna:
        df = df.dropna().to_dict()

    return df


def process_data(
    params_info : dict, input_folder : str
) -> dict:
    """Load and process data from input folder based on parameters settings.

    Parameters
    ----------
    params_info : dict
        Dictionary containing parameters information.
    input_folder : str
        Path to the input folder.

    Returns
    -------
    dict
        Dictionary containing processed parameters.
    """
    data_store = {}
    load_excel_data(input_folder, params_info, data_store)
    extract_sets(data_store)
    compute_cost_factors(data_store)

    return data_store
