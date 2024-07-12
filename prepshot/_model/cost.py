#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""This module contains objective functions for the model.
"""

import pyoptinterface as poi

class AddCostObjective:
    """Objective function class to determine the total cost of the model.
    """
    def __init__(self, model):
        """The constructor for objective functions class.

        Parameters
        ----------
        model : pyoptinterface._src.solver.Model
            Model to be solved.
        """
        self.model = model
        self.define_objective()

    def define_objective(self):
        """Objective function of the model, to minimize total cost.
        """
        model = self.model
        model.cost_var = self.var_cost_rule()
        model.cost_newtech = self.newtech_cost_rule()
        model.cost_fix = self.fix_cost_rule()
        model.cost_newline = self.newline_cost_rule()
        model.income = self.income_rule()
        model.cost = model.cost_var + model.cost_newtech                     \
            + model.cost_fix + model.cost_newline - model.income
        model.set_objective(model.cost, sense=poi.ObjectiveSense.Minimize)

    def fuel_cost_breakdown(self, y, z, te):
        """Fuel cost breakdown of technologies.

        Parameters
        ----------
        y : int
            Year.
        z : str
            Zone.
        te : str
            Technology.

        Returns
        -------
        pyoptinterface._src.core_ext.ExprBuilder
            Fuel cost at a given year, zone and technology.
        """
        model = self.model
        fp = model.params['fuel_price'][te, y]
        dt = model.params['dt']
        vf = model.params['var_factor'][y]
        w = model.params['weight']
        return 1 / w * fp * sum(model.gen[h, m, y, z, te]
            for (h,m) in model.hour_month_tuples) * dt * vf

    def cost_var_line_breakdown(self, y, z, z1):
        """Variable operation and maintenance cost breakdown of transmission 
        lines.

        Parameters
        ----------
        y : int
            Year.
        z : str
            Zone.
        z1 : str
            Zone.

        Returns
        -------
        pyoptinterface._src.core_ext.ExprBuilder
            Variable operation and maintenance cost of transmission lines at a 
            given year, source and destination zone.
        """
        model = self.model
        lvc = model.params['transmission_line_variable_OM_cost'][z, z1]
        dt = model.params['dt']
        vf = model.params['var_factor'][y]
        w = model.params['weight']
        return 0.5 / w * lvc * dt * vf * \
            sum(model.trans_export[h, m, y, z, z1]
            for (h,m) in model.hour_month_tuples)

    def cost_var_tech_breakdown(self, y, z, te):
        """Variable operation and maintenance cost breakdown.

        Parameters
        ----------
        y : int
            Year.
        z : str
            Zone.
        te : str
            Technology.

        Returns
        -------
        pyoptinterface._src.core_ext.ExprBuilder
            Variable operation and maintenance cost of technologies at a given 
            year, zone and technology.
        """
        model = self.model
        tvc = model.params['technology_variable_OM_cost'][te, y]
        dt = model.params['dt']
        vf = model.params['var_factor'][y]
        w = model.params['weight']
        return 1 / w * tvc * sum(model.gen[h, m, y, z, te]
            for (h,m) in model.hour_month_tuples) * dt * vf

    def cost_fix_line_breakdown(self, y, z, z1):
        """Fixed operation and maintenance cost breakdown of transmission 
        lines.

        Parameters
        ----------
        y : int
            Year.
        z : str
            Zone.
        z1 : str
            Zone.

        Returns
        -------
        pyoptinterface._src.core_ext.ExprBuilder
            Fixed operation and maintenance cost of transmission lines at a given 
            year, source and destination zone.
        """
        model = self.model
        lfc = model.params['transmission_line_fixed_OM_cost']
        ff = model.params['fix_factor']
        return lfc[z, z1] * model.cap_lines_existing[y, z, z1] * ff[y] * 0.5

    def cost_fix_tech_breakdown(self, y, z, te):
        """Fixed operation and maintenance cost breakdown.

        Parameters
        ----------
        y : int
            Year.
        z : str
            Zone.
        te : str
            Technology.

        Returns
        -------
        pyoptinterface._src.core_ext.ExprBuilder
            Fixed operation and maintenance cost of technologies at a given year, 
            zone and technology.
        """
        model = self.model
        tfc = model.params['technology_fixed_OM_cost'][te, y]
        ff = model.params['fix_factor'][y]
        return  tfc * model.cap_existing[y, z, te] * ff

    def cost_newtech_breakdown(self, y, z, te):
        """New technology investment cost breakdown.

        Parameters
        ----------
        y : int
            Year.
        z : str
            Zone.
        te : str
            Technology.

        Returns
        -------
        pyoptinterface._src.core_ext.ExprBuilder
            Investment cost of new technologies at a given year, zone and 
            technology.
        """
        model = self.model
        tic = model.params['technology_investment_cost'][te, y]
        ivf = model.params['inv_factor'][te, y]
        return tic * model.cap_newtech[y, z, te] * ivf

    def cost_newline_breakdown(self, y, z, z1):
        """New transmission line investment cost breakdown.

        Parameters
        ----------
        y : int
            Year.
        z : str
            Zone.
        z1 : str
            Zone.

        Returns
        -------
        pyoptinterface._src.core_ext.ExprBuilder
            Investment cost of new transmission lines at a given year, source and 
            destination zone.
        """
        model = self.model
        lic = model.params['transmission_line_investment_cost'][z, z1]
        d = model.params['distance'][z, z1]
        ivf = model.params['trans_inv_factor'][y]
        capacity_invested_line = model.cap_newline[y, z, z1]
        return lic * capacity_invested_line * d * ivf * 0.5

    def income_rule(self):
        """Income from water withdrawal.
        Reference: https://www.nature.com/articles/s44221-023-00126-0

        Returns
        -------
        pyoptinterface._src.core_ext.ExprBuilder
            Income from water withdrawal.
        """
        model = self.model
        if model.params['isinflow']:
            coef = 3600 * model.params['dt'] * model.params['price']
            income = sum(
                model.withdraw[s, h, m, y] * coef
                for s, h, m, y in model.station_hour_month_year_tuples
            )
            return income

        return poi.ExprBuilder(0)

    def var_cost_rule(self):
        """Calculate total variable cost, which is sum of the fuel cost of 
        technologies and variable Operation and maintenance (O&M) cost of 
        technologies and transmission lines.
        
        Returns
        -------
        pyoptinterface._src.core_ext.ExprBuilder
            Total variable cost across all years, zones and technologies.
        """
        model = self.model
        model.cost_var_tech_breakdown = poi.make_tupledict(
            model.year_zone_tech_tuples,
            rule=self.cost_var_tech_breakdown
        )

        model.cost_fuel_breakdown = poi.make_tupledict(
            model.year_zone_tech_tuples,
            rule=self.fuel_cost_breakdown
        )

        model.cost_var_line_breakdown = poi.make_tupledict(
            model.year_zone_zone_tuples,
            rule=self.cost_var_line_breakdown
        )
        cost_var = poi.ExprBuilder()
        cost_var += poi.quicksum(model.cost_var_tech_breakdown)
        cost_var += poi.quicksum(model.cost_fuel_breakdown)
        cost_var += poi.quicksum(model.cost_var_line_breakdown)
        return cost_var

    def newtech_cost_rule(self):
        """Total investment cost of new technologies.
        
        Returns
        -------
        pyoptinterface._src.core_ext.ExprBuilder
            Total investment cost of new technologies over all years, zones and 
            technologies.
        """
        model = self.model
        model.cost_newtech_breakdown = poi.make_tupledict(
            model.year_zone_tech_tuples,
            rule=self.cost_newtech_breakdown
        )
        return poi.quicksum(model.cost_newtech_breakdown)

    def newline_cost_rule(self):
        """Total investment cost of new transmission lines.

        Returns
        -------
        pyoptinterface._src.core_ext.ExprBuilder
            Total investment cost of new transmission lines over all years, 
            zones.
        """
        model = self.model
        model.cost_newline_breakdown = poi.make_tupledict(
            model.year_zone_zone_tuples,
            rule=self.cost_newline_breakdown
        )
        return poi.quicksum(model.cost_newline_breakdown)

    def fix_cost_rule(self):
        """Fixed O&M cost of technologies and transmission lines.
        
        Returns
        -------
        pyoptinterface._src.core_ext.ExprBuilder
            Total fixed O&M cost of technologies and transmission lines over
            all years, zones and technologies.
        """
        model = self.model
        model.cost_fix_tech_breakdown = poi.make_tupledict(
            model.year_zone_tech_tuples,
            rule=self.cost_fix_tech_breakdown
        )
        model.cost_fix_line_breakdown = poi.make_tupledict(
            model.year_zone_zone_tuples,
            rule=self.cost_fix_line_breakdown
        )
        return poi.quicksum(model.cost_fix_tech_breakdown) + \
            poi.quicksum(model.cost_fix_line_breakdown)
