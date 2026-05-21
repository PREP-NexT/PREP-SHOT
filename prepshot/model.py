#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""This module defines the PREP-SHOT model. The model is created using 
the pyoptinterface library.
"""

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

def define_active_zone_tech(model : object) -> None:
    """Pull the sparse ``(zone, tech)`` set from ``model.params`` (built
    once at file-read time by ``load_data.compute_active_zone_tech``)
    and derive the time-indexed key lists used by the constraint
    builders.

    The (zone, tech) set itself is data-property (depends only on
    ``existing_fleet`` + ``expansion_candidates``), so we compute it
    in ``load_data`` and reuse it unchanged across every PCM window.
    The (h, m, y, z, te) lists DO depend on the per-window time
    index sets, so they're materialised here.
    """
    from prepshot.load_data import compute_active_zone_tech
    if 'active_zt' not in model.params:
        # PCM windows go through ``_build_window_params`` which copies
        # params and possibly overrides ``existing_fleet`` -- recompute
        # the sparse set on the fly so the override is respected.
        compute_active_zone_tech(model.params)
    model.active_zt = model.params['active_zt']
    model.tech_zones = model.params['tech_zones']
    model.zone_techs = model.params['zone_techs']
    model.active_zt_storage = model.params['active_zt_storage']
    model.active_lines = model.params.get('active_lines') or []
    model.out_neighbours = model.params.get('out_neighbours') or {}
    model.in_neighbours = model.params.get('in_neighbours') or {}

    # Time-indexed key lists used by generation.py, heat_rate.py,
    # unit_commitment.py, demand.py, etc.
    model.active_hmyzte = [
        (h, m, y, z, te)
        for h in model.hour
        for m in model.month
        for y in model.year
        for (z, te) in model.active_zt
    ]
    model.active_hmyzte_storage = [
        (h, m, y, z, te)
        for h in model.hour
        for m in model.month
        for y in model.year
        for (z, te) in model.active_zt_storage
    ]
    # (h, m, y, z1, z2) over real lines only -- used by transmission.py
    # and demand.py.
    model.active_hmyz1z2 = [
        (h, m, y, z1, z2)
        for h in model.hour
        for m in model.month
        for y in model.year
        for (z1, z2) in model.active_lines
    ]
    model.active_yz1z2 = [
        (y, z1, z2)
        for y in model.year
        for (z1, z2) in model.active_lines
    ]


def define_complex_sets(model : object) -> None:
    """Validate that every line param needed by the constraints is
    actually present in the loaded CSVs.

    Refuses to silently default a missing entry. Each (active line,
    year) combination MUST have a row in the CSV.
    """
    # Year-indexed params: keyed by (zone1, zone2, year).
    year_indexed = (
        'transmission_line_variable_OM_cost',
        'transmission_line_fixed_OM_cost',
        'transmission_line_investment_cost',
        'transmission_line_lifetime',
    )
    # Static (no year) params: keyed by (zone1, zone2). Susceptance
    # is only required in DC-flow mode and is validated separately
    # inside dc_flow.py's gated init.
    static_indexed = (
        'transmission_line_efficiency',
        'distance',
    )
    years = list(model.params['year'])

    for k in year_indexed:
        d = model.params.get(k)
        if d is None:
            raise KeyError(
                f"{k!r} is missing from model.params; the loader "
                f"failed to read its CSV."
            )
        missing = [
            (z1, z2, y)
            for (z1, z2) in model.active_lines
            for y in years
            if (z1, z2, y) not in d
        ]
        if missing:
            raise KeyError(
                f"{k!r} has no entry for {len(missing)} "
                f"(zone1, zone2, year) tuples needed by active_lines. "
                f"First few: {missing[:5]}. Add the missing rows to "
                f"input/{k.removeprefix('transmission_line_')}.csv "
                f"(schema: zone1,zone2,year,unit,value) or drop the "
                f"line from transmission_existing / candidates."
            )

    for k in static_indexed:
        d = model.params.get(k)
        if d is None:
            raise KeyError(
                f"{k!r} is missing from model.params; the loader "
                f"failed to read its CSV."
            )
        missing = [
            (z1, z2)
            for (z1, z2) in model.active_lines
            if (z1, z2) not in d
        ]
        if missing:
            raise KeyError(
                f"{k!r} has no entry for {len(missing)} "
                f"(zone1, zone2) line(s). First few: {missing[:5]}."
            )


def define_variables(model : object) -> None:
    """Define variables for the model.

    Parameters
    ----------
    model : object
        Model to be solved.
    """
    from prepshot.utils import sparse_tupledict

    model.cap_newtech = model.add_variables(
        model.year, model.zone, model.tech, lb=0
    )
    # Sparsify cap_newline / trans_export over real (z1, z2) lines
    # only. Thai PCM goes from 222k dense pairs to ~615 lines; that
    # propagates into 6 transmission constraint families and the
    # demand power-balance neighbour quicksums.
    _new_var = lambda *_: model.add_variable(lb=0)
    model.cap_newline = sparse_tupledict(model.active_yz1z2, _new_var)
    # Sparsify gen / charge / storage variable creation: only build
    # variables for (z, te) pairs that have either existing capacity
    # at the zone or a candidate row allowing build there. Inactive
    # pairs would just be lb=ub=0 for every (h, m, y) anyway -- on
    # full-nodal Thai PCM this drops gen / storage / charge from
    # ~5M variables each to ~10k each.
    model.gen = sparse_tupledict(model.active_hmyzte, _new_var)
    # storage has hour_p anchor (hour - 1) for the cycle close.
    active_h_p_myzte = [
        (h, m, y, z, te)
        for h in model.hour_p
        for m in model.month
        for y in model.year
        for (z, te) in model.active_zt_storage
    ]
    model.storage = sparse_tupledict(active_h_p_myzte, _new_var)
    model.charge = sparse_tupledict(model.active_hmyzte_storage, _new_var)
    model.trans_export = sparse_tupledict(model.active_hmyz1z2, _new_var)
    # Load-not-served slack, one per (h, m, y, z). Created only when
    # the user opts in; demand.power_balance_rule and the cost
    # objective check ``hasattr(model, 'lns')``.
    if model.params.get('allow_load_shedding', False):
        model.lns = model.add_variables(
            model.hour, model.month, model.year, model.zone, lb=0
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
    define_active_zone_tech(model)
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
