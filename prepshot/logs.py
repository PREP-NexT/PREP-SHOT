#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""  
This module contains functions to set up logging for the model run, and to log
    the start and end of functions.
"""
import logging
import time
from pathlib import Path
import functools

def setup_logging():
    """Set up logging file to log model run.

    Parameters
    ----------
        None

    Returns
    -------
        None
    """
    # Create a directory for the log file if it doesn't exist.
    Path('log').parent.mkdir(parents=True, exist_ok=True)

    # Create a log file with a timestamp.
    log_dir = Path('log')
    log_time = time.strftime("%Y-%m-%d-%H-%M-%S")
    log_file = log_dir / f'main_{log_time}.log'

    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format='%(asctime)s %(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        force=True
    )
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s', '%Y-%m-%d %H:%M:%S'
    ))
    logging.getLogger().addHandler(console)

def log_parameter_info(config_data):
    """Log the parameters used for the model.

    Parameters
    ----------
        Config_data : dict
            Dictionary containing configuration data for 
            the model.

    Returns
    -------
        None
    """
    logging.info(
        "Set parameter solver to value %s",
        config_data['solver_parameters']['solver']
    )
    logging.info(
        "Set parameter input folder to value %s",
        config_data['general_parameters']['input_folder']
    )
    logging.info(
        "Set parameter output_filename to value %s.nc",
        config_data['general_parameters']['output_filename']
    )
    logging.info(
        "Set parameter time_length to value %s",
        config_data['general_parameters']['hour']
    )

def timer(func):
    """A decorator that times a function.

    Parameters
    ----------
    func : function
        The function to be timed.

    Returns
    -------
    function
        The decorated function.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        value = func(*args, **kwargs)
        end_time = time.perf_counter()
        run_time = end_time - start_time
        logging.info(
            "Finished %s in %.2f mins", repr(func.__name__),
            run_time/60
        )

        return value

    return wrapper
