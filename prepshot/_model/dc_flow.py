#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""DC linearised power-flow constraints (zonal), with optional N-1.

PREP-SHOT's default transmission representation is a "transport" or
"pipe" model: net flow ``trans_export[z1,z2]`` is bounded by line
capacity, and that's it. There's no Kirchhoff voltage law, no loop
flow, no reactance -- power can flow whichever way the LP optimum
prefers. That's fine for capacity-expansion screening, where the
question is "where to build" rather than "what does the AC network
actually do."

When ``config.json.dc_parameters.is_dc_flow`` is ``true``, this module
adds the standard DC linearisation: for every connected zone pair
``(z1, z2)`` with a positive susceptance ``b[z1,z2]``, the **net** flow
between the two zones is locked to the phase-angle difference times the
susceptance:

.. math::

    \\text{trans\\_export}_{h,m,y,z_1,z_2}
      - \\text{trans\\_export}_{h,m,y,z_2,z_1}
    = b_{z_1,z_2} \\cdot
      (\\theta_{h,m,y,z_1} - \\theta_{h,m,y,z_2}) \\cdot \\Delta h

The capacity bound on each direction (``trans_export <= cap_lines_
existing``) carries over unchanged, which means the *thermal* limit
still applies but Kirchhoff is now enforced too. Loop flows on a
multi-zone network are no longer free.

N-1 security-constrained mode (v1.18+)
======================================

When ``dc_parameters.is_n1_secure`` is also ``true`` and
``transmission_contingencies.csv`` lists which lines to protect
against, the model is solved under a **preventive** security policy:
the same ``gen`` decision must be feasible in the base case AND in
every contingency where one listed line is out of service. For each
contingency ``c``, the module adds a parallel set of state variables
(``theta_c``, ``trans_export_c``) and constraints (DC flow with the
outaged line forced to zero, capacity bounds, demand balance with
contingency flows). ``gen`` and ``charge`` are NOT duplicated --
preventive policy means the same dispatch must work everywhere.

Inputs (all optional):

