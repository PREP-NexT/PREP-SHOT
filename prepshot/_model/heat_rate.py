#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Piecewise-linear heat rates (convex, no UC required).

Standard CEM/PCM addition for thermal generators: their fuel-burn-
per-MWh isn't constant across the operating range. Above the design
point, marginal heat rate increases (each additional MWh costs more
fuel than the previous one). LP-friendly approximation: split the
operating range into K segments with monotone-non-decreasing
multipliers, force the dispatch to use the cheapest segment first.

The convexity matters: with non-decreasing multipliers across
ascending output ranges, the LP optimum naturally fills segments in
order (cheapest first) without any binary ordering constraints.
Real heat-rate curves below the design point (where part-load
losses dominate) are concave -- those can only be modelled with no-
load + startup costs in the UC overlay (v1.15+).

Inputs
======

``tech_heat_rate.csv`` (table format) -- one row per (tech,
segment), with columns:

* ``tech`` -- technology name
* ``segment`` -- integer index (1, 2, 3, ...)
* ``frac_max`` -- cumulative cap fraction at the upper edge of this
  segment (e.g., 0.5 for segment 1 means "0-50 % of cap").
  Segments must form a partition: ``frac_max`` strictly increasing,
  last value = 1.0.
* ``multiplier`` -- relative heat rate within this segment, 1.0 ==
  baseline (whatever ``tech_fuel_price`` already implies). The
  multiplier sequence MUST be non-decreasing for LP convexity.

Techs not listed in the CSV keep the v1.18 single-rate fuel cost
(``fuel_price * gen``). Mixing piecewise and flat-rate techs is
fine.

Constraints
===========

Per ``(h, m, y, z, te)`` in the heat-rate set:

* sum-to-gen:
  ``sum_s gen_segment[h, m, y, z, te, s] == gen[h, m, y, z, te]``
* per-segment width:
  ``gen_segment[..., s] <= width[s] * cap_existing[y, z, te] * dt``

where ``width[s] = frac_max[s] - frac_max[s-1]``.

Fuel cost replaces the flat ``fuel_price * gen`` with:

  ``fuel_price[te, y] * sum_s multiplier[s] * gen_segment[..., s]``

NPV-discounted via ``var_factor[y, z]`` and divided by ``weight``,
identical to the rest of ``cost_var``.

Config
======

* ``cost_parameters.is_piecewise_heat_rate`` (bool, default False).
  When False, the module is a no-op and PREP-SHOT keeps the
  v1.18 flat-rate behaviour byte-for-byte.
