#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""This module contains the constraints and expressions related to
carbon emissions. The model computes the carbon emissions for each year, 
based on the sum of carbon emissions from each zone, and from each technology
as follows:

.. math::

    {\\rm{carbon}}_y=\\sum_{e\\in\\mathcal{E}}\\sum_{z\\in\mathcal{Z}}
    \\sum_{m\\in\mathcal{M}}\\sum_{h\\in\mathcal{H}}
    \\left({{\\rm{CARBON}}}_{y,z,e}\\times 
    {\\rm{gen}}_{h,m,y,z,e}\\right)\\quad\\forall y

The calculated carbon emission for each year lower than its upper bound, as follows:

.. math::
    
    {\\rm{carbon}}_y\\le{\\overline{{\\rm{CARBON}}}}_y\\quad\\forall y
    
"""
import pyoptinterface as poi
import numpy as np

class AddCo2EmissionConstraints:
    """Class for carbon emission constraints and calculations.
    """
    def __init__(self, model : object) -> None:
        """Initialize the class.

        Parameters
        ----------
        model : object
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
            model.year, model.zone,
            rule=self.emission_limit_rule
        )

    def emission_limit_rule(self, y : int, z : str) -> poi.ConstraintIndex:
        """Annual carbon emission limits across all zones and technologies.
        
        Parameters
        ----------
        y : int
            Planned year.
            
        Returns
        -------
        poi.ConstraintIndex
            A constraint of the model.
        """
        model = self.model
        limit = model.params['carbon_emission_limit'][z, y]
        if limit == np.Inf:
            return None
        lhs = model.carbon_capacity[y, z] - limit
        return model.add_linear_constraint(lhs, poi.Leq, 0)

    def emission_calc_rule(self, y : int) -> poi.ConstraintIndex:
        """Calculation of annual carbon emission across all zones and
        technologies.

        Parameters
        ----------
        y : int
            Planned year.

        Returns
        -------
        poi.ConstraintIndex
            A constraint of the model.
        """
        model = self.model
        return poi.quicksum(model.carbon_capacity.select(y, '*'))

    def emission_calc_by_zone_rule(
        self, y : int, z : str
    ) -> poi.ConstraintIndex:
        """Calculation of annual carbon emissions by zone.

        Parameters
        ----------
        y : int
            Planned year.
        z : str
            Zone.

        Returns
        -------
        poi.ConstraintIndex
            A constraint of the model.
        """
        model = self.model
        return poi.quicksum(model.carbon_breakdown.select(y, z, '*'))

    def carbon_breakdown(
        self,
        y : int,
        z : str,
        te : str
    ) -> poi.ExprBuilder:
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
        poi.ExprBuilder
            The expression of the model.
        """
        model = self.model
        ef = model.params['emission_factor'][te, y]
        w = model.params['weight']
        if ef == 0:
            return poi.ExprBuilder(0)
        return 1 / w * ef * poi.quicksum(model.gen.select('*', '*', y, z, te))
