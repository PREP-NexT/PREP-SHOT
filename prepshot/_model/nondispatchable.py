#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""This module contains functions related to nondispatchable technologies. 
For non-dispatchable technologies, their power output is constrained by
the predefined capacity factors as follows:

.. math::

    {\\rm{power}}_{h,m,y,z,e}\le{{\\rm{CF}}}_{h,m,y,z,e}\\times
    {\\rm{cap}}_{y,z,e}^{\\rm{existingtech}}\\quad\\forall h,m,y,z,e\\in
    {\\mathcal{NDISP}}

"""
import pyoptinterface as poi

class AddNondispatchableConstraints:
    """Add constraints for nondispatchable technologies. 
    """
    def __init__(self, model : object) -> None:
        """Initialize the class and add constraints.
        
        Parameters
        ----------
        model : object
            Model object depending on the solver.
        """
        self.model = model
        if model.nondispatchable_tech != 0:
            model.renew_gen_cons = poi.make_tupledict(
                model.hour, model.month, model.year, model.zone,
                model.nondispatchable_tech, rule=self.renew_gen_rule
            )

    def renew_gen_rule(
        self, h : int, m : int, y : int, z : str, te : str
    ) -> poi.ConstraintIndex:
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
        poi.ConstraintIndex
            The constraint of the model.
        """
        model = self.model
        cf = model.params['capacity_factor'][te, z, y, m, h]
        dt = model.params['dt']
        cap = model.cap_existing[y, z, te]
        gen = model.gen[h, m, y, z, te]
        lhs = gen - cap * cf * dt
        return model.add_linear_constraint(lhs, poi.Leq, 0)
