#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""This module contains transmission related functions. """ 

import pyoptinterface as poi

class AddTransmissionConstraints:
    """ Add constraints for transmission lines while considering multiple 
    zones. 
    """
    def __init__(self, model):
        """ Initialize the class and add constraints.
        """
        self.model = model
        model.trans_capacity_cons = poi.make_tupledict(
            model.year_zone_zone_tuples, rule=self.trans_capacity_rule
        )
        model.trans_physical_cons = poi.make_tupledict(
            model.year_zone_zone_tuples, rule=self.trans_physical_rule
        )
        model.trans_balance_cons = poi.make_tupledict(
            model.hour_month_year_zone_zone_tuples,
            rule=self.trans_balance_rule
        )
        model.trans_up_bound_cons = poi.make_tupledict(
            model.hour_month_year_zone_zone_tuples,
            rule=self.trans_up_bound_rule
        )
    def trans_physical_rule(self, y, z, z1):
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
        lhs = model.cap_newline[y, z, z1] - model.cap_newline[y, z1, z]
        return model.add_linear_constraint(lhs, poi.Eq, 0)


    def trans_capacity_rule(self, y, z, z1):
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
        pyoptinterface._src.core_ext.ConstraintIndex
            Constraint index of the model.
        """
        model = self.model
        year = model.para['year']
        lc = model.para['transmission_line_existing_capacity']
        remaining_capacity_line = lc[z, z1]
        new_capacity_line = poi.quicksum(
            model.cap_newline[yy, z, z1] for yy in year[:year.index(y) + 1]
        )
        lhs = new_capacity_line
        lhs += remaining_capacity_line
        lhs -= model.cap_lines_existing[y, z, z1]
        return model.add_linear_constraint(lhs, poi.Eq, 0)

    def trans_balance_rule(self, h, m, y, z, z1):
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
        eff = model.para['transmission_line_efficiency'][z, z1]
        lhs = model.trans_import[h, m, y, z, z1] \
            - eff * model.trans_export[h, m, y, z, z1]
        return model.add_linear_constraint(lhs, poi.Eq, 0)


    def trans_up_bound_rule(self, h, m, y, z, z1):
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
        lhs = model.trans_export[h, m, y, z, z1] \
            - model.cap_lines_existing[y, z, z1]
        return model.add_linear_constraint(lhs, poi.Leq, 0)
