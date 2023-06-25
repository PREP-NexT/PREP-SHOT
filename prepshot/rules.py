import numpy as np
from pyomo.environ import Constraint

def cost_rule(model):
    """
    Objective function of the model, to minimize total cost.

    Args:
        model (pyomo.core.base.PyomoModel.ConcreteModel): Model to be solved.

    Returns:
        pyomo.core.base.PyomoModel.ConcreteModel: Model with cost constraints.
    """
    return model.cost == model.cost_var + model.cost_newtech + model.cost_fix + model.cost_newline - model.income


def create_var_cost_rule(para):
    def var_cost_rule(model):
        """
        Rule for total fuel cost of technologies and variable Operation and maintenance (O&M) cost of technologies and transmission lines.

        Args:
            model (pyomo.core.base.PyomoModel.ConcreteModel): Model to be solved.

        Returns:
            pyomo.core.base.PyomoModel.ConcreteModel: Model with variable cost constraints.
        """
        var_OM_tech_cost = sum([para['technology_variable_cost'][te, y] * model.gen[h, m, y, z, te] * para['dt'] * para['var_factor'][y] for h, m, y, z, te in model.hour_month_year_zone_tech_tuples])/para['weight']
        fuel_cost = sum([para['fuel_price'][te, y] * model.gen[h, m, y, z, te] * para['dt'] * para['var_factor'][y] for h, m, y, z, te in model.hour_month_year_zone_tech_tuples])/para['weight']
        var_OM_line_cost = 0.5 * sum([para['transline_variable_cost'][z, z1] * model.trans_export[h, m, y, z, z1] * para['var_factor'][y] for h, m, y, z, z1 in model.hour_month_year_zone_zone_tuples])/para['weight']
        return model.cost_var == var_OM_tech_cost + fuel_cost + var_OM_line_cost
    return var_cost_rule


def create_newtech_cost_rule(para):
    def newtech_cost_rule(model):
        """
        Rule for total investment cost of new technologies.

        Args:
            model (pyomo.core.base.PyomoModel.ConcreteModel): Model to be solved.

        Returns:
            pyomo.core.base.PyomoModel.ConcreteModel: Model with investment cost of new technologies constraints.
        """
        return model.cost_newtech == sum(para['technology_investment_cost'][te, y] * model.cap_newtech[y, z, te] * para['inv_factor'][te, y] for y, z, te in model.year_zone_tech_tuples)
    return newtech_cost_rule


def create_newline_cost_rule(para):
    def newline_cost_rule(model):
        """
        Rule for total investment cost of new transmission lines.

        Args:
            model (pyomo.core.base.PyomoModel.ConcreteModel): Model to be solved.

        Returns:
            pyomo.core.base.PyomoModel.ConcreteModel: Model with investment cost of new transmission lines constraints.
        """
        return model.cost_newline == 0.5 * sum(para['transline_investment_cost'][z, z1] * model.cap_newline[y, z, z1] * para['distance'][z, z1] * para['trans_inv_factor'][y] for y, z, z1 in model.year_zone_zone_tuples)
    return newline_cost_rule


def create_fix_cost_rule(para):
    def fix_cost_rule(model):
        """
        Rule for fixed O&M cost of technologies and transmission lines.

        Args:
            model (pyomo.core.base.PyomoModel.ConcreteModel): Model to be solved.

        Returns:
            pyomo.core.base.PyomoModel.ConcreteModel: Model with fixed O&M cost of technologies and transmission line constraints.
        """
        fix_cost_tech = sum(para['technology_fix_cost'][te, y] * model.cap_existing[y, z, te] * para['fix_factor'][y] for y, z, te in model.year_zone_tech_tuples)
        fix_cost_line = 0.5 * sum(para['transline_fix_cost'][z, z1] * model.cap_lines_existing[y, z, z1] * para['fix_factor'][y] for y, z1, z in model.year_zone_zone_tuples)
        return model.cost_fix == fix_cost_tech + fix_cost_line
    return fix_cost_rule


