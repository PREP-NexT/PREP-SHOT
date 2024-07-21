#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""This module contains functions for setting params and configuring
logging. 
"""

import logging
import argparse
from os import path, makedirs
from typing import Dict, List, Union, Tuple

import pandas as pd

from prepshot.load_data import load_json, extract_config_data, process_data
from prepshot.logs import setup_logging, log_parameter_info


def parse_cli_arguments(params_list : List[str]) -> argparse.Namespace:
    """Parse command-line arguments from a list of parameter names.

    Parameters
    ----------
    params_list : List[str]
        List of parameter names.

    Returns
    -------
    argparse.Namespace
        Parsed command-line arguments.
    """
    parser = argparse.ArgumentParser(
        description='Command-line arguments parser'
    )
    for param in params_list:
        parser.add_argument(
            f'--{param}', type=str, default=None, 
            help=f'Suffix of input paramemeters: {param}'
        )
    return parser.parse_args()


def initialize_environment(
    config_files : Dict[str, str]
) -> Dict[
        str,
        Union[
            int, float, bool, str, argparse.Namespace, pd.DataFrame, pd.Series,
            List[Union[str, int]],
            Dict[
                Union[str, int, Tuple[Union[str, int]]],
                Union[str, float]
            ]
        ]
    ]:
    """Load configuration data, set up logging, and process input params.
    
    Parameters
    ----------
    config_files : dict
        Dictionary containing paths to params and configuration files.

    Returns
    -------
    Dict[
        str,
        Union[
            int, float, bool, str, argparse.Namespace, pd.DataFrame, pd.Series,
            List[Union[str, int]],
            Dict[
                Union[str, int, Tuple[Union[str, int]]],
                Union[str, float]
            ]
        ]
    ]
        Dictionary containing the global params.
    """
    params_filename = config_files['params_filename']
    config_filename = config_files['config_filename']
    filepath = config_files['filepath']

    config_data = load_json(config_filename)
    required_config_data = extract_config_data(config_data)

    setup_logging()
    log_parameter_info(config_data)

    params = load_json(params_filename)
    params_list = [params[key]["file_name"] for key in params]
    args = parse_cli_arguments(params_list)

    # Determine the input folder path.
    input_filename = str(config_data['general_parameters']['input_folder'])
    input_filepath = path.join(filepath, input_filename)

    # Update params with command-line arguments if provided.
    for param in params.keys():
        if getattr(args, param) is not None:
            params[param]["file_name"] = params[param]["file_name"] \
                + f"_{getattr(args, param)}"

    # Load and process params data
    params = process_data(params, input_filepath)
    params['command_line_args'] = args

    # Combine the configuration data with processed parameter data.
    params.update(required_config_data)

    # Determine the output folder path.
    output_folder = './'                                                      \
        + str(config_data['general_parameters']['output_folder'])
    if not path.exists(output_folder):
        makedirs(output_folder)
        logging.warning(
            "Folder %s created", output_folder
        )

    # Determine the output filename.
    output_filename =  output_folder + '/'                                    \
        + str(config_data['general_parameters']['output_filename'])

    params['output_filename'] = output_filename
    return params
