from pyomo.environ import Constraint, NonNegativeReals, Objective, Var, ConcreteModel, Set, Reals, Suffix, minimize, Param
from prepshot.rules import RuleContainer

def define_model():
    """
    Define a pyomo ConcreateModel object.

    Args:
        None

    Returns:
        pyomo.core.base.PyomoModel.ConcreteModel: A pyomo ConcreateModel object.
    """
    model = ConcreteModel(name='PREP-SHOT')
    model.dual = Suffix(direction=Suffix.IMPORT)
    return model


def define_sets(model, para):
    """
    Define sets for the model.

    Args:
        model (pyomo.core.base.PyomoModel.ConcreteModel): Model to be solved.
        para (dict): Dictionary of parameters for the model.

    Returns:
        None
    """
    sets_to_initialize = ["year", "zone", "tech", "hour", "month"]
    tech_types = ["storage", "nondispatchable", "dispatchable", "hydro"]

    for set_name in sets_to_initialize:
        model.add_component(set_name, Set(initialize=para[set_name], ordered=True, doc=f'Set of {set_name}'))
    model.hour_p = Set(initialize=[0] + para['hour'], ordered=True, doc='Set of operation timesteps')

    for tech_type in tech_types:
        if tech_type in para['technology_type'].values():
            model.add_component(f"{tech_type}_tech", Set(initialize=[i for i, j in para['technology_type'].items() if j == tech_type], ordered=True, doc=f'Set of {tech_type} technology'))
        else:
            model.add_component(f"{tech_type}_tech", Set(initialize=[], ordered=True, doc=f'Set of {tech_type} technology'))

    if para['isinflow']:
        model.station = Set(initialize=para['stcd'], ordered=True, doc='Set of hydropower plants')


def create_tuples(model, para):
    """
    Create tuples for the model. 

    Note: The existing capacity between two zones is set to empty (i.e., No value is filled in the Excel cell), which means that these two 
    zones cannot have newly built transmission lines. If you want to enable two zones which do not have any existing transmission lines, 
    to build new transmission lines in the planning horizon, you need to set their capacity as zero explicitly.

    Args:
        model (pyomo.core.base.PyomoModel.ConcreteModel): Model to be solved.

    Returns:
        None
    """
    model.hour_month_year_tuples = model.hour * model.month * model.year
    model.hour_month_year_zone_storage_tuples = model.hour * model.month * model.year * model.zone * model.storage_tech
    model.hour_month_year_zone_nondispatchable_tuples = model.hour * model.month * model.year * model.zone * model.nondispatchable_tech
    model.hour_month_year_zone_tech_tuples = model.hour * model.month * model.year * model.zone * model.tech
    model.hour_month_year_zone_tuples = model.hour * model.month * model.year * model.zone
    model.year_zone_zone_tuples = Set(initialize=[(y, z, z1) for y in model.year for z in model.zone for z1 in model.zone if (z, z1) in para['transmission_line_existing_capacity'].keys()])
    model.hour_month_year_zone_zone_tuples = Set(initialize=[(h, m, y, z, z1) for h in model.hour for m in model.month for y, z, z1 in model.year_zone_zone_tuples])
    model.hour_month_tech_tuples = model.hour * model.month * model.tech
    model.hour_p_month_year_zone_tuples = model.hour_p * model.month * model.year * model.zone
    model.hour_p_month_year_zone_tech_tuples = model.hour_p * model.month * model.year * model.zone * model.tech
    model.hour_p_month_year_zone_storage_tuples = model.hour_p * model.month * model.year * model.zone * model.storage_tech
    model.month_year_zone_tuples = model.month * model.year * model.zone
    model.month_year_zone_storage_tuples = model.month * model.year * model.zone * model.storage_tech
    model.year_zone_tuples = model.year * model.zone
    model.year_zone_tech_tuples = model.year * model.zone * model.tech
    model.year_tech_tuples = model.year * model.tech

    if para['isinflow']:
        model.station_hour_month_year_tuples = model.station * model.hour * model.month * model.year
        model.station_hour_p_month_year_tuples = model.station * model.hour_p * model.month * model.year
        model.station_month_year_tuples = model.station * model.month * model.year
        model.head_para = Param(model.station_hour_month_year_tuples, mutable=True)