* ``transmission_susceptance.csv`` -- columns ``zone1, zone2, value``
  (one row per UNORDERED zone pair; the loader symmetrises to both
  directions). Units: MW per radian (so ``b * angle_diff`` is MW).
  Missing rows -> 0 (no constraint, equivalent to "no electrical
  connection between these zones").

* ``transmission_contingencies.csv`` -- columns ``zone1, zone2``,
  one line per contingency case. Each row removes the named line in
  one parallel solve. Empty file -> no contingencies, equivalent to
  ``is_n1_secure=false``.

Config:

* ``dc_parameters.is_dc_flow`` (bool, default false) -- enable/disable
  base-case DC flow.
* ``dc_parameters.reference_zone`` (str, optional) -- zone whose phase
  angle is pinned to 0. Defaults to the first zone in ``model.zone``.
* ``dc_parameters.is_n1_secure`` (bool, default false) -- adds N-1
  contingency constraints. Requires ``is_dc_flow=true``.

The phase-angle variable ``model.theta`` is bounded to ``[-pi, pi]``
for numerical stability; in practice DC OPF angles stay well within
``+/- pi/2``.

This module is LP-stable: no binaries, no new non-convexity.
"""
import math

import pyoptinterface as poi


class AddDCFlowConstraints:
    """DC linearised power-flow constraints, opt-in."""

    def __init__(self, model: object) -> None:
        self.model = model
        if not model.params.get('is_dc_flow', False):
            return

        # Reference bus: use config override if given, else the first
        # zone the dataset declared. Pinning one phase angle anchors
        # the otherwise translationally-invariant theta solution.
        self.ref_zone = (
            model.params.get('reference_zone') or model.zone[0]
        )
        if self.ref_zone not in set(model.zone):
            raise ValueError(
                f"DC flow reference_zone={self.ref_zone!r} is not in "
                f"the model's zone set {sorted(model.zone)!r}."
            )

        # Symmetrise the susceptance lookup: the CSV ships one row per
        # unordered pair, but the rule below queries by ordered pair.
        susc_raw = model.params.get('transmission_susceptance') or {}
        self.b = {}
        for key, val in susc_raw.items():
            if not isinstance(key, tuple) or len(key) != 2:
                continue
            z1, z2 = key
            self.b[(z1, z2)] = val
            self.b[(z2, z1)] = val

        # Phase angle, bounded to +/- pi for numerical stability. DC
        # OPF rarely needs more than +/- pi/2, but pi gives slack.
        model.theta = model.add_variables(
            model.hour, model.month, model.year, model.zone,
            lb=-math.pi, ub=math.pi,
        )

        model.dc_theta_ref_cons = poi.make_tupledict(
            model.hour, model.month, model.year,
            rule=self.theta_ref_rule,
        )
        model.dc_flow_cons = poi.make_tupledict(
            model.hour, model.month, model.year, model.zone, model.zone,
            rule=self.flow_rule,
        )

        # N-1 security-constrained mode (v1.18+). For each line listed
        # in transmission_contingencies.csv, build a parallel set of
        # state variables + constraints under that contingency. Same
        # `gen` decision must be feasible in every case (preventive
        # policy).
        if not model.params.get('is_n1_secure', False):
            return
        # ``contingencies`` arrives from the CSV loader as a pandas
        # DataFrame with columns ``zone1, zone2`` (table format).
        # Normalise to a list of unordered (z1, z2) tuples,
        # alphabetised so we can compare against the b-lookup keys.
        contingencies_raw = model.params.get('contingencies')
        zone_set = set(model.zone)
        pairs = []
        if contingencies_raw is not None and hasattr(contingencies_raw, 'iterrows'):
            for _, r in contingencies_raw.iterrows():
                a, b_ = str(r['zone1']), str(r['zone2'])
                if a in zone_set and b_ in zone_set and a != b_:
                    pairs.append(tuple(sorted([a, b_])))
        # De-duplicate while preserving order.
        seen = set()
        self.contingencies = []
        for p in pairs:
            if p not in seen:
                seen.add(p)
                self.contingencies.append(p)
        if not self.contingencies:
            return
        contingency_idx = list(range(len(self.contingencies)))
        model.contingency_idx = contingency_idx

        # theta_c[h, m, y, z, c] -- phase angle in contingency c.
        model.theta_c = model.add_variables(
            model.hour, model.month, model.year, model.zone, contingency_idx,
            lb=-math.pi, ub=math.pi,
        )
        # trans_export_c[h, m, y, z1, z2, c] -- flow per direction in
        # contingency c, mirroring the base-case trans_export shape.
        model.trans_export_c = model.add_variables(
            model.hour, model.month, model.year, model.zone, model.zone,
            contingency_idx,
            lb=0,
        )

        # Reference bus per contingency.
        model.dc_theta_ref_c_cons = poi.make_tupledict(
            model.hour, model.month, model.year, contingency_idx,
            rule=self.theta_ref_c_rule,
        )
        # DC flow eq per (line, contingency).
        model.dc_flow_c_cons = poi.make_tupledict(
            model.hour, model.month, model.year, model.zone, model.zone,
            contingency_idx,
            rule=self.flow_c_rule,
        )
        # Capacity bound per (direction, contingency).
        model.dc_cap_c_cons = poi.make_tupledict(
            model.hour, model.month, model.year, model.zone, model.zone,
            contingency_idx,
            rule=self.cap_c_rule,
        )
        # Per-(zone, contingency) demand balance: same gen + charge as
        # base case, but flows redistributed.
        model.demand_balance_c_cons = poi.make_tupledict(
            model.hour, model.month, model.year, model.zone, contingency_idx,
            rule=self.demand_balance_c_rule,
        )

    def theta_ref_rule(
        self, h: int, m: int, y: int
    ) -> poi.ConstraintIndex:
        """Pin the reference zone's phase angle to 0."""
        model = self.model
        return model.add_linear_constraint(
            model.theta[h, m, y, self.ref_zone], poi.Eq, 0
        )

    def flow_rule(
        self, h: int, m: int, y: int, z1: str, z2: str
    ) -> poi.ConstraintIndex:
        """Net flow = susceptance * angle difference * dt.

        Only emitted for ordered pairs ``(z1, z2)`` with ``z1 < z2``
        and a positive susceptance, so each electrical line gets one
        constraint instead of two redundant ones. The capacity bound
        on each ``trans_export`` direction stays in place.
        """
        if z1 >= z2:
            return None
        b = self.b.get((z1, z2), 0)
        if b == 0:
            return None
        model = self.model
        dt = model.params['dt']
        lhs = (
            model.trans_export[h, m, y, z1, z2]
            - model.trans_export[h, m, y, z2, z1]
            - b * dt * (
                model.theta[h, m, y, z1] - model.theta[h, m, y, z2]
            )
        )
        return model.add_linear_constraint(lhs, poi.Eq, 0)

    # ------------------------------------------------------------------
    # N-1 contingency rules

    def theta_ref_c_rule(
        self, h: int, m: int, y: int, c: int
    ) -> poi.ConstraintIndex:
        """Pin reference zone's phase angle to 0 in contingency c."""
        model = self.model
        return model.add_linear_constraint(
            model.theta_c[h, m, y, self.ref_zone, c], poi.Eq, 0
        )

    def flow_c_rule(
        self, h: int, m: int, y: int, z1: str, z2: str, c: int
    ) -> poi.ConstraintIndex:
        """Per-line DC flow eq in contingency c.

        The outaged line ``self.contingencies[c]`` has its flow forced
        to zero (both directions). Every other line follows the same
        susceptance-times-angle-difference relation as the base case.
        """
        if z1 >= z2:
            return None
        b = self.b.get((z1, z2), 0)
        if b == 0:
            return None
        out_pair = self.contingencies[c]  # alphabetised tuple
        model = self.model
        dt = model.params['dt']
        if (z1, z2) == out_pair:
            # Force both directions of the outaged line to zero.
            model.add_linear_constraint(
                model.trans_export_c[h, m, y, z1, z2, c], poi.Eq, 0
            )
            return model.add_linear_constraint(
                model.trans_export_c[h, m, y, z2, z1, c], poi.Eq, 0
            )
        lhs = (
            model.trans_export_c[h, m, y, z1, z2, c]
            - model.trans_export_c[h, m, y, z2, z1, c]
            - b * dt * (
                model.theta_c[h, m, y, z1, c]
                - model.theta_c[h, m, y, z2, c]
            )
        )
        return model.add_linear_constraint(lhs, poi.Eq, 0)

    def cap_c_rule(
        self, h: int, m: int, y: int, z1: str, z2: str, c: int
    ) -> poi.ConstraintIndex:
        """Capacity bound on contingency-case flow.

        ``trans_export_c[h, m, y, z1, z2, c] <= cap_lines_existing[y,
        z1, z2]``. Same numeric bound as the base case -- ``gen`` is
        shared between base and contingency, so capacity stays
        consistent.
        """
        model = self.model
        lhs = (
            model.trans_export_c[h, m, y, z1, z2, c]
            - model.cap_lines_existing[y, z1, z2]
        )
        return model.add_linear_constraint(lhs, poi.Leq, 0)

    def demand_balance_c_rule(
        self, h: int, m: int, y: int, z: str, c: int
    ) -> poi.ConstraintIndex:
        """Power balance in contingency c.

        Same as the base-case ``power_balance_rule`` in ``demand.py``,
        but with contingency-case flows. ``gen`` and ``charge`` are
        the shared base-case decisions (preventive policy).
        """
        model = self.model
        load = model.params['demand']
        dt = model.params['dt']
        eff = model.params['transmission_line_efficiency']
        # Imports = sum of inbound flows weighted by line efficiency.
        imp_z = poi.quicksum(
            eff[z1, z] * model.trans_export_c[h, m, y, z1, z, c]
            for z1 in model.zone
        )
        exp_z = poi.quicksum(
            model.trans_export_c[h, m, y, z, z1, c]
            for z1 in model.zone
        )
        gen_z = poi.quicksum(
            model.gen[h, m, y, z, te]
            for te in model.zone_techs.get(z, [])
        )
        storage_set = set(model.storage_tech)
        charge_z = poi.quicksum(
            model.charge[h, m, y, z, te]
            for te in model.zone_techs.get(z, [])
            if te in storage_set
        )
        # Mirror the base-case load-shedding slack so contingency
        # power balance can use it too.
        demand_z = load[z, y, m, h] * dt
        if hasattr(model, 'lns'):
            demand_z = demand_z - model.lns[h, m, y, z]
        lhs = demand_z - (imp_z - exp_z + gen_z - charge_z)
        return model.add_linear_constraint(lhs, poi.Eq, 0)
