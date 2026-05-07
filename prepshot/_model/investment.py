#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""This module is used to determine investment-related constraints. 
The model computes the retirement of each technology and transmission line
with these considerations:

* The historical capacity of the technology and transmission line is
  based on its capacity ratio.
* Each planning and scheduling period is based on the existing capacity.

The existing capacity for each year, in each zone, for each technology,
is as follows:

.. math::
    
    {\\rm{cap}}_{y,z,e}^{\\rm{existingtech}}=
    \\sum_{{\\rm{age}}=1}^{{{T}}_e
    -(y-y_{\\rm{start}})}{{\\rm{CAP}}}_{{\\rm{age}},z,e}^{\\rm{inittech}}
    +\\sum_{y_{\\rm{pre}}={\\max}(y_{\\rm{start}}, y-{{T}}_e)}^{y}
    {{\\rm{cap}}_{y_{\\rm{pre}},z,e}^{\\rm{invtech}}}\\quad\\forall y,z,e

The existing capacity of the transmission lines for each year,
from :math:`z_{\\rm{from}}` zone to :math:`z_{\\rm{to}}`-th zone, is as
follows:

.. math::

    {\\rm{cap}}_{y,z_{\\rm{from}},z_{\\rm{to}}}^{\\rm{existingline}}=
    \\sum_{{\\rm{age}}=1}^{{T}_{\\rm{line}}
    -(y-y_{\\rm{start}})}{{\\rm{CAP}}}_{{\\rm{age}},z_{\\rm{from}},
    z_{\\rm{to}}}^{\\rm{initline}}
    +\\sum_{y_{\\rm{pre}}={\\max}(y_{\\rm{start}}, y-{{T}}_{\\rm{line}})}^{y}
    {{\\rm{cap}}_{y_{\\rm{pre}},
    z_{\\rm{from}},z_{\\rm{to}}}^{\\rm{invline}}}\\quad\\forall
    y,z_{\\rm{from}}\\neq z_{\\rm{to}}
