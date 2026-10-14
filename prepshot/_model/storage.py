#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""This module contains energy storage related functions. Symmetrical energy 
storage system is considered in this module. It means that the energy storage
system has the same power capacity for charging and discharging.

Similar to the power discharging process, the charging energy drawn from
the grid by storage technology :math:`e` in each time step
(:math:`{\\rm{charge}}_{h,m,y,z,e}`) is limited by the existing installed
capacity:

.. math::

    {\\rm{charge}}_{h,m,y,z,e}\\le
    {\\rm{cap}}_{y,z,e}^{\\rm{existingtech}}\\times\\Delta h
    \\quad\\forall h,m,y,z,e\\in {\\mathcal{STOR}}

Changes in stored electricity
(:math:`{\\rm{storage}}_{h,m,y,z,e}^{\\rm{energy}}`) in two successive periods
should be balanced by the charging (:math:`{\\rm{charge}}_{h,m,y,z,e}`) and
discharging (:math:`{\\rm{gen}}_{h,m,y,z,e}`) processes. Both are measured on
the grid side, so the charging efficiency (:math:`\\eta_{y,e}^{\\rm{in}}`) and
discharging efficiency (:math:`\\eta_{y,e}^{\\rm{out}}`) enter the balance:

.. math::
    
    {\\rm{storage}}_{h,m,y,z,e}^{\\rm{energy}}-
    {\\rm{storage}}_{h-1,m,y,z,e}^{\\rm{energy}}
    ={\\rm{charge}}_{h,m,y,z,e}\\times\\eta_{y,e}^{\\rm{in}}
    -{\\rm{gen}}_{h,m,y,z,e}/\\eta_{y,e}^{\\rm{out}}

The energy discharged in a time step cannot exceed the energy stored at the
end of the previous one:

.. math::

    {\\rm{gen}}_{h,m,y,z,e}/\\eta_{y,e}^{\\rm{out}}\\le
    {\\rm{storage}}_{h-1,m,y,z,e}^{\\rm{energy}}
    \\quad\\forall h,m,y,z,e\\in {\\mathcal{STOR}}

In addition, the initial (when :math:`h=h_{\rm{start}}`) stored electricity
(:math:`{\\rm{storage}}_{h=h_{\\rm{start}},m,y,z,e}^{\\rm{energy}}`) of
storage technology :math:`e` in each month of each year can be calculated
based on the proportion of the maximum storage capacity, as follows:

.. math::

    {\\rm{storage}}_{h=h_{\\rm{start}},m,y,z,e}^{\\rm{energy}}
    ={{\\rm{STORAGE}}}_{m,y,z,e}^{\\rm{energy}}\\times{{\\rm{EP}}}_e\\times
    {\\rm{cap}}_{y,z,e}^{\\rm{existingtech}}\\quad\\forall m,y,z,e\\in
    {\\mathcal{STOR}}

The instantaneous storage energy level
(:math:`{\\rm{storage}}_{h,m,y,z,e}^{\\rm{energy}}`) of storage technology
:math:`e` should not exceed the maximum energy storage capacity, as follows:

.. math::

    {\\rm{storage}}_{h,m,y,z,e}^{\\rm{energy}}\\le{{\\rm{EP}}}_e\\times
    {\\rm{cap}}_{y,z,e}^{\\rm{existingtech}}
    \\quad\\forall h,m,y,z,e\\in {\\mathcal{STOR}}
