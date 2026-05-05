#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""DC linearised power-flow constraints (zonal).

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

Inputs (all optional, gated by ``is_dc_flow``):

* ``transmission_susceptance.csv`` -- columns ``zone1, zone2, value``
  (one row per UNORDERED zone pair; the loader symmetrises to both
  directions). Units: MW per radian (so ``b * angle_diff`` is MW).
  Missing rows -> 0 (no constraint, equivalent to "no electrical
  connection between these zones").

Config:

* ``dc_parameters.is_dc_flow`` (bool, default false) -- enable/disable.
* ``dc_parameters.reference_zone`` (str, optional) -- zone whose phase
  angle is pinned to 0. Defaults to the first zone in ``model.zone``.

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
