#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""This module contains constraints related to technology generation. 
"""

import pyoptinterface as poi

class AddGenerationConstraints:
    """Add constraints for generation in the model.
    """
    def __init__(self, model):
        """Initialize the class and add constraints.
        """
        self.model = model
        model.gen_up_bound_cons = poi.make_tupledict(
            model.hour_month_year_zone_tech_tuples, rule=self.gen_up_bound_rule
        )
        model.ramping_up_cons = poi.make_tupledict(
            model.hour_month_year_zone_tech_tuples, rule=self.ramping_up_rule
        )
        model.ramping_down_cons = poi.make_tupledict(
            model.hour_month_year_zone_tech_tuples, rule=self.ramping_down_rule
        )
    
    def gen_up_bound_rule(self, h, m, y, z, te):
        """Generation is less than or equal to the existing capacity.

        Parameters
        ----------
        h : int
            Hour.
        m : int
            Month.
        y : int
            Year.
        z : str
            Zone.
        te : str
            Technology.
            
        Returns
        -------
        pyoptinterface._src.core_ext.ConstraintIndex
            Constraint index of the model.
        """
        model = self.model
        lhs = model.gen[h, m, y, z, te] - model.cap_existing[y, z, te]
        return model.add_linear_constraint(lhs, poi.Leq, 0)

    def ramping_up_rule(self, h, m, y, z, te):
        """Ramping up limits.

        Parameters
        ----------
        h : int
            Hour.
        m : int
            Month.
        y : int
            Year.
        z : str
            Zone.
        te : str
            Technology.
            
        Returns
        -------
        pyoptinterface._src.core_ext.ConstraintIndex
            Constraint index of the model.
        """
        model = self.model
        rp = model.params['ramp_up'][te] * model.params['dt']
        if h > 1 and rp < 1:
            lhs = (
                model.gen[h, m, y, z, te] - model.gen[h-1, m, y, z, te]
                - rp * model.cap_existing[y, z, te]
            )
            return model.add_linear_constraint(lhs, poi.Leq, 0)
        else:
            return None


    def ramping_down_rule(self, h, m, y, z, te):
        """Ramping down limits.

        Parameters
        ----------
        h : int
            Hour.
        m : int
            Month.
        y : int
            Year.
        z : str
            Zone.
        te : str
            Technology.
            
        Returns
        -------
        pyoptinterface._src.core_ext.ConstraintIndex
            Constraint index of the model.
        """
        model = self.model
        rd = model.params['ramp_down'][te] * model.params['dt']
        if h > 1 and  rd < 1:
            lhs = (
                model.gen[h-1, m, y, z, te] - model.gen[h, m, y, z, te]
                - rd * model.cap_existing[y, z, te]
            )
            return model.add_linear_constraint(lhs, poi.Leq, 0)
        else:
            return None
