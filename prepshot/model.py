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
from prepshot._model.transmission import AddTransmissionConstraints
from prepshot._model.investment import AddInvestmentConstraints
from prepshot._model.finance import AddFinanceConstraints
from prepshot._model.reserve import AddReserveConstraints
from prepshot._model.dc_flow import AddDCFlowConstraints
from prepshot._model.unit_commitment import AddUnitCommitmentConstraints
from prepshot._model.heat_rate import AddHeatRateConstraints
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
    for set_name in basic_sets:
        setattr(model, set_name, params[set_name])
    # hour_p is the hour set augmented with one "previous" hour at the
    # front, used as the anchor for storage / reservoir balances:
    # storage[h] = storage[h-1] + ... links each hour to the prior one,
    # and storage[hour_p[0]] = initial_storage closes the chain.
    # For CEM (hour starts at 1) hour_p[0] = 0; for PCM windows
    # starting at h_first, hour_p[0] = h_first - 1, so the prior-hour
    # anchor lives just outside the window.
    hours_list = list(params['hour'])
    model.hour_p = [hours_list[0] - 1] + hours_list

    # PyPSA-style: a free-form `carrier` string plus per-tech behavior
    # flags. Hydropower is a special-cased carrier (carrier == 'hydro')
    # so the existing reservoir / water-flow constraints continue to
    # apply unchanged. Other behaviors (VRE, storage, must-run) are
    # driven by the boolean flag columns rather than a fixed type enum.
    techs_df = params['technologies']

    def _tech_filter(mask):
        return techs_df.loc[mask, 'tech'].tolist()

    model.hydro_tech = _tech_filter(techs_df['carrier'] == 'hydro')
    model.storage_tech = _tech_filter(techs_df['is_storage'].astype(bool))
    # PyPSA-style: variable / must-run / curtailable behaviors are no
    # longer flag-driven. Any tech can have a time-varying max/min
    # generation profile via tech_max_gen_profile.csv /
    # tech_min_gen_profile.csv. The unified per-tech generation bound
    # constraint lives in AddGenerationConstraints.
    # `dispatchable_tech` = anything that's not hydro and not storage
    # (i.e. its generation is bounded by cap × p_max_pu).
    special_mask = (
        (techs_df['carrier'] == 'hydro')
        | techs_df['is_storage'].astype(bool)
    )
    model.dispatchable_tech = _tech_filter(~special_mask)
    model.tech_types = ['dispatchable_tech', 'hydro_tech', 'storage_tech']
    if params['isinflow']:
        # Hydro plants are first-class techs (carrier='hydro');
        # model.station is the list of those tech names for
        # backwards-compat with the hydro module.
        model.station = model.hydro_tech

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
    # transmission_existing is keyed by (zone1, zone2, commission_year);
    # auto-pad missing zone pairs (e.g. self-loops) with a sentinel
    # commission_year=0 entry of value=0. Efficiency padding uses the
    # 2-tuple key it always had.
    trans_pairs = {(z1, z2) for (z1, z2, _cy) in
                   model.params['transmission_existing'].keys()}
    for z_i, z1_i in cartesian_product(model.zone, model.zone):
        if (z_i, z1_i) not in trans_pairs:
            model.params['transmission_existing'][z_i, z1_i, 0] = 0
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

    # Reserve variables are created INSIDE AddReserveConstraints (v1.16)
    # because the product set comes from the eligibility CSV at runtime
    # rather than being a fixed list here. Skip if reserve is off.

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
    AddDCFlowConstraints(model)
    AddCo2EmissionConstraints(model)
    AddStorageConstraints(model)
    AddHydropowerConstraints(model)
    AddReserveConstraints(model)
    AddUnitCommitmentConstraints(model)
    AddHeatRateConstraints(model)
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
    # Optional public-debt accounting: only wired up when the user
    # supplies a finance dataset (public_debt_ratio + cost-of-capital
    # tables). Reads cost_newtech_breakdown built by AddCostObjective.
    if params.get('public_debt_ratio'):
        AddFinanceConstraints(model)

    return model
