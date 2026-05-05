#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""This module contains functions related to hydropower technologies.

1. Water balance of reservoirs.

Similar to the storage technologies, changes in reservoir storage
(:math:`{\\rm{storage}}_{s,h,m,y}^{\\rm{reservoir}}`) in two successive periods
should be balanced by total inflow
(:math:`{\\rm{inflow}}_{s,h,m,y}^{\\rm{total}}`) and total outflow
(:math:`{\\rm{outflow}}_{s,h,m,y}^{\\rm{total}}`):

.. math::
    
    {\\rm{storage}}_{s,h,m,y}^{\\rm{reservoir}}-
    {\\rm{storage}}_{s,h-1,m,y}^{\\rm{reservoir}}=
    \\Delta h\\times3600\\times\\left({\\rm{inflow}}_{s,h,m,y}^{\\rm{total}}
    -{\\rm{outflow}}_{s,h,m,y}^{\\rm{total}}\\right)\\quad\\forall s,h,m,y

Here :math:`{\\rm{inflow}}_{s,h,m,y}^{\\rm{total}}` consists of two parts:
the total outflow received from all immediate upstream reservoirs
(:math:`\\sum_{{\\rm{su}}\\in{\\mathcal{IU}}_s}{{\\rm{outflow}}_
{{\\rm{su}},h-\\tau_{{\\rm{su}},s},m,y}^{\\rm{total}}}`)
and the net inflow (also called incremental inflow) of the drainage area
controlled by this hydropower reservoir
(:math:`{{\\rm{INFLOW}}}_{s,h,m,y}^{\\rm{net}}`),
which can be expressed as follows:

.. math::
    
    {\\rm{inflow}}_{s,h,m,y}^{\\rm{total}}
    ={{\\rm{INFLOW}}}_{s,h,m,y}^{\\rm{net}}+\\sum_{{\\rm{su}}\\in
    {\\mathcal{IU}}_s}{{\\rm{outflow}}_{{\\rm{su}},h-
    \\tau_{{\\rm{su}},s},m,y}^{\\rm{total}}}\\quad\\forall s,h,m,y

Note that PREP-SHOT assumes a constant water travel (or propagation) time
(:math:`{\\tau}_{{\\rm{su}},s}`). The total outflow of each reservoir consists
of three parts: upstream water withdrawal (i.e., water used for non-hydro
purposes such as agriculture irrigation and urban water supply)
(:math:`{\\rm{outflow}}_{s,h,m,y}^{\\rm{withdraw}}`), generation flow
(i.e., water flow through the turbines of the hydropower plant)
(:math:`{\\rm{outflow}}_{s,h,m,y}^{\\rm{gen}}`) and spillage flow
(i.e., water spilled over the spillways)
(:math:`{\\rm{outflow}}_{s,h,m,y}^{\\rm{spillage}}`):

.. math::
    
    {\\rm{outflow}}_{s,h,m,y}^{\\rm{total}}
    ={\\rm{outflow}}_{s,h,m,y}^{\\rm{withdraw}}
    +{\\rm{outflow}}_{s,h,m,y}^{\\rm{gen}}
    +{\\rm{outflow}}_{s,h,m,y}^{\\rm{spillage}}\\quad\\forall s,h,m,y

2. Reservoir outflow

The generation flow and spillage flow of the reservoir are limited by the
maximum outflow capacity of turbines (:math:`{\\rm{OUTFLOW}}_s^{\\rm{gen}}`)
and spillway (:math:`{\\rm{OUTFLOW}}_s^{\\rm{spillage}}`), respectively.
The sum of these two parts also needs to meet the minimum outflow required
(:math:`{{\\rm{OUTFLOW}}}_s`) for other purposes
(e.g., ecological flow, shipping flow). These constraints are summarized as:

.. math::
    
    {\\rm{outflow}}_{s,h,m,y}^{\\rm{gen}}\\le{\\rm{OUTFLOW}}_s^{\\rm{gen}}
    \\quad\\forall s,h,m,y
    
    {\\rm{outflow}}_{s,h,m,y}^{\\rm{spillage}}\\le
    {\\rm{OUTFLOW}}_s^{\\rm{spillage}}\\quad\\forall s,h,m,y

    {{\\rm{OUTFLOW}}}_s\\le {\\rm{outflow}}_{s,h,m,y}^{\\rm{gen}}
    +{\\rm{outflow}}_{s,h,m,y}^{\\rm{spillage}}\\quad\\forall s,h,m,y