def create_remaining_capacity_rule(para):
    def remaining_capacity_rule(model, y, z, te):
        """
        Rule for lifetime restrictions.
        
        Note: Where in modeled year y, the available technology consists of the following.
            1. The remaining in-service installed capacity from the initial technology.
            2. The remaining in-service installed capacity from newly built technology in the previous modelled years.

        Args:
            model (pyomo.core.base.PyomoModel.ConcreteModel): Model to be solved.
            y (int): Year.
            z (str): Zone.
            te (str): Technology.

        Returns:
            pyomo.core.base.PyomoModel.ConcreteModel: Model with lifetime restriction constraints.
        """
        year = para['year']
        new_tech = sum([model.cap_newtech[yy, z, te] for yy in year[:year.index(y) + 1] if y - yy < para['lifetime'][te, y]])
        return model.cap_existing[y, z, te] == model.remaining_technology[y, z, te] + new_tech
    return remaining_capacity_rule


def create_emission_limit_rule(para):
    def emission_limit_rule(model, y):
        """
        Rule for carbon emission restrictions.

        Args:
            model (pyomo.core.base.PyomoModel.ConcreteModel): Model to be solved.
            y (int): Year.

        Returns:
            pyomo.core.base.PyomoModel.ConcreteModel: Model with carbon emission restriction constraints.
        """
        return model.carbon[y] <= para['carbon'][y]
    return emission_limit_rule


def emission_calc_rule(model, y):
    """
    Rule for carbon emission calculation.

    Args:
        model (pyomo.core.base.PyomoModel.ConcreteModel): Model to be solved.
        y (int): Year.

    Returns:
        pyomo.core.base.PyomoModel.ConcreteModel: Model with carbon emission calculation rule.
    """
    return model.carbon[y] == sum(model.carbon_capacity[y, z] for z in model.zone)


def create_emission_calc_by_zone_rule(para):
    def emission_calc_by_zone_rule(model, y, z):
        """
        Rule for carbon emission calculation by zone.

        Args:
            model (pyomo.core.base.PyomoModel.ConcreteModel): Model to be solved.
            y (int): Year.
            z (str): Zone.

        Returns:
            pyomo.core.base.PyomoModel.ConcreteModel: Model with carbon emission calculation by zone rule.
        """
        return model.carbon_capacity[y, z] == sum(para['carbon_content'][te, y] * model.gen[h, m, y, z, te] * para['dt'] for h, m, te in model.hour_month_tech_tuples)
    return emission_calc_by_zone_rule


def create_power_balance_rule(para):
    def power_balance_rule(model, h, m, y, z):
        """
        Rule for power balance.

        Note: The total electricity demand for each time period and in each zone should be met by the following.
            1. The sum of imported power energy from other zones.
            2. The generation from zone z minus the sum of exported power energy from zone z to other zones.
            3. The charging power energy of storage technologies in zone z.

        Args:
            model (pyomo.core.base.PyomoModel.ConcreteModel): Model to be solved.
            h (int): Hour.
            m (int): Month.
            y (int): Year.
            z (str): Zone.

        Returns:
            pyomo.core.base.PyomoModel.ConcreteModel: Model with power balance constraints.
        """
        imp_z = sum([model.trans_import[h, m, y, z1, z] for z1 in model.zone if (z, z1) in para['transline'].keys()])
        exp_z = sum([model.trans_export[h, m, y, z, z1] for z1 in model.zone if (z, z1) in para['transline'].keys()])
        gen_z = sum([model.gen[h, m, y, z, te] for te in model.tech])
        charge_z = sum([model.charge[h, m, y, z, te] for te in model.storage_tech])
        demand_z = para['demand'][z, y, m, h]
        return demand_z == imp_z - exp_z + gen_z - charge_z
    return power_balance_rule


def trans_physical_rule(model, y, z, z1):
    """
    Rule for physical transmission lines.

    Args:
        model (pyomo.core.base.PyomoModel.ConcreteModel): Model to be solved.
        y (int): Year.
        z (str): Zone.
        z1 (str): Zone.

    Returns:
        pyomo.core.base.PyomoModel.ConcreteModel: Model with physical transmission line constraints.
    """
    return model.cap_newline[y, z, z1] == model.cap_newline[y, z1, z]


