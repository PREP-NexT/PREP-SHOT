#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Unit-commitment (UC) overlay -- clustered MILP formulation.

Standard "clustered UC" representation, used by GenX, PowNet, and
similar planning models that need the MILP fidelity without modelling
each plant individually:

* Each UC-eligible tech (typically thermal: coal, gas, oil) is a
  cluster of identical units of size ``tech_unit_size[te]`` MW. The
  total cluster capacity is ``cap_existing[y, z, te]``, so the
  *integer* number of units is ``cap / unit_size``.

* New decision variables per ``(h, m, y, z, te)``:

  - ``online[h]`` -- number of units online (integer, 0..N_units).
  - ``startup[h]`` -- number of units started this hour (integer >=0).
  - ``shutdown[h]`` -- number of units shut down this hour (integer
    >=0).

* New constraints:

  - **State evolution** (h > hour[0]):
    ``online[h] - online[h-1] = startup[h] - shutdown[h]``
  - **Capacity bound on dispatch**:
    ``gen[h] <= online[h] * unit_size * p_max_pu * dt``
    ``gen[h] >= online[h] * unit_size * p_min_pu * dt``

    These REPLACE the standard ``gen <= cap_existing * p_max_pu * dt``
    bound for UC-eligible techs (the standard one is now redundant
    because ``online <= N_units = cap/unit_size``).
  - **Minimum up time** (``online >= sum of recent startups``):
    ``online[h] >= sum_{i=0..MinUp-1} startup[h-i]``
  - **Minimum down time** (``offline >= sum of recent shutdowns``):
    ``(N_units - online[h]) >= sum_{i=0..MinDown-1} shutdown[h-i]``

* New cost terms (added to the objective):

  - ``startup_cost[te] * unit_size[te] * startup[h]`` per hour
  - ``no_load_cost[te] * unit_size[te] * online[h] * dt`` per hour

  Both NPV-discounted via ``var_factor[y, z]`` like the rest of the
  variable cost.

This module turns PREP-SHOT into a **MILP** when enabled. HiGHS solves
it; runtime grows several-fold relative to the LP. Recommended only
for small-to-medium scenarios -- ``three_zone`` (48 hours) takes a
few seconds; full-year 8760-hour PCM mode with UC is feasible only
in rolling-horizon windows (see ``prepshot.pcm``).

Configuration
=============

Add to ``config.json``::

    "uc_parameters": {
        "is_uc": true,
        "uc_relaxation": "integer"   // or "continuous" for LP relaxation
    }

When ``is_uc`` is missing or ``false``, the module is a no-op and
PREP-SHOT stays LP. When ``uc_relaxation`` is ``"continuous"``, the
binaries become continuous in their natural ranges -- useful for
scaling tests and for warm-starting an integer solve.

Inputs
======

All optional (rows missing or files missing -> safe defaults):

* ``tech_uc_eligible.csv`` -- ``tech, eligible``. Default ``0``.
* ``tech_unit_size.csv`` -- ``tech, value`` (MW). Default ``1`` (one
  cluster = one unit at full cap, equivalent to LP behaviour).
