#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""This module contains constraints related to demand. 
"""
from typing import Union

import pyoptinterface as poi

class AddDemandConstraints:
    """This class contains demand constraints.
    """
    def __init__(self,
        model : Union[
            poi._src.highs.Model,
            poi._src.gurobi.Model,
            poi._src.mosek.Model,
            poi._src.copt.Model
        ]
    ) -> None:
        """Initialize the class and add constraints.
        """
        self.model = model
        model.power_balance_cons = poi.make_tupledict(
            model.hour, model.month, model.year, model.zone,
            rule=self.power_balance_rule
        )
    def power_balance_rule(self,
        h : int, m : int, y : int, z : str
    ) -> poi._src.core_ext.ConstraintIndex:
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
        load = model.params['demand']
        imp_z = poi.quicksum(
            model.trans_import[h, m, y, z1, z] for z1 in model.zone
        )
        exp_z = poi.quicksum(
            model.trans_export[h, m, y, z, z1] for z1 in model.zone
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
 