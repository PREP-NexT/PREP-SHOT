#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""This module contains constraints related to carbon emissions. 
"""

from typing import Union

import pyoptinterface as poi
import numpy as np

class AddCo2EmissionConstraints:
    """Class for carbon emission constraints and calculations.
    """
    def __init__(self,
        model : Union[
            poi._src.highs.Model,
            poi._src.gurobi.Model,
            poi._src.mosek.Model,
            poi._src.copt.Model
        ],
    ) -> None:
        """Initialize the class.

        Parameters
        ----------
        model : Union[
            poi._src.highs.Model,
            poi._src.gurobi.Model,
            poi._src.mosek.Model,
            poi._src.copt.Model
        ]
            Model object depending on the solver.
        """
        self.model = model
        model.carbon_breakdown = poi.make_tupledict(
            model.year, model.zone, model.tech,
            rule=self.carbon_breakdown
        )
        model.carbon_capacity = poi.make_tupledict(
            model.year, model.zone,
            rule=self.emission_calc_by_zone_rule
        )
        model.carbon = poi.make_tupledict(
            model.year,
            rule=self.emission_calc_rule
        )
        model.emission_limit_cons = poi.make_tupledict(
            model.year,
            rule=self.emission_limit_rule
        )

    def emission_limit_rule(
        self,
        y : int
    ) -> poi._src.core_ext.ConstraintIndex:
        """Annual carbon emission limits across all zones and technologies.
        
        Parameters
        ----------
        y : int
            Planned year.
            
        Returns
        -------
        pyoptinterface._src.core_ext.ConstraintIndex
            Constraint index of the model.
        """
        model = self.model
        limit = model.params['carbon_emission_limit']
        if limit[y] == np.Inf:
            return None
        lhs = model.carbon[y] - limit[y]
        return model.add_linear_constraint(lhs, poi.Leq, 0)

    def emission_calc_rule(
        self,
        y : int
    ) -> poi._src.core_ext.ConstraintIndex:
        """Calculation of annual carbon emission across all zones and
        technologies.

        Parameters
        ----------
        y : int
            Planned year.

        Returns
        -------
        pyoptinterface._src.core_ext.ConstraintIndex
            Constraint index of the model.
        """
        model = self.model
        return poi.quicksum(
            model.carbon_capacity[y, z]
            for z in model.zone
        )

    def emission_calc_by_zone_rule(
        self,
        y : int,
        z : str
    ) -> poi._src.core_ext.ConstraintIndex:
        """Calculation of annual carbon emissions by zone.

        Parameters
        ----------
        y : int
            Planned year.
        z : str
            Zone.

        Returns
        -------
        pyoptinterface._src.core_ext.ConstraintIndex
            Constraint index of the model.
        """
        model = self.model
        return poi.quicksum(
            model.carbon_breakdown[y, z, te]
            for te in model.tech
        )

    def carbon_breakdown(
        self,
        y : int,
        z : str,
        te : str
    ) -> poi._src.core_ext.ExprBuilder:
        """Carbon emission cost breakdown.

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
            index of expression of the model.
        """
        model = self.model
        ef = model.params['emission_factor'][te, y]
        dt = model.params['dt']
        return poi.quicksum(
            ef * model.gen[h, m, y, z, te] * dt
            for h in model.hour for m in model.month
        )
