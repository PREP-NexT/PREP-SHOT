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

def get_solver(para):
    """Get the solver object.
    
    Parameters
    ----------
    para : dict
        Dictionary containing parameters.
    
    Returns
    -------
    pyoptinterface._src.solver
        Solver object depending on the predefined solver.
    """
    solver_map = {
        'mosek': mosek,
        'gurobi': gurobi,
        'highs': highs,
        'copt': copt
    }

    solver = para['solver']['solver']
    if solver in solver_map:
        poi_solver = solver_map[solver]
    else:
        raise ValueError(f"Unsupported solver: {solver}")
    if not poi_solver.autoload_library():
        logging.warning(
            "%s library failed to load automatically." 
            + "Attempting to load manually.", solver
        )
        if 'solver_path' not in para:
            raise ValueError(
                f"Solver path for {solver} not found in the configuration."
            )
        if not poi_solver.load_library(para['solver']['solver_path']):
            raise ValueError(f"Failed to load {solver} library.")
        logging.info("Loaded %s library manually.", solver)
    else:
        logging.info("Loaded %s library automatically.", solver)

    return poi_solver

def set_solver_parameters(model):
    """Set the solver parameters.
    
    Parameters
    ----------
    model : pyoptinterface._src.solver.Model 
        Model to be solved.
    """
    # set the value of the solver-specific parameters
    for key, value in model.para['solver'].items():
        if key not in ('solver', 'solver_path'):
            model.set_raw_parameter(key, value)

@timer
def solve_model(model, parameters):
    """Solve the model.

    Parameters
    ----------
    model : pyoptinterface._src.solver.Model
        Model to be solved.
    parameters : dict
        Dictionary of parameters for the model.

    Returns
    -------
    bool
        True if the model is solved, False otherwise.
    """
    if parameters['isinflow']:
        error_threshold = parameters['error_threshold']
        iteration_number = parameters['iteration_number']
        return run_model_iteration(
            model, parameters, error_threshold, iteration_number
        )
    model.optimize()
    status = model.get_model_attribute(poi.ModelAttribute.TerminationStatus)
    if status != poi.TerminationStatusCode.OPTIMAL:
        return False
    return True
