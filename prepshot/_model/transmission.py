#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""This module contains transmission related functions. """ 

from typing import Union

import pyoptinterface as poi

class AddTransmissionConstraints:
    """Add constraints for transmission lines while considering multiple 
    zones. 
    """
    def __init__(self,
        model : Union[
            poi._src.highs.Model,
            poi._src.gurobi.Model,
            poi._src.mosek.Model,
            poi._src.copt.Model
        ]
    ):
        """Initialize the class and add constraints.
        """
        self.model = model
        model.cap_lines_existing = poi.make_tupledict(
            model.year, model.zone, model.zone,
            rule=self.trans_capacity_rule
        )
        model.trans_import = poi.make_tupledict(
            model.hour, model.month, model.year, model.zone, model.zone,
            rule=self.trans_balance_rule
        )
        model.trans_physical_cons = poi.make_tupledict(
            model.year, model.zone, model.zone,
            rule=self.trans_physical_rule
        )
        model.trans_up_bound_cons = poi.make_tupledict(
            model.hour, model.month, model.year, model.zone, model.zone,
            rule=self.trans_up_bound_rule
        )


    def trans_physical_rule(self,
        y : int, z : str, z1 : str
    ) -> poi._src.core_ext.ConstraintIndex:
        """Physical transmission lines.

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
        pyoptinterface._src.core_ext.ConstraintIndex
            Constraint index of the model.
        """
        model = self.model
        if z != z1:
            lhs = model.cap_newline[y, z, z1] - model.cap_newline[y, z1, z]
            return model.add_linear_constraint(lhs, poi.Eq, 0)


    def trans_capacity_rule(self,
        y : int, z : str, z1 : str
    ) -> poi._src.core_ext.ExprBuilder:
        """Transmission capacity equal to the sum of the existing capacity 
        and the new capacity in previous planned years.

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
            Index of expression of the model.
        """
        model = self.model
        year = model.params['year']
        lc = model.params['transmission_line_existing_capacity']
        remaining_capacity_line = lc[z, z1]
        cap_lines_existing = poi.ExprBuilder()
        new_capacity_line = poi.quicksum(
            model.cap_newline[yy, z, z1] for yy in year[:year.index(y) + 1]
        )
        cap_lines_existing += new_capacity_line
        cap_lines_existing += remaining_capacity_line
        return cap_lines_existing


    def trans_balance_rule(self,
        h : int, m : int, y : int, z : str, z1 : str
    ) -> poi._src.core_ext.ConstraintIndex:
        """Transmission balance, i.e., the electricity imported from zone z1 
        to zone z should be equal to the electricity exported from zone z 
        to zone z1 multiplied by the transmission line efficiency.

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
        z1 : str
            Zone.

        Returns
        -------
        pyoptinterface._src.core_ext.ConstraintIndex
            Constraint index of the model.
        """
        model = self.model
        eff = model.params['transmission_line_efficiency'][z, z1]
        return eff * model.trans_export[h, m, y, z, z1]


    def trans_up_bound_rule(self,
        h : int, m : int, y : int, z : str, z1 : str
    ) -> poi._src.core_ext.ConstraintIndex:
        """Transmitted power is less than or equal to the transmission line 
        capacity.

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
        z1 : str
            Zone.

        Returns
        -------
        pyoptinterface._src.core_ext.ConstraintIndex
            Constraint index of the model.
        """
        model = self.model
        lhs = model.trans_export[h, m, y, z, z1]                              \
            - model.cap_lines_existing[y, z, z1]
        return model.add_linear_constraint(lhs, poi.Leq, 0)
