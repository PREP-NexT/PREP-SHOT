#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""This module contains the definition of the solver class.""" 

import logging
import pyoptinterface as poi
from pyoptinterface import mosek
from pyoptinterface import gurobi
from pyoptinterface import highs
from pyoptinterface import copt

from prepshot.logs import timer
from prepshot._model.head_iteration import run_model_iteration

def get_solver(params):
    """Retrieve the solver object based on parameters.
    
    Parameters
    ----------
    params : dict
        Configuration dictionary with solver details.
    
    Returns
    -------
    pyoptinterface._src.solver
        Solver object.
    """
    solver_map = {
        'mosek': mosek,
        'gurobi': gurobi,
        'highs': highs,
        'copt': copt
    }

    solver = params['solver']['solver']
    if solver in solver_map:
        poi_solver = solver_map[solver]
    else:
        raise ValueError(f"Unsupported solver: {solver}")
    if not poi_solver.autoload_library():
        logging.warning(
            "%s library failed to load automatically." 
            + "Attempting to load manually.", solver
        )
        if 'solver_path' not in params:
            raise ValueError(
                f"Solver path for {solver} not found in the configuration."
            )
        if not poi_solver.load_library(params['solver']['solver_path']):
            raise ValueError(f"Failed to load {solver} library.")
        logging.info("Loaded %s library manually.", solver)
    else:
        logging.info("Loaded %s library automatically.", solver)

    return poi_solver

def set_solver_parameters(model):
    """Set the solver-specific parameters for the model.
    
    Parameters
    ----------
    model : pyoptinterface._src.solver.Model 
        Model to configurable.
    """
    for key, value in model.para['solver'].items():
        if key not in ('solver', 'solver_path'):
            model.set_raw_parameter(key, value)

@timer
def solve_model(model, params):
    """Solve the model using the provided parameters.

    Parameters
    ----------
    model : pyoptinterface._src.solver.Model
        Model to solve.
    params : dict
        Configuration parameters for solving the model.

    Returns
    -------
    bool
        True if the model is solved optimally, False otherwise.
    """
    if params['isinflow']:
        error_threshold = params['error_threshold']
        iteration_number = params['iteration_number']
        return run_model_iteration(
            model, params, error_threshold, iteration_number
        )
    model.optimize()
    status = model.get_model_attribute(poi.ModelAttribute.TerminationStatus)
    if status != poi.TerminationStatusCode.OPTIMAL:
        return False
    return True
