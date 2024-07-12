#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""This module is used to determine investment-related constraints. 
"""

import numpy as np
import pyoptinterface as poi

class AddInvestmentConstraints:
    """Add constraints for investment in the model.
    """
    def __init__(self, model):
        """Initialize the class and add constraints.
        """
        self.model = model
        model.tech_up_bound_cons = poi.make_tupledict(
            model.year_zone_tech_tuples, rule=self.tech_up_bound_rule
        )
        model.new_tech_up_bound_cons = poi.make_tupledict(
            model.year_zone_tech_tuples, rule=self.new_tech_up_bound_rule
        )
        model.new_tech_low_bound_cons = poi.make_tupledict(
            model.year_zone_tech_tuples, rule=self.new_tech_low_bound_rule
        )
        model.tech_lifetime_cons = poi.make_tupledict(
            model.year_zone_tech_tuples, rule=self.tech_lifetime_rule
        )
        model.remaining_capacity_cons = poi.make_tupledict(
            model.year, model.zone, model.tech,
            rule=self.remaining_capacity_rule
        )

    def tech_up_bound_rule(self, y, z, te):
        """Allowed capacity of commercial operation technology is less than or 
        equal to the predefined upper bound.

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
        pyoptinterface._src.core_ext.ConstraintIndex
            Constraint index of the model.
        """
        model = self.model
        tub =  model.params['technology_upper_bound'][te, z]
        if tub != np.Inf:
            lhs = model.cap_existing[y, z, te] - tub
            return model.add_linear_constraint(lhs, poi.Leq, 0)
        return None

    def new_tech_up_bound_rule(self, y, z, te):
        """New investment technology upper bound in specific year and zone.

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
        pyoptinterface._src.core_ext.ConstraintIndex
            Constraint index of the model.
        """
        model = self.model
        ntub = model.params['new_technology_upper_bound'][te, z]
        if ntub == np.Inf:
            return None
        else:
            lhs = model.cap_newtech[y, z, te] - ntub
            return model.add_linear_constraint(lhs, poi.Leq, 0)

    def new_tech_low_bound_rule(self, y, z, te):
        """New investment technology lower bound.

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
        pyoptinterface._src.core_ext.ConstraintIndex
            Constraint index of the model.
        """
        model = self.model
        ntlb = model.params['new_technology_lower_bound'][te, z]
        lhs = model.cap_newtech[y, z, te] - ntlb
        return model.add_linear_constraint(lhs, poi.Geq, 0)

    def tech_lifetime_rule(self, y, z, te):
        """Caculation of remaining technology capacity based on lifetime 
        constraints.

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
        pyoptinterface._src.core_ext.ConstraintIndex
            Constraint index of the model.
        """
        model = self.model
        lifetime = model.params['lifetime'][te, y]
        service_time = y - model.params['year'][0]
        hcap = model.params['historical_capacity']
        rt = model.remaining_technology[y, z, te]
        remaining_time = int(lifetime - service_time)
        if remaining_time <= 0:
            lhs = model.remaining_technology[y, z, te]
        else:
            lhs = poi.quicksum(
                hcap[z, te, a] for a in range(0, remaining_time)
            )
            lhs -= rt
        return model.add_linear_constraint(lhs, poi.Eq, 0)

    def remaining_capacity_rule(self, y, z, te):
        """Remaining capacity of initial technology due to lifetime 
        restrictions. Where in modeled year y, the available technology
        consists of the following.
        
        1. The remaining in-service installed capacity from the initial 
           technology.
        2. The remaining in-service installed capacity from newly built 
           technology in the previous modelled years.

        Parameters
        ----------
        y : int
            Planned year.
        z : str
            Zone.
        te : str
            technology.

        Returns
        -------
        pyoptinterface._src.core_ext.ConstraintIndex
            Constraint index of the model.
        """
        model = self.model
        year = model.params['year']
        lt = model.params['lifetime']
        new_tech = poi.quicksum(
            model.cap_newtech[yy, z, te]
            for yy in year[:year.index(y) + 1]
            if y - yy < lt[te, y]
        )
        lhs = new_tech
        lhs += model.remaining_technology[y, z, te]
        lhs -= model.cap_existing[y, z, te]
        return model.add_linear_constraint(lhs, poi.Eq, 0)