def create_trans_capacity_rule(para):
    def trans_capacity_rule(model, y, z, z1):
        """
        Rule for transmission capacity.

        Args:
            model (pyomo.core.base.PyomoModel.ConcreteModel): Model to be solved.
            y (int): Year.
            z (str): Zone.
            z1 (str): Zone.

        Returns:
            pyomo.core.base.PyomoModel.ConcreteModel: Model with transmission capacity constraints.
        """
        Year = para['year']
        remaining_capacity_line = para['transline'][z, z1]
        new_capacity_line = sum(model.cap_newline[yy, z, z1] for yy in Year[:Year.index(y) + 1])
        return model.cap_lines_existing[y, z, z1] == remaining_capacity_line + new_capacity_line
    return trans_capacity_rule


def create_trans_balance_rule(para):
    def trans_balance_rule(model, h, m, y, z, z1):
        """
        Rule for transmission balance.

        Args:
            model (pyomo.core.base.PyomoModel.ConcreteModel): Model to be solved.
            h (int): Hour.
            m (int): Month.
            y (int): Year.
            z (str): Zone.
            z1 (str): Zone.

        Returns:
            pyomo.core.base.PyomoModel.ConcreteModel: Model with transmission balance constraints.
        """
        eff = para['transline_efficiency'][z, z1]
        return eff * model.trans_export[h, m, y, z, z1] == model.trans_import[h, m, y, z, z1]
    return trans_balance_rule


def trans_up_bound_rule(model, h, m, y, z, z1):
    """
    Rule for transmission upper bound.

    Args:
        model (pyomo.core.base.PyomoModel.ConcreteModel): Model to be solved.
        h (int): Hour.
        m (int): Month.
        y (int): Year.
        z (str): Zone.
        z1 (str): Zone.

    Returns:
        pyomo.core.base.PyomoModel.ConcreteModel: Model with transmission upper bound constraints.
    """
    return model.trans_export[h, m, y, z, z1] <= model.cap_lines_existing[y, z, z1]


def gen_up_bound_rule(model, h, m, y, z, te):
    """
    Rule for generation upper bound.

    Args:
        model (pyomo.core.base.PyomoModel.ConcreteModel): Model to be solved.
        h (int): Hour.
        m (int): Month.
        y (int): Year.
        z (str): Zone.
        te (str): Technology.

    Returns:
        pyomo.core.base.PyomoModel.ConcreteModel: Model with generation upper bound constraints.
    """
    return model.gen[h, m, y, z, te] <= model.cap_existing[y, z, te]


def create_tech_up_bound_rule(para):
    def tech_up_bound_rule(model, y, z, te):
        """
        Rule for technology upper bound.

        Args:
            model (pyomo.core.base.PyomoModel.ConcreteModel): Model to be solved.
            y (int): Year.
            z (str): Zone.
            te (str): Technology.

        Returns:
            pyomo.core.base.PyomoModel.ConcreteModel: Model with technology upper bound constraints.
        """
        if para['technology_upper_bound'][te, z] == np.Inf:
            return Constraint.Skip
        else:
            return model.cap_existing[y, z, te] <= para['technology_upper_bound'][te, z]
    return tech_up_bound_rule


def create_new_tech_up_bound_rule(para):
    def new_tech_up_bound_rule(model, y, z, te):
        """
        Rule for new technology upper bound.

        Args:
            model (pyomo.core.base.PyomoModel.ConcreteModel): Model to be solved.
            y (int): Year.
            z (str): Zone.
            te (str): Technology.

        Returns:
            pyomo.core.base.PyomoModel.ConcreteModel: Model with new technology upper bound constraints.
        """
        if para['new_technology_upper_bound'][te, z] == np.Inf:
            return Constraint.Skip
        else:
            return model.cap_newtech[y, z, te] <= para['new_technology_upper_bound'][te, z]
    return new_tech_up_bound_rule


