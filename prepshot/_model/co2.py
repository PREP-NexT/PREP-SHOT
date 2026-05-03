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
        model.carbon_offset = model.add_variables(
            model.year, model.zone, lb=0
        )
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
        # Carbon emission limits: one row per (limit_id, year) in
        # policy_carbon_emission_limit.csv with cols
        #   limit_id, year, unit, value, zones
        # where `zones` is a comma-separated list of member zone codes.
        # Each row becomes one LP constraint:
        #   sum(carbon_capacity[year, z] for z in zones) <= value
        emission_limits_df = model.params['carbon_emission_limit']
        for _, lr in emission_limits_df.iterrows():
            if lr['value'] == np.inf:
                continue
            member_zones = [z.strip() for z in str(lr['zones']).split(',') if z.strip()]
            if not member_zones:
                continue
            lhs = poi.quicksum(
                model.carbon_capacity[lr['year'], z] for z in member_zones
            ) - lr['value']
            model.add_linear_constraint(
                lhs, poi.Leq, 0,
                name=f"emission_limit_{lr['limit_id']}_{lr['year']}",
            )
        model.carbon_offset_limit_cons = poi.make_tupledict(
            model.year, model.zone,
            rule=self.carbon_offset_limit_rule
        )

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
    ) -> poi.ExprBuilder:
        """Calculation of annual net carbon emissions by zone, after subtracting
        purchased carbon offsets.

        Parameters
        ----------
        y : int
            Planned year.
        z : str
            Zone.

        Returns
        -------
        poi.ExprBuilder
            An expression for net zonal emissions.
        """
        model = self.model
        return poi.quicksum(model.carbon_breakdown.select(y, z, '*'))         \
            - model.carbon_offset[y, z]

    def carbon_offset_limit_rule(
        self, y : int, z : str
    ) -> poi.ConstraintIndex:
        """Limit purchased carbon offsets to a fraction of raw zonal emissions.

        ``carbon_offset[y,z] <= rate * raw_emissions[y,z]``

        where ``raw_emissions = carbon_capacity + carbon_offset`` (i.e. the
        emissions before offsets are deducted).

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
        rate = model.params['carbon_offset_limit'][z, y]
        raw_emissions = poi.quicksum(model.carbon_breakdown.select(y, z, '*'))
        lhs = model.carbon_offset[y, z] - rate * raw_emissions
        return model.add_linear_constraint(lhs, poi.Leq, 0)

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
        return 1 / w * ef * poi.quicksum(model.gen.select('*', '*', y, z, te))
