#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""This module is used to determine investment-related constraints. 
The model computes the retirement of each technology and transmission line
with these considerations:

* The historical capacity of the technology and transmission line is
  based on its capacity ratio.
* Each planning and scheduling period is based on the existing capacity.

The existing capacity for each year, in each zone, for each technology,
is as follows:

.. math::
    
    {\\rm{cap}}_{y,z,e}^{\\rm{existingtech}}=
    \\sum_{{\\rm{age}}=1}^{{{T}}_e
    -(y-y_{\\rm{start}})}{{\\rm{CAP}}}_{{\\rm{age}},z,e}^{\\rm{inittech}}
    +\\sum_{y_{\\rm{pre}}={\\max}(y_{\\rm{start}}, y-{{T}}_e)}^{y}
    {{\\rm{cap}}_{y_{\\rm{pre}},z,e}^{\\rm{invtech}}}\\quad\\forall y,z,e

The existing capacity of the transmission lines for each year,
from :math:`z_{\\rm{from}}` zone to :math:`z_{\\rm{to}}`-th zone, is as
follows:

.. math::

    {\\rm{cap}}_{y,z_{\\rm{from}},z_{\\rm{to}}}^{\\rm{existingline}}=
    \\sum_{{\\rm{age}}=1}^{{T}_{\\rm{line}}
    -(y-y_{\\rm{start}})}{{\\rm{CAP}}}_{{\\rm{age}},z_{\\rm{from}},
    z_{\\rm{to}}}^{\\rm{initline}}
    +\\sum_{y_{\\rm{pre}}={\\max}(y_{\\rm{start}}, y-{{T}}_{\\rm{line}})}^{y}
    {{\\rm{cap}}_{y_{\\rm{pre}},
    z_{\\rm{from}},z_{\\rm{to}}}^{\\rm{invline}}}\\quad\\forall
    y,z_{\\rm{from}}\\neq z_{\\rm{to}}
"""

from typing import Union

import numpy as np
import pyoptinterface as poi

class AddInvestmentConstraints:
    """Add constraints for investment in the model.
    """
    def __init__(self, model : object) -> None:
        """Initialize the class and add constraints.
        
        Parameters
        ----------
        model : object
            Model object depending on the solver.
        """
        self.model = model
        model.remaining_technology = poi.make_tupledict(
            model.year, model.zone, model.tech,
            rule=self.tech_lifetime_rule
        )
        model.cap_existing = poi.make_tupledict(
            model.year, model.zone, model.tech,
            rule=self.remaining_capacity_rule
        )
        model.tech_up_bound_cons = poi.make_tupledict(
            model.year, model.zone, model.tech,
            rule=self.tech_up_bound_rule
        )
        model.new_tech_up_bound_cons = poi.make_tupledict(
            model.year, model.zone, model.tech,
            rule=self.new_tech_up_bound_rule
        )
        model.new_tech_low_bound_cons = poi.make_tupledict(
            model.year, model.zone, model.tech,
            rule=self.new_tech_low_bound_rule
        )

    def tech_up_bound_rule(
        self, y : int, z : str, te : str
    ) -> poi.ConstraintIndex:
        """Allowed capacity of commercial operation technology is less than or 
        equal to the predefined upper bound.

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
        poi.ConstraintIndex
            The constraint of the model.
        """
        model = self.model
        tub =  model.params['technology_upper_bound'][te, z]
        if tub != np.Inf:
            lhs = model.cap_existing[y, z, te] - tub
            return model.add_linear_constraint(lhs, poi.Leq, 0)
        return None

    def new_tech_up_bound_rule(
        self, y : int, z : str, te : str
    ) -> poi.ConstraintIndex:
        """New investment technology upper bound in specific year and zone.

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
        poi.ConstraintIndex
            The constraint of the model.
        """
        model = self.model
        ntub = model.params['new_technology_upper_bound'][te, z]
        if ntub != np.Inf:
            lhs = model.cap_newtech[y, z, te] - ntub
            return model.add_linear_constraint(lhs, poi.Leq, 0)
        return None

    def new_tech_low_bound_rule(
        self, y : int, z : str, te : str
    ) -> poi.ConstraintIndex:
        """New investment technology lower bound.

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
        poi.ConstraintIndex
            The constraint of the model.
        """
        model = self.model
        ntlb = model.params['new_technology_lower_bound'][te, z]
        lhs = model.cap_newtech[y, z, te] - ntlb
        return model.add_linear_constraint(lhs, poi.Geq, 0)

    def tech_lifetime_rule(
        self, y : int, z : str, te : str
    ) -> poi.ConstraintIndex:
        """Caculation of remaining technology capacity based on lifetime 
        constraints.

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
            The expression of the model.
        """
        model = self.model
        lifetime = model.params['lifetime'][te, y]
        service_time = y - model.params['year'][0]
        hcap = model.params['historical_capacity']
        remaining_time = int(lifetime - service_time)
        if remaining_time <= 0:
            return 0
        return poi.quicksum(hcap[z, te, a] for a in range(0, remaining_time))

    def remaining_capacity_rule(
        self, y : int, z : str, te : str
    ) -> poi.ExprBuilder:
        """Remaining capacity of initial technology due to lifetime 
        restrictions. Where in modeled year y, the available technology
        consists of the following.
        
        1. The remaining in-service installed capacity from the initial 
           technology.
        2. The remaining in-service installed capacity from newly built 
           technology in the previous modelled years.

        Parameters
        ----------
        y : int
            Planned year.
        z : str
            Zone.
        te : str
            technology.

        Returns
        -------
        poi.ExprBuilder
            The expression of the model.
        """
        model = self.model
        year = model.params['year']
        lt = model.params['lifetime']
        cap_existing = poi.ExprBuilder()
        new_tech = poi.quicksum(
            model.cap_newtech[yy, z, te]
            for yy in year[:year.index(y) + 1]
            if y - yy < lt[te, y]
        )
        cap_existing += new_tech
        cap_existing += model.remaining_technology[y, z, te]
        return cap_existing