def define_variables(model, para):
    """
    Define variables for the model.

    Args:
        model (pyomo.core.base.PyomoModel.ConcreteModel): Model to be solved.
        para (dict): Dictionary of parameters for the model.

    Returns:
        None
    """
    model.cost = Var(within=NonNegativeReals, doc='total cost of system [RMB]')
    model.cost_var = Var(within=NonNegativeReals, doc='Variable O&M costs [RMB]')
    model.cost_fix = Var(within=NonNegativeReals, doc='Fixed O&M costs [RMB/MW/year]')
    model.cost_newtech = Var(within=NonNegativeReals, doc='Investment costs of new technology [RMB]')
    model.cost_newline = Var(within=NonNegativeReals, doc='Investment costs of new transmission lines [RMB]')
    model.income = Var(within=NonNegativeReals, doc='total income of withdraw water [RMB]')
    model.cap_existing = Var(model.year_zone_tech_tuples, within=NonNegativeReals, doc='Capacity of existing technology [MW]')
    model.cap_newtech = Var(model.year_zone_tech_tuples, within=NonNegativeReals, doc='Capacity of newbuild technology [MW]')
    model.cap_newline = Var(model.year_zone_zone_tuples, within=NonNegativeReals, doc='Capacity of new transmission lines [MW]')
    model.cap_lines_existing = Var(model.year_zone_zone_tuples, within=NonNegativeReals, doc='Capacity of existing transmission line [MW]')
    model.carbon = Var(model.year, within=NonNegativeReals, doc='Total carbon dioxide emission in each years [tonne]')
    model.carbon_capacity = Var(model.year_zone_tuples, within=NonNegativeReals, doc='Carbon dioxide emission in each year and each zone [tonne]')
    model.gen = Var(model.hour_month_year_zone_tech_tuples, within=NonNegativeReals, doc='Output of each technology in each year, each zone and each time period [MWh]')
    model.storage = Var(model.hour_p_month_year_zone_tech_tuples, within=NonNegativeReals, doc='Storage of energy technology in each year, each zone and each time period [MW]')
    model.charge = Var(model.hour_month_year_zone_tech_tuples, within=NonNegativeReals, doc='Storage in each year, each zone and each time period [MWh]')
    model.trans_export = Var(model.hour_month_year_zone_zone_tuples, within=NonNegativeReals, doc='Transfer output from zone A to zone B (A is not equals to B)in each year and each time period [MWh]')
    model.trans_import = Var(model.hour_month_year_zone_zone_tuples, within=NonNegativeReals, doc='Transfer output from zone B to zone A (A is not equals to B) in each year and each time period [MWh]')
    model.remaining_technology = Var(model.year_zone_tech_tuples, within=NonNegativeReals, doc='remaining technology [MW]')

    if para['isinflow']:
        model.naturalinflow = Var(model.station_hour_month_year_tuples, within=Reals, doc='natural inflow of reservoir [m3/s]')
        model.inflow = Var(model.station_hour_month_year_tuples, within=Reals, doc='inflow of reservoir [m3/s]')
        model.outflow = Var(model.station_hour_month_year_tuples, within=NonNegativeReals, doc='inflow of reservoir [m3/s]')
        model.genflow = Var(model.station_hour_month_year_tuples, within=NonNegativeReals, doc='generation flow of reservoir [m3/s]')
        model.spillflow = Var(model.station_hour_month_year_tuples, within=NonNegativeReals, doc='water spillage flow of reservoir [m3/s]')
        model.withdraw = Var(model.station_hour_month_year_tuples, within=NonNegativeReals, doc='withdraw from reservoir [m^3/s]')
        model.storage_reservoir = Var(model.station_hour_p_month_year_tuples, within=NonNegativeReals, doc='storage of reservoir [m3]')
        model.output = Var(model.station_hour_month_year_tuples, within=NonNegativeReals, doc='output of reservoir [MW]')


