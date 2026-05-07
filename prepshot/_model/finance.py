#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Public-debt accounting and caps for new-build investment.

Each new-tech investment carries a public-debt obligation equal to
``public_debt_ratio[te]`` times its discounted investment cost. The
module exposes that obligation as an indexed expression
``public_debt_newtech[y, z, te]`` and (optionally) caps the public
debt taken on each year, system-wide and per-zone:

.. math::

    {\\rm{public\\_debt}}_{y,z,te}
    = {\\rm{cost\\_newtech}}_{y,z,te} \\times r^{\\rm{public}}_{te}

    \\sum_{z, te} {\\rm{public\\_debt}}_{y,z,te}
    \\le \\overline{D^{\\rm{sys}}_{y}}\\quad\\forall y

    \\sum_{te} {\\rm{public\\_debt}}_{y,z,te}
    \\le \\overline{D^{\\rm{zone}}_{y, z}}\\quad\\forall y, z

This module is OFF unless the user provides ``public_debt_ratio``;
the optional caps default to ``+inf`` (no constraint added).
"""

import numpy as np
import pyoptinterface as poi

from prepshot.utils import sparse_tupledict


class AddFinanceConstraints:
    """Public-debt expressions and (optional) cap constraints."""

    def __init__(self, model : object) -> None:
        """Initialize the class and add expressions / constraints.

        Reads ``model.cost_newtech_breakdown`` (built by
        :class:`AddCostObjective`), so this must run AFTER
        ``AddCostObjective``.

        Parameters
        ----------
        model : object
            Model object depending on the solver.
        """
        self.model = model
        active_yzt = [(y, z, te) for y in model.year
                      for (z, te) in model.active_zt]
        model.public_debt_newtech = sparse_tupledict(
            active_yzt, self.public_debt_newtech_rule
        )
        model.public_debt_max_system_cons = poi.make_tupledict(
            model.year,
            rule=self.public_debt_max_system_rule,
        )
        model.public_debt_max_zone_cons = poi.make_tupledict(
            model.year, model.zone,
            rule=self.public_debt_max_zone_rule,
        )

    def public_debt_newtech_rule(
        self, y : int, z : str, te : str,
    ) -> poi.ExprBuilder:
        """Public-debt obligation incurred by a new-tech investment.

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
            Discounted public-debt obligation for ``(y, z, te)``.
        """
        model = self.model
        ratio = model.params['public_debt_ratio'][te]
        return model.cost_newtech_breakdown[y, z, te] * ratio

    def public_debt_max_system_rule(
        self, y : int,
    ) -> poi.ConstraintIndex:
        """System-wide upper bound on public debt taken in year ``y``.

        Missing entry or ``+inf`` skips the constraint.

        Parameters
        ----------
        y : int
            Year.

        Returns
        -------
        poi.ConstraintIndex or None
            The cap constraint, or ``None`` if uncapped.
        """
        model = self.model
        caps = model.params.get('public_debt_max_system') or {}
        cap = caps.get(y)
        if cap is None or cap == np.inf:
            return None
        lhs = poi.ExprBuilder(0)
        lhs += poi.quicksum(model.public_debt_newtech.select(y, '*', '*'))
        lhs -= cap
        return model.add_linear_constraint(lhs, poi.Leq, 0)

    def public_debt_max_zone_rule(
        self, y : int, z : str,
    ) -> poi.ConstraintIndex:
        """Per-zone upper bound on public debt taken in year ``y``.

        Parameters
        ----------
        y : int
            Year.
        z : str
            Zone.

        Returns
        -------
        poi.ConstraintIndex or None
            The cap constraint, or ``None`` if uncapped.
        """
        model = self.model
        caps = model.params.get('public_debt_max_zone') or {}
        cap = caps.get((z, y))
        if cap is None or cap == np.inf:
            return None
        lhs = poi.ExprBuilder(0)
        lhs += poi.quicksum(model.public_debt_newtech.select(y, z, '*'))
        lhs -= cap
        return model.add_linear_constraint(lhs, poi.Leq, 0)
