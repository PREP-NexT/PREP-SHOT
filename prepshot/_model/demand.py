#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""This module contains constraints related to demand. The model computes
the power balance for each hour, in each time period, for each year,
and in each zone, as follows:

.. math::

    {{\\rm{DEMAND}}}_{h,m,y,z}\\times\\Delta h = \\sum_{z_{\\rm{from}}\\in 
    {\\mathcal{Z}}\\backslash{\\{z\\}}}{{\\rm{import}}_{h,m,y,z_{\\rm{from}},z}} 
    - \\sum_{z_{\\rm{to}}\\in {\\mathcal{Z}}\\backslash{\\{z\\}}}
    {{\\rm{export}}_{h,m,y,z,z_{\\rm{to}}}}

    + \\sum_{e\\in {\\mathcal{E}}}{{\\rm{gen}}_{h,m,y,z,e}} 
    - \\sum_{e\in {\\mathcal{STOR}}}{{\\rm{charge}}_{h,m,y,z,e}}
    \\quad\\forall h,m,y,z

"""

import pyoptinterface as poi

class AddDemandConstraints:
    """This class contains demand constraints.
    """
    def __init__(self, model : object) -> None:
        """Initialize the class and add constraints.
        
        Parameters
        ----------
        model : object
            Model object depending on the solver.
        """
        self.model = model
        model.power_balance_cons = poi.make_tupledict(
            model.hour, model.month, model.year, model.zone,
            rule=self.power_balance_rule
        )
    def power_balance_rule(
        self, h : int, m : int, y : int, z : str
    ) -> poi.ConstraintIndex:
        """Nodal power balance. The total electricity demand for each time 
        period and in each zone should be met by the following.
        
        1. The sum of imported power energy from other zones.
        2. The generation from zone z minus the sum of exported power 
           energy from zone z to other zones.
        3. The charging power energy of storage technologies in zone z.  

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
        
        Returns
        -------
        poi.ConstraintIndex
            The constraint of the model.
        """
        model = self.model
        load = model.params['demand']
        dt = model.params['dt']
        # Sum only over real neighbours (lines that actually exist),
        # not the full zone set. On Thai PCM 472 buses this changes
        # 472 terms per bus into ~3 terms per bus.
        imp_z = poi.quicksum(
            model.trans_import[h, m, y, z1, z]
            for z1 in model.in_neighbours.get(z, [])
        )
        exp_z = poi.quicksum(
            model.trans_export[h, m, y, z, z1]
            for z1 in model.out_neighbours.get(z, [])
        )
        # Sum only over (z, te) pairs that actually have a gen variable
        # (sparse creation in model.py). For dense models this is
        # identical to ``for te in model.tech``.
        gen_z = poi.quicksum(
            model.gen[h, m, y, z, te]
            for te in model.zone_techs.get(z, [])
        )
        # storage_tech intersected with techs deployed at z.
        storage_set = set(model.storage_tech)
        charge_z = poi.quicksum(
            model.charge[h, m, y, z, te]
            for te in model.zone_techs.get(z, [])
            if te in storage_set
        )
        # demand[z, y, m, h] is in MW (instantaneous power, PyPSA-style);
        # multiply by dt to get MWh per timestep -- matching gen and
        # charge which are already in MWh per timestep.
        demand_z = load[z, y, m, h] * dt
        # Optional load-shedding slack: when on, allow up to
        # ``demand`` MWh of unserved load at the VOLL penalty added
        # to the objective in cost.py. The slack absorbs windows that
        # would otherwise be infeasible (e.g. cascaded-hydro at a
        # PCM boundary) and surfaces (hour, zone) reliability gaps.
        if hasattr(model, 'lns'):
            demand_z = demand_z - model.lns[h, m, y, z]
        lhs = demand_z - (imp_z - exp_z + gen_z - charge_z)
        return model.add_linear_constraint(lhs, poi.Eq, 0)
 