def define_constraints(model, para):
    """
    Define constraints for the model.

    Args:
        model (pyomo.core.base.PyomoModel.ConcreteModel): Model to be solved.
        para (dict): Dictionary of parameters for the model.

    Returns:
        None
    """
    rules = RuleContainer(para)

    model.total_cost_cons = Constraint(rule=rules.cost_rule, doc='System total cost')
    model.power_balance_cons = Constraint(model.hour_month_year_zone_tuples, rule=rules.power_balance_rule, doc='Power balance')
    model.trans_capacity_cons = Constraint(model.year_zone_zone_tuples, rule=rules.trans_capacity_rule, doc='Trans capacity')
    model.trans_physical_cons = Constraint(model.year_zone_zone_tuples, rule=rules.trans_physical_rule, doc='Two-way trans capacity equals')
    model.trans_balance_cons = Constraint(model.hour_month_year_zone_zone_tuples, rule=rules.trans_balance_rule, doc='Trans balance')
    model.trans_up_bound_cons = Constraint(model.hour_month_year_zone_zone_tuples, rule=rules.trans_up_bound_rule, doc='Trans upper bound')
    model.gen_up_bound_cons = Constraint(model.hour_month_year_zone_tech_tuples, rule=rules.gen_up_bound_rule, doc='Maximum output constraint')
    model.tech_up_bound_cons = Constraint(model.year_zone_tech_tuples, rule=rules.tech_up_bound_rule, doc='technology upper bound')
    model.new_tech_up_bound_cons = Constraint(model.year_zone_tech_tuples, rule=rules.new_tech_up_bound_rule, doc='new technology upper bound')
    model.new_tech_low_bound_cons = Constraint(model.year_zone_tech_tuples, rule=rules.new_tech_low_bound_rule, doc='new technology lower bound')
    model.tech_lifetime_cons = Constraint(model.year_zone_tech_tuples, rule=rules.tech_lifetime_rule, doc='Remaining technology')
    model.ramping_up_cons = Constraint(model.hour_month_year_zone_tech_tuples, rule=rules.ramping_up_rule, doc='Ramping up constraint')
    model.ramping_down_cons = Constraint(model.hour_month_year_zone_tech_tuples, rule=rules.ramping_down_rule, doc='Ramping down constraint')
    model.cost_var_cons = Constraint(rule=rules.var_cost_rule, doc='Variable O&M cost and fuel cost')
    model.newtech_cost_cons = Constraint(rule=rules.newtech_cost_rule, doc='Investment costs of new technology')
    model.newline_cost_cons = Constraint(rule=rules.newline_cost_rule, doc='Investment costs of new transmission lines')
    model.fix_cost_cons = Constraint(rule=rules.fix_cost_rule, doc='Fix O&M costs of new transmission lines')
    model.remaining_capacity_cons = Constraint(model.year, model.zone, model.tech, rule=rules.remaining_capacity_rule, doc='Capacity increasment of technology')
    model.emission_limit_cons = Constraint(model.year, rule=rules.emission_limit_rule, doc='Carbon dioxide emission limit')
    model.emission_calc_cons = Constraint(model.year, rule=rules.emission_calc_rule, doc='Carbon dioxide emission of each year')
    model.emission_calc_by_zone_cons = Constraint(model.year_zone_tuples, rule=rules.emission_calc_by_zone_rule, doc='Carbon dioxide emission of each year')
    model.hydro_output_cons = Constraint(model.hour_month_year_zone_tuples, rule=rules.hydro_output_rule, doc='define hydropower output')

    if model.nondispatchable_tech != 0:
        model.renew_gen_cons = Constraint(model.hour_month_year_zone_nondispatchable_tuples, rule=rules.renew_gen_rule, doc='define renewable output')

    if model.storage_tech != 0:
        model.energy_storage_balance_cons = Constraint(model.hour_month_year_zone_storage_tuples, rule=rules.energy_storage_balance_rule, doc='Storage constraint')
        model.init_energy_storage_cons = Constraint(model.month_year_zone_storage_tuples, rule=rules.init_energy_storage_rule, doc='Init Storage')
        model.end_energy_storage_cons = Constraint(model.month_year_zone_storage_tuples, rule=rules.end_energy_storage_rule, doc='End storage == Init Storage')
        model.energy_storage_up_bound_cons = Constraint(model.hour_month_year_zone_storage_tuples, rule=rules.energy_storage_up_bound_rule, doc='Storage bound')
        model.energy_storage_gen_cons = Constraint(model.hour_month_year_zone_storage_tuples, rule=rules.energy_storage_gen_rule, doc='Storage bound')

    if para['isinflow']:
        model.natural_inflow_cons = Constraint(model.station_hour_month_year_tuples, rule=rules.natural_inflow_rule, doc='Natural flow')
        model.total_inflow_cons = Constraint(model.station_hour_month_year_tuples, rule=rules.total_inflow_rule, doc='Hydraulic Connection Constraints')
        model.water_balance_cons = Constraint(model.station_hour_month_year_tuples, rule=rules.water_balance_rule, doc='Water Balance Constraints')
        model.discharge_cons = Constraint(model.station_hour_month_year_tuples, rule=rules.discharge_rule, doc='Discharge Constraints')
        model.outflow_low_bound_cons = Constraint(model.station_hour_month_year_tuples, rule=rules.outflow_low_bound_rule, doc='Discharge lower limits')
        model.outflow_up_bound_cons = Constraint(model.station_hour_month_year_tuples, rule=rules.outflow_up_bound_rule, doc='Discharge upper limits')
        model.storage_low_bound_cons = Constraint(model.station_hour_month_year_tuples, rule=rules.storage_low_bound_rule, doc='Storage lower limits')
        model.storage_up_bound_cons = Constraint(model.station_hour_month_year_tuples, rule=rules.storage_up_bound_rule, doc='Storage upper limits')
        model.output_low_bound_cons = Constraint(model.station_hour_month_year_tuples, rule=rules.output_low_bound_rule, doc='Power Output lower limits')
        model.output_up_bound_cons = Constraint(model.station_hour_month_year_tuples, rule=rules.output_up_bound_rule, doc='Power Output upper limits')
        model.output_calc_cons = Constraint(model.station_hour_month_year_tuples, rule=rules.output_calc_rule, doc='Power Output Constraints')
        model.init_storage_cons = Constraint(model.station_month_year_tuples, rule=rules.init_storage_rule, doc='Initial storage Constraints')
        model.end_storage_cons = Constraint(model.station_month_year_tuples, rule=rules.end_storage_rule, doc='Terminal storage Constraints')
        model.income_cons = Constraint(expr=model.income == sum([model.withdraw[s, h, m, y] * 3600 * para['dt'] * para['price'] for s, h, m, y in model.station_hour_month_year_tuples]))
    else:
        model.income_cons = Constraint(expr=model.income == 0)

def create_model(para):
    """
    Create the PREP-SHOT model.

    Args:
        para (dict): Dictionary of parameters for the model.

    Returns:
        pyomo.core.base.PyomoModel.ConcreteModel: A pyomo ConcreateModel object.
    """
    # Define a pyomo ConcreteModel object.
    model = define_model()

    # Define sets for the model.
    define_sets(model, para)

    # Create tuples for the model.
    create_tuples(model, para)

    # Define variables for the model.
    define_variables(model, para)

    # Define objective function for the model.
    model.total_cost = Objective(expr=model.cost, sense=minimize, doc='Minimize the sum of all cost types)')

    # Define constraints for the model.
    define_constraints(model, para)

    return model
