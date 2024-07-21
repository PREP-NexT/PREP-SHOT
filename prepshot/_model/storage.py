#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""This module contains energy storage related functions. Symmetrical energy 
storage system is considered in this module. It means that the energy storage
system has the same power capacity for charging and discharging.
"""

from typing import Union

import pyoptinterface as poi

class AddStorageConstraints:
    """Energy storage class.
    """
    def __init__(self,
        model : Union[
            poi._src.highs.Model,
            poi._src.gurobi.Model,
            poi._src.mosek.Model,
            poi._src.copt.Model
        ]
    ) -> None:
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

    def energy_storage_balance_rule(self,
        h : int, m : int, y : int, z : str, te : str
    ) -> poi._src.core_ext.ConstraintIndex:
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
        pyoptinterface._src.core_ext.ConstraintIndex
            Constraint index of the model.
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

    def init_energy_storage_rule(self,
        m : int, y : int, z : str, te : str
    ) -> poi._src.core_ext.ConstraintIndex:
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
        pyoptinterface._src.core_ext.ConstraintIndex
            Constraint index of the model.
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

    def end_energy_storage_rule(self,
        m : int, y : int, z : str, te : str
    ) -> poi._src.core_ext.ConstraintIndex:
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
        pyoptinterface._src.core_ext.ConstraintIndex
            Constraint index of the model.
        """
        model = self.model
        h_init = model.params['hour'][-1]
        lhs = (
            model.storage[h_init, m, y, z, te]
            - model.storage[0, m, y, z, te]
        )
        return model.add_linear_constraint(lhs, poi.Eq, 0)

    def energy_storage_up_bound_rule(self,
        h : int, m : int, y : int, z : str, te : str
    ) -> poi._src.core_ext.ConstraintIndex:
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
        pyoptinterface._src.core_ext.ConstraintIndex
            Constraint index of the model.
        """
        model = self.model
        epr = model.params['energy_to_power_ratio'][te]
        dt = model.params['dt']
        lhs = (
            model.storage[h, m, y, z, te]
            - model.cap_existing[y, z, te] * epr * dt
        )
        return model.add_linear_constraint(lhs, poi.Leq, 0)

    def energy_storage_gen_rule(self,
        h : int, m : int, y : int, z : str, te : str
    ) -> poi._src.core_ext.ConstraintIndex:
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
        pyoptinterface._src.core_ext.ConstraintIndex
            Constraint index of the model.
        """
        model = self.model
        de = model.params['discharge_efficiency'][te, y]
        lhs = model.gen[h, m, y, z, te] / de                                  \
            - model.storage[h-1, m, y, z, te]
        return model.add_linear_constraint(lhs, poi.Leq, 0)
