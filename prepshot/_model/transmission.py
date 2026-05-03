#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""This module contains transmission related functions. We simplify the
transmission of electricity as a transportation model.
The model computes the transmission loss for each hour, in each time period,
for each year, from :math:`z_{\\rm{from}}` zone to :math:`z_{\\rm{to}}` zone,
as follows:

.. math::

    {\\rm{import}}_{h,m,y,z_{\\rm{from}},z_{\\rm{to}}}
    ={\\rm{export}}_{h,m,y,z_{\\rm{from}},z_{\\rm{to}}}\\times
    \\eta_{z_{\\rm{from}},z_{\\rm{to}}}^{\\rm{trans}}
    \\quad\\forall h,m,y,z_{\\rm{from}}\\neq z_{\\rm{to}}

This model assumes that the transmitted power of each transmission line is only
constrained by the transmission capacity between two zones as follows:

.. math::

    {\\rm{import}}_{h,m,y,z_{\\rm{from}},z_{\\rm{to}}}\\le
    {\\rm{cap}}_{y,z_{\\rm{from}},z_{\\rm{to}}}^{\\rm{existingline}}
    \\times\\Delta h\\quad\\forall h,m,y,z_{\\rm{from}}\\neq z_{\\rm{to}}

    {\\rm{export}}_{h,m,y,z_{\\rm{from}},z_{\\rm{to}}} \\le
    {\\rm{cap}}_{y,z_{\\rm{from}},z_{\\rm{to}}}^{\\rm{existingline}}
    \\times\\Delta h\\quad\\forall h,m,y,z_{\\rm{from}}\\neq z_{\\rm{to}}
"""

import pyoptinterface as poi

class AddTransmissionConstraints:
    """Add constraints for transmission lines while considering multiple 
    zones. 
    """
    def __init__(self, model : object) -> None:
        """Initialize the class and add constraints.
        
        Parameters
        ----------
        model : object
            Model object depending on the solver.
        """
        self.model = model
        # Pre-compute fast lookups from the table-format candidates df
        # (cols: zone1, zone2, year, unit, capacity_min, capacity_max).
        cand = model.params['transmission_candidates']
        self._cand_min = {
            (r.zone1, r.zone2, r.year): r.capacity_min for _, r in cand.iterrows()
        }
        self._cand_max = {
            (r.zone1, r.zone2, r.year): r.capacity_max for _, r in cand.iterrows()
        }
        model.cap_lines_existing = poi.make_tupledict(
            model.year, model.zone, model.zone,
            rule=self.trans_capacity_rule
        )
        model.trans_import = poi.make_tupledict(
            model.hour, model.month, model.year, model.zone, model.zone,
            rule=self.trans_balance_rule
        )
        model.trans_physical_cons = poi.make_tupledict(
            model.year, model.zone, model.zone,
            rule=self.trans_physical_rule
        )
        model.new_line_up_bound_cons = poi.make_tupledict(
            model.year, model.zone, model.zone,
            rule=self.new_line_up_bound_rule
        )
        model.new_line_low_bound_cons = poi.make_tupledict(
            model.year, model.zone, model.zone,
            rule=self.new_line_low_bound_rule
        )
        model.trans_up_bound_cons = poi.make_tupledict(
            model.hour, model.month, model.year, model.zone, model.zone,
            rule=self.trans_up_bound_rule
        )

    def trans_physical_rule(
        self, y : int, z : str, z1 : str
    ) -> poi.ConstraintIndex:
        """Physical transmission lines.

        Parameters
        ----------
        y : int
            Year.
        z : str
            Zone.
        z1 : str
            Zone.

        Returns
        -------
        poi.ConstraintIndex
            The constraint of the model.
        """
        model = self.model
        if z != z1:
            lhs = model.cap_newline[y, z, z1] - model.cap_newline[y, z1, z]
            return model.add_linear_constraint(lhs, poi.Eq, 0)


    def trans_capacity_rule(
        self, y : int, z : str, z1 : str
    ) -> poi.ExprBuilder:
        """Transmission capacity equal to the sum of the existing capacity 
        and the new capacity in previous planned years.

        Parameters
        ----------
        y : int
            Year.
        z : str
            Zone.
        z1 : str
            Zone.

        Returns
        -------
        poi.ExprBuilder
            The expression of the model.
        """
        model = self.model
        year = model.params['year']
        lifetime = model.params['transmission_line_lifetime']
        existing = model.params['transmission_existing']
        # Sum over (zone1, zone2, commission_year) entries that are
        # still in service in year y: cy <= y < cy + lifetime[z, z1].
        # transmission_line_lifetime has not been changed in this
        # release; it remains keyed by (zone1, zone2).
        lt = lifetime.get((z, z1), 0)
        remaining_capacity_line = sum(
            cap for (zz1, zz2, cy), cap in existing.items()
            if zz1 == z and zz2 == z1 and cy <= y < cy + lt
        )
        cap_lines_existing = poi.ExprBuilder()
        new_capacity_line = poi.quicksum(
            model.cap_newline[yy, z, z1] for yy in year[:year.index(y) + 1]
        )
        cap_lines_existing += new_capacity_line
        cap_lines_existing += remaining_capacity_line
        return cap_lines_existing

    def new_line_up_bound_rule(
        self, y : int, z : str, z1 : str
    ) -> poi.ConstraintIndex:
        """Upper bound on new transmission capacity built in (y, z, z1).

        Default for missing (z, z1, y) is 0 -- the candidates table is
        the canonical list of buildable line-year combinations.
        """
        model = self.model
        ub = self._cand_max.get((z, z1, y), 0)
        if ub == float('inf'):
            return None
        lhs = model.cap_newline[y, z, z1] - ub
        return model.add_linear_constraint(lhs, poi.Leq, 0)

    def new_line_low_bound_rule(
        self, y : int, z : str, z1 : str
    ) -> poi.ConstraintIndex:
        """Lower bound on new transmission capacity built in (y, z, z1).
        Default 0; redundant with the variable's lb=0 unless the user
        sets a positive minimum.
        """
        model = self.model
        lb = self._cand_min.get((z, z1, y), 0)
        if lb == 0:
            return None
        lhs = model.cap_newline[y, z, z1] - lb
        return model.add_linear_constraint(lhs, poi.Geq, 0)

    def trans_balance_rule(
        self, h : int, m : int, y : int, z : str, z1 : str
    ) -> poi.ConstraintIndex:
        """Transmission balance, i.e., the electricity imported from zone z1 
        to zone z should be equal to the electricity exported from zone z 
        to zone z1 multiplied by the transmission line efficiency.

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
        z1 : str
            Zone.

        Returns
        -------
        poi.ConstraintIndex
            The constraint of the model.
        """
        model = self.model
        eff = model.params['transmission_line_efficiency'][z, z1]
        return eff * model.trans_export[h, m, y, z, z1]

    def trans_up_bound_rule(
        self, h : int, m : int, y : int, z : str, z1 : str
    ) -> poi.ConstraintIndex:
        """Transmitted power is less than or equal to the transmission line 
        capacity.

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
        z1 : str
            Zone.

        Returns
        -------
        poi.ConstraintIndex
            The constraint of the model.
        """
        model = self.model
        lhs = model.trans_export[h, m, y, z, z1]                              \
            - model.cap_lines_existing[y, z, z1]
        return model.add_linear_constraint(lhs, poi.Leq, 0)