def create_new_tech_low_bound_rule(para):
    def new_tech_low_bound_rule(model, y, z, te):
        """
        Rule for new technology lower bound.

        Args:
            model (pyomo.core.base.PyomoModel.ConcreteModel): Model to be solved.
            y (int): Year.
            z (str): Zone.
            te (str): Technology.

        Returns:
            pyomo.core.base.PyomoModel.ConcreteModel: Model with new technology lower bound constraints.
        """
        return model.cap_newtech[y, z, te] >= para['new_technology_lower_bound'][te, z]
    return new_tech_low_bound_rule


def create_renew_gen_rule(para):
    def renew_gen_rule(model, h, m, y, z, te):
        """
        Rule for renewable generation.

        Args:
            model (pyomo.core.base.PyomoModel.ConcreteModel): Model to be solved.
            h (int): Hour.
            m (int): Month.
            y (int): Year.
            z (str): Zone.
            te (str): Technology.

        Returns:
            pyomo.core.base.PyomoModel.ConcreteModel: Model with renewable generation constraints.
        """
        return model.gen[h, m, y, z, te] <= para['capacity_factor'][te, z, y, m, h] * model.cap_existing[y, z, te] * para['dt']
    return renew_gen_rule


def create_tech_lifetime_rule(para):
    def tech_lifetime_rule(model, y, z, te):
        """
        Rule for technology lifetime.

        Args:
            model (pyomo.core.base.PyomoModel.ConcreteModel): Model to be solved.
            y (int): Year.
            z (str): Zone.
            te (str): Technology.

        Returns:
            pyomo.core.base.PyomoModel.ConcreteModel: Model with technology lifetime constraints.
        """
        lifetime = para['lifetime'][te, y]
        service_time = y - para['year'][0]
        remaining_time = int(lifetime - service_time)
        if remaining_time <= 1:
            return model.remaining_technology[y, z, te] == 0
        else:
            return model.remaining_technology[y, z, te] == sum([para['age'][z, te, a] for a in range(1, remaining_time)])
    return tech_lifetime_rule


def create_energy_storage_balance_rule(para):
    def energy_storage_balance_rule(model, h, m, y, z, te):
        """
        Rule for energy storage balance.

        Args:
            model (pyomo.core.base.PyomoModel.ConcreteModel): Model to be solved.
            h (int): Hour.
            m (int): Month.
            y (int): Year.
            z (str): Zone.
            te (str): Technology.

        Returns:
            pyomo.core.base.PyomoModel.ConcreteModel: Model with energy storage balance constraints.
        """
        return (model.storage[h, m, y, z, te] == model.storage[h-1, m, y, z, te] - model.gen[h, m, y, z, te] * para['efficiency_out'][te, y]*para['dt'] + model.charge[h, m, y, z, te] * para['efficiency_in'][te, y]*para['dt'])
    return energy_storage_balance_rule


def create_init_energy_storage_rule(para):
    def init_energy_storage_rule(model, m, y, z, te):
        """
        Rule for initial energy storage.

        Args:
            model (pyomo.core.base.PyomoModel.ConcreteModel): Model to be solved.
            m (int): Month.
            y (int): Year.
            z (str): Zone.
            te (str): Technology.

        Returns:
            pyomo.core.base.PyomoModel.ConcreteModel: Model with initial energy storage constraints.
        """
        return (model.storage[0, m, y, z, te] == para['init_storage_level'][te, z] * model.cap_existing[y, z, te] * para['energy_power_ratio'][te])
    return init_energy_storage_rule


def create_end_energy_storage_rule(para):
    def end_energy_storage_rule(model, m, y, z, te):
        """
        Rule for end energy storage.

        Args:
            model (pyomo.core.base.PyomoModel.ConcreteModel): Model to be solved.
            m (int): Month.
            y (int): Year.
            z (str): Zone.
            te (str): Technology.

        Returns:
            pyomo.core.base.PyomoModel.ConcreteModel: Model with end energy storage constraints.
        """
        return model.storage[para['hour'][-1], m, y, z, te] == model.storage[0, m, y, z, te]
    return end_energy_storage_rule


