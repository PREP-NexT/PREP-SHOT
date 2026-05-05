#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Granular operating-reserve constraints (multi-product, LP relaxation).

Generalises the v1.12 / v1.14 reserve module from "one reserve_up +
one reserve_down" to **named reserve products**, each with its own
eligibility and zonal requirement -- matching the structure of real
ancillary-services markets (CAISO, ERCOT, MISO, etc.) and the way
GenX, ReEDS, and PowNet model reserves.

Default product set
===================

Four products ship by default. The direction (up vs down) is encoded
in the product *name* and inferred by the suffix:

* ``regulation_up`` -- frequency regulation, increase output
* ``regulation_down`` -- frequency regulation, decrease output
* ``spinning`` -- contingency reserve, online + ready, up-only
* ``non_spinning`` -- contingency reserve, may be offline, up-only

The full set is read from the ``reserve_eligible`` CSV (column
``product``); any product name that ends in ``_down`` is treated as
a down-direction product, everything else is up.

Constraints
===========

Per ``(h, m, y, z, te)`` and per direction ``d`` -- *headroom is
shared across products in the same direction* (otherwise we would
double-count: a unit's spare megawatts can serve regulation OR
spinning, not both at the same instant):

.. math::

    \\sum_{p \\in \\text{products}_d} \\text{reserve}_{h,m,y,z,t,p}
      + \\text{gen}_{h,m,y,z,t}
    \\le \\text{cap}_{y,z,t} \\cdot p^{\\max}_{t,z,y,m,h} \\cdot \\Delta h
    \\quad (d = \\text{up})

.. math::

    \\sum_{p \\in \\text{products}_d} \\text{reserve}_{h,m,y,z,t,p}
    \\le \\text{gen}_{h,m,y,z,t}
      - \\text{cap}_{y,z,t} \\cdot p^{\\min}_{t,z,y,m,h} \\cdot \\Delta h
    \\quad (d = \\text{down})

Per ``(h, m, y, z, p)`` zonal requirement:

.. math::

    \\sum_{t} \\text{reserve}_{h,m,y,z,t,p}
    \\ge \\text{REQ}_{z,y,p} \\cdot \\Delta h

Non-eligible (tech, product) cells are forced to zero. Products with
no eligible techs in a zone produce a non-binding requirement.

Inputs
======

* ``tech_reserve_eligible.csv`` -- columns ``tech, product, eligible``.
  Missing rows default to ``eligible=0``. v1.12 files (cols ``tech,
  eligible``) are NOT readable by this module; migrate by:

      old:  Coal,1
      new:  Coal,regulation_up,1
            Coal,regulation_down,1
            Coal,spinning,1
            Coal,non_spinning,1

* ``reserve_requirement.csv`` -- columns ``zone, year, product, unit,
  value``. Missing rows default to 0 (non-binding).