"""

from typing import Union

import pyoptinterface as poi

from prepshot.utils import sparse_tupledict

class AddStorageConstraints:
    """Energy storage class.
    """
    def __init__(self, model : object) -> None:
        """Initialize the class and add constraints.
        
        Parameters
        ----------
        model : object
            Model object depending on the solver.
        """
        self.model = model
        # Iterate sparsely over (z, te) pairs in ``model.active_zt_storage``.
        # Matches the sparse creation of ``model.storage`` / ``model.gen`` /
        # ``model.charge`` in model.py: a storage tech that is not
        # deployed (nor buildable) in a zone has no variables there, so
        # a dense zone x storage_tech product would KeyError.
        active_myzte_storage = [
            (m, y, z, te)
            for m in model.month
            for y in model.year
            for (z, te) in model.active_zt_storage
        ]
        model.energy_storage_balance_cons = sparse_tupledict(
            model.active_hmyzte_storage, self.energy_storage_balance_rule
        )
        model.init_energy_storage_cons = sparse_tupledict(
            active_myzte_storage, self.init_energy_storage_rule
        )
        model.end_energy_storage_cons = sparse_tupledict(
            active_myzte_storage, self.end_energy_storage_rule
        )
        model.energy_storage_up_bound_cons = sparse_tupledict(
            model.active_hmyzte_storage, self.energy_storage_up_bound_rule
        )
        model.energy_storage_gen_cons = sparse_tupledict(
            model.active_hmyzte_storage, self.energy_storage_gen_rule
        )
        model.charge_up_bound_cons = sparse_tupledict(
            model.active_hmyzte_storage, self.charge_up_bound_rule
        )

    def energy_storage_balance_rule(
        self, h : int, m : int, y : int, z : str, te : str
    ) -> poi.ConstraintIndex:
        """Energy storage balance.

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
        te : str
            Technology.
            
        Returns
        -------
        poi.ConstraintIndex
            The constraint of the model.
        """
        model = self.model
        de = model.params['discharge_efficiency'][te, y]
        ce = model.params['charge_efficiency'][te, y]
        return model.add_linear_constraint(
            model.storage[h, m, y, z, te] - (
                model.storage[h-1, m, y, z, te]
                - model.gen[h, m, y, z, te] / de
                + model.charge[h, m, y, z, te] * ce
            ),
            poi.Eq,
            0
        )

    def init_energy_storage_rule(
        self, m : int, y : int, z : str, te : str
    ) -> poi.ConstraintIndex:
        """Initial energy storage.

        Parameters
        ----------
        m : int
            Month.
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
        esl = model.params['initial_energy_storage_level'][te, z]
        # Energy-to-power ratio is in hours (MWh per MW), so the energy
        # capacity cap * epr does not depend on the time step length.
        epr = model.params['energy_to_power_ratio'][te]
        # storage[hour_p[0], ...] is the prior-hour anchor: hour 0 in
        # CEM mode (where model.hour starts at 1), or h_first - 1 in a
        # PCM rolling-horizon window.
        lhs = (
            model.storage[model.hour_p[0], m, y, z, te]
            - esl * model.cap_existing[y, z, te] * epr
        )
        return model.add_linear_constraint(lhs, poi.Eq, 0)

    def end_energy_storage_rule(
        self, m : int, y : int, z : str, te : str
    ) -> poi.ConstraintIndex:
        """End energy storage.

        Parameters
        ----------
        m : int
            Month.
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
        # PCM windows want SOC to flow into the next window, so skip
        # the cyclical close-the-loop equality. Storage upper / lower
        # bounds keep the trajectory inside [0, cap].
        if model.params.get('skip_end_storage', False):
            return None
        h_init = model.params['hour'][-1]
        lhs = (
            model.storage[h_init, m, y, z, te]
            - model.storage[model.hour_p[0], m, y, z, te]
        )
        return model.add_linear_constraint(lhs, poi.Eq, 0)

    def energy_storage_up_bound_rule(
        self, h : int, m : int, y : int, z : str, te : str
    ) -> poi.ConstraintIndex:
        """Energy storage upper bound.

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
        te : str
            Technology.

        Returns
        -------
        poi.ConstraintIndex
            The constraint of the model.
        """
        model = self.model
        epr = model.params['energy_to_power_ratio'][te]
        lhs = (
            model.storage[h, m, y, z, te]
            - model.cap_existing[y, z, te] * epr
        )
        return model.add_linear_constraint(lhs, poi.Leq, 0)

    def charge_up_bound_rule(
        self, h : int, m : int, y : int, z : str, te : str
    ) -> poi.ConstraintIndex:
        """charge[h,m,y,z,te] <= cap_existing * dt.

        Symmetric to gen_up_bound_rule on the discharge side. Bounds
        grid-side charging energy per timestep by the installed power
        capacity (storage is assumed symmetric: same power rating for
        charge and discharge, per the module docstring). Without this
        rule, charge is implicitly capped only by the SOC ceiling --
        letting a 1 MW / 10 MWh battery draw 10 MW for one hour.
        """
        model = self.model
        lhs = (
            model.charge[h, m, y, z, te]
            - model.cap_existing[y, z, te] * model.params['dt']
        )
        return model.add_linear_constraint(lhs, poi.Leq, 0)

    def energy_storage_gen_rule(
        self, h : int, m : int, y : int, z : str, te : str
    ) -> poi.ConstraintIndex:
        """Energy storage generation.

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
        te : str
            Technology.
            
        Returns
        -------
        poi.ConstraintIndex
            The constraint of the model.
        """
        model = self.model
        de = model.params['discharge_efficiency'][te, y]
        lhs = model.gen[h, m, y, z, te] / de                                  \
            - model.storage[h-1, m, y, z, te]
        return model.add_linear_constraint(lhs, poi.Leq, 0)
