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
the model, loads the configuration data, parses command line arguments, 
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
    2024-07-11
"""
import os

from prepshot.set_up import initialize_environment
from prepshot.model import create_model
from prepshot.solver import solve_model
from prepshot.output_data import save_result

# Name of the configuration and parameters files located in the same directory
# as `run.py`.
CONFIG_FILENAME = 'config.json'
PARAMS_FILENAME = 'params.json'


def main():
    """Main function for the PREP-SHOT model.
    """
    root_dir = os.path.dirname(os.path.abspath(__file__))
    config_files = {
        "filepath": root_dir,
        "config_filename": os.path.join(root_dir, CONFIG_FILENAME),
        "params_filename": os.path.join(root_dir, PARAMS_FILENAME),
    }
    parameters = initialize_environment(config_files)
    model = create_model(parameters)
    solved = solve_model(model, parameters)
    if solved:
        save_result(model)


if __name__ == "__main__":
    main()