3. Reservoir storage

The initial (when :math:`h=h_{\\rm{start}}`) and terminal
(when :math:`h=h_{\\rm{end}}`) storage
(:math:`{\\rm{storage}}_{s,h=h_{\\rm{start}},m,y}^{\\rm{reservoir}}`
and :math:`{\\rm{storage}}_{s,h=h_{\\rm{end}},m,y}^{\\rm{reservoir}}`)
of hydropower reservoir in each month of each year should be assigned as:

.. math::

    {\\rm{storage}}_{s,h=h_{\\rm{start}},m,y}^{\\rm{reservoir}}
    ={{\\rm{STORAGE}}}_{s,m,y}^{\\rm{initreservoir}}\\quad\\forall s,m,y

    {\\rm{storage}}_{s,h=h_{\\rm{end}},m,y}^{\\rm{reservoir}}
    ={{\\rm{STORAGE}}}_{s,m,y}^{\\rm{endreservoir}}\\quad\\forall s,m,y

The reservoir storage is bounded between the maximum
(:math:`{\\overline{{\\rm{STORAGE}}}}_s^{\\rm{reservoir}}`) and minimum storage
(:math:`{\\underline{{\\rm{STORAGE}}}}_s^{\\rm{reservoir}}`) depending on the
functions (e.g., flood control, recreation, and water supply) of the reservoir:

.. math::
    
    {\\underline{{\\rm{STORAGE}}}}_s^{\\rm{reservoir}}\\le
    {\\rm{storage}}_{s,h,m,y}^{\\rm{reservoir}}\\le
    {\\overline{{\\rm{STORAGE}}}}_s^{\\rm{reservoir}}\\quad\\forall s,h,m,y
