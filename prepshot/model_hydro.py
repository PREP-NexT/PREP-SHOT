from pyomo.environ import *

def create_hydro_model(para):
    model = ConcreteModel(name='SHOT')

    # Sets
    model.year = Set(initialize=para['year_sets'], ordered=True, doc='Set of planned timesteps')
    model.zone = Set(initialize=para['zone_sets'], ordered=True, doc='Set of zones')
    model.hour = Set(initialize=para['hour_sets'], ordered=True, doc='Set of operation timesteps')
    model.hour_p = Set(initialize=[0]+para['hour_sets'], ordered=True,
                       doc='Set of operation timesteps')
    model.month = Set(initialize=para['month_sets'], ordered=True, doc='Set of plnning timesteps')

    model.hour_month_year_zone_tuples = model.hour * model.month *  model.year * model.zone

    # hydropower output
    model.gen = Var(model.hour_month_year_zone_tuples, within=NonNegativeReals,
                    doc='Output of hydropower, each zone and each time period [MW]')
    model.delta = Var(model.hour_month_year_zone_tuples, within=NonNegativeReals,
                    doc='Anomaly output of hydropower, each zone and each time period [MW]')

    ################################# objective funtion: Minimize the output anomaly ###################################
    def peak_shaving_rule(model):
        return sum([(para['demand'][z, y, m, h] - model.gen[h, m, y, z])*(para['demand'][z, y, m, h] - model.gen[h, m, y, z]) for h, m, y, z in model.hour_month_year_zone_tuples])
        # return sum([model.delta[h, m, y, z] * model.delta[h, m, y, z] for h, m, y, z in model.hour_month_year_zone_tuples])
        # return sum([model.delta[h, m, y, z] * model.delta[h, m, y, z] for h, m, y, z in model.hour_month_year_zone_tuples])
        # upper_bound = {"Hainan":4199,"Guangdong":98574,"Guangxi":19438,"Yunnan":19709,"Guizhou":19429}
        # return sum([model.gen[h, m, y, z] * para['demand'][z, y, m, h]/upper_bound[z] for h, m, y, z in model.hour_month_year_zone_tuples])

    model.total_delta = Objective(rule = peak_shaving_rule, sense = minimize, doc = 'Minimize the anomaly')

    # def anomaly1_rule(model, h, m, y, z):
    #     return model.delta[h, m, y, z] >= para['demand'][z, y, m, h] - model.gen[h, m, y, z]
    # def anomaly2_rule(model, h, m, y, z):
    #     return model.delta[h, m, y, z] >= model.gen[h, m, y, z] - para['demand'][z, y, m, h]

    # model.anomaly1_cons = Constraint(model.hour_month_year_zone_tuples,
    #                                             rule=anomaly1_rule,
    #                                             doc='anomaly output limits')
    # model.anomaly2_cons = Constraint(model.hour_month_year_zone_tuples,
    #                                             rule=anomaly2_rule,
    #                                             doc='anomaly output limits')
    model = add_hydro(model, para)
    return model

