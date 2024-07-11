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

def define_model(para):
    """This function creates the model class depending on predefined solver.

    Parameters
    ----------
    para : dict
        parameters for the model

    Returns
    -------
    pyoptinterface._src.solver.Model
        A pyoptinterface Model object depending on the solver

    Raises
    ------
    ValueError
        Unsupported or undefined solver
    """
    solver = get_solver(para)
    model = solver.Model()
    model.para = para
    set_solver_parameters(model)

    return model

def define_basic_sets(model):
    """Define sets for the model.

    Parameters
    ----------
    model : pyoptinterface._src.solver.Model
        Model to be solved.
    """
    para = model.para
    basic_sets = ["year", "zone", "tech", "hour", "month"]
    tech_types = ["storage", "nondispatchable", "dispatchable", "hydro"]

    model.tech_types = tech_types
    for set_name in basic_sets:
        setattr(model, set_name, para[set_name])
    # TODO: Generate the hour_p set based on the hour set
    model.hour_p = [0] + para['hour']
    tech_category = para['technology_type']
    # tech_category: {
    #    'Coal': 'dispatchable',
    #    'Solar': 'nondispatchable',
    #    ...
    # }
    for tech_type in tech_types:
        tech_set = [k for k, v in tech_category.items() if v == tech_type]
        setattr(model, f"{tech_type}_tech", tech_set)
    if para['isinflow']:
        model.station = para['stcd']

def define_complex_sets(model):
    """Create complex sets based on simple sets and some conditations.
    Note: The existing capacity between two zones is set to empty 
    (i.e., No value is filled in the Excel cell), which means that these two 
    zones cannot have newly built transmission lines. If you want to enable 
    two zones which do not have any existing transmission lines, 
    to build new transmission lines in the planning horizon, you need to set 
    their capacity as zero explicitly.

    Parameters
    ----------
    model : pyoptinterface._src.solver.Model
        Model to be solved.
    """
    para = model.para
    h = model.hour
    hp = model.hour_p
    m = model.month
    y = model.year
    z = model.zone
    te = model.tech
    st = model.storage_tech
    nd = model.nondispatchable_tech

    model.hour_month_year_tuples = cartesian_product(h, m, y)
    model.hour_month_tuples = cartesian_product(h, m)
    model.hour_month_year_zone_storage_tuples = \
        cartesian_product(h, m, y, z, st)
    model.hour_month_year_zone_nondispatchable_tuples = \
        cartesian_product(h, m, y, z, nd)
    model.hour_month_year_zone_tech_tuples = cartesian_product(h, m, y, z, te)
    model.hour_month_year_zone_tuples = cartesian_product(h, m, y, z)
    trans_sets = para['transmission_line_existing_capacity'].keys()
    model.year_zone_zone_tuples = [
        (y_i, z_i, z1_i) for y_i, z_i, z1_i in cartesian_product(y, z, z)
        if (z_i, z1_i) in trans_sets
    ]
    model.hour_month_year_zone_zone_tuples = [
        (h_i, m_i, y_i, z_i, z1_i)
        for h_i, m_i, y_i, z_i, z1_i in cartesian_product(h, m, y, z, z)
        if (z_i, z1_i) in trans_sets
    ]
    model.hour_month_tech_tuples = cartesian_product(h, m, te)
    model.hour_p_month_year_zone_tuples = cartesian_product(hp, m, y, z)
    model.hour_p_month_year_zone_tech_tuples = \
        cartesian_product(hp, m, y, z, te)
    model.hour_p_month_year_zone_storage_tuples = \
        cartesian_product(hp, m, y, z, st)
    model.month_year_zone_tuples = cartesian_product(m, y, z)
    model.month_year_zone_storage_tuples = cartesian_product(m, y, z, st)
    model.year_zone_tuples = cartesian_product(y, z)
    model.year_zone_tech_tuples = cartesian_product(y, z, te)
    model.year_tech_tuples = cartesian_product(y, te)

    if para['isinflow']:
        s = model.station
        model.station_hour_month_year_tuples = cartesian_product(s, h, m, y)
        model.station_hour_p_month_year_tuples = cartesian_product(s, hp, m, y)
        model.station_month_year_tuples = cartesian_product(s, m, y)

def define_variables(model):
    """Define variables for the model.

    Parameters
    ----------
    model : pyoptinterface._src.solver.Model
        Model to be solved.
    """
    model.cost = model.add_variable(lb=0)
    model.cost_var = model.add_variable(lb=0)
    model.cost_fix = model.add_variable(lb=0)
    model.cost_newtech = model.add_variable(lb=0)
    model.cost_newline = model.add_variable(lb=0)
    model.income = model.add_variable(lb=0)
    model.cap_existing = model.add_variables(model.year_zone_tech_tuples, lb=0)
    model.cap_newtech = model.add_variables(model.year_zone_tech_tuples, lb=0)
    model.cap_newline = model.add_variables(model.year_zone_zone_tuples, lb=0)
    model.cap_lines_existing = model.add_variables(
        model.year_zone_zone_tuples, lb=0
    )
    model.carbon = model.add_variables(model.year, lb=0)
    model.carbon_capacity = model.add_variables(model.year_zone_tuples, lb=0)
    model.gen = model.add_variables(
        model.hour_month_year_zone_tech_tuples, lb=0
    )
    model.storage = model.add_variables(
        model.hour_p_month_year_zone_tech_tuples, lb=0
    )
    model.charge = model.add_variables(
        model.hour_month_year_zone_tech_tuples, lb=0
    )
    model.trans_export = model.add_variables(
        model.hour_month_year_zone_zone_tuples, lb=0
    )
    model.trans_import = model.add_variables(
        model.hour_month_year_zone_zone_tuples, lb=0
    )
    model.remaining_technology = model.add_variables(
        model.year_zone_tech_tuples, lb=0
    )

#    if para['isinflow']:
#        model.genflow = model.add_variables(
#            model.station_hour_month_year_tuples, lb=0
#        )
#        model.spillflow = model.add_variables(
#            model.station_hour_month_year_tuples, lb=0
#        )
#        model.withdraw = model.add_variables(
#            model.station_hour_month_year_tuples, lb=0
#        )
#        model.storage_reservoir = model.add_variables(
#            model.station_hour_p_month_year_tuples, lb=0
#        )
#        model.output = model.add_variables(
#            model.station_hour_month_year_tuples, lb=0
#        )

def define_constraints(model):
    """Define constraints for the model.
    
    Parameters
    ----------
    model : pyoptinterface._src.solver.Model
        Model to be solved.
    """
    AddDemandConstraints(model)
    AddGenerationConstraints(model)
    AddTransmissionConstraints(model)
    AddInvestmentConstraints(model)
    AddCo2EmissionConstraints(model)
    AddNondispatchableConstraints(model)
    AddStorageConstraints(model)
    AddHydropowerConstraints(model)

@timer
def create_model(para):
    """Create the PREP-SHOT model.

    Parameters
    ----------
    para : dict
        Dictionary of parameters for the model.

    Returns
    -------
    pyoptinterface._src.solver.Model
        A pyoptinterface Model object.
    """
    model = define_model(para)
    define_basic_sets(model)
    define_complex_sets(model)
    define_variables(model)
    define_constraints(model)
    AddCostObjective(model)

    return model