* ``tech_min_up_time.csv`` -- ``tech, value`` (hours). Default ``1``.
* ``tech_min_down_time.csv`` -- ``tech, value`` (hours). Default ``1``.
* ``tech_startup_cost.csv`` -- ``tech, value`` ($/MW). Default ``0``.
* ``tech_no_load_cost.csv`` -- ``tech, value`` ($/MW-h). Default ``0``.
"""
import pyoptinterface as poi

from prepshot.utils import sparse_tupledict


class AddUnitCommitmentConstraints:
    """Clustered unit-commitment constraints + cost terms."""

    def __init__(self, model: object) -> None:
        self.model = model
        if not model.params.get('is_uc', False):
            return

        # Eligibility: techs missing from tech_uc_eligible.csv default
        # to ``not eligible`` and pass through this module untouched.
        elig = model.params.get('uc_eligible') or {}
        self.is_eligible = {
            t: bool(elig.get(t, False)) for t in model.tech
        }
        if not any(self.is_eligible.values()):
            return  # nothing to do; module is a no-op

        # Tech parameters with safe defaults.
        self.unit_size = model.params.get('uc_unit_size') or {}
        self.min_up = model.params.get('uc_min_up_time') or {}
        self.min_down = model.params.get('uc_min_down_time') or {}
        self.startup_cost = model.params.get('uc_startup_cost') or {}
        self.no_load_cost = model.params.get('uc_no_load_cost') or {}

        # Domain: integer for true clustered MILP, continuous for LP
        # relaxation. ``set_variable_attribute`` flips the domain
        # post-construction; for integer we set during creation.
        relax = model.params.get('uc_relaxation', 'integer')
        domain = (
            poi.VariableDomain.Integer
            if relax == 'integer' else poi.VariableDomain.Continuous
        )

        # Per-(zone, tech) integer count of units in the existing cluster.
        # cap_existing is an ExprBuilder; we use the *params* ['existing_
        # fleet'] dict directly so this stays a Python integer.
        self.n_units = {}
        fleet = model.params.get('existing_fleet') or {}
        for z in model.zone:
            for te in model.tech:
                if not self.is_eligible[te]:
                    continue
                u = float(self.unit_size.get(te, 1.0))
                if u <= 0:
                    self.n_units[(z, te)] = 0
                    continue
                # Sum capacity across commission years for this (zone, tech)
                cap_mw = sum(
                    float(cap) for (t, zz, _cy), cap in fleet.items()
                    if t == te and zz == z
                )
                self.n_units[(z, te)] = int(cap_mw / u + 1e-6)

        # p_max_pu / p_min_pu lookups (same source as generation.py).
        # Must be computed BEFORE make_tupledict invokes the rules.
        self._p_max_pu = dict(model.params.get('max_gen_profile') or {})
        self._p_min_pu = dict(model.params.get('min_gen_profile') or {})

        # Sparse: only (z, te) where the tech is both UC-eligible AND
        # actually deployed at the zone. Drops ~99% of dense at full-
        # nodal scale; on three_zone (all techs at all zones) it's
        # equivalent to the original.
        active_zt_uc = [
            (z, te) for (z, te) in model.active_zt
            if self.is_eligible.get(te, False)
        ]
        active_hmyzte_uc = [
            (h, m, y, z, te)
            for h in model.hour
            for m in model.month
            for y in model.year
            for (z, te) in active_zt_uc
        ]
        self._active_zt_uc = active_zt_uc
        self._active_hmyzte_uc = active_hmyzte_uc

        _new_var = lambda *_: model.add_variable(lb=0, domain=domain)
        model.online = sparse_tupledict(active_hmyzte_uc, _new_var)
        model.startup = sparse_tupledict(active_hmyzte_uc, _new_var)
        model.shutdown = sparse_tupledict(active_hmyzte_uc, _new_var)

        # Constraints. Each rule already early-returns for non-eligible
        # techs; sparsifying just skips the rule call for those cells.
        model.uc_n_unit_bound_cons = sparse_tupledict(
            active_hmyzte_uc, self.n_unit_bound_rule
        )
        model.uc_state_evolution_cons = sparse_tupledict(
            active_hmyzte_uc, self.state_evolution_rule
        )
        model.uc_gen_up_cons = sparse_tupledict(
            active_hmyzte_uc, self.gen_up_uc_rule
        )
        model.uc_gen_low_cons = sparse_tupledict(
            active_hmyzte_uc, self.gen_low_uc_rule
        )
        model.uc_min_up_cons = sparse_tupledict(
            active_hmyzte_uc, self.min_up_rule
        )
        model.uc_min_down_cons = sparse_tupledict(
            active_hmyzte_uc, self.min_down_rule
        )

    # ------------------------------------------------------------------
    # Rules

    def n_unit_bound_rule(self, h, m, y, z, te):
        """``online[h] <= N_units`` and force online=startup=shutdown=0
        for non-eligible (z, te) cells."""
        model = self.model
        if not self.is_eligible[te]:
            # Lock all three to 0 so they don't drift in the LP relax.
            model.add_linear_constraint(model.online[h, m, y, z, te], poi.Eq, 0)
            model.add_linear_constraint(model.startup[h, m, y, z, te], poi.Eq, 0)
            return model.add_linear_constraint(
                model.shutdown[h, m, y, z, te], poi.Eq, 0
            )
        n = self.n_units.get((z, te), 0)
        return model.add_linear_constraint(
            model.online[h, m, y, z, te] - n, poi.Leq, 0
        )

    def state_evolution_rule(self, h, m, y, z, te):
        """``online[h] - online[h-1] = startup[h] - shutdown[h]``.

        At the first hour of a window, ``online[h-1]`` does not exist
        in this LP, so the rule consults
        ``params['prior_uc_online'][(z, te)]`` (terminal online count
        from the previous PCM window).  When that lookup is missing
        (very first window of the run, or non-PCM CEM model) the
        boundary condition degenerates to "online[h0] free, no
        startup / shutdown linkage" -- same behaviour as before.
        """
        model = self.model
        if not self.is_eligible[te]:
            return None
        h0 = model.hour[0]
        if h == h0:
            prior_online = (
                model.params.get('prior_uc_online') or {}
            ).get((z, te))
            if prior_online is None:
                return None
            lhs = (
                model.online[h, m, y, z, te]
                - prior_online
                - model.startup[h, m, y, z, te]
                + model.shutdown[h, m, y, z, te]
            )
            return model.add_linear_constraint(lhs, poi.Eq, 0)
        lhs = (
            model.online[h, m, y, z, te]
            - model.online[h - 1, m, y, z, te]
            - model.startup[h, m, y, z, te]
            + model.shutdown[h, m, y, z, te]
        )
        return model.add_linear_constraint(lhs, poi.Eq, 0)

    def gen_up_uc_rule(self, h, m, y, z, te):
        """``gen[h] <= online[h] * unit_size * p_max_pu * dt``."""
        model = self.model
        if not self.is_eligible[te]:
            return None
        u = float(self.unit_size.get(te, 1.0))
        p_max_pu = self._p_max_pu.get((te, z, y, m, h), 1)
        dt = model.params['dt']
        lhs = (
            model.gen[h, m, y, z, te]
            - model.online[h, m, y, z, te] * u * p_max_pu * dt
        )
        return model.add_linear_constraint(lhs, poi.Leq, 0)

    def gen_low_uc_rule(self, h, m, y, z, te):
        """``gen[h] >= online[h] * unit_size * p_min_pu * dt``."""
        model = self.model
        if not self.is_eligible[te]:
            return None
        u = float(self.unit_size.get(te, 1.0))
        p_min_pu = self._p_min_pu.get((te, z, y, m, h), 0)
        if p_min_pu == 0:
            return None  # trivial constraint; gen >= 0 already enforced
        dt = model.params['dt']
        lhs = (
            model.gen[h, m, y, z, te]
            - model.online[h, m, y, z, te] * u * p_min_pu * dt
        )
        return model.add_linear_constraint(lhs, poi.Geq, 0)

    def min_up_rule(self, h, m, y, z, te):
        """``online[h] >= sum_{i=0..MinUp-1} startup[h-i]`` -- if a
        unit started in any of the last MinUp hours, it must be
        online now.

        The lookback spans absolute hours ``[h - mu + 1, h]``.  Hours
        that fall inside the current window pull
        ``model.startup[h_abs, ...]``; hours that fall before the
        window's first hour pull the carried-over count from
        ``params['prior_uc_startup'][(z, te, h_abs)]`` (populated by
        the previous PCM window's ``_extract_window_state``).
        Missing prior values default to 0, equivalent to "no startup
        recorded that hour" -- a safe under-count that only affects
        very early hours of the first run.
        """
        model = self.model
        if not self.is_eligible[te]:
            return None
        mu = int(self.min_up.get(te, 1))
        if mu <= 1:
            return None  # 1-hour min-up = no real constraint
        h0 = model.hour[0]
        in_window = [hh for hh in range(h - mu + 1, h + 1) if hh >= h0]
        prior_starts = (model.params.get('prior_uc_startup') or {})
        prior_total = sum(
            float(prior_starts.get((z, te, hh), 0.0))
            for hh in range(h - mu + 1, h0)
        )
        if not in_window and prior_total == 0.0:
            return None
        lhs = (
            poi.quicksum(
                model.startup[hh, m, y, z, te] for hh in in_window
            )
            + prior_total
            - model.online[h, m, y, z, te]
        )
        return model.add_linear_constraint(lhs, poi.Leq, 0)

    def min_down_rule(self, h, m, y, z, te):
        """``(N_units - online[h]) >= sum_{i=0..MinDown-1} shutdown[h-i]``.

        Symmetric to ``min_up_rule``: the lookback over absolute hours
        ``[h - md + 1, h]`` pulls in-window shutdowns from
        ``model.shutdown`` and pre-window shutdowns from
        ``params['prior_uc_shutdown'][(z, te, h_abs)]``.
        """
        model = self.model
        if not self.is_eligible[te]:
            return None
        md = int(self.min_down.get(te, 1))
        if md <= 1:
            return None
        h0 = model.hour[0]
        in_window = [hh for hh in range(h - md + 1, h + 1) if hh >= h0]
        prior_shuts = (model.params.get('prior_uc_shutdown') or {})
        prior_total = sum(
            float(prior_shuts.get((z, te, hh), 0.0))
            for hh in range(h - md + 1, h0)
        )
        if not in_window and prior_total == 0.0:
            return None
        n = self.n_units.get((z, te), 0)
        lhs = (
            model.online[h, m, y, z, te]
            + poi.quicksum(
                model.shutdown[hh, m, y, z, te] for hh in in_window
            )
            + prior_total
            - n
        )
        return model.add_linear_constraint(lhs, poi.Leq, 0)


def add_uc_cost_terms(model) -> "poi.ExprBuilder":
    """Return the UC cost contribution (startup + no-load) as an
    ExprBuilder, NPV-discounted by ``var_factor`` and divided by
    ``weight`` to align with the rest of ``cost_var``.

    Returns a zero ExprBuilder when UC is disabled, so callers can
    add it unconditionally.
    """
    cost = poi.ExprBuilder()
    if not model.params.get('is_uc', False):
        return cost
    if not hasattr(model, 'online'):
        return cost
    elig = model.params.get('uc_eligible') or {}
    is_eligible = {t: bool(elig.get(t, False)) for t in model.tech}
    if not any(is_eligible.values()):
        return cost

    unit_size = model.params.get('uc_unit_size') or {}
    startup_cost = model.params.get('uc_startup_cost') or {}
    no_load_cost = model.params.get('uc_no_load_cost') or {}
    vf = model.params['var_factor']
    w = model.params['weight']
    dt = model.params['dt']

    # Sparse: walk only (z, te) where the tech is eligible AND
    # actually deployed at the zone (online/startup variables only
    # exist there).
    active_zt_uc = [
        (z, te) for (z, te) in model.active_zt
        if is_eligible.get(te, False)
    ]
    for h in model.hour:
        for m in model.month:
            for y in model.year:
                for (z, te) in active_zt_uc:
                    u = float(unit_size.get(te, 1.0))
                    sc = float(startup_cost.get(te, 0.0))
                    nl = float(no_load_cost.get(te, 0.0))
                    if sc == 0 and nl == 0:
                        continue
                    factor = vf[y, z] / w
                    if sc != 0:
                        cost += (
                            sc * u
                            * model.startup[h, m, y, z, te]
                            * factor
                        )
                    if nl != 0:
                        cost += (
                            nl * u * dt
                            * model.online[h, m, y, z, te]
                            * factor
                        )
    return cost