"""
import pyoptinterface as poi


class AddHeatRateConstraints:
    """Piecewise-linear heat rate, opt-in."""

    def __init__(self, model: object) -> None:
        self.model = model
        if not model.params.get('is_piecewise_heat_rate', False):
            return

        # ``heat_rate`` arrives as a DataFrame (table format). Build
        # per-tech ordered segment lists so the rules can iterate.
        df = model.params.get('heat_rate')
        if df is None or not hasattr(df, 'iterrows') or df.empty:
            return

        # Per-tech: list of (frac_max, multiplier) tuples, sorted by
        # frac_max ascending. Validation: multipliers must be
        # non-decreasing for LP convexity.
        self.segments_by_tech: dict = {}
        for tech, grp in df.groupby('tech'):
            segs = grp.sort_values('frac_max')[
                ['frac_max', 'multiplier']
            ].itertuples(index=False, name=None)
            segs = list(segs)
            if not segs:
                continue
            mults = [m for _, m in segs]
            if any(b < a - 1e-9 for a, b in zip(mults[:-1], mults[1:])):
                raise ValueError(
                    f"tech_heat_rate.csv: multipliers for tech={tech!r} "
                    f"are not non-decreasing ({mults}). LP-convex "
                    f"piecewise-linear heat rates require monotone "
                    f"slopes; resort the CSV or fix the multipliers."
                )
            self.segments_by_tech[tech] = segs

        if not self.segments_by_tech:
            return

        # Index set for segments. We size to the max-K seen in the
        # CSV and let unused (tech, seg) cells be locked to zero by
        # the segment-bound rule.
        max_segments = max(
            len(segs) for segs in self.segments_by_tech.values()
        )
        segment_idx = list(range(1, max_segments + 1))
        model.heat_rate_segments = segment_idx

        model.gen_segment = model.add_variables(
            model.hour, model.month, model.year, model.zone, model.tech,
            segment_idx, lb=0,
        )

        # Lock unused segments to zero, so the LP can't take advantage
        # of phantom segment width when (tech, seg) isn't defined.
        model.gen_segment_zero_cons = poi.make_tupledict(
            model.hour, model.month, model.year, model.zone, model.tech,
            segment_idx,
            rule=self.segment_zero_rule,
        )

        # Per-segment width bound:
        #   gen_segment[s] <= (frac_max[s] - frac_max[s-1]) * cap * dt
        model.gen_segment_width_cons = poi.make_tupledict(
            model.hour, model.month, model.year, model.zone, model.tech,
            segment_idx,
            rule=self.segment_width_rule,
        )

        # Sum-to-gen: per (h, m, y, z, te) in the heat-rate set,
        #   sum_s gen_segment[..., s] == gen[h, m, y, z, te].
        model.gen_sum_to_total_cons = poi.make_tupledict(
            model.hour, model.month, model.year, model.zone, model.tech,
            rule=self.sum_to_gen_rule,
        )

    # ------------------------------------------------------------------
    # Rules

    def segment_zero_rule(self, h, m, y, z, te, s):
        """Force ``gen_segment[..., s] = 0`` for (te, s) not defined."""
        segs = self.segments_by_tech.get(te)
        if segs is not None and s <= len(segs):
            return None
        return self.model.add_linear_constraint(
            self.model.gen_segment[h, m, y, z, te, s], poi.Eq, 0
        )

    def segment_width_rule(self, h, m, y, z, te, s):
        """``gen_segment[s] <= (width[s] * cap_existing) * dt``."""
        segs = self.segments_by_tech.get(te)
        if segs is None or s > len(segs):
            return None
        prev = 0.0 if s == 1 else float(segs[s - 2][0])
        width = float(segs[s - 1][0]) - prev
        if width <= 0:
            return self.model.add_linear_constraint(
                self.model.gen_segment[h, m, y, z, te, s], poi.Eq, 0
            )
        model = self.model
        dt = model.params['dt']
        lhs = (
            model.gen_segment[h, m, y, z, te, s]
            - width * model.cap_existing[y, z, te] * dt
        )
        return model.add_linear_constraint(lhs, poi.Leq, 0)

    def sum_to_gen_rule(self, h, m, y, z, te):
        """``sum_s gen_segment[..., s] == gen[h, m, y, z, te]``."""
        segs = self.segments_by_tech.get(te)
        if segs is None:
            return None  # tech keeps the flat-rate fuel cost
        model = self.model
        lhs = poi.quicksum(
            model.gen_segment[h, m, y, z, te, s]
            for s in range(1, len(segs) + 1)
        ) - model.gen[h, m, y, z, te]
        return model.add_linear_constraint(lhs, poi.Eq, 0)


def add_heat_rate_fuel_cost(model) -> "poi.ExprBuilder":
    """Per-segment fuel cost contribution, NPV-discounted.

    For each tech with a heat-rate curve, the fuel cost becomes:

      fuel_price[te, y] * sum_s multiplier[s] * gen_segment[..., s]

    summed over (h, m, y, z), discounted by ``var_factor[y, z]``,
    and divided by ``weight``. Returned as an ExprBuilder. Returns
    a zero ExprBuilder when the module is disabled or no heat-rate
    curves are loaded.

    The CALLER (``cost.var_cost_rule``) must remove the corresponding
    techs' contribution from the existing flat-rate
    ``fuel_cost_breakdown`` to avoid double-counting -- handled by
    skipping those techs in the original ``fuel_cost_breakdown``
    loop when ``hasattr(model, 'gen_segment')`` and the tech is in
    ``segments_by_tech``.
    """
    cost = poi.ExprBuilder()
    if not model.params.get('is_piecewise_heat_rate', False):
        return cost
    if not hasattr(model, 'gen_segment'):
        return cost

    df = model.params.get('heat_rate')
    if df is None or not hasattr(df, 'iterrows') or df.empty:
        return cost

    fuel_price = model.params.get('fuel_price') or {}
    vf = model.params['var_factor']
    w = model.params['weight']

    # Re-build per-tech segment lists (mirrors AddHeatRateConstraints
    # __init__; cheap relative to the LP build cost).
    segs_by_tech = {}
    for tech, grp in df.groupby('tech'):
        segs_by_tech[tech] = list(
            grp.sort_values('frac_max')[
                ['frac_max', 'multiplier']
            ].itertuples(index=False, name=None)
        )

    for te, segs in segs_by_tech.items():
        if te not in set(model.tech):
            continue
        for s, (_, mult) in enumerate(segs, start=1):
            for y in model.year:
                fp = float(fuel_price.get((te, y), 0.0))
                if fp == 0.0:
                    continue
                for z in model.zone:
                    factor = vf[y, z] / w
                    cost += (
                        fp * float(mult) * factor
                        * poi.quicksum(
                            model.gen_segment[h, m, y, z, te, s]
                            for h in model.hour
                            for m in model.month
                        )
                    )
    return cost


def techs_with_heat_rate_curve(model) -> set:
    """Return the set of techs that have a heat-rate curve loaded.

    Used by ``cost.fuel_cost_breakdown`` to skip techs that should
    be priced through ``add_heat_rate_fuel_cost`` instead of the
    flat-rate fallback.
    """
    if not model.params.get('is_piecewise_heat_rate', False):
        return set()
    if not hasattr(model, 'gen_segment'):
        return set()
    df = model.params.get('heat_rate')
    if df is None or not hasattr(df, 'iterrows') or df.empty:
        return set()
    return set(df['tech'].astype(str))