Module is gated by ``config.json.reserve_parameters.is_reserve``;
when off, no variables / constraints are built.
"""
import pyoptinterface as poi


def _is_down_product(product: str) -> bool:
    """``True`` for down-direction products (suffix ``_down``).

    Convention chosen so the eligibility CSV stays a single column;
    new products encode their direction in the name (e.g.
    ``flex_ramp_up``, ``flex_ramp_down``).
    """
    return product.endswith('_down')


class AddReserveConstraints:
    """Granular operating-reserve constraints (multi-product)."""

    def __init__(self, model: object) -> None:
        self.model = model
        if not model.params.get('is_reserve', False):
            return

        # Eligibility: dict[(tech, product) -> 0/1]. The set of
        # *products* is harvested from this dict's keys (any product
        # mentioned for any tech). Keeps the schema lean -- no
        # separate "products" file.
        elig = model.params.get('reserve_eligible') or {}
        if not elig:
            # No eligibility data -> nothing to constrain.
            model.reserve_products = []
            return

        products = sorted({p for (_, p) in elig.keys()})
        model.reserve_products = products
        self.products_up = [p for p in products if not _is_down_product(p)]
        self.products_down = [p for p in products if _is_down_product(p)]

        # Per-(tech, product) eligibility lookup; default False.
        self.is_eligible = {
            (t, p): bool(elig.get((t, p), False))
            for t in model.tech for p in products
        }

        # Same p_max_pu / p_min_pu sources as gen_up_bound_rule.
        self._p_max_pu = dict(model.params.get('max_gen_profile') or {})
        self._p_min_pu = dict(model.params.get('min_gen_profile') or {})

        # Decision variable: reserve[h, m, y, z, t, p] in MWh / step.
        # Single 6-D variable; the v1.12 reserve_up / reserve_down
        # become the sum across products in their respective direction.
        model.reserve = model.add_variables(
            model.hour, model.month, model.year,
            model.zone, model.tech, products,
            lb=0,
        )

        # Lock non-eligible (tech, product) cells to 0. We prefer this
        # over relying on the LP optimum because the requirement
        # constraint sums across techs -- if non-eligible techs are
        # free to take any value, the requirement is trivial.
        model.reserve_non_eligible_cons = poi.make_tupledict(
            model.hour, model.month, model.year,
            model.zone, model.tech, products,
            rule=self.non_eligible_zero_rule,
        )

        # Two headroom rules per (h, m, y, z, te) -- one per direction
        # -- summing across products in that direction.
        model.reserve_headroom_up_cons = poi.make_tupledict(
            model.hour, model.month, model.year, model.zone, model.tech,
            rule=self.headroom_up_rule,
        )
        model.reserve_headroom_down_cons = poi.make_tupledict(
            model.hour, model.month, model.year, model.zone, model.tech,
            rule=self.headroom_down_rule,
        )

        # Per-(h, m, y, z, product) zonal requirement.
        model.reserve_requirement_cons = poi.make_tupledict(
            model.hour, model.month, model.year, model.zone, products,
            rule=self.requirement_rule,
        )

    # ------------------------------------------------------------------
    # Rules

    def non_eligible_zero_rule(self, h, m, y, z, te, p):
        """Force ``reserve[..., te, p] = 0`` when (te, p) isn't eligible."""
        if self.is_eligible[(te, p)]:
            return None
        return self.model.add_linear_constraint(
            self.model.reserve[h, m, y, z, te, p], poi.Eq, 0
        )

    def headroom_up_rule(self, h, m, y, z, te):
        """``sum_{p in up} reserve[..., p] + gen <= cap * p_max * dt``."""
        if not self.products_up:
            return None
        # Skip when no (te, p) in up direction is eligible -- the sum
        # would be zero by the non_eligible rule, leaving the trivial
        # `gen <= cap * p_max * dt` (already enforced by gen_up_bound).
        if not any(self.is_eligible[(te, p)] for p in self.products_up):
            return None
        model = self.model
        p_max_pu = self._p_max_pu.get((te, z, y, m, h), 1)
        dt = model.params['dt']
        lhs = (
            poi.quicksum(
                model.reserve[h, m, y, z, te, p] for p in self.products_up
            )
            + model.gen[h, m, y, z, te]
            - model.cap_existing[y, z, te] * p_max_pu * dt
        )
        return model.add_linear_constraint(lhs, poi.Leq, 0)

    def headroom_down_rule(self, h, m, y, z, te):
        """``sum_{p in down} reserve[..., p] <= gen - cap * p_min * dt``."""
        if not self.products_down:
            return None
        if not any(self.is_eligible[(te, p)] for p in self.products_down):
            return None
        model = self.model
        p_min_pu = self._p_min_pu.get((te, z, y, m, h), 0)
        dt = model.params['dt']
        lhs = (
            poi.quicksum(
                model.reserve[h, m, y, z, te, p]
                for p in self.products_down
            )
            - model.gen[h, m, y, z, te]
            + model.cap_existing[y, z, te] * p_min_pu * dt
        )
        return model.add_linear_constraint(lhs, poi.Leq, 0)

    def requirement_rule(self, h, m, y, z, p):
        """``sum_t reserve[..., t, p] >= REQ[z, y, p] * dt``.

        Requirement file ``reserve_requirement.csv`` cols
        ``zone, year, product, unit, value``. Missing rows -> 0 (the
        constraint becomes ``0 >= 0`` and is skipped here for solver
        cleanliness).
        """
        model = self.model
        req_lookup = model.params.get('reserve_requirement') or {}
        req_mw = req_lookup.get((z, y, p), 0)
        if req_mw == 0:
            return None
        dt = model.params['dt']
        lhs = poi.quicksum(
            model.reserve[h, m, y, z, t, p] for t in model.tech
        ) - req_mw * dt
        return model.add_linear_constraint(lhs, poi.Geq, 0)
