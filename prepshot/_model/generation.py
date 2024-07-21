#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""This module contains constraints related to technology generation. 
"""

from typing import Union

import pyoptinterface as poi

class AddGenerationConstraints:
    """Add constraints for generation in the model.
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
        model.gen_up_bound_cons = poi.make_tupledict(
            model.hour, model.month, model.year, model.zone, model.tech,
            rule=self.gen_up_bound_rule
        )
        model.ramping_up_cons = poi.make_tupledict(
            model.hour, model.month, model.year, model.zone, model.tech,
            rule=self.ramping_up_rule
        )
        model.ramping_down_cons = poi.make_tupledict(
            model.hour, model.month, model.year, model.zone, model.tech,
            rule=self.ramping_down_rule
        )

    def gen_up_bound_rule(self,
        h : int, m : int, y : int, z : str, te : str
    ) -> poi._src.core_ext.ConstraintIndex:
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


    def ramping_up_rule(self,
        h : int, m : int, y : int, z : str, te : str
    ) -> poi._src.core_ext.ConstraintIndex:
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
        if rp < 1 < h:
            lhs = (
                model.gen[h, m, y, z, te] - model.gen[h-1, m, y, z, te]
                - rp * model.cap_existing[y, z, te]
            )
            return model.add_linear_constraint(lhs, poi.Leq, 0)


    def ramping_down_rule(self,
        h : int, m : int, y : int, z : str, te : str
    ) -> poi._src.core_ext.ConstraintIndex:
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
        if rd < 1 < h:
            lhs = (
                model.gen[h-1, m, y, z, te] - model.gen[h, m, y, z, te]
                - rd * model.cap_existing[y, z, te]
            )
            return model.add_linear_constraint(lhs, poi.Leq, 0)
