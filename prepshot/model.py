#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""This module defines the PREP-SHOT model. The model is created using 
the pyoptinterface library.
"""

from prepshot.utils import cartesian_product
from prepshot._model.demand import AddDemandConstraints
from prepshot._model.generation import AddGenerationConstraints
from prepshot._model.cost import AddCostObjective
from prepshot._model.co2 import AddCo2EmissionConstraints
from prepshot._model.hydro import AddHydropowerConstraints
from prepshot._model.storage import AddStorageConstraints
from prepshot._model.nondispatchable import AddNondispatchableConstraints
from prepshot._model.transmission import AddTransmissionConstraints
from prepshot._model.investment import AddInvestmentConstraints
from prepshot.logs import timer
from prepshot.solver import get_solver
from prepshot.solver import set_solver_parameters

def define_model(
    params : dict
) -> object:
    """This function creates the model class depending on predefined solver.

    Parameters
    ----------
    params : dict
        parameters for the model

    Returns
    -------
    object
        A pyoptinterface Model object depending on the solver

    Raises
    ------
    ValueError
        Unsupported or undefined solver
    """
    solver = get_solver(params)
    model = solver.Model()
    model.params = params
    set_solver_parameters(model)

    return model

def define_basic_sets(model : object) -> None:
    """Define sets for the model.

    Parameters
    ----------
    model : object
        Model object to be solved.
    """
    params = model.params
    basic_sets = ["year", "zone", "tech", "hour", "month"]
    tech_types = ["storage", "nondispatchable", "dispatchable", "hydro"]

    model.tech_types = tech_types
    for set_name in basic_sets:
        setattr(model, set_name, params[set_name])
    # TODO: Generate the hour_p set based on the hour set
    model.hour_p = [0] + params['hour']
    tech_category = params['technology_type']
    # tech_category: {
    #    'Coal': 'dispatchable',
    #    'Solar': 'nondispatchable',
    #    ...
    # }
    for tech_type in tech_types:
        tech_set = [k for k, v in tech_category.items() if v == tech_type]
        setattr(model, f"{tech_type}_tech", tech_set)
    if params['isinflow']:
        model.station = params['stcd']

def define_complex_sets(model : object) -> None:
    """Create complex sets based on simple sets and some conditations. The
    existing capacity between two zones is set to empty (i.e., No value is
    filled in the Excel cell), which means that these two zones cannot have
    newly built transmission lines. If you want to enable two zones which do
    not have any existing transmission lines, to build new transmission lines
    in the planning horizon, you need to set their capacity as zero explicitly.

    Parameters
    ----------
    model : object
        Model to be solved.
    """
    trans_sets = model.params['transmission_line_existing_capacity'].keys()
    for z_i, z1_i in cartesian_product(model.zone, model.zone):
        if (z_i, z1_i) not in trans_sets:
            model.params['transmission_line_existing_capacity'][z_i, z1_i] = 0
            model.params['transmission_line_efficiency'][z_i, z1_i] = 0
            # TODO: Set the capacity of new transmission lines to 0


def define_variables(model : object) -> None:
    """Define variables for the model.

    Parameters
    ----------
    model : object
        Model to be solved.
    """

    model.cap_newtech = model.add_variables(
        model.year, model.zone, model.tech, lb=0
    )
    model.cap_newline = model.add_variables(
        model.year, model.zone, model.zone, lb=0
    )
    model.gen = model.add_variables(
        model.hour, model.month, model.year, model.zone, model.tech, lb=0
    )
    model.storage = model.add_variables(
        model.hour_p, model.month, model.year, model.zone, model.tech, lb=0
    )
    model.charge = model.add_variables(
        model.hour, model.month, model.year, model.zone, model.tech, lb=0
    )
    model.trans_export = model.add_variables(
        model.hour, model.month, model.year, model.zone, model.zone, lb=0
    )

    if model.params['isinflow']:
        model.genflow = model.add_variables(
            model.station, model.hour, model.month, model.year, lb=0
        )
        model.spillflow = model.add_variables(
            model.station, model.hour, model.month, model.year, lb=0
        )
        model.withdraw = model.add_variables(
            model.station, model.hour, model.month, model.year, lb=0
        )
        model.storage_reservoir = model.add_variables(
            model.station, model.hour_p, model.month, model.year, lb=0
        )
        model.output = model.add_variables(
            model.station, model.hour, model.month, model.year, lb=0
        )

def define_constraints(model : object) -> None:
    """Define constraints for the model.
    
    Parameters
    ----------
    model : object
        Model to be solved.
    """
    AddInvestmentConstraints(model)
    AddGenerationConstraints(model)
    AddTransmissionConstraints(model)
    AddCo2EmissionConstraints(model)
    AddNondispatchableConstraints(model)
    AddStorageConstraints(model)
    AddHydropowerConstraints(model)
    AddDemandConstraints(model)

@timer
def create_model(params : dict) -> object:
    """Create the PREP-SHOT model.

    Parameters
    ----------
    params : dict
        Dictionary of parameters for the model.

    Returns
    -------
    object
        Model object.
    """
    model = define_model(params)
    define_basic_sets(model)
    define_complex_sets(model)
    define_variables(model)
    define_constraints(model)
    AddCostObjective(model)

    return model
