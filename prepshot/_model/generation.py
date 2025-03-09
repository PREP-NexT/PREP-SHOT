#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""This module contains constraints related to technology generation.
The power output of storage and each dispatchable (exclude hydropower)
technology (:math:`{\\rm{power}}_{h,m,y,z,e}`) is limited by the existing
installed capacity (:math:`{\\rm{cap}}_{y,z,e}^{\\rm{existingtech}}`)
and minimum technical output, as follows:

.. math::

    {\\underline{{\\rm{POWER}}}}_{h,m,y,z,e}\\times
    {\\rm{cap}}_{y,z,e}^{\\rm{existingtech}}\\le{\\rm{power}}_{h,m,y,z,e}\\le
    {\\rm{cap}}_{y,z,e}^{\\rm{existingtech}}\\quad\\forall h,m,y,z,e\\in
    {\\mathcal{STOR}}\ \&\ {\\mathcal{DISP}}

Since hydropower processes are explicitly modelled at the plant level in
PREP-SHOT, total hydropower output in zone
:math:`z` (:math:`{\\rm{power}}_{h,m,y,z,e={\\rm{hydro}}}`) is the sum of the
plant-level hydropower output
(:math:`{\\rm{power}}_{\\it{s,h,m,y}}^{\\rm{hydro}}`):

.. math::

    {\\rm{power}}_{h,m,y,z,e={\\rm{hydro}}}=\\sum_{s\\in{\\mathcal{SZ}}_z}
    {\\rm{power}}_{s,h,m,y}^{\\rm{hydro}}\\quad\\forall h,m,y,z

Here, calculation of :math:`{\\rm{power}}^{\\rm{hydro}}_{s,h,m,y}` is obtained
by external net water head simulation procedure. In addition,
:math:`{\\rm{power}}^{\\rm{hydro}}_{s,h,m,y}` is bounded between the guaranteed
minimum output (:math:`{\\underline{{\\rm{POWER}}}}_s^{\\rm{hydro}}`) and the
nameplate capacity (:math:`{{\\rm{CAP}}}_s^{\\rm{hydro}}`), as follows:

Regardless of the technology type, actual power generation
(:math:`{\\rm{gen}}_{h,m,y,z,e}`) in a corresponding period :math:`\\Delta h`
can be calculated based on the power output (:math:`{\\rm{power}}_{h,m,y,z,e}`)
and the generation efficiency (:math:`\\eta_{y,e}^{\\rm{out}}`):

.. math::

    {\\rm{gen}}_{h,m,y,z,e} = {\\rm{power}}_{h,m,y,z,e}\\times\\Delta h
    \\times\eta_{y,e}^{\\rm{out}}\\quad \\forall h,m,y,z,e\\in {\\mathcal{E}}

Note that :math:`\\eta_{y,e}^{\\rm{out}}=1` when
:math:`e\\in {\\mathcal{E}}\\backslash {\\mathcal{STOR}}`. 

All technologies apart from dispatchable technology are limited by the
so-called ramping capability, meaning that the variation of their power output
in two successive periods is limited.  We introduce two non-negative auxiliary
variables: increment (:math:`{\rm{power}}_{h,m,y,z,e}^{\rm{up}}`) and decrement
(:math:`{\rm{power}}_{h,m,y,z,e}^{\rm{down}}`) to describe changes in power
output in two successive periods (from :math:`h`-1 to :math:`h`) as follows:

.. math::

    {\\rm{power}}_{h,m,y,z,e}^{\\rm{up}}-{\\rm{power}}_{h,m,y,z,e}^{\\rm{down}}
    ={\\rm{power}}_{h,m,y,z,e}-{\\rm{power}}_{h-1,m,y,z,e}
    \\quad\\forall h,m,y,z,e\ \\in {\\mathcal{E}}\\backslash {\\mathcal{NDISP}}

When the power plant ramps up from :math:`h`-1 to :math:`h`,
the minimum of :math:`{\\rm{power}}_{h,m,y,z,e}^{\\rm{up}}` is obtained when
:math:`{\\rm{power}}_{h,m,y,z,e}^{\\rm{down}}` becomes zero. Similarly, when
the power plant ramps down from :math:`h`-1 to :math:`h`, the minimum of
:math:`{\\rm{power}}_{h,m,y,z,e}^{\\rm{down}}` is obtained when
:math:`{\\rm{power}}_{h,m,y,z,e}^{\\rm{up}}` becomes zero. Therefore,
we can constrain the maximum ramping up and down respectively, as follows:

.. math::
    
    {\\rm{power}}_{h,m,y,z,e}^{\\rm{up}}\\le{{R}}_e^{\\rm{up}}\\times
    \\Delta h\\times {\\rm{cap}}_{y,z,e}^{\\rm{existingtech}}\\quad
    \\forall h,m,y,z,e\\in {\\mathcal{E}}\\backslash {\\mathcal{NDISP}}

.. math::
    
    {\\rm{power}}_{h,m,y,z,e}^{\\rm{down}}\\le{{R}}_e^{\\rm{down}}\\times
    \\Delta h\\times {\\rm{cap}}_{y,z,e}^{\\rm{existingtech}}
    \\quad\\forall h,m,y,z,e\\in {\\mathcal{E}}\\backslash {\\mathcal{NDISP}}

where :math:`{{R}}_e^{\\rm{up}}$/${{R}}_e^{\\rm{down}}` is the allowed
maximum/minimum ramping up/down capacity of technology :math:`e` in two
successive periods, expressed as a percentage of the existing capacity
of storage technology :math:`e`.

"""
import pyoptinterface as poi

class AddGenerationConstraints:
    """Add constraints for generation in the model.
    """
    def __init__(self, model : object) -> None:
        """Initialize the class and add constraints.
        
        Parameters
        ----------
        model : object
            Model object depending on the solver.
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

    def gen_up_bound_rule(
        self, h : int, m : int, y : int, z : str, te : str
    ) -> poi.ConstraintIndex:
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
        poi.ConstraintIndex
            The constraint of the model.
        """
        model = self.model
        lhs = model.gen[h, m, y, z, te] \
            - model.cap_existing[y, z, te] * model.params['dt']
        return model.add_linear_constraint(lhs, poi.Leq, 0)


    def ramping_up_rule(
        self, h : int, m : int, y : int, z : str, te : str
    ) -> poi.ConstraintIndex:
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
        poi.ConstraintIndex
            The constraint of the model.
        """
        model = self.model
        rp = model.params['ramp_up'][te] * model.params['dt']
        if rp < 1 < h:
            lhs = (
                model.gen[h, m, y, z, te] - model.gen[h-1, m, y, z, te]
                - rp * model.cap_existing[y, z, te]
            )
            return model.add_linear_constraint(lhs, poi.Leq, 0)


    def ramping_down_rule(
        self, h : int, m : int, y : int, z : str, te : str
    ) -> poi.ConstraintIndex:
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
        poi.ConstraintIndex
            The constraint of the model.
        """
        model = self.model
        rd = model.params['ramp_down'][te] * model.params['dt']
        if rd < 1 < h:
            lhs = (
                model.gen[h-1, m, y, z, te] - model.gen[h, m, y, z, te]
                - rd * model.cap_existing[y, z, te]
            )
            return model.add_linear_constraint(lhs, poi.Leq, 0)
