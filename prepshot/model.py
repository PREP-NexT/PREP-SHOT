""" 
This module defines the PREP-SHOT model. The model is created using 
the pyoptinterface library.
"""
from itertools import product
import pyoptinterface as poi
from pyoptinterface import mosek
from pyoptinterface import gurobi
from pyoptinterface import highs
from pyoptinterface import copt
from prepshot.rules import RuleContainer

def define_model(para):
    """This function defines the model using the pyoptinterface library.

    Parameters
    ----------
    para : dict
        parameters for the model

    Returns
    -------
    pyoptinterface._src.mosek.Model
        A pyoptinterface Model object

    Raises
    ------
    ValueError
        Unsupported solver
    """
    solver_map = {
        'mosek': mosek,
        'gurobi': gurobi,
        'highs': highs,
        'copt': copt
    }

    solver = para.get('solver')
    if solver in solver_map:
        poi_solver = solver_map[solver]
    else:
        raise ValueError(f"Unsupported solver: {solver}")

    model = poi_solver.Model()
    return model

def define_sets(model, para):
    """Define sets for the model.

    Parameters
    ----------
    model : pyoptinterface._src.mosek.Model
        Model to be solved.
    para : dict
        Dictionary of parameters for the model.

    Returns
    -------
    None
    """
    basic_sets = ["year", "zone", "tech", "hour", "month"]
    tech_types = ["storage", "nondispatchable", "dispatchable", "hydro"]

    model.tech_types = tech_types
    for set_name in basic_sets:
        setattr(model, set_name, para[set_name])
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

def create_tuples(model, para):
    """Create tuples for the model. 

    Note: The existing capacity between two zones is set to empty 
    (i.e., No value is filled in the Excel cell), which means that these two 
    zones cannot have newly built transmission lines. If you want to enable 
    two zones which do not have any existing transmission lines, 
    to build new transmission lines in the planning horizon, you need to set 
    their capacity as zero explicitly.

    Parameters
    ----------
    model : pyoptinterface._src.mosek.Model
        Model to be solved.

    Returns
    -------
    None
    """
    def cartesian_product(*args):
        # [1, 2], [7, 8] -> [(1, 7), (1, 8), (2, 7), (2, 8)]
        return list(product(*args))
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

