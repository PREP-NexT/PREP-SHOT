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

from prepshot.utils import sparse_tupledict

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
        # Pre-compute fast (tech, zone, year, month, hour) -> per-unit
        # bound dicts. Both files are optional; missing entries fall
        # back to defaults (p_max_pu = 1, p_min_pu = 0). This unifies
        # the previous capacity-factor-bounded VRE constraint and the
        # cap-bounded dispatchable constraint into one rule.
        self._p_max_pu = dict(model.params.get('max_gen_profile') or {})
        self._p_min_pu = dict(model.params.get('min_gen_profile') or {})
        # UC-eligible techs get their min-gen lower bound gated by
        # `online[h]` in unit_commitment.gen_low_uc_rule; the
        # cap_existing-based lower bound here would override that gate
        # (cap_existing * p_min_pu >= online * unit_size * p_min_pu
        # whenever online < n_units), pinning units permanently on.
        # Skip the rule for those techs.
        self._uc_active = bool(model.params.get('is_uc', False))
        elig = model.params.get('uc_eligible') or {}
        self._uc_eligible_techs = {
            t for t, v in elig.items() if bool(v)
        } if self._uc_active else set()
        # Iterate sparsely over (h, m, y, z, te) where (z, te) is in
        # ``model.active_zt``. Inactive (z, te) pairs have no
        # ``model.gen`` variable (sparse creation in model.py), and
        # the matching constraint would be ``gen <= 0 * dt = 0``
        # which the absent variable already enforces.
        model.gen_up_bound_cons = sparse_tupledict(
            model.active_hmyzte, self.gen_up_bound_rule
        )
        model.gen_low_bound_cons = sparse_tupledict(
            model.active_hmyzte, self.gen_low_bound_rule
        )
        model.ramping_up_cons = sparse_tupledict(
            model.active_hmyzte, self.ramping_up_rule
        )
        model.ramping_down_cons = sparse_tupledict(
            model.active_hmyzte, self.ramping_down_rule
        )

    def gen_up_bound_rule(
        self, h : int, m : int, y : int, z : str, te : str
    ) -> poi.ConstraintIndex:
        """gen[h,m,y,z,te] <= cap_existing × p_max_pu × dt.

        Defaults to p_max_pu = 1 (full capacity) when the tech has no
        entry in tech_max_gen_profile.csv. Variable renewables specify
        a time-varying p_max_pu < 1 to cap by capacity factor; must-run
        techs set p_max_pu = p_min_pu to lock generation to a profile.
        """
        model = self.model
        p_max_pu = self._p_max_pu.get((te, z, y, m, h), 1)
        lhs = model.gen[h, m, y, z, te] \
            - model.cap_existing[y, z, te] * p_max_pu * model.params['dt']
        return model.add_linear_constraint(lhs, poi.Leq, 0)

    def gen_low_bound_rule(
        self, h : int, m : int, y : int, z : str, te : str
    ) -> poi.ConstraintIndex:
        """gen[h,m,y,z,te] >= cap_existing × p_min_pu × dt.

        Defaults to p_min_pu = 0 (no minimum) when the tech has no
        entry in tech_min_gen_profile.csv. Set p_min_pu > 0 for
        must-run plants with a minimum stable load.

        Skipped when the tech is UC-eligible -- in that case the
        commitment-gated rule in unit_commitment.gen_low_uc_rule
        (gen >= online * unit_size * p_min_pu * dt) is the
        authoritative lower bound, and adding this cap_existing-based
        version would force gen >= cap_existing * p_min_pu regardless
        of the online state, defeating shutdowns.
        """
        if te in self._uc_eligible_techs:
            return None
        model = self.model
        p_min_pu = self._p_min_pu.get((te, z, y, m, h), 0)
        if p_min_pu == 0:
            return None  # trivial constraint; gen is already lb=0
        lhs = model.gen[h, m, y, z, te] \
            - model.cap_existing[y, z, te] * p_min_pu * model.params['dt']
        return model.add_linear_constraint(lhs, poi.Geq, 0)


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
        if rp >= 1:
            return None  # ramp >= full capacity per step -- not binding
        if h > model.hour[0]:
            prev_gen = model.gen[h - 1, m, y, z, te]
        else:
            # First hour of window: pull terminal gen from the prior
            # PCM window if available; otherwise leave the boundary
            # unconstrained (original behaviour for CEM / first window).
            prior_gen = (model.params.get('prior_gen') or {}).get((z, te))
            if prior_gen is None:
                return None
            prev_gen = prior_gen
        lhs = (
            model.gen[h, m, y, z, te] - prev_gen
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
        if rd >= 1:
            return None
        if h > model.hour[0]:
            prev_gen = model.gen[h - 1, m, y, z, te]
        else:
            prior_gen = (model.params.get('prior_gen') or {}).get((z, te))
            if prior_gen is None:
                return None
            prev_gen = prior_gen
        lhs = (
            prev_gen - model.gen[h, m, y, z, te]
            - rd * model.cap_existing[y, z, te]
        )
        return model.add_linear_constraint(lhs, poi.Leq, 0)
