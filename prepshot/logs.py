#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""This module contains functions to set up logging for the model run and to log
the start and end of functions.
"""

import logging
import time
from typing import Any
from pathlib import Path
from functools import wraps


def setup_logging() -> None:
    """Set up logging configuration for the model run.
    """
    # Ensure the log directory exists.
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

    # Set up console logging.
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s', '%Y-%m-%d %H:%M:%S'
    ))
    logging.getLogger().addHandler(console)

def log_parameter_info(config_data : dict) -> None:
    """Log key parameters used for the model.

    Parameters
    ----------
    config_data : dict
        Dictionary containing configuration data for the model.
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

def timer(func : object) -> Any:
    """Decorator to log the start and end of a function and its runtime.

    Parameters
    ----------
    func : function
        The function to be decorated.

    Returns
    ----------
    Any
        The return value of decorated function.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        logging.info("Start running %s", repr(func.__name__))
        start_time = time.time()
        result = func(*args, **kwargs)
        run_time = time.time() - start_time
        logging.info(
            "Finished %s in %.2f seds", repr(func.__name__),
            run_time
        )
        return result
    return wrapper
