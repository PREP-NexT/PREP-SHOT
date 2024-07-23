#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""This module contains objective functions for the model. The objective
function of the model is to minimize the net present value of the system's
cost. This includes capital cost, fixed O&M cost, variable cost and fuel cost
by cost type, technology cost, transmission line cost by the source of cost,
and operation cost and planning cost by the source of cost.

The cost equations are defined as follows:

.. image:: ../_static/cost_eq.png
    :width: 700
    :align: center
    :alt: Calculation of system-wide total cost

.. math::

    \\rm{cost}_{\\rm{tech}}^{\\rm{var}} &= \\frac{\\sum_{h,m,y,z,\\rm{e}}
    C_{y,z,\\rm{e}}^{\\rm{tech-var}}\\times \\rm{gen}_{h,m,y,z,\\rm{e}}}
    {\omega} \\times \\rm{factor}_{y}^{\\rm{var}} 
    
    \\rm{cost}_{\\rm{line}}^{\\rm{var}} &= \\frac{\\sum_{h,m,y,z_s,z_o}
    C_{y,z}^{\\rm{line-var}}\\times \\rm{export}_{h,m,y,z_s,z_o}}{\omega}
    \\times \\rm{factor}_{y}^{\\rm{var}}
    
    \\rm{cost}^{\\rm{fuel}} & = \\frac{\\sum_{h,m,y,z,\\rm{e}}
    C_{y,z,\\rm{e}}^{\\rm{fuel}}\\times \\rm{gen}_{h,m,y,z,\\rm{e}}}{\omega}
    \\times \\rm{factor}_{y}^{\\rm{var}} 

    \\rm{cost}_{\\rm{tech}}^{\\rm{fix}} &= \\sum_{y,z,\\rm{e}}
    C_{y,z,\\rm{e}}^{\\rm{tech-fix}}\\times 
    \\rm{cap}_{y,z,\\rm{e}}^{\\rm{existing-tech}}\\times 
    \\rm{factor}_{y}^{\\rm{fix}}

    \\rm{cost}_{\\rm{line}}^{\\rm{fix}} &= \\sum_{y,z_s,z_o}
    C_{y,z_s,z_o}^{\\rm{line-fix}}\\times 
    \\rm{cap}_{y,z_s,z_o}^{\\rm{existing-line}}\\times
    \\rm{factor}_{y}^{\\rm{fix}}

    \\rm{cost}_{\\rm{tech}}^{\\rm{inv}} &=  \\sum_{y,z,\\rm{e}}
    C_{y,z,\\rm{e}}^{\\rm{tech-inv}}\\times 
    \\rm{cap}_{y,z,\\rm{e}}^{\\rm{tech-inv}}\\times
    \\rm{factor}_{y}^{\\rm{inv}}

    \\rm{cost}_{\\rm{line}}^{\\rm{inv}} &= \\sum_{y,z_s,z_o}
    C_{y,z_s,z_o}^{\\rm{line-inv}}\\times
    \\rm{cap}_{y,z_s,z_o}^{\\rm{line-inv}}\\times
    \\rm{factor}_{y}^{\\rm{inv}} \\times 0.5