"""

from typing import Union

from collections import defaultdict

import numpy as np
import pyoptinterface as poi

from prepshot.utils import sparse_tupledict


class AddInvestmentConstraints:
    """Add constraints for investment in the model.
    """
    def __init__(self, model : object) -> None:
        """Initialize the class and add constraints.
        
        Parameters
        ----------
        model : object
            Model object depending on the solver.
        """
        self.model = model
        # Pre-compute fast (zone, tech, year) -> bound dicts from the
        # expansion_candidates DataFrame. The DataFrame is loaded as
        # format:"table" because it has two value columns
        # (capacity_min and capacity_max); we materialize it into dicts
        # here for constant-time lookup inside the rule callbacks.
        candidates = model.params['expansion_candidates']
        self.candidate_min = {
            (r.zone, r.tech, r.year): r.capacity_min
            for _, r in candidates.iterrows()
        }
        self.candidate_max = {
            (r.zone, r.tech, r.year): r.capacity_max
            for _, r in candidates.iterrows()
        }
        # Pre-index existing fleet by (zone, tech) so the lifetime
        # rule does an O(1) lookup instead of an O(N) scan over the
        # whole fleet dict for every (y, z, te). On Thai PCM this is
        # the single biggest leftover bottleneck (0.6+s of pure
        # genexpr scanning).
        fleet_by_zte = defaultdict(list)
        for (t, z, cy), cap in (
            model.params.get('existing_fleet') or {}
        ).items():
            fleet_by_zte[z, t].append((cy, cap))
        self._fleet_by_zte = dict(fleet_by_zte)

        # Iterate sparse over (y, z, te) only where (z, te) is in the
        # active set. On Thai PCM 1*472*212 = 100k -> 1*212 = 212.
        active_yzt = [
            (y, z, te)
            for y in model.year
            for (z, te) in model.active_zt
        ]
        self._active_yzt = active_yzt
        model.remaining_technology = sparse_tupledict(
            active_yzt, self.tech_lifetime_rule
        )
        model.cap_existing = sparse_tupledict(
            active_yzt, self.remaining_capacity_rule
        )
        model.tech_up_bound_cons = sparse_tupledict(
            active_yzt, self.tech_up_bound_rule
        )
        model.tech_low_bound_cons = sparse_tupledict(
            active_yzt, self.tech_low_bound_rule
        )
        model.new_tech_up_bound_cons = sparse_tupledict(
            active_yzt, self.new_tech_up_bound_rule
        )
        model.new_tech_low_bound_cons = sparse_tupledict(
            active_yzt, self.new_tech_low_bound_rule
        )

    def tech_up_bound_rule(
        self, y : int, z : str, te : str
    ) -> poi.ConstraintIndex:
        """Allowed capacity of commercial operation technology is less than or 
        equal to the predefined upper bound.

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
        poi.ConstraintIndex
            The constraint of the model.
        """
        model = self.model
        tub =  model.params['technology_capacity_max'][z, te, y]
        if tub != np.inf:
            lhs = model.cap_existing[y, z, te] - tub
            return model.add_linear_constraint(lhs, poi.Leq, 0)
        return None

    def tech_low_bound_rule(
        self, y : int, z : str, te : str
    ) -> poi.ConstraintIndex:
        """Allowed capacity of commercial operation technology is greater than
        or equal to the predefined lower bound.

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
        poi.ConstraintIndex
            The constraint of the model.
        """
        model = self.model
        tlb = model.params['technology_capacity_min'][z, te, y]
        if tlb == 0:
            return None
        lhs = model.cap_existing[y, z, te] - tlb
        return model.add_linear_constraint(lhs, poi.Geq, 0)

    def new_tech_up_bound_rule(
        self, y : int, z : str, te : str
    ) -> poi.ConstraintIndex:
        """New investment technology upper bound in specific year and zone.

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
        poi.ConstraintIndex
            The constraint of the model.
        """
        model = self.model
        # If (z, te, y) is not in expansion_candidates, this combination
        # cannot be expanded -- the file is the canonical list of
        # buildable options. Default upper bound: 0.
        ntub = self.candidate_max.get((z, te, y), 0)
        if ntub != np.inf:
            lhs = model.cap_newtech[y, z, te] - ntub
            return model.add_linear_constraint(lhs, poi.Leq, 0)
        return None

    def new_tech_low_bound_rule(
        self, y : int, z : str, te : str
    ) -> poi.ConstraintIndex:
        """New investment technology lower bound.

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
        poi.ConstraintIndex
            The constraint of the model.
        """
        model = self.model
        ntlb = self.candidate_min.get((z, te, y), 0)
        lhs = model.cap_newtech[y, z, te] - ntlb
        return model.add_linear_constraint(lhs, poi.Geq, 0)

    def tech_lifetime_rule(
        self, y : int, z : str, te : str
    ) -> poi.ConstraintIndex:
        """Caculation of remaining technology capacity based on lifetime 
        constraints.

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
        lt = self.model.params['lifetime']
        # An existing fleet entry (te, z, commission_year) -> capacity is
        # in service in year y when commission_year <= y < commission_year
        # + lifetime. Lifetime is looked up at the commissioning year
        # cy, not the current year y -- once a unit is built, its
        # lifetime is fixed at construction.
        # Pre-indexed by (z, te) for O(1) per-rule lookup.
        return poi.quicksum(
            cap for (cy, cap) in self._fleet_by_zte.get((z, te), [])
            if cy <= y < cy + lt[te, cy]
        )

    def remaining_capacity_rule(
        self, y : int, z : str, te : str
    ) -> poi.ExprBuilder:
        """Remaining capacity of initial technology due to lifetime 
        restrictions. Where in modeled year y, the available technology
        consists of the following.
        
        1. The remaining in-service installed capacity from the initial 
           technology.
        2. The remaining in-service installed capacity from newly built 
           technology in the previous modelled years.

        Parameters
        ----------
        y : int
            Planned year.
        z : str
            Zone.
        te : str
            technology.

        Returns
        -------
        poi.ExprBuilder
            The expression of the model.
        """
        model = self.model
        year = model.params['year']
        lt = model.params['lifetime']
        cap_existing = poi.ExprBuilder()
        new_tech = poi.quicksum(
            model.cap_newtech[yy, z, te]
            for yy in year[:year.index(y) + 1]
            if y - yy < lt[te, yy]
        )
        cap_existing += new_tech
        cap_existing += model.remaining_technology[y, z, te]
        return cap_existing
