#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module contains utility functions to set the parameters and logging. 
"""

import logging
import argparse
from os import path, makedirs

from prepshot.load_data import load_json, get_required_config_data, load_data
from prepshot.logs import setup_logging, log_parameter_info


def parse_arguments(params_list):
    """Parse arguments from list of parameters.

    Parameters
    ----------
    params_list : list
        List of parameters.

    Returns
    -------
    argparse.Namespace
        Arguments parsed by argparse.
    """
    parser = argparse.ArgumentParser(description='filename')
    for param in params_list:
        parser.add_argument(
            f'--{param}', type=str, default=None, 
            help=f'The suffix of input paramemeters: {param}'
        )
    return parser.parse_args()


def setup(config_files):
    """Load data and set up logging.
    
    Parameters
    ----------
    config_files : dict
        Path of parameters files and configuration files.

    Returns
    -------
    tuple
        A tuple containing the parameters dictionary and 
            the output filename.
    """
    params_filename = config_files['params_filename']
    config_filename = config_files['config_filename']
    filepath = config_files['filepath']

    config_data = load_json(config_filename)
    required_config_data = get_required_config_data(config_data)

    setup_logging()
    log_parameter_info(config_data)

    params = load_json(params_filename)
    params_list = [params[key]["file_name"] for key in params]
    args = parse_arguments(params_list)

    # Get the path to input folder.
    input_filename = str(config_data['general_parameters']['input_folder'])
    input_filepath = path.join(filepath, input_filename)

    # update command-line arguments to set different scenarios easily.
    # Load parameters by parsing params.json and command-line arguments.
    # command-line arguments will overwrite the parameters in params.json.
    for param in params.keys():
        if getattr(args, param) is not None:
            params[param]["file_name"] = params[param]["file_name"] \
                + f"_{getattr(args, param)}"

    # Load parameters data
    parameters = load_data(params, input_filepath)
    parameters['command_line_args'] = args

    # Combine the configuration data and parameters data.
    parameters.update(required_config_data)

    # Get the output folder.
    output_folder = './'                                                      \
        + str(config_data['general_parameters']['output_folder'])
    if not path.exists(output_folder):
        makedirs(output_folder)
        logging.warning(
            "Folder %s created", output_folder
        )

    # Get the output filename.
    output_filename =  output_folder + '/'                                    \
        + str(config_data['general_parameters']['output_filename'])
 
    parameters['output_filename'] = output_filename
    return parameters
