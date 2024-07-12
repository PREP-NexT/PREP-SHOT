#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""This module contains constraints related to demand. 
"""

import pyoptinterface as poi

class AddDemandConstraints:
    """This class contains demand constraints.
    """
    def __init__(self, model):
        """Initialize the class and add constraints.
        """
        self.model = model
        model.power_balance_cons = poi.make_tupledict(
            model.hour_month_year_zone_tuples, rule=self.power_balance_rule
        )
    def power_balance_rule(self, h, m, y, z):
        """Nodal power balance. The total electricity demand for each time 
        period and in each zone should be met by the following.
        
        1. The sum of imported power energy from other zones.
        2. The generation from zone z minus the sum of exported power 
           energy from zone z to other zones.
        3. The charging power energy of storage technologies in zone z.  

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
        
        Returns
        -------
        pyoptinterface._src.core_ext.ConstraintIndex
            Constraint index of the model.
        """
        model = self.model
        lc = model.params['transmission_line_existing_capacity']
        load = model.params['demand']
        imp_z = poi.quicksum(
            model.trans_import[h, m, y, z1, z]
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
 