"""
import pyoptinterface as poi

class AddHydropowerConstraints:
    """Class for hydropower constraints and calculations.
    """
    def __init__(self, model : object) -> None:
        """Initialize the class. Here I define the variables needed and the 
        constraints for the hydropower model.

        Parameters
        ----------
        model : object
            Model container which is a dict-like objective and includes
            parameters, variables and constraints.
        """
        self.model = model
        self.is_inflow = model.params['isinflow']
        techs_df = model.params['technologies']
        self.hydro_type = techs_df.loc[
            techs_df['carrier'] == 'hydro', 'tech'
        ].tolist()
        # `main_hydro` was the old single aggregate-Hydro tech name.
        # As of v1.8.0 each hydro plant is its own tech; `main_hydro`
        # remains as a non-empty/None flag for callers checking
        # "any hydro present at all".
        self.main_hydro = self.hydro_type[0] if self.hydro_type else None
        if self.is_inflow:
            # Pre-computed dict for lookup efficiency
            # Replaces repetitive DataFrame queries with direct memory access
            self.wdt_dict = {
                k: v[['upstream_tech', 'delay']].values
                for k, v in model.params['water_delay_time'].groupby('downstream_tech')
            }
            self.station_zone = {
                s: model.params['reservoir_zone'][s]
                for s in model.station
            }
            self.efficiency_cache = {
                s: model.params['reservoir_coefficient'][s]
                for s in model.station
            }
            self.min_outflow_cache = {
                s: model.params['reservoir_outflow_min'][s]
                for s in model.station
            }
            self.max_outflow_cache = {
                s: model.params['reservoir_outflow_max'][s]
                for s in model.station
            }
            self.max_genflow_cache = {
                s: model.params['reservoir_generation_flow_max'][s]
                for s in model.station
            }
            self.min_capacity_cache = {
                s: model.params['reservoir_capacity_min'][s]
                for s in model.station
            }
            self.max_capacity_cache = {
                s: model.params['reservoir_capacity_max'][s]
                for s in model.station
            }
            # Define variables and constraints
            model.outflow = poi.make_tupledict(
                model.station, model.hour, model.month, model.year,
                rule=self.outflow_rule
            )
            model.inflow = poi.make_tupledict(
                model.station, model.hour, model.month, model.year,
                rule=self.inflow_rule
            )
            model.water_balance_cons = poi.make_tupledict(
                model.station, model.hour, model.month, model.year,
                rule=self.water_balance_rule
            )
            model.init_storage_cons = poi.make_tupledict(
                model.station, model.month, model.year,
                rule=self.init_storage_rule
            )
            model.end_storage_cons = poi.make_tupledict(
                model.station, model.month, model.year,
                rule=self.end_storage_rule
            )
            model.output_calc_cons = poi.make_tupledict(
                model.station, model.hour, model.month, model.year,
                rule=self.output_calc_rule
            )
            model.outflow_low_bound_cons = poi.make_tupledict(
                model.station, model.hour, model.month, model.year,
                rule=self.outflow_low_bound_rule
            )
            model.outflow_up_bound_cons = poi.make_tupledict(
                model.station, model.hour, model.month, model.year,
                rule=self.outflow_up_bound_rule
            )
            model.genflow_up_bound_cons = poi.make_tupledict(
                model.station, model.hour, model.month, model.year,
                rule=self.genflow_up_bound_rule
            )
            model.storage_low_bound_cons = poi.make_tupledict(
                model.station, model.hour, model.month, model.year,
                rule=self.storage_low_bound_rule
            )
            model.storage_up_bound_cons = poi.make_tupledict(
                model.station, model.hour, model.month, model.year,
                rule=self.storage_up_bound_rule
            )
            model.output_low_bound_cons = poi.make_tupledict(
                model.station, model.hour, model.month, model.year,
                rule=self.output_low_bound_rule
            )
            model.output_up_bound_cons = poi.make_tupledict(
                model.station, model.hour, model.month, model.year,
                rule=self.output_up_bound_rule
            )
        # One constraint per hydro station (now a first-class tech),
        # binding its gen variable to either water-flow output (when
        # isinflow=True) or the must-run profile (when isinflow=False).
        # gen[*, *, y, z, te] is automatically zero in zones != te's
        # home zone because cap_existing[y, z, te] = 0 there.
        model.hydro_output_cons = poi.make_tupledict(
            self.hydro_type, model.hour, model.month, model.year,
            rule=self.hydro_output_rule
        )

    def inflow_rule(
        self, s : str, h : int, m : int, y : int
    ) -> poi.ExprBuilder:
        """Define hydrolic connnect between cascade reservoirs, total inflow of 
        downsteam reservoir = natural inflow + upstream outflow from upsteam
        reservoir(s).

        Parameters
        ----------
        s : str
            hydropower plant.
        h : int
            Hour.
        m : int
            Month.
        y : int
            Year.
            
        Returns
        -------
        poi.ExprBuilder
            Total inflow of reservoir.
        """
        model = self.model
        hour = model.params['hour']
        up_streams = self.wdt_dict.get(s, [])
        dt = model.params['dt']
        up_stream_outflow = poi.ExprBuilder()
        # Assume the delay time is a constant by default. Other routing methods
        # can be implemented here such as Muskingum method, piecewise linear
        # routing method, etc.
        # When the delayed hour falls before the modelled period, wrap
        # cyclically into [hour[0], hour[-1]]. The modular form below
        # works for any window starting at hour[0] >= 1 (CEM uses
        # hour=[1..N] so it lands at N; PCM rolling windows wrap into
        # the same window -- approximate, but the alternative is a
        # cross-window state variable which Phase A doesn't model).
        period_len = hour[-1] - hour[0] + 1
        for ups, delay in up_streams:
            delay = int(int(delay) / dt)
            offset = (h - delay - hour[0]) % period_len
            t = hour[0] + offset
            up_stream_outflow += model.outflow[ups, t, m, y]
        return up_stream_outflow + model.params['inflow'][s, y, m, h]

    def outflow_rule(
        self, s : str, h : int, m : int, y : int
    ) -> poi.ExprBuilder:
        """Total outflow of reservoir is equal to the sum of generation and 
        spillage.

        Parameters
        ----------
        s : str
            hydropower plant.
        h : int
            Hour.
        m : int
            Month.
        y : int
            Year.
            
        Returns
        -------
        poi.ExprBuilder
            Total outflow of reservoir.
        """
        model = self.model
        return model.genflow[s, h, m, y] + model.spillflow[s, h, m, y]

    def water_balance_rule(
        self, s : str, h : int, m : int, y : int
    ) -> poi.ConstraintIndex:
        """Water balance of reservoir, i.e., storage[t] = storage[t-1] + 
        net_storage[t].

        Parameters
        ----------
        s : str
            hydropower plant.
        h : int
            Hour.
        m : int
            Month.
        y : int
            Year.
            
        Returns
        -------
        poi.ConstraintIndex
            The constraint of the model.
        """
        model = self.model
        lhs = poi.ExprBuilder()
        lhs += 3600 * model.params['dt'] * (
            model.inflow[s, h, m, y]
            - model.outflow[s, h, m, y]
            - model.withdraw[s, h, m, y]
        ) # netstorage
        lhs += model.storage_reservoir[s, h-1, m, y]
        lhs -= model.storage_reservoir[s, h, m, y]
        return model.add_linear_constraint(lhs, poi.Eq, 0, name=f'water_balance_{s}_{y}_{m}_{h}')

    def init_storage_rule(
        self, s : str, m : int, y : int
    ) -> poi.ConstraintIndex:
        """Determine storage of reservoir in the initial hour of each month.

        Parameters
        ----------
        s : str
            hydropower plant.
        m : int
            Month.
        y : int
            Year.
            
        Returns
        -------
        poi.ConstraintIndex
            The constraint of the model.
        """
        model = self.model
        hour_period = model.hour_p
        init_storage = model.params['initial_reservoir_storage_level'][s]
        lhs = model.storage_reservoir[s, hour_period[0], m, y] - init_storage
        return model.add_linear_constraint(lhs, poi.Eq, 0)

    def end_storage_rule(
        self, s : str, m : int, y : int
    ) -> poi.ConstraintIndex:
        """Determine storage of reservoir in the terminal hour of each month.

        For PCM rolling-horizon windows, the end of one window flows
        into the start of the next, so we skip the terminal-storage
        equality (params['skip_end_storage'] = True). The storage
        upper / lower bounds still apply, so the trajectory stays
        within [storage_min, storage_max].

        Parameters
        ----------
        s : str
            hydropower plant.
        m : int
            Month.
        y : int
            Year.

        Returns
        -------
        poi.ConstraintIndex
            The constraint of the model, or ``None`` when skipped.
        """
        model = self.model
        if model.params.get('skip_end_storage', False):
            return None
        hour_period = model.hour_p
        final_storage = model.params['final_reservoir_storage_level'][s]
        lhs = model.storage_reservoir[s, hour_period[-1], m, y] - final_storage
        return model.add_linear_constraint(lhs, poi.Eq, 0)

    def outflow_low_bound_rule(
        self, s : str, h : int, m : int, y : int
    ) -> poi.ConstraintIndex:
        """Lower bound of total outflow.

        Parameters
        ----------
        s : str
            hydropower plant.
        h : int
            Hour.
        m : int
            Month.
        y : int
            Year.
            
        Returns
        -------
        poi.ConstraintIndex
            The constraint of the model.
        """
        model = self.model
        min_outflow = self.min_outflow_cache[s]
        lhs = model.outflow[s, h, m, y] - min_outflow
        return model.add_linear_constraint(lhs, poi.Geq, 0)

    def outflow_up_bound_rule(
        self, s : str, h : int, m : int, y : int
    ) -> poi.ConstraintIndex:
        """Upper bound of total outflow.
        
        Parameters
        ----------
        s : str
            hydropower plant.
        h : int
            Hour.
        m : int
            Month.
        y : int
            Year.
            
        Returns
        -------
        poi.ConstraintIndex
            The constraint of the model.
        """
        model = self.model
        max_outflow = self.max_outflow_cache[s]
        lhs = model.outflow[s, h, m, y] - max_outflow
        return model.add_linear_constraint(lhs, poi.Leq, 0)

    def genflow_up_bound_rule(
        self, s : str, h : int, m : int, y : int
    ) -> poi.ConstraintIndex:
        """Upper bound of generation flow.
        
        Parameters
        ----------
        s : str
            hydropower plant.
        h : int
            Hour.
        m : int
            Month.
        y : int
            Year.
            
        Returns
        -------
        poi.ConstraintIndex
            The constraint of the model. 
        """
        model = self.model
        max_genflow = self.max_genflow_cache[s]
        lhs = model.genflow[s, h, m, y] - max_genflow
        return model.add_linear_constraint(lhs, poi.Leq, 0)

    def storage_low_bound_rule(
        self, s : str, h : int, m : int, y : int
    ) -> poi.ConstraintIndex:
        """Lower bound of reservoir storage.
        
        Parameters
        ----------
        s : str
            hydropower plant.
        h : int
            Hour.
        m : int
            Month.
        y : int
            Year.
        
        Returns
        -------
        poi.ConstraintIndex
            The constraint of the model.
        """
        model = self.model
        min_storage = model.params['reservoir_storage_min'][s, m, h]
        lhs = model.storage_reservoir[s, h, m, y] - min_storage
        return model.add_linear_constraint(lhs, poi.Geq, 0)

    def storage_up_bound_rule(
        self, s : str, h : int, m : int, y : int
    ) -> poi.ConstraintIndex:
        """Upper bound of reservoir storage.

        Parameters
        ----------
        s : str
            hydropower plant.
        h : int
            Hour.
        m : int
            Month.
        y : int
            Year.
            
        Returns
        -------
        poi.ConstraintIndex
            The constraint of the model.
        """
        model = self.model
        max_storage = model.params['reservoir_storage_max'][s, m, h]
        lhs = model.storage_reservoir[s, h, m, y] - max_storage
        return model.add_linear_constraint(lhs, poi.Leq, 0)

    def output_low_bound_rule(
        self, s : str, h : int, m : int, y : int
    ) -> poi.ConstraintIndex:
        """Lower bound of hydropower output.

        Parameters
        ----------
        s : str
            hydropower plant.
        h : int
            Hour.
        m : int
            Month.
        y : int
            Year.
            
        Returns
        -------
        poi.ConstraintIndex
            The constraint of the model.
        """
        model = self.model
        min_output = self.min_capacity_cache[s]
        lhs = model.output[s, h, m, y] - min_output
        return model.add_linear_constraint(lhs, poi.Geq, 0)

    def output_up_bound_rule(
        self, s : str, h : int, m : int, y : int
    ) -> poi.ConstraintIndex:
        """Upper bound of hydropower output.

        Parameters
        ----------
        s : str
            hydropower plant.
        h : int
            Hour.
        m : int
            Month.
        y : int
            Year.
            
        Returns
        -------
        poi.ConstraintIndex
            The constraint of the model.
        """
        model = self.model
        max_output = self.max_capacity_cache[s]
        lhs = model.output[s, h, m, y] - max_output
        return model.add_linear_constraint(lhs, poi.Leq, 0)

    def output_calc_rule(
        self, s : str, h : int, m : int, y :int
    ) -> poi.ConstraintIndex:
        """Hydropower production calculation. Head parameter is specified after
        building the model.

        Parameters
        ----------
        s : str
            hydropower plant.
        h : int
            Hour.
        m : int
            Month.
        y : int
            Year.
            
        Returns
        -------
        poi.ConstraintIndex
            The constraint of the model.
        """
        model = self.model
        efficiency = self.efficiency_cache[s]
        lhs = (
            model.output[s, h, m, y]
            - model.genflow[s, h, m, y] * efficiency * 1e-3 #  * head_param
        )
        return model.add_linear_constraint(lhs, poi.Eq, 0)

    def hydro_output_rule(
        self, te : str, h : int, m : int, y : int
    ) -> poi.ConstraintIndex:
        """Bind the generation variable for a hydro plant to its
        physical output (when isinflow=True) or to its must-run profile
        (when isinflow=False).

        Parameters
        ----------
        te : str
            Hydro plant tech name.
        h : int
            Hour.
        m : int
            Month.
        y : int
            Year.

        Returns
        -------
        poi.ConstraintIndex
            The constraint of the model.
        """
        if not self.hydro_type:
            return None
        model = self.model
        dt = model.params['dt']

        if self.is_inflow:
            # Bind plant gen to its physical water-flow output.
            z = self.station_zone[te]
            lhs = (
                model.output[te, h, m, y] * dt - model.gen[h, m, y, z, te]
            )
            return model.add_linear_constraint(
                lhs, poi.Eq, 0, name=f'Hydro_output_{y}_{m}_{h}_{te}'
            )

        # isinflow=False: hydro plants act like dispatchable techs --
        # their generation is bounded only by the unified
        # gen_up_bound / gen_low_bound (cap * p_max_pu / cap * p_min_pu).
        # To force a fixed must-run profile, set
        # tech_min_gen_profile = tech_max_gen_profile for the plant.
        return None
