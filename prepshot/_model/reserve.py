#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Operating-reserve constraints, two directions (LP relaxation).

PREP-SHOT is a pure LP. True spinning-reserve modelling needs a binary
"unit is online" variable, which would push the model into MILP land.
This module ships the standard LP relaxation: any plant whose dispatched
capacity has spare headroom can count that headroom toward reserve, with
no separate online/offline distinction. Acceptable for capacity-expansion
planning (hourly operations are smoothed); not acceptable for chronological
unit-commitment studies.

Two reserve directions are tracked:

* **Up reserve** -- capacity available to *increase* output if demand
  spikes or another plant trips. Bounded above by the gap between
  dispatched output and the unit's max:

  .. math::

      \\text{reserve\\_up}_{h,m,y,z,t} \\le
      \\text{cap}_{y,z,t}\\cdot p^{\\max}_{t,z,y,m,h}\\cdot \\Delta h
      - \\text{gen}_{h,m,y,z,t}

* **Down reserve** -- capacity available to *decrease* output if a
  variable-renewable plant over-generates or load drops. Bounded above
  by the gap between dispatched output and the unit's minimum stable
  load:

  .. math::

      \\text{reserve\\_down}_{h,m,y,z,t} \\le
      \\text{gen}_{h,m,y,z,t}
      - \\text{cap}_{y,z,t}\\cdot p^{\\min}_{t,z,y,m,h}\\cdot \\Delta h

Non-eligible techs (typically solar / wind / storage discharge) are
forced to ``reserve_up = reserve_down = 0`` regardless of headroom.
Eligibility is read once from ``tech_reserve_eligible.csv`` and applied
to both directions.

Per-zone-year requirements are read from two separate CSVs, both in
MW (multiplied by ``dt`` internally to match ``gen``'s MWh-per-timestep
unit):

* ``reserve_requirement_up.csv`` -- size for contingency / load growth
* ``reserve_requirement_down.csv`` -- size for over-generation absorption

Both are optional; missing rows / files default to 0 and yield
trivially-satisfied constraints.

The whole module is gated by ``config.json.reserve_parameters.is_reserve``;
when that flag is ``False`` the variables and constraints are not built,
preserving byte-for-byte behaviour for any pre-1.12 ``config.json``.

No cost term is added: reserve is "free" in this LP relaxation. If you
want to penalise holding reserve (e.g. a small per-MWh opportunity
cost), add it to ``cost.py`` -- the variables are exposed as
``model.reserve_up`` and ``model.reserve_down``.
"""
import pyoptinterface as poi


class AddReserveConstraints:
    """Operating-reserve constraints, up and down directions."""

    def __init__(self, model: object) -> None:
        self.model = model
        if not model.params.get('is_reserve', False):
            return

        # Eligibility lookup with default False. Allows the input file
        # to be partial -- techs not listed are treated as ineligible.
        eligible = model.params.get('reserve_eligible') or {}
        self.is_eligible = {
            t: bool(eligible.get(t, False)) for t in model.tech
        }

        # Same p_max_pu / p_min_pu sources as gen_up_bound_rule /
        # gen_low_bound_rule -- keeps the headroom constraints aligned
        # with the dispatch bounds.
        self._p_max_pu = dict(model.params.get('max_gen_profile') or {})
        self._p_min_pu = dict(model.params.get('min_gen_profile') or {})

        model.reserve_headroom_up_cons = poi.make_tupledict(
            model.hour, model.month, model.year, model.zone, model.tech,
            rule=self.headroom_up_rule,
        )
        model.reserve_headroom_down_cons = poi.make_tupledict(
            model.hour, model.month, model.year, model.zone, model.tech,
            rule=self.headroom_down_rule,
        )
        model.reserve_requirement_up_cons = poi.make_tupledict(
            model.hour, model.month, model.year, model.zone,
            rule=self.requirement_up_rule,
        )
        model.reserve_requirement_down_cons = poi.make_tupledict(
            model.hour, model.month, model.year, model.zone,
            rule=self.requirement_down_rule,
        )

    def headroom_up_rule(
        self, h: int, m: int, y: int, z: str, te: str
    ) -> poi.ConstraintIndex:
        """Up-reserve bounded by spare capacity above current dispatch."""
        model = self.model
        if not self.is_eligible[te]:
            return model.add_linear_constraint(
                model.reserve_up[h, m, y, z, te], poi.Eq, 0
            )
        p_max_pu = self._p_max_pu.get((te, z, y, m, h), 1)
        dt = model.params['dt']
        lhs = (
            model.reserve_up[h, m, y, z, te]
            + model.gen[h, m, y, z, te]
            - model.cap_existing[y, z, te] * p_max_pu * dt
        )
        return model.add_linear_constraint(lhs, poi.Leq, 0)

    def headroom_down_rule(
        self, h: int, m: int, y: int, z: str, te: str
    ) -> poi.ConstraintIndex:
        """Down-reserve bounded by margin above the dispatch floor."""
        model = self.model
        if not self.is_eligible[te]:
            return model.add_linear_constraint(
                model.reserve_down[h, m, y, z, te], poi.Eq, 0
            )
        p_min_pu = self._p_min_pu.get((te, z, y, m, h), 0)
        dt = model.params['dt']
        # reserve_down <= gen - cap * p_min_pu * dt
        # rearranged: reserve_down - gen + cap * p_min_pu * dt <= 0
        lhs = (
            model.reserve_down[h, m, y, z, te]
            - model.gen[h, m, y, z, te]
            + model.cap_existing[y, z, te] * p_min_pu * dt
        )
        return model.add_linear_constraint(lhs, poi.Leq, 0)

    def requirement_up_rule(
        self, h: int, m: int, y: int, z: str
    ) -> poi.ConstraintIndex:
        """Zonal up-reserve requirement (MW input, scaled by dt)."""
        return self._requirement(h, m, y, z, 'up')

    def requirement_down_rule(
        self, h: int, m: int, y: int, z: str
    ) -> poi.ConstraintIndex:
        """Zonal down-reserve requirement (MW input, scaled by dt)."""
        return self._requirement(h, m, y, z, 'down')

    def _requirement(self, h, m, y, z, direction):
        """Shared body for the up / down zonal requirement constraint.

        ``direction`` is ``'up'`` or ``'down'``; both the param key
        (``reserve_requirement_<direction>``) and the model variable
        (``reserve_<direction>``) follow the same naming, so a single
        helper covers both rules.
        """
        model = self.model
        req_lookup = model.params.get(f'reserve_requirement_{direction}') or {}
        req_mw = req_lookup.get((z, y), 0)
        if req_mw == 0:
            return None
        reserve_var = getattr(model, f'reserve_{direction}')
        dt = model.params['dt']
        lhs = poi.quicksum(
            reserve_var[h, m, y, z, t] for t in model.tech
        ) - req_mw * dt
        return model.add_linear_constraint(lhs, poi.Geq, 0)
