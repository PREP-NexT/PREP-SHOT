import numpy as np
# from pyomo.environ import Constraint
import pyoptinterface as poi

class RuleContainer:
    """
    Class for rules of the model. Used to pass 'para' dictionary to the rules.
    """
    def __init__(self, para, model):
        """
        Args:
            para (dict): Dictionary of parameters for the model.
        """
        self.para = para
        self.model = model

    def cost_rule(self):
        """
        Objective function of the model, to minimize total cost.

        Args:
            model (pyomo.core.base.PyomoModel.ConcreteModel): Model to be solved.

        Returns:
            pyomo.core.base.PyomoModel.ConcreteModel: Model with cost constraints.
        """
        model = self.model
        lhs = model.cost - (model.cost_var + model.cost_newtech 
            + model.cost_fix + model.cost_newline - model.income)
        return model.add_linear_constraint(lhs, poi.Eq, 0)
    
    def income_rule(self):
        """
        Rule for income from electricity generation.

        Args:
            model (pyomo.core.base.PyomoModel.ConcreteModel): Model to be solved.

        Returns:
            pyomo.core.base.PyomoModel.ConcreteModel: Model with income constraints.
        """
        model = self.model
        if self.para['isinflow']:
            coef = 3600 * self.para['dt'] * self.para['price']
            lhs = model.income - poi.quicksum(
                model.withdraw[s, h, m, y] * coef 
                for s, h, m, y in model.station_hour_month_year_tuples
            )
            return model.add_linear_constraint(lhs, poi.Eq, 0)
        else:
            return model.add_linear_constraint(model.income, poi.Eq, 0)


    def var_cost_rule(self):
        """
        Rule for total fuel cost of technologies and variable Operation and maintenance (O&M) cost of technologies and transmission lines.

        Args:
            model (pyomo.core.base.PyomoModel.ConcreteModel): Model to be solved.

        Returns:
            pyomo.core.base.PyomoModel.ConcreteModel: Model with variable cost constraints.
        """
        model = self.model
        tvc = self.para['technology_variable_OM_cost']
        lvc = self.para['transmission_line_variable_OM_cost']
        dt = self.para['dt']
        w = self.para['weight']
        vf = self.para['var_factor']
        fp = self.para['fuel_price']
        var_OM_tech_cost = 1  / w * poi.quicksum(
            tvc[te, y] * model.gen[h, m, y, z, te] * dt * vf[y] 
            for h, m, y, z, te in model.hour_month_year_zone_tech_tuples
        )
        
        fuel_cost = 1  / w * poi.quicksum(
            fp[te, y] * model.gen[h, m, y, z, te] * dt * vf[y]
            for h, m, y, z, te in model.hour_month_year_zone_tech_tuples
        )
        
        var_OM_line_cost = 0.5 / w * poi.quicksum(
            lvc[z, z1] * model.trans_export[h, m, y, z, z1] * dt * vf[y]
            for h, m, y, z, z1 in model.hour_month_year_zone_zone_tuples
        ) 
        lhs = model.cost_var - (var_OM_tech_cost + fuel_cost 
            + var_OM_line_cost)
        return model.add_linear_constraint(lhs, poi.Eq, 0)


    def newtech_cost_rule(self):
        """
        Rule for total investment cost of new technologies.

        Args:
            model (pyomo.core.base.PyomoModel.ConcreteModel): Model to be solved.

        Returns:
            pyomo.core.base.PyomoModel.ConcreteModel: Model with investment cost of new technologies constraints.
        """
        model = self.model
        tic = self.para['technology_investment_cost']
        ivf = self.para['inv_factor']
        lhs = model.cost_newtech - poi.quicksum(
            tic[te, y] * model.cap_newtech[y, z, te] * ivf[te, y]
            for y, z, te in model.year_zone_tech_tuples
        )
        return model.add_linear_constraint(lhs, poi.Eq, 0)


    def newline_cost_rule(self):
        """
        Rule for total investment cost of new transmission lines.

        Args:
            model (pyomo.core.base.PyomoModel.ConcreteModel): Model to be solved.

        Returns:
            pyomo.core.base.PyomoModel.ConcreteModel: Model with investment cost of new transmission lines constraints.
        """
        model = self.model
        lc = self.para['transmission_line_existing_capacity']
        d = self.para['distance']
        ivf = self.para['trans_inv_factor']
        lhs = model.cost_newline - 0.5 * poi.quicksum(
            lc[z, z1] * model.cap_newline[y, z, z1] * d[z, z1] * ivf[y]
            for y, z, z1 in model.year_zone_zone_tuples
        )
        return model.add_linear_constraint(lhs, poi.Eq, 0)


    def fix_cost_rule(self):
        """
        Rule for fixed O&M cost of technologies and transmission lines.

        Args:
            model (pyomo.core.base.PyomoModel.ConcreteModel): Model to be solved.

        Returns:
            pyomo.core.base.PyomoModel.ConcreteModel: Model with fixed O&M cost of technologies and transmission line constraints.
        """
        model = self.model
        fc = self.para['technology_fixed_OM_cost']
        ff = self.para['fix_factor']
        lfc = self.para['transmission_line_fixed_OM_cost']
        
        fix_cost_tech = poi.quicksum(
            fc[te, y] * model.cap_existing[y, z, te] * ff[y]
            for y, z, te in model.year_zone_tech_tuples
        )
        fix_cost_line = 0.5 * poi.quicksum(
            lfc[z, z1] * model.cap_lines_existing[y, z, z1] * ff[y]
            for y, z1, z in model.year_zone_zone_tuples
        )
        lhs = model.cost_fix - (fix_cost_tech + fix_cost_line)
        return model.add_linear_constraint(lhs, poi.Eq, 0)


    def remaining_capacity_rule(self, y, z, te):
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
        model = self.model
        year = self.para['year']
        lt = self.para['lifetime']
        new_tech = poi.quicksum(
            model.cap_newtech[yy, z, te] 
            for yy in year[:year.index(y) + 1] 
            if y - yy < lt[te, y]
        )
        lhs = model.cap_existing[y, z, te] - (
            model.remaining_technology[y, z, te] + new_tech
        )
        return model.add_linear_constraint(lhs, poi.Eq, 0)


    def emission_limit_rule(self, y):
        """
        Rule for carbon emission restrictions.

        Args:
            model (pyomo.core.base.PyomoModel.ConcreteModel): Model to be solved.
            y (int): Year.

        Returns:
            pyomo.core.base.PyomoModel.ConcreteModel: Model with carbon emission restriction constraints.
        """
        model = self.model
        limit = self.para['carbon_emission_limit']
        lhs = model.carbon[y] - limit[y]
        return model.add_linear_constraint(lhs, poi.Leq, 0)


    def emission_calc_rule(self, y):
        """
        Rule for carbon emission calculation.

        Args:
            model (pyomo.core.base.PyomoModel.ConcreteModel): Model to be solved.
            y (int): Year.

        Returns:
            pyomo.core.base.PyomoModel.ConcreteModel: Model with carbon emission calculation rule.
        """
        model = self.model
        lhs = model.carbon[y] - poi.quicksum(
            model.carbon_capacity[y, z] 
            for z in model.zone
        )
        return model.add_linear_constraint(lhs, poi.Eq, 0)


    def emission_calc_by_zone_rule(self, y, z):
        """
        Rule for carbon emission calculation by zone.

        Args:
            model (pyomo.core.base.PyomoModel.ConcreteModel): Model to be solved.
            y (int): Year.
            z (str): Zone.

        Returns:
            pyomo.core.base.PyomoModel.ConcreteModel: Model with carbon emission calculation by zone rule.
        """
        model = self.model
        ef = self.para['emission_factor']
        dt = self.para['dt']
        lhs = model.carbon_capacity[y, z] - poi.quicksum(
            ef[te, y] * model.gen[h, m, y, z, te] * dt
            for h, m, te in model.hour_month_tech_tuples
        )
        return model.add_linear_constraint(lhs, poi.Eq, 0)


    def power_balance_rule(self, h, m, y, z):
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
        model = self.model
        lc = self.para['transmission_line_existing_capacity']
        load = self.para['demand']
        imp_z = poi.quicksum(
            model.trans_import[h, m, y, z, z1] 
            for z1 in model.zone if (z, z1) in lc.keys()
        )
        exp_z = poi.quicksum(
            model.trans_export[h, m, y, z, z1] 
            for z1 in model.zone if (z, z1) in lc.keys()
        )
        gen_z = poi.quicksum(
            model.gen[h, m, y, z, te] for te in model.tech
        )
        charge_z = poi.quicksum(
            model.charge[h, m, y, z, te] for te in model.storage_tech
        )
        demand_z = load[z, y, m, h]
        lhs = demand_z - (imp_z - exp_z + gen_z - charge_z)
        return model.add_linear_constraint(lhs, poi.Eq, 0)


    def trans_physical_rule(self, y, z, z1):
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
        model = self.model
        lhs = model.cap_newline[y, z, z1] - model.cap_newline[y, z1, z]
        return model.add_linear_constraint(lhs, poi.Eq, 0)


    def trans_capacity_rule(self, y, z, z1):
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
        model = self.model
        Year = self.para['year']
        lc = self.para['transmission_line_existing_capacity']
        remaining_capacity_line = lc[z, z1]
        new_capacity_line = poi.quicksum(
            model.cap_newline[yy, z, z1] for yy in Year[:Year.index(y) + 1]
        )
        lhs = model.cap_lines_existing[y, z, z1] - \
            (remaining_capacity_line + new_capacity_line)
        return model.add_linear_constraint(lhs, poi.Eq, 0)


    def trans_balance_rule(self, h, m, y, z, z1):
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
        model = self.model
        eff = self.para['transmission_line_efficiency'][z, z1]
        lhs = model.trans_import[h, m, y, z, z1] \
            - eff * model.trans_export[h, m, y, z, z1]
        return model.add_linear_constraint(lhs, poi.Eq, 0)


    def trans_up_bound_rule(self, h, m, y, z, z1):
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
        model = self.model
        lhs = model.trans_export[h, m, y, z, z1] \
            - model.cap_lines_existing[y, z, z1]
        return model.add_linear_constraint(lhs, poi.Leq, 0)


    def gen_up_bound_rule(self, h, m, y, z, te):
        """
        model = self.model
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
        model = self.model
        lhs = model.gen[h, m, y, z, te] - model.cap_existing[y, z, te]
        return model.add_linear_constraint(lhs, poi.Leq, 0)


    def tech_up_bound_rule(self, y, z, te):
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
        model = self.model
        tub =  self.para['technology_upper_bound'][te, z]
        if tub == np.Inf:
            return None
        else:
            lhs = model.cap_existing[y, z, te] - tub
            return model.add_linear_constraint(lhs, poi.Leq, 0)


    def new_tech_up_bound_rule(self, y, z, te):
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
        model = self.model
        ntub = self.para['new_technology_upper_bound'][te, z]
        if ntub == np.Inf:
            return None
        else:
            lhs = model.cap_newtech[y, z, te] - ntub
            return model.add_linear_constraint(lhs, poi.Leq, 0)


    def new_tech_low_bound_rule(self, y, z, te):
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
        model = self.model
        ntlb = self.para['new_technology_lower_bound'][te, z]
        lhs = model.cap_newtech[y, z, te] - ntlb
        return model.add_linear_constraint(lhs, poi.Geq, 0)


    def renew_gen_rule(self, h, m, y, z, te):
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
        model = self.model
        cf = self.para['capacity_factor'][te, z, y, m, h]
        dt = self.para['dt']
        cap = model.cap_existing[y, z, te]
        gen = model.gen[h, m, y, z, te]
        lhs = gen - cap * cf * dt
        return model.add_linear_constraint(lhs, poi.Leq, 0)


    def tech_lifetime_rule(self, y, z, te):
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
        model = self.model
        lifetime = self.para['lifetime'][te, y]
        service_time = y - self.para['year'][0]
        hcap = self.para['historical_capacity']
        rt = model.remaining_technology[y, z, te]
        remaining_time = int(lifetime - service_time)
        if remaining_time <= 0:
            lhs = model.remaining_technology[y, z, te]
        else:
            lhs = rt - poi.quicksum(
                hcap[z, te, a] for a in range(0, remaining_time)
            )
        return model.add_linear_constraint(lhs, poi.Eq, 0)


    def energy_storage_balance_rule(self, h, m, y, z, te):
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
        model = self.model
        de = self.para['discharge_efficiency'][te, y]
        dt = self.para['dt']
        ce = self.para['charge_efficiency'][te, y]
        lhs = model.storage[h, m, y, z, te] - (
            model.storage[h-1, m, y, z, te] 
            - model.gen[h, m, y, z, te] * de * dt 
            + model.charge[h, m, y, z, te] * ce * dt
        )
        return model.add_linear_constraint(lhs, poi.Eq, 0)


    def init_energy_storage_rule(self, m, y, z, te):
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
        model = self.model
        esl = self.para['initial_energy_storage_level'][te, z]
        epr = self.para['energy_to_power_ratio'][te]
        lhs = (
            model.storage[0, m, y, z, te] 
            - esl * model.cap_existing[y, z, te] * epr
        )
        return model.add_linear_constraint(lhs, poi.Eq, 0)


    def end_energy_storage_rule(self, m, y, z, te):
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
        model = self.model
        h_init = self.para['hour'][-1]
        lhs = (
            model.storage[h_init, m, y, z, te] 
            - model.storage[0, m, y, z, te]
        )
        return model.add_linear_constraint(lhs, poi.Eq, 0)


    def energy_storage_up_bound_rule(self, h, m, y, z, te):
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
        model = self.model
        epr = self.para['energy_to_power_ratio'][te]
        lhs = (
            model.storage[h, m, y, z, te] 
            - model.cap_existing[y, z, te] * epr
        )
        return model.add_linear_constraint(lhs, poi.Leq, 0)


    def energy_storage_gen_rule(self, h, m, y, z, te):
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
        model = self.model
        de = self.para['discharge_efficiency'][te, y]
        dt = self.para['dt']
        lhs = model.gen[h, m, y, z, te] * de * dt - model.storage[h-1, m, y, z, te]
        return model.add_linear_constraint(lhs, poi.Leq, 0)


    def ramping_up_rule(self, h, m, y, z, te):
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
        model = self.model
        rp = self.para['ramp_up'][te] * self.para['dt']
        if h > 1 and rp < 1:
            lhs = (
                model.gen[h, m, y, z, te] - model.gen[h-1, m, y, z, te] 
                - rp * model.cap_existing[y, z, te]
            )
            return model.add_linear_constraint(lhs, poi.Leq, 0)
        else:
            return None


    def ramping_down_rule(self, h, m, y, z, te):
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
        model = self.model
        rd = self.para['ramp_down'][te] * self.para['dt']
        if h > 1 and  rd < 1:
            lhs = (
                model.gen[h-1, m, y, z, te] - model.gen[h, m, y, z, te] 
                - rd * model.cap_existing[y, z, te]
            )
            return model.add_linear_constraint(lhs, poi.Leq, 0)
        else:
            return None


    def natural_inflow_rule(self, s, h, m, y):
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
        model = self.model
        inflow = self.para['inflow'][s, y, m, h]
        lhs = model.naturalinflow[s, h, m, y] - inflow
        return model.add_linear_constraint(lhs, poi.Eq, 0)


    def total_inflow_rule(self, s, h, m, y):
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
        model = self.model
        hour = self.para['hour']
        wdt = self.para['water_delay_time']
        dt = self.para['dt']
        up_stream_outflow = 0
        for ups, delay in zip(
            wdt[wdt['NEXTPOWER_ID'] == s].POWER_ID, 
            wdt[wdt['NEXTPOWER_ID'] == s].delay
        ):
            delay = int(int(delay)/dt)
            if (h - delay >= hour[0]):
                t = h-delay
            else:
                t = hour[-1] - delay + h
            up_stream_outflow += model.outflow[ups, t, m, y]
        lhs = (model.inflow[s, h, m, y] - 
            (model.naturalinflow[s, h, m, y] + up_stream_outflow)
        )
        return model.add_linear_constraint(lhs, poi.Eq, 0)


    def water_balance_rule(self, s, h, m, y):
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
        model = self.model
        netflow = (
            model.inflow[s, h, m, y] 
            - model.outflow[s, h, m, y] 
            - model.withdraw[s, h, m, y]
        )
        netstorage = 3600 * self.para['dt'] * netflow
        lhs = model.storage_reservoir[s, h, m, y] - (
            model.storage_reservoir[s, h-1, m, y] + netstorage
        )
        return model.add_linear_constraint(lhs, poi.Eq, 0)


    def discharge_rule(self, s, h, m, y):
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
        model = self.model
        lhs = model.outflow[s, h, m, y] - (
            model.genflow[s, h, m, y] + model.spillflow[s, h, m, y]
        )
        return model.add_linear_constraint(lhs, poi.Eq, 0)


    def outflow_low_bound_rule(self, s, h, m, y):
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
        model = self.model
        min_outflow = self.para['reservoir_characteristics']['outflow_min', s]
        lhs = model.outflow[s, h, m, y] - min_outflow
        return model.add_linear_constraint(lhs, poi.Geq, 0)


    def outflow_up_bound_rule(self, s, h, m, y):
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
        model = self.model
        max_outflow = self.para['reservoir_characteristics']['outflow_max', s]
        lhs = model.outflow[s, h, m, y] - max_outflow
        return model.add_linear_constraint(lhs, poi.Leq, 0)


    def storage_low_bound_rule(self, s, h, m, y):
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
        model = self.model
        min_storage = self.para['reservoir_storage_lower_bound'][s, m, h]
        lhs = model.storage_reservoir[s, h, m, y] - min_storage
        return model.add_linear_constraint(lhs, poi.Geq, 0)


    def storage_up_bound_rule(self, s, h, m, y):
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
        model = self.model
        max_storage = self.para['reservoir_storage_upper_bound'][s, m, h]
        lhs = model.storage_reservoir[s, h, m, y] - max_storage
        return model.add_linear_constraint(lhs, poi.Leq, 0)


    def output_low_bound_rule(self, s, h, m, y):
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
        model = self.model
        min_output = self.para['reservoir_characteristics']['N_min', s]
        lhs = model.output[s, h, m, y] - min_output
        return model.add_linear_constraint(lhs, poi.Geq, 0)


    def output_up_bound_rule(self, s, h, m, y):
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
        model = self.model
        max_output = self.para['reservoir_characteristics']['N_max', s]
        lhs = model.output[s, h, m, y] - max_output
        return model.add_linear_constraint(lhs, poi.Leq, 0)


    def output_calc_rule(self, s, h, m, y):
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
        model = self.model
        efficiency = self.para['reservoir_characteristics']['coeff', s]
        lhs = (
            model.output[s, h, m, y] 
            - model.genflow[s, h, m, y] * efficiency * 1e-3 # head_param
        )
        return model.add_linear_constraint(lhs, poi.Eq, 0)


    def init_storage_rule(self, s, m, y):
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
        model = self.model
        hour_period = [0] + self.para['hour']
        init_storage = self.para['initial_reservoir_storage_level'][m, s]
        lhs = model.storage_reservoir[s, hour_period[0], m, y] - init_storage
        return model.add_linear_constraint(lhs, poi.Eq, 0)


    def end_storage_rule(self, s, m, y):
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
        model = self.model
        hour_period = [0] + self.para['hour']
        final_storage = self.para['final_reservoir_storage_level'][m, s]
        lhs = model.storage_reservoir[s, hour_period[-1], m, y] - final_storage
        return model.add_linear_constraint(lhs, poi.Eq, 0)


    def hydro_output_rule(self, h, m, y, z):
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
        model = self.model
        tech_type = self.para['technology_type']
        res_char = self.para['reservoir_characteristics']
        dt = self.para['dt']
        predifined_hydro = self.para['predefined_hydropower']
        hydro_type = [i for i, j in tech_type.items() if j == 'hydro']
        if len(hydro_type) == 0:
            return None
        if self.para['isinflow']:
            hydro_output = poi.quicksum(
                model.output[s, h, m, y] * self.para['dt'] 
                for s in model.station if res_char['zone', s] == z
            )
            lhs = model.gen[h, m, y, z, hydro_type[0]] - hydro_output
        else:
            lhs = (model.gen[h, m, y, z, hydro_type[0]] 
                - predifined_hydro['Hydro', z, y, m, h] * dt
            )
        return model.add_linear_constraint(lhs, poi.Eq, 0)

    # Rules to generate expressions for the model
    def _cost_var_breakdown(self, y, z, te):
        model = self.model
        tvc = self.para['technology_variable_OM_cost'][te, y]
        dt = self.para['dt']
        vf = self.para['var_factor'][y] 
        return poi.quicksum(
            tvc * model.gen[h, m, y, z, te] * dt * vf
            for h, m in model.hour_month_tuples
        )
        
    def _cost_fix_breakdown(self, y, z, te):
        model = self.model
        tfc = self.para['technology_fixed_OM_cost'][te, y]
        ff = self.para['fix_factor'][y]
        return tfc * model.cap_existing[y, z, te] * ff

    def _cost_newtech_breakdown(self, y, z, te):
        model = self.model
        tic = self.para['technology_investment_cost'][te, y]
        ivf = self.para['inv_factor'][te, y]
        return tic * model.cap_newtech[y, z, te] * ivf
    
    def _cost_newline_breakdown(self, y, z, z1):
        model = self.model
        lic = self.para['transmission_line_investment_cost'][z, z1]
        return lic * model.cap_newline[y, z, z1]
    
    def _carbon_breakdown(self, y, z, te):
        model = self.model
        ef = self.para['emission_factor'][te, y]
        dt = self.para['dt']
        return poi.quicksum(
            ef * model.gen[h, m, y, z, te] * dt 
            for h, m in model.hour_month_tuples
        )