def add_hydro(model, para):

    Hour = para['hour_sets']
    Hour_period = [0] + Hour  # storage

    model.station = Set(initialize=para['stcd_sets'], ordered=True, doc='Set of hydropower plants')

    model.station_month_year_tuples = model.station * model.month * model.year
    model.station_hour_p_month_year_tuples = model.station * model.hour_p * model.month * model.year

    model.station_hour_month_year_tuples = model.station * model.hour * model.month * model.year 
    model.head_para = Param(model.station_hour_month_year_tuples, mutable=True)

    ################################## hydropower operation start #########################
    # Hydropower plant variables
    model.naturalinflow = Var(model.station_hour_month_year_tuples, within=Reals,
                              doc='natural inflow of reservoir [m3/s]')
    model.inflow = Var(model.station_hour_month_year_tuples, within=Reals, doc='inflow of reservoir [m3/s]')
    model.outflow = Var(model.station_hour_month_year_tuples, within=NonNegativeReals, doc='inflow of reservoir [m3/s]')
    model.genflow = Var(model.station_hour_month_year_tuples, within=NonNegativeReals,
                        doc='generation flow of reservoir [m3/s]')
    model.spillflow = Var(model.station_hour_month_year_tuples, within=NonNegativeReals,
                          doc='water spillage flow of reservoir [m3/s]')
    model.withdraw = Var(model.station_hour_month_year_tuples, within=NonNegativeReals,
            doc = 'withdraw from reservoir [m^3/s]')

    model.storage_hydro = Var(model.station_hour_p_month_year_tuples, within=NonNegativeReals,
                              doc='storage of reservoir [10^8 m3]')
    model.output = Var(model.station_hour_month_year_tuples, within=NonNegativeReals,
                       doc='output of reservoir [MW]')

    ################################# Hydropower output ###################################
    def natural_inflow_rule(model, s, h, m, y):
        return model.naturalinflow[s, h, m, y] == para['inflow'][s, m, h]

    def total_inflow_rule(model, s, h, m, y):
        up_stream_outflow = 0
        for ups, delay in zip(para['connect'][para['connect']['NEXTPOWER_ID'] == s].POWER_ID, para['connect'][para['connect']['NEXTPOWER_ID']==s].delay):
            delay = int(int(delay)/para['dt'])
            if (h - delay >= Hour[0]):
                up_stream_outflow += model.outflow[ups, h-delay, m, y]
            else:
                # It is assumed to dispatch periodically every day to maintain water balance
                # up_stream_outflow += 0
                up_stream_outflow += model.outflow[ups, Hour[-1] - delay + h, m, y]
                
        return model.inflow[s, h, m, y] == model.naturalinflow[s, h, m, y] + up_stream_outflow

    def water_balance_rule(model, s, h, m, y):
        return model.storage_hydro[s, h, m, y] == model.storage_hydro[s, h-1, m, y] +  (model.inflow[s, h, m, y]-
                model.outflow[s, h, m, y] - model.withdraw[s, h, m, y])*3600*para['dt']*1e-8

    def discharge_rule(model, s, h, m, y):
        return model.outflow[s, h, m, y] == model.genflow[s, h, m, y] + model.spillflow[s, h, m, y]

    def outflow_low_bound_rule(model, s, h, m, y):
        return model.outflow[s, h, m, y] >= para['static']['outflow_min', s]

    def outflow_up_bound_rule(model, s, h, m, y):
        return model.outflow[s, h, m, y] <= para['static']['outflow_max', s]

    def storage_low_bound_rule(model, s, h, m, y):
        return model.storage_hydro[s, h, m, y] >= para['storagedown'][s, m, h]

    def storage_up_bound_rule(model, s, h, m, y):
        return model.storage_hydro[s, h, m, y] <= para['storageup'][s, m, h]

    def output_low_bound_rule(model, s, h, m, y):
        return model.output[s, h, m, y] >= para['static']['N_min', s]

    def output_up_bound_rule(model, s, h, m, y):
        return model.output[s, h, m, y] <= para['static']['N_max', s]

    def output_calc_rule(model, s, h, m, y):
        return model.output[s, h, m, y] == para['static']['coeff', s] * model.genflow[s, h, m, y] * model.head_para[s, h, m, y] * 1e-3

    model.natural_inflow_cons = Constraint(model.station_hour_month_year_tuples,
                                                rule=natural_inflow_rule,
                                                doc='Natural flow')
    model.total_inflow_cons = Constraint(model.station_hour_month_year_tuples,
                                                rule=total_inflow_rule,
                                                doc='Hydraulic Connection Constraints')
    model.water_balance_cons = Constraint(model.station_hour_month_year_tuples,
                                                rule=water_balance_rule,
                                                doc='Water Balance Constraints')
    model.discharge_cons = Constraint(model.station_hour_month_year_tuples,
                                                rule=discharge_rule,
                                                doc='Discharge Constraints')
    model.outflow_low_bound_cons = Constraint(model.station_hour_month_year_tuples,
                                                rule=outflow_low_bound_rule,
                                                doc='Discharge lower limits')
    model.outflow_up_bound_cons = Constraint(model.station_hour_month_year_tuples,
                                                rule=outflow_up_bound_rule,
                                                doc='Discharge upper limits')
    model.storage_low_bound_cons = Constraint(model.station_hour_month_year_tuples,
                                                rule=storage_low_bound_rule,
                                                doc='Storage lower limits')
    model.storage_up_bound_cons = Constraint(model.station_hour_month_year_tuples,
                                                rule=storage_up_bound_rule,
                                                doc='Storage upper limits')
    model.output_low_bound_cons = Constraint(model.station_hour_month_year_tuples,
                                                rule=output_low_bound_rule,
                                                doc='Power Output lower limits')
    model.output_up_bound_cons = Constraint(model.station_hour_month_year_tuples,
                                                rule=output_up_bound_rule,
                                                doc='Power Output upper limits')
    model.output_calc_cons = Constraint(model.station_hour_month_year_tuples,
                                                rule=output_calc_rule,
                                                doc='Power Output Constraints')

    def init_storage_rule(model, s, m, y):
        return model.storage_hydro[s, Hour_period[0], m, y] == para['storageinit'][m,s]

    def end_storage_rule(model, s, m, y):
        return model.storage_hydro[s, Hour_period[-1], m, y] == para['storageend'][m,s]

    model.init_storage_cons = Constraint(model.station_month_year_tuples,
                                                rule=init_storage_rule,
                                                doc='Initial storage Constraints')
    model.end_storage_cons = Constraint(model.station_month_year_tuples,
                                                rule=end_storage_rule,
                                                doc='Terminal storage Constraints')
    # model.income_cons = Constraint(expr=model.income==sum([model.withdraw[s, h, m]*3600*para['dt']*para['price'] 
                                                        #    for s,h,m,y in model.station_hour_month_year_tuples]))
    # hydropower not curtailment
    def hydro_output_rule(model, h, m, y, z):
        hydro_output = 0
        for s in model.station:
            if para['static']['zone',s] == z:
                hydro_output += model.output[s, h, m, y] #* para['dt']
        return model.gen[h, m, y, z] == hydro_output

    model.hydro_output_cons = Constraint(model.hour_month_year_zone_tuples,
                                                rule=hydro_output_rule,
                                                doc='define hydropower output')
    
    return model