def define_variables(model, para):
    """Define variables for the model.

    Parameters
    ----------
    model : pyoptinterface._src.mosek.Model
        Model to be solved.
    para : dict
        Dictionary of parameters for the model.
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

    if para['isinflow']:
        model.naturalinflow = model.add_variables(
            model.station_hour_month_year_tuples, lb=-float('inf')
        )
        model.inflow = model.add_variables(
            model.station_hour_month_year_tuples, lb=-float('inf')
        )
        model.outflow = model.add_variables(
            model.station_hour_month_year_tuples, lb=0
        )
        model.genflow = model.add_variables(
            model.station_hour_month_year_tuples, lb=0
        )
        model.spillflow = model.add_variables(
            model.station_hour_month_year_tuples, lb=0
        )
        model.withdraw = model.add_variables(
            model.station_hour_month_year_tuples, lb=0
        )
        model.storage_reservoir = model.add_variables(
            model.station_hour_p_month_year_tuples, lb=0
        )
        model.output = model.add_variables(
            model.station_hour_month_year_tuples, lb=0
        )


def define_constraints(model, para):
    """Define constraints for the model.
    
    Parameters
    ----------
    model : pyoptinterface._src.mosek.Model
        Model to be solved.
    para : dict
        Dictionary of parameters for the model.

    Returns:
    None
    """
    rules = RuleContainer(para, model)

    model.total_cost_cons = rules.cost_rule()
    model.power_balance_cons = poi.make_tupledict(
        model.hour_month_year_zone_tuples, rule=rules.power_balance_rule
    )
    model.trans_capacity_cons = poi.make_tupledict(
        model.year_zone_zone_tuples, rule=rules.trans_capacity_rule
    )
    model.trans_physical_cons = poi.make_tupledict(
        model.year_zone_zone_tuples, rule=rules.trans_physical_rule
    )
    model.trans_balance_cons = poi.make_tupledict(
        model.hour_month_year_zone_zone_tuples, rule=rules.trans_balance_rule
    )
    model.trans_up_bound_cons = poi.make_tupledict(
        model.hour_month_year_zone_zone_tuples, rule=rules.trans_up_bound_rule
    )
    model.gen_up_bound_cons = poi.make_tupledict(
        model.hour_month_year_zone_tech_tuples, rule=rules.gen_up_bound_rule
    )
    model.tech_up_bound_cons = poi.make_tupledict(
        model.year_zone_tech_tuples, rule=rules.tech_up_bound_rule
    )
    model.new_tech_up_bound_cons = poi.make_tupledict(
        model.year_zone_tech_tuples, rule=rules.new_tech_up_bound_rule
    )
    model.new_tech_low_bound_cons = poi.make_tupledict(
        model.year_zone_tech_tuples, rule=rules.new_tech_low_bound_rule
    )
    model.tech_lifetime_cons = poi.make_tupledict(
        model.year_zone_tech_tuples, rule=rules.tech_lifetime_rule
    )
    model.ramping_up_cons = poi.make_tupledict(
        model.hour_month_year_zone_tech_tuples, rule=rules.ramping_up_rule
    )
    model.ramping_down_cons = poi.make_tupledict(
        model.hour_month_year_zone_tech_tuples, rule=rules.ramping_down_rule
    )
    model.cost_var_cons = rules.var_cost_rule()
    model.newtech_cost_cons = rules.newtech_cost_rule()
    model.newline_cost_cons = rules.newline_cost_rule()
    model.fix_cost_cons = rules.fix_cost_rule()
    model.remaining_capacity_cons = poi.make_tupledict(
        model.year, model.zone, model.tech, rule=rules.remaining_capacity_rule
    )
    model.emission_limit_cons = poi.make_tupledict(
        model.year, rule=rules.emission_limit_rule
    )
    model.emission_calc_cons = poi.make_tupledict(
        model.year, rule=rules.emission_calc_rule
    )
    model.emission_calc_by_zone_cons = poi.make_tupledict(
        model.year_zone_tuples, rule=rules.emission_calc_by_zone_rule
    )
    model.hydro_output_cons = poi.make_tupledict(
        model.hour_month_year_zone_tuples, rule=rules.hydro_output_rule
    )

    if model.nondispatchable_tech != 0:
        model.renew_gen_cons = poi.make_tupledict(
            model.hour_month_year_zone_nondispatchable_tuples,
            rule=rules.renew_gen_rule
        )

    if model.storage_tech != 0:
        model.energy_storage_balance_cons = poi.make_tupledict(
            model.hour_month_year_zone_storage_tuples,
            rule=rules.energy_storage_balance_rule
        )
        model.init_energy_storage_cons = poi.make_tupledict(
            model.month_year_zone_storage_tuples,
            rule=rules.init_energy_storage_rule
        )
        model.end_energy_storage_cons = poi.make_tupledict(
            model.month_year_zone_storage_tuples,
            rule=rules.end_energy_storage_rule
        )
        model.energy_storage_up_bound_cons = poi.make_tupledict(
            model.hour_month_year_zone_storage_tuples,
            rule=rules.energy_storage_up_bound_rule
        )
        model.energy_storage_gen_cons = poi.make_tupledict(
            model.hour_month_year_zone_storage_tuples,
            rule=rules.energy_storage_gen_rule
        )

    if para['isinflow']:
        model.natural_inflow_cons = poi.make_tupledict(
            model.station_hour_month_year_tuples,
            rule=rules.natural_inflow_rule
        )
        model.total_inflow_cons = poi.make_tupledict(
            model.station_hour_month_year_tuples,
            rule=rules.total_inflow_rule
        )
        model.water_balance_cons = poi.make_tupledict(
            model.station_hour_month_year_tuples,
            rule=rules.water_balance_rule
        )
        model.discharge_cons = poi.make_tupledict(
            model.station_hour_month_year_tuples,
            rule=rules.discharge_rule
        )
        model.outflow_low_bound_cons = poi.make_tupledict(
            model.station_hour_month_year_tuples,
            rule=rules.outflow_low_bound_rule
        )
        model.outflow_up_bound_cons = poi.make_tupledict(
            model.station_hour_month_year_tuples,
            rule=rules.outflow_up_bound_rule
        )
        model.storage_low_bound_cons = poi.make_tupledict(
            model.station_hour_month_year_tuples,
            rule=rules.storage_low_bound_rule
        )
        model.storage_up_bound_cons = poi.make_tupledict(
            model.station_hour_month_year_tuples,
            rule=rules.storage_up_bound_rule
        )
        model.output_low_bound_cons = poi.make_tupledict(
            model.station_hour_month_year_tuples,
            rule=rules.output_low_bound_rule
        )
        model.output_up_bound_cons = poi.make_tupledict(
            model.station_hour_month_year_tuples,
            rule=rules.output_up_bound_rule
        )
        model.output_calc_cons = poi.make_tupledict(
            model.station_hour_month_year_tuples,
            rule=rules.output_calc_rule
        )
        model.init_storage_cons = poi.make_tupledict(
            model.station_month_year_tuples,
            rule=rules.init_storage_rule
        )
        model.end_storage_cons = poi.make_tupledict(
            model.station_month_year_tuples,
            rule=rules.end_storage_rule
        )
        model.income_cons = rules.income_rule()

    # define expression for breakdown output
    model.cost_var_breakdown = poi.make_tupledict(
        model.year_zone_tech_tuples, rule=rules.cost_var_breakdown_ep
    )
    model.cost_fix_breakdown = poi.make_tupledict(
        model.year_zone_tech_tuples, rule=rules.cost_fix_breakdown_ep
    )
    model.cost_newtech_breakdown = poi.make_tupledict(
        model.year_zone_tech_tuples, rule=rules.cost_newtech_breakdown_ep
    )
    model.cost_newline_breakdown = poi.make_tupledict(
        model.year_zone_zone_tuples, rule=rules.cost_newline_breakdown_ep
    )
    model.carbon_breakdown = poi.make_tupledict(
        model.year_zone_tech_tuples, rule=rules.carbon_breakdown_ep
    )

def create_model(para):
    """Create the PREP-SHOT model.

    Parameters
    ----------
    para : dict
        Dictionary of parameters for the model.

    Returns
    -------
    pyoptinterface._src.mosek.Model
        A pyoptinterface Model object.
    """
    # Define a pyomo ConcreteModel object.
    model = define_model(para)

    # Define sets for the model.
    define_sets(model, para)

    # Create tuples for the model.
    create_tuples(model, para)

    # Define variables for the model.
    define_variables(model, para)

    obj = poi.ExprBuilder()
    obj += model.cost
    # Define objective function for the model.
    model.set_objective(obj, sense=poi.ObjectiveSense.Minimize)

    # Define constraints for the model.
    define_constraints(model, para)

    return model