def create_energy_storage_up_bound_rule(para):
    def energy_storage_up_bound_rule(model, h, m, y, z, te):
        """
        Rule for energy storage upper bound.

        Args:
            model (pyomo.core.base.PyomoModel.ConcreteModel): Model to be solved.
            h (int): Hour.
            m (int): Month.
            y (int): Year.
            z (str): Zone.
            te (str): Technology.

        Returns:
            pyomo.core.base.PyomoModel.ConcreteModel: Model with energy storage upper bound constraints.
        """
        return model.storage[h, m, y, z, te] <= model.cap_existing[y, z, te] * para['energy_power_ratio'][te]
    return energy_storage_up_bound_rule


def create_energy_storage_gen_rule(para):
    def energy_storage_gen_rule(model, h, m, y, z, te):
        """
        Rule for energy storage generation.

        Args:
            model (pyomo.core.base.PyomoModel.ConcreteModel): Model to be solved.
            h (int): Hour.
            m (int): Month.
            y (int): Year.
            z (str): Zone.
            te (str): Technology.

        Returns:
            pyomo.core.base.PyomoModel.ConcreteModel: Model with energy storage generation constraints.
        """
        return model.gen[h, m, y, z, te] * para['efficiency_out'][te, y] * para['dt'] <= model.storage[h-1, m, y, z, te]
    return energy_storage_gen_rule


def create_ramping_up_rule(para):
    def ramping_up_rule(model, h, m, y, z, te):
        """
        Rule for ramping up.

        Args:
            model (pyomo.core.base.PyomoModel.ConcreteModel): Model to be solved.
            h (int): Hour.
            m (int): Month.
            y (int): Year.
            z (str): Zone.
            te (str): Technology.

        Returns:
            pyomo.core.base.PyomoModel.ConcreteModel: Model with ramping up constraints.
        """
        if h > 1 and para['ramp_up'][te] * para['dt'] < 1:
            return model.gen[h, m, y, z, te] - model.gen[h-1, m, y, z, te] <= para['ramp_up'][te] * para['dt'] * model.cap_existing[y, z, te]
        else:
            return Constraint.Skip
    return ramping_up_rule


def create_ramping_down_rule(para):
    def ramping_down_rule(model, h, m, y, z, te):
        """
        Rule for ramping down.

        Args:
            model (pyomo.core.base.PyomoModel.ConcreteModel): Model to be solved.
            h (int): Hour.
            m (int): Month.
            y (int): Year.
            z (str): Zone.
            te (str): Technology.

        Returns:
            pyomo.core.base.PyomoModel.ConcreteModel: Model with ramping down constraints.
        """
        if h > 1 and para['ramp_down'][te] * para['dt'] < 1:
            return model.gen[h-1, m, y, z, te] - model.gen[h, m, y, z, te] <= para['ramp_down'][te] * para['dt'] * model.cap_existing[y, z, te]
        else:
            return Constraint.Skip
    return ramping_down_rule


def create_hydro_output_rule(para):
    def hydro_output_rule(model, h, m, y, z):
        """
        Rule for hydrological output.

        Args:
            model (pyomo.core.base.PyomoModel.ConcreteModel): Model to be solved.
            h (int): Hour.
            m (int): Month.
            y (int): Year.
            z (str): Zone.

        Returns:
            pyomo.core.base.PyomoModel.ConcreteModel: Model with hydrological output constraints.
        """
        return model.gen[h, m, y, z, [i for i, j in para['type'].items() if j == 'hydro'][0]] <= float(para['hydropower']['Hydro', z, y, m, h]) * para['dt']
    return hydro_output_rule


def create_natural_inflow_rule(para):
    def natural_inflow_rule(model, s, h, m, y):
        """
        Rule for natural inflow.

        Args:
            model (pyomo.core.base.PyomoModel.ConcreteModel): Model to be solved.
            s (str): Power plant.
            h (int): Hour.
            m (int): Month.
            y (int): Year.

        Returns:
            pyomo.core.base.PyomoModel.ConcreteModel: Model with natural inflow constraints.
        """
        return model.naturalinflow[s, h, m, y] == para['inflow'][s, y, m, h]
    return natural_inflow_rule


