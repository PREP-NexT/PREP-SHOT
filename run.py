#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
run.py: PREP-SHOT Entry Point
=============================

██████   ██████   ███████  ██████            ███████  █     █   █████   ███████
█     █  █     █  █        █     █           █        █     █  █     █     █
█     █  █     █  █        █     █           █        █     █  █     █     █
██████   ██████   ███████  ██████   ███████  ███████  ███████  █     █     █
█        █   █    █        █                       █  █     █  █     █     █
█        █    █   █        █                       █  █     █  █     █     █
█        █     █  ███████  █                 ███████  █     █   █████      █

This script serves as the main entry point for the PREP-SHOT. It initializes
the PREP-SHOT, loads the configuration data, parses command line arguments, 
and starts the primary process.

Usage:
    To run this script from the command line, use the following command:
        $ python run.py --<param> <value>
    or simply:
        $ python run.py
    or:
        $ ./run.py

Author:
    Zhanwei LIU <liuzhanwei@u.nus.edu>
    
Last Updated:
    2024-07-01
"""

import logging
from os import path, makedirs

from prepshot.load_data import load_json, get_required_config_data, load_data
from prepshot.logs import setup_logging, log_parameter_info
from prepshot.model import create_model
from prepshot.parameters import parse_arguments
from prepshot.utils import (
    extract_result, update_output_filename, solve_model, save_to_excel
)

# Name of the configuration file and parameters file in the
# same directory with `run.py`.
CONFIG_FILENAME = 'config.json'
PARAMS_FILENAME = 'params.json'

def setup(params_data, args):
    """Load data and set up logging.
    
    Parameters
    ----------
    params_data : dict
        Dictionary of parameters data.
    args : argparse.Namespace
        Arguments parsed by argparse.

    Returns
    -------
    tuple
        A tuple containing the parameters dictionary and 
            the output filename.
    """
    config_data = load_json(CONFIG_FILENAME)
    required_config_data = get_required_config_data(config_data)

    # Get the path to input folder.
    filepath = path.dirname(path.abspath(__file__))
    input_filename = str(config_data['general_parameters']['input_folder'])
    input_filepath = path.join(filepath, input_filename)

    # update command-line arguments to set different scenarios easily.
    for param in params_data.keys():
        if getattr(args, param) is not None:
            params_data[param]["file_name"] = params_data[param]["file_name"] \
                + f"_{getattr(args, param)}"

    # Load parameters data
    parameters = load_data(params_data, input_filepath)

    # Combine the configuration data and parameters data.
    parameters.update(required_config_data)

    setup_logging()
    log_parameter_info(config_data)

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

    return parameters, output_filename

def run_model(parameters, output_filename, args):
    """Create and solve the model.

    Parameters
    ----------
    parameters : dict
        Dictionary of parameters for the model.
    output_filename : str
        The name of the output file.
    args : argparse.Namespace
        Arguments parsed by argparse.
    """
    model = create_model(parameters)
    output_filename = update_output_filename(output_filename, args)
    solved = solve_model(model, parameters)
    if solved:
        ds = extract_result(model, isinflow=parameters['isinflow'])
        ds.to_netcdf(f'{output_filename}.nc')
        logging.info(
            "Results are written to %s.nc", output_filename
        )
        save_to_excel(ds, output_filename)
        logging.info("Results are written to separate excel files")

def main():
    """The entry function of the PREP-SHOT model.
    """
    # Load parameters by parsing params.json and command-line arguments.
    # command-line arguments will overwrite the parameters in params.json.
    params_data = load_json(PARAMS_FILENAME)
    params_list = [params_data[key]["file_name"] for key in params_data]
    args = parse_arguments(params_list)

    # Set up model.
    parameters, output_filename = setup(params_data, args)

    # Run model.
    run_model(parameters, output_filename, args)
    
if __name__ == "__main__":
    main()