"""

from typing import Union

import pyoptinterface as poi

class AddCostObjective:
    """Objective function class to determine the total cost of the model.
    """
    def __init__(self, model : object) -> None:
        """The constructor for objective functions class.

        Parameters
        ----------
        model : object
            Model to be solved.
        """
        self.model = model
        self.define_objective()

    def define_objective(self) -> None:
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

    def fuel_cost_breakdown(
        self, y : int, z : str, te : str
    ) -> poi.ExprBuilder:
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
        poi.ExprBuilder
            Fuel cost at a given year, zone and technology.
        """
        model = self.model
        fp = model.params['fuel_price'][te, y]
        dt = model.params['dt']
        vf = model.params['var_factor'][y]
        w = model.params['weight']
        return (1 / w * fp * dt * vf
            * poi.quicksum(model.gen.select('*', '*', y, z, te)))

    def cost_var_line_breakdown(
        self, y : int, z : str, z1 : str
    ) -> poi.ExprBuilder:
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
        poi.ExprBuilder
            Variable operation and maintenance cost of transmission lines at a 
            given year, source and destination zone.
        """
        model = self.model
        lvc = model.params['transmission_line_variable_OM_cost'][z, z1]
        dt = model.params['dt']
        vf = model.params['var_factor'][y]
        w = model.params['weight']
        return (0.5 / w * lvc * dt * vf
            * poi.quicksum(model.trans_export.select('*', '*', y, z, z1)))

    def cost_var_tech_breakdown(
        self, y : int, z : str, te : str
    ) -> poi.ExprBuilder:
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
        poi.ExprBuilder
            Variable operation and maintenance cost of technologies at a given 
            year, zone and technology.
        """
        model = self.model
        tvc = model.params['technology_variable_OM_cost'][te, y]
        dt = model.params['dt']
        vf = model.params['var_factor'][y]
        w = model.params['weight']
        return (1 / w * tvc * dt * vf
            * poi.quicksum(model.gen.select('*', '*', y, z, te)))

    def cost_fix_line_breakdown(
        self, y : int, z : str, z1 : str
    ) -> poi.ExprBuilder:
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
        poi.ExprBuilder
            Fixed operation and maintenance cost of transmission lines at a given 
            year, source and destination zone.
        """
        model = self.model
        lfc = model.params['transmission_line_fixed_OM_cost']
        ff = model.params['fix_factor']
        return lfc[z, z1] * model.cap_lines_existing[y, z, z1] * ff[y] * 0.5

    def cost_fix_tech_breakdown(
        self, y : int, z : str, te : str
    ) -> poi.ExprBuilder:
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
        poi.ExprBuilder
            Fixed operation and maintenance cost of technologies at a given year, 
            zone and technology.
        """
        model = self.model
        tfc = model.params['technology_fixed_OM_cost'][te, y]
        ff = model.params['fix_factor'][y]
        return  tfc * model.cap_existing[y, z, te] * ff

    def cost_newtech_breakdown(
        self, y : int, z : str, te : str
    ) -> poi.ExprBuilder:
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
        poi.ExprBuilder
            Investment cost of new technologies at a given year, zone and 
            technology.
        """
        model = self.model
        tic = model.params['technology_investment_cost'][te, y]
        ivf = model.params['inv_factor'][te, y]
        return tic * model.cap_newtech[y, z, te] * ivf

    def cost_newline_breakdown(
        self, y : int, z : str, z1 : str
    ) -> poi.ExprBuilder:
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
        poi.ExprBuilder
            Investment cost of new transmission lines at a given year, source and 
            destination zone.
        """
        model = self.model
        lic = model.params['transmission_line_investment_cost'][z, z1]
        d = model.params['distance'][z, z1]
        ivf = model.params['trans_inv_factor'][y]
        capacity_invested_line = model.cap_newline[y, z, z1]
        return lic * capacity_invested_line * d * ivf * 0.5

    def income_rule(self) -> poi.ExprBuilder:
        """Income from water withdrawal.
        Reference: https://www.nature.com/articles/s44221-023-00126-0

        Returns
        -------
        poi.ExprBuilder
            Income from water withdrawal.
        """
        model = self.model
        if model.params['isinflow']:
            coef = 3600 * model.params['dt'] * model.params['price']
            income = sum(
                model.withdraw[s, h, m, y] * coef
                for s in model.station
                for h in model.hour
                for m in model.month
                for y in model.year
            )
            return income

        return poi.ExprBuilder(0)

    def var_cost_rule(self) -> poi.ExprBuilder:
        """Calculate total variable cost, which is sum of the fuel cost of 
        technologies and variable Operation and maintenance (O&M) cost of 
        technologies and transmission lines.
        
        Returns
        -------
        poi.ExprBuilder
            Total variable cost across all years, zones and technologies.
        """
        model = self.model
        model.cost_var_tech_breakdown = poi.make_tupledict(
            model.year, model.zone, model.tech,
            rule=self.cost_var_tech_breakdown
        )

        model.cost_fuel_breakdown = poi.make_tupledict(
            model.year, model.zone, model.tech,
            rule=self.fuel_cost_breakdown
        )

        model.cost_var_line_breakdown = poi.make_tupledict(
            model.year, model.zone, model.zone,
            rule=self.cost_var_line_breakdown
        )
        cost_var = poi.ExprBuilder()
        cost_var += poi.quicksum(model.cost_var_tech_breakdown)
        cost_var += poi.quicksum(model.cost_fuel_breakdown)
        cost_var += poi.quicksum(model.cost_var_line_breakdown)
        return cost_var

    def newtech_cost_rule(self) -> poi.ExprBuilder:
        """Total investment cost of new technologies.
        
        Returns
        -------
        poi.ExprBuilder
            Total investment cost of new technologies over all years, zones and 
            technologies.
        """
        model = self.model
        model.cost_newtech_breakdown = poi.make_tupledict(
            model.year, model.zone, model.tech,
            rule=self.cost_newtech_breakdown
        )
        return poi.quicksum(model.cost_newtech_breakdown)

    def newline_cost_rule(self) -> poi.ExprBuilder:
        """Total investment cost of new transmission lines.

        Returns
        -------
        poi.ExprBuilder
            Total investment cost of new transmission lines over all years, 
            zones.
        """
        model = self.model
        model.cost_newline_breakdown = poi.make_tupledict(
            model.year, model.zone, model.zone,
            rule=self.cost_newline_breakdown
        )
        return poi.quicksum(model.cost_newline_breakdown)

    def fix_cost_rule(self) -> poi.ExprBuilder:
        """Fixed O&M cost of technologies and transmission lines.
        
        Returns
        -------
        poi.ExprBuilder
            Total fixed O&M cost of technologies and transmission lines over
            all years, zones and technologies.
        """
        model = self.model
        model.cost_fix_tech_breakdown = poi.make_tupledict(
            model.year, model.zone, model.tech,
            rule=self.cost_fix_tech_breakdown
        )
        model.cost_fix_line_breakdown = poi.make_tupledict(
            model.year, model.zone, model.zone,
            rule=self.cost_fix_line_breakdown
        )
        return poi.quicksum(model.cost_fix_tech_breakdown) + \
            poi.quicksum(model.cost_fix_line_breakdown)