def create_total_inflow_rule(para):
    def total_inflow_rule(model, s, h, m, y):
        """
        Rule for total inflow.

        Note: Outflows are assumed to occur everyday to maintain water level.

        Args:
            model (pyomo.core.base.PyomoModel.ConcreteModel): Model to be solved.
            s (str): Power plant.
            h (int): Hour.
            m (int): Month.
            y (int): Year.

        Returns:
            pyomo.core.base.PyomoModel.ConcreteModel: Model with total inflow constraints.
        """
        hour = para['hour']
        up_stream_outflow = 0
        for ups, delay in zip(para['connect'][para['connect']['NEXTPOWER_ID'] == s].POWER_ID, para['connect'][para['connect']['NEXTPOWER_ID'] == s].delay):
            delay = int(int(delay)/para['dt'])
            if (h - delay >= hour[0]):
                up_stream_outflow += model.outflow[ups, h-delay, m, y]
            else:
                up_stream_outflow += model.outflow[ups, hour[-1] - delay + h, m, y]

        return model.inflow[s, h, m, y] == model.naturalinflow[s, h, m, y] + up_stream_outflow
    return total_inflow_rule


def create_water_balance_rule(para):
    def water_balance_rule(model, s, h, m, y):
        """
        Rule for water balance.

        Args:
            model (pyomo.core.base.PyomoModel.ConcreteModel): Model to be solved.
            s (str): Power plant.
            h (int): Hour.
            m (int): Month.
            y (int): Year.

        Returns:
            pyomo.core.base.PyomoModel.ConcreteModel: Model with water balance constraints.
        """
        return model.storage_hydro[s, h, m, y] == model.storage_hydro[s, h-1, m, y] + (model.inflow[s, h, m, y] - model.outflow[s, h, m, y] - model.withdraw[s, h, m, y])*3600*para['dt']*1e-8
    return water_balance_rule


def discharge_rule(model, s, h, m, y):
    """
    Rule for discharge.

    Args:
        model (pyomo.core.base.PyomoModel.ConcreteModel): Model to be solved.
        s (str): Power plant.
        h (int): Hour.
        m (int): Month.
        y (int): Year.

    Returns:
        pyomo.core.base.PyomoModel.ConcreteModel: Model with discharge constraints.
    """
    return model.outflow[s, h, m, y] == model.genflow[s, h, m, y] + model.spillflow[s, h, m, y]


def create_outflow_low_bound_rule(para):
    def outflow_low_bound_rule(model, s, h, m, y):
        """
        Rule for outflow lower bound.

        Args:
            model (pyomo.core.base.PyomoModel.ConcreteModel): Model to be solved.
            s (str): Power plant.
            h (int): Hour.
            m (int): Month.
            y (int): Year.

        Returns:
            pyomo.core.base.PyomoModel.ConcreteModel: Model with outflow lower bound constraints.
        """
        return model.outflow[s, h, m, y] >= para['static']['outflow_min', s]
    return outflow_low_bound_rule


def create_outflow_up_bound_rule(para):
    def outflow_up_bound_rule(model, s, h, m, y):
        """
        Rule for outflow upper bound.

        Args:
            model (pyomo.core.base.PyomoModel.ConcreteModel): Model to be solved.
            s (str): Power plant.
            h (int): Hour.
            m (int): Month.
            y (int): Year.

        Returns:
            pyomo.core.base.PyomoModel.ConcreteModel: Model with outflow upper bound constraints.
        """
        return model.outflow[s, h, m, y] <= para['static']['outflow_max', s]
    return outflow_up_bound_rule


def create_storage_low_bound_rule(para):
    def storage_low_bound_rule(model, s, h, m, y):
        """
        Rule for storage lower bound.

        Args:
            model (pyomo.core.base.PyomoModel.ConcreteModel): Model to be solved.
            s (str): Power plant.
            h (int): Hour.
            m (int): Month.
            y (int): Year.

        Returns:
            pyomo.core.base.PyomoModel.ConcreteModel: Model with storage lower bound constraints.
        """
        return model.storage_hydro[s, h, m, y] >= para['storage_downbound'][s, m, h]
    return storage_low_bound_rule


