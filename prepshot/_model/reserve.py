#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Operating-reserve constraints (LP relaxation, no unit commitment).

PREP-SHOT is a pure LP. True spinning-reserve modelling needs a binary
"unit is online" variable, which would push the model into MILP land.
This module ships the standard LP relaxation: any plant whose dispatched
capacity has spare headroom can count that headroom toward reserve, with
no separate online/offline distinction. Acceptable for capacity-expansion
planning (hourly operations are smoothed); not acceptable for chronological
unit-commitment studies.

Two constraints per timestep, gated by ``config.json.reserve_parameters.
is_reserve``:

1. **Plant-level headroom** (one per ``h, m, y, z, t``):

   .. math::

      \\text{reserve}_{h,m,y,z,t} \\le
      \\text{cap\\_existing}_{y,z,t}\\cdot p^{\\max}_{t,z,y,m,h}\\cdot \\Delta h
      - \\text{gen}_{h,m,y,z,t}

   Non-eligible techs are forced to ``reserve = 0``.

2. **Zonal requirement** (one per ``h, m, y, z``):

   .. math::

      \\sum_{t}\\text{reserve}_{h,m,y,z,t}\\ge
      \\text{REQ}_{z,y}\\cdot \\Delta h

The reserve variable itself is in MWh-per-timestep (matching ``gen``);
the requirement input ``reserve_requirement.csv`` is in MW (matching
``demand.csv``) and gets multiplied by ``dt`` internally.

No cost term is added: reserve is "free" in this LP relaxation. If you
want to penalize holding reserve (e.g. a small per-MWh opportunity cost),
add it to ``cost.py`` -- the variable is exposed as ``model.reserve``.
"""
import pyoptinterface as poi


class AddReserveConstraints:
    """Operating-reserve constraints.

    Skips entirely when ``params['is_reserve']`` is ``False`` -- the
    ``model.reserve`` variable is not even created in that case (see
    ``model.define_variables``).
    """

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

        # Same p_max_pu source as gen_up_bound_rule -- keeps the headroom
        # constraint aligned with the dispatch upper bound.
        self._p_max_pu = dict(model.params.get('max_gen_profile') or {})

        model.reserve_headroom_cons = poi.make_tupledict(
            model.hour, model.month, model.year, model.zone, model.tech,
            rule=self.reserve_headroom_rule,
        )
        model.reserve_requirement_cons = poi.make_tupledict(
            model.hour, model.month, model.year, model.zone,
            rule=self.reserve_requirement_rule,
        )

    def reserve_headroom_rule(
        self, h: int, m: int, y: int, z: str, te: str
    ) -> poi.ConstraintIndex:
        """Per-plant headroom on dispatched capacity.

        For ineligible techs, force ``reserve = 0`` so the variable
        contributes nothing to the zonal sum even if presolve doesn't
        eliminate it.
        """
        model = self.model
        if not self.is_eligible[te]:
            lhs = model.reserve[h, m, y, z, te]
            return model.add_linear_constraint(lhs, poi.Eq, 0)
        p_max_pu = self._p_max_pu.get((te, z, y, m, h), 1)
        dt = model.params['dt']
        lhs = (
            model.reserve[h, m, y, z, te]
            + model.gen[h, m, y, z, te]
            - model.cap_existing[y, z, te] * p_max_pu * dt
        )
        return model.add_linear_constraint(lhs, poi.Leq, 0)

    def reserve_requirement_rule(
        self, h: int, m: int, y: int, z: str
    ) -> poi.ConstraintIndex:
        """Zonal reserve requirement (MW input, scaled by dt).

        Missing (zone, year) keys default to 0 -- if a zone has no
        requirement it gets a trivially-satisfied 0 >= 0 constraint.
        """
        model = self.model
        req_lookup = model.params.get('reserve_requirement') or {}
        # reserve_requirement.csv is keyed (zone, year)
        req_mw = req_lookup.get((z, y), 0)
        if req_mw == 0:
            return None
        dt = model.params['dt']
        lhs = poi.quicksum(
            model.reserve[h, m, y, z, t] for t in model.tech
        ) - req_mw * dt
        return model.add_linear_constraint(lhs, poi.Geq, 0)
