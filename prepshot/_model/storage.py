#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""This module contains energy storage related functions. Symmetrical energy 
storage system is considered in this module. It means that the energy storage
system has the same power capacity for charging and discharging.

Similar to the power discharging process, the charging power of storage
technology :math:`e` (:math:`{\\rm{power}}_{h,m,y,z,e}^{{c}}`) is also limited
by the existing installed capacity and technical minimum charging power
(:math:`{\\underline{{\\rm{POWER}}}}_{h,m,y,z,e}^{{c}}`) as follows:

.. math::

    {\\underline{{\\rm{POWER}}}}_{h,m,y,z,e}^{{c}}\\times
    {\\rm{cap}}_{y,z,e}^{\\rm{existingtech}}\\le{\\rm{power}}_{h,m,y,z,e}^{{c}}
    \\le {\\rm{cap}}_{y,z,e}^{\\rm{existingtech}}\\quad\\forall h,m,y,z,e
    \\in {\\mathcal{STOR}}

The charging generation (:math:`{\\rm{charge}}_{h,m,y,z,e}`) and
:math:`{\\rm{power}}_{h,m,y,z,e}^{c}` need to meet the following formula:

.. math::
    
    {\\rm{charge}}_{h,m,y,z,e}={\\rm{power}}_{h,m,y,z,e}^{\\rm{c}}\\times
    \\Delta h{\\times\\eta}_{y,e}^{{\\rm{in}}}
    \\quad\\forall h,m,y,z,e\\in {\\mathcal{STOR}}

Changes in stored electricity
(:math:`{\\rm{storage}}_{h,m,y,z,e}^{\\rm{energy}}`) in two successive periods
should be balanced by the charging (:math:`{\\rm{charge}}_{h,m,y,z,e}`) and
discharging (:math:`{\\rm{gen}}_{h,m,y,z,e}`) processes:

.. math::
    
    {\\rm{storage}}_{h,m,y,z,e}^{\\rm{energy}}-
    {\\rm{storage}}_{h-1,m,y,z,e}^{\\rm{energy}}
    ={\\rm{charge}}_{h,m,y,z,e}-{\\rm{gen}}_{h,m,y,z,e}

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
        model.energy_storage_balance_cons = poi.make_tupledict(
            model.hour, model.month, model.year, model.zone,
            model.storage_tech, rule=self.energy_storage_balance_rule
        )
        model.init_energy_storage_cons = poi.make_tupledict(
            model.month, model.year, model.zone,
            model.storage_tech, rule=self.init_energy_storage_rule
        )
        model.end_energy_storage_cons = poi.make_tupledict(
            model.month, model.year, model.zone, model.storage_tech,
            rule=self.end_energy_storage_rule
        )
        model.energy_storage_up_bound_cons = poi.make_tupledict(
            model.hour, model.month, model.year, model.zone,
            model.storage_tech, rule=self.energy_storage_up_bound_rule
        )
        model.energy_storage_gen_cons = poi.make_tupledict(
            model.hour, model.month, model.year, model.zone,
            model.storage_tech, rule=self.energy_storage_gen_rule
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
        epr = model.params['energy_to_power_ratio'][te]
        dt = model.params['dt']
        lhs = (
            model.storage[0, m, y, z, te]
            - esl * model.cap_existing[y, z, te] * epr * dt
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
        h_init = model.params['hour'][-1]
        lhs = (
            model.storage[h_init, m, y, z, te]
            - model.storage[0, m, y, z, te]
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
        dt = model.params['dt']
        lhs = (
            model.storage[h, m, y, z, te]
            - model.cap_existing[y, z, te] * epr * dt
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