def create_storage_up_bound_rule(para):
    def storage_up_bound_rule(model, s, h, m, y):
        """
        Rule for storage upper bound.

        Args:
            model (pyomo.core.base.PyomoModel.ConcreteModel): Model to be solved.
            s (str): Power plant.
            h (int): Hour.
            m (int): Month.
            y (int): Year.

        Returns:
            pyomo.core.base.PyomoModel.ConcreteModel: Model with storage upper bound constraints.
        """
        return model.storage_hydro[s, h, m, y] <= para['storage_upbound'][s, m, h]
    return storage_up_bound_rule


def create_output_low_bound_rule(para):
    def output_low_bound_rule(model, s, h, m, y):
        """
        Rule for output lower bound.

        Args:
            model (pyomo.core.base.PyomoModel.ConcreteModel): Model to be solved.
            s (str): Power plant.
            h (int): Hour.
            m (int): Month.
            y (int): Year.

        Returns:
            pyomo.core.base.PyomoModel.ConcreteModel: Model with output lower bound constraints.
        """
        return model.output[s, h, m, y] >= para['static']['N_min', s]
    return output_low_bound_rule


def create_output_up_bound_rule(para):
    def output_up_bound_rule(model, s, h, m, y):
        """
        Rule for output upper bound.

        Args:
            model (pyomo.core.base.PyomoModel.ConcreteModel): Model to be solved.
            s (str): Power plant.
            h (int): Hour.
            m (int): Month.
            y (int): Year.

        Returns:
            pyomo.core.base.PyomoModel.ConcreteModel: Model with output upper bound constraints.
        """
        return model.output[s, h, m, y] <= para['static']['N_max', s]
    return output_up_bound_rule


def create_output_calc_rule(para):
    def output_calc_rule(model, s, h, m, y):
        """
        Rule for output calculation.

        Args:
            model (pyomo.core.base.PyomoModel.ConcreteModel): Model to be solved.
            s (str): Power plant.
            h (int): Hour.
            m (int): Month.
            y (int): Year.

        Returns:
            pyomo.core.base.PyomoModel.ConcreteModel: Model with output calculation constraints.
        """
        return model.output[s, h, m, y] == para['static']['coeff', s] * model.genflow[s, h, m, y] * model.head_para[s, h, m, y] * 1e-3
    return output_calc_rule


def create_init_storage_rule(para):
    def init_storage_rule(model, s, m, y):
        """
        Rule for initial storage.

        Args:
            model (pyomo.core.base.PyomoModel.ConcreteModel): Model to be solved.
            s (str): Power plant.
            m (int): Month.
            y (int): Year.

        Returns:
            pyomo.core.base.PyomoModel.ConcreteModel: Model with initial storage constraints.
        """
        hour_period = [0] + para['hour']
        return model.storage_hydro[s, hour_period[0], m, y] == para['storage_init'][m, s]
    return init_storage_rule


def create_end_storage_rule(para):
    def end_storage_rule(model, s, m, y):
        """
        Rule for end storage.

        Args:
            model (pyomo.core.base.PyomoModel.ConcreteModel): Model to be solved.
            s (str): Power plant.
            m (int): Month.
            y (int): Year.

        Returns:
            pyomo.core.base.PyomoModel.ConcreteModel: Model with end storage constraints.
        """
        hour_period = [0] + para['hour']
        return model.storage_hydro[s, hour_period[-1], m, y] == para['storage_end'][m, s]
    return end_storage_rule


def create_hydro_output_rule(para):
    def hydro_output_rule(model, h, m, y, z):
        """
        Rule for hydrological output.

        Args:
            model (pyomo.core.base.PyomoModel.ConcreteModel): Model to be solved.
            h (int): Hour.
            m (int): Month.
            y (int): Year.
            z (str): Zone.

        Returns:
            pyomo.core.base.PyomoModel.ConcreteModel: Model with hydrological output constraints.
        """
        hydro_output = 0
        for s in model.station:
            if para['static']['zone', s] == z:
                hydro_output += model.output[s, h, m, y] * para['dt']
        return model.gen[h, m, y, z, [i for i, j in para['type'].items() if j == 'hydro'][0]] == hydro_output
    return hydro_output_rule
