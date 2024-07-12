#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""This module contains functions related to hydropower technologies. 
"""

import pyoptinterface as poi

class AddHydropowerConstraints:
    """Class for hydropower constraints and calculations.
    """
    def __init__(self, model):
        """Initialize the class. Here I define the variables needed and the 
        constraints for the hydropower model.

        Parameters
        ----------
        model : pyoptinterface._src.solver.Model
            Model container which is a dict-like objective and includes
            parameters, variables and constraints.
        """
        self.model = model
        if model.params['isinflow']:
            self.define_variable()
            model.outflow = poi.make_tupledict(
                model.station_hour_month_year_tuples,
                rule=self.outflow_rule
            )
            model.inflow = poi.make_tupledict(
                model.station_hour_month_year_tuples,
                rule=self.inflow_rule
            )
            model.water_balance_cons = poi.make_tupledict(
                model.station_hour_month_year_tuples,
                rule=self.water_balance_rule
            )
            model.init_storage_cons = poi.make_tupledict(
                model.station_month_year_tuples,
                rule=self.init_storage_rule
            )
            model.end_storage_cons = poi.make_tupledict(
                model.station_month_year_tuples,
                rule=self.end_storage_rule
            )
            model.output_calc_cons = poi.make_tupledict(
                model.station_hour_month_year_tuples,
                rule=self.output_calc_rule
            )
            model.outflow_low_bound_cons = poi.make_tupledict(
                model.station_hour_month_year_tuples,
                rule=self.outflow_low_bound_rule
            )
            model.outflow_up_bound_cons = poi.make_tupledict(
                model.station_hour_month_year_tuples,
                rule=self.outflow_up_bound_rule
            )
            model.storage_low_bound_cons = poi.make_tupledict(
                model.station_hour_month_year_tuples,
                rule=self.storage_low_bound_rule
            )
            model.storage_up_bound_cons = poi.make_tupledict(
                model.station_hour_month_year_tuples,
                rule=self.storage_up_bound_rule
            )
            model.output_low_bound_cons = poi.make_tupledict(
                model.station_hour_month_year_tuples,
                rule=self.output_low_bound_rule
            )
            model.output_up_bound_cons = poi.make_tupledict(
                model.station_hour_month_year_tuples,
                rule=self.output_up_bound_rule
            )
        model.hydro_output_cons = poi.make_tupledict(
            model.hour_month_year_zone_tuples,
            rule=self.hydro_output_rule
        )

    def define_variable(self):
        """Define variables for hydropower production constraints. 
        """
        model = self.model 
        model.genflow = model.add_variables(
            model.station_hour_month_year_tuples, lb=0
        )
        model.spillflow = model.add_variables(
            model.station_hour_month_year_tuples, lb=0
        )
        model.withdraw = model.add_variables(
            model.station_hour_month_year_tuples, lb=0
        )
        model.storage_reservoir = model.add_variables(
            model.station_hour_p_month_year_tuples, lb=0
        )
        model.output = model.add_variables(
            model.station_hour_month_year_tuples, lb=0
        )

    def inflow_rule(self, s, h, m, y):
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
        pyoptinterface._src.core_ext.ExprBuilder
            Total inflow of reservoir.
        """
        model = self.model
        hour = model.params['hour']
        wdt = model.params['water_delay_time']
        dt = model.params['dt']
        up_stream_outflow = poi.ExprBuilder()
        # Assume the delay time is a constant by default. Other routing methods
        # can be implemented here such as Muskingum method, piecewise linear
        # routing method, etc.
        for ups, delay in zip(
            wdt[wdt['NEXTPOWER_ID'] == s].POWER_ID,
            wdt[wdt['NEXTPOWER_ID'] == s].delay
        ):
            delay = int(int(delay)/dt)
            if (h - delay >= hour[0]):
                t = h - delay
            else:
                t = hour[-1] + h - delay
            up_stream_outflow += model.outflow[ups, t, m, y]
        return up_stream_outflow + model.params['inflow'][s, y, m, h]

    def outflow_rule(self, s, h, m, y):
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
        pyoptinterface._src.core_ext.ExprBuilder
            Total outflow of reservoir.
        """
        model = self.model
        return model.genflow[s, h, m, y] + model.spillflow[s, h, m, y]

    def water_balance_rule(self, s, h, m, y):
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
        pyoptinterface._src.core_ext.ConstraintIndex
            Constraint index of the model.
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
        return model.add_linear_constraint(lhs, poi.Eq, 0)

    def init_storage_rule(self, s, m, y):
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
        pyoptinterface._src.core_ext.ConstraintIndex
            Constraint index of the model.
        """
        model = self.model
        hour_period = model.hour_p
        init_storage = model.params['initial_reservoir_storage_level'][m, s]
        lhs = model.storage_reservoir[s, hour_period[0], m, y] - init_storage
        return model.add_linear_constraint(lhs, poi.Eq, 0)

    def end_storage_rule(self, s, m, y):
        """Determine storage of reservoir in the terminal hour of each month.

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
        pyoptinterface._src.core_ext.ConstraintIndex
            Constraint index of the model.
        """
        model = self.model
        hour_period = model.hour_p
        final_storage = model.params['final_reservoir_storage_level'][m, s]
        lhs = model.storage_reservoir[s, hour_period[-1], m, y] - final_storage
        return model.add_linear_constraint(lhs, poi.Eq, 0)

    def outflow_low_bound_rule(self, s, h, m, y):
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
        pyoptinterface._src.core_ext.ConstraintIndex
            Constraint index of the model.
        """
        model = self.model
        min_outflow = model.params['reservoir_characteristics']['outflow_min', s]
        lhs = model.outflow[s, h, m, y] - min_outflow
        return model.add_linear_constraint(lhs, poi.Geq, 0)

    def outflow_up_bound_rule(self, s, h, m, y):
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
        pyoptinterface._src.core_ext.ConstraintIndex
            Constraint index of the model.
        """
        model = self.model
        max_outflow = model.params['reservoir_characteristics']['outflow_max', s]
        lhs = model.outflow[s, h, m, y] - max_outflow
        return model.add_linear_constraint(lhs, poi.Leq, 0)

    def storage_low_bound_rule(self, s, h, m, y):
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
        pyoptinterface._src.core_ext.ConstraintIndex
            Constraint index of the model.
        """
        model = self.model
        min_storage = model.params['reservoir_storage_lower_bound'][s, m, h]
        lhs = model.storage_reservoir[s, h, m, y] - min_storage
        return model.add_linear_constraint(lhs, poi.Geq, 0)

    def storage_up_bound_rule(self, s, h, m, y):
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
        pyoptinterface._src.core_ext.ConstraintIndex
            Constraint index of the model.
        """
        model = self.model
        max_storage = model.params['reservoir_storage_upper_bound'][s, m, h]
        lhs = model.storage_reservoir[s, h, m, y] - max_storage
        return model.add_linear_constraint(lhs, poi.Leq, 0)

    def output_low_bound_rule(self, s, h, m, y):
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
        pyoptinterface._src.core_ext.ConstraintIndex
            Constraint index of the model.
        """
        model = self.model
        min_output = model.params['reservoir_characteristics']['N_min', s]
        lhs = model.output[s, h, m, y] - min_output
        return model.add_linear_constraint(lhs, poi.Geq, 0)

    def output_up_bound_rule(self, s, h, m, y):
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
        pyoptinterface._src.core_ext.ConstraintIndex
            Constraint index of the model.
        """
        model = self.model
        max_output = model.params['reservoir_characteristics']['N_max', s]
        lhs = model.output[s, h, m, y] - max_output
        return model.add_linear_constraint(lhs, poi.Leq, 0)

    def output_calc_rule(self, s, h, m, y):
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
        pyoptinterface._src.core_ext.ConstraintIndex
            Constraint index of the model.
        """
        model = self.model
        efficiency = model.params['reservoir_characteristics']['coeff', s]
        lhs = (
            model.output[s, h, m, y]
            - model.genflow[s, h, m, y] * efficiency * 1e-3 #  * head_param
        )
        return model.add_linear_constraint(lhs, poi.Eq, 0)

    def hydro_output_rule(self, h, m, y, z):
        """Hydropower output of all hydropower plants across each zone.

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
        pyoptinterface._src.core_ext.ConstraintIndex
            Constraint index of the model.
        """
        model = self.model
        tech_type = model.params['technology_type']
        res_char = model.params['reservoir_characteristics']
        dt = model.params['dt']
        predifined_hydro = model.params['predefined_hydropower']
        hydro_type = [i for i, j in tech_type.items() if j == 'hydro']
        if len(hydro_type) == 0:
            return None
        if model.params['isinflow']:
            hydro_output = poi.quicksum(
                model.output[s, h, m, y] * model.params['dt']
                for s in model.station if res_char['zone', s] == z
            )
            lhs = hydro_output
            lhs -= model.gen[h, m, y, z, hydro_type[0]]
        else:
            lhs = (model.gen[h, m, y, z, hydro_type[0]]
                - predifined_hydro['Hydro', z, y, m, h] * dt
            )
        return model.add_linear_constraint(lhs, poi.Eq, 0)
