#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""This module contains functions for setting parameters and configuring
logging. 
"""

import logging
import argparse
from os import path, makedirs

from prepshot.load_data import load_json, extract_config_data, process_data
from prepshot.logs import setup_logging, log_parameter_info


def parse_cli_arguments(params_list):
    """Parse command-line arguments from a list of parameter names.

    Parameters
    ----------
    params_list : list
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


def initialize_environment(config_files):
    """Load configuration data, set up logging, and process input parameters.
    
    Parameters
    ----------
    config_files : dict
        Dictionary containing paths to parameters and configuration files.

    Returns
    -------
    tuple
        A tuple containing the parameters dictionary and the output filename.
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

    # Update parameters with command-line arguments if provided.
    for param in params.keys():
        if getattr(args, param) is not None:
            params[param]["file_name"] = params[param]["file_name"] \
                + f"_{getattr(args, param)}"

    # Load and process parameters data
    parameters = process_data(params, input_filepath)
    parameters['command_line_args'] = args

    # Combine the configuration data with processed parameter data.
    parameters.update(required_config_data)

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
 
    parameters['output_filename'] = output_filename
    return parameters
