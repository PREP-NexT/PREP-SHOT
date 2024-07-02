#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" 
This module contains functions to parse parameters from command line. 
"""
import argparse

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
