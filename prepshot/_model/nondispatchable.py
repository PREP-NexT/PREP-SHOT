#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""This module contains functions related to nondispatchable technologies. 
"""

import pyoptinterface as poi

class AddNondispatchableConstraints:
    """Add constraints for nondispatchable technologies. 
    """
    def __init__(self, model):
        self.model = model
        if model.nondispatchable_tech != 0:
            model.renew_gen_cons = poi.make_tupledict(
                model.hour_month_year_zone_nondispatchable_tuples,
                rule=self.renew_gen_rule
            )

    def renew_gen_rule(self, h, m, y, z, te):
        """Renewable generation is determined by the capacity factor and 
        existing capacity.
        
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
        cf = model.params['capacity_factor'][te, z, y, m, h]
        dt = model.params['dt']
        cap = model.cap_existing[y, z, te]
        gen = model.gen[h, m, y, z, te]
        lhs = gen - cap * cf * dt
        return model.add_linear_constraint(lhs, poi.Leq, 0)
