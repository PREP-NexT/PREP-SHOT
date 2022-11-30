from pyomo.environ import *
import numpy as np

def create_model(para):
    """ Create a pyomo ConcreateModel object according to the given data.    
    """
    model = ConcreteModel(name='PREP-SHOT')
    # Define dual problem to extract the solution of dual problem.
    model.dual = Suffix(direction=Suffix.IMPORT)

    # Define sets
    model.year = Set(initialize=para['year_sets'], ordered=True, doc='Set of planned timesteps')
    model.zone = Set(initialize=para['zone_sets'], ordered=True, doc='Set of zones')
    model.tech = Set(initialize=para['tech_sets'], ordered=True, doc='Set of technologies')
    model.hour = Set(initialize=para['hour_sets'], ordered=True, doc='Set of operation timesteps')
    model.hour_p = Set(initialize=[0]+para['hour_sets'], ordered=True,
                       doc='Set of operation timesteps')
    model.month = Set(initialize=para['month_sets'], ordered=True, doc='Set of plnning timesteps')

    model.year_zone_tuples = model.year * model.zone
    model.year_tech_tuples = model.year * model.tech
    model.year_zone_tech_tuples = model.year * model.zone * model.tech
    # The existing capacity between two zones is set to empty (i.e., No value is filled in the Excel cell), 
    # which means that these two zones cannot have newly built transmission lines. 
    # If you want to enable two zones which do not have any existing transmission lines to be allowed to 
    # build new transmission lines in the planning horizon, you need to set their capacity as zero explicitly instead of empty.
    # Besides, single zone cannot have a new transmission line.
    model.year_zone_zone_tuples = Set(initialize=[(y, z, z1) for y in model.year for z in model.zone for z1 in model.zone  if (z != z1 and not np.isnan(para['transmission'][z,z1]))])
    model.hour_month_tech_tuples = model.hour * model.month * model.tech
    model.hour_month_year_zone_tech_tuples = model.hour * model.month * model.year * model.zone * model.tech
    model.hour_p_month_year_zone_tuples = model.hour_p * model.month * model.year * model.zone
    model.hour_month_year_zone_tuples = model.hour * model.month * model.year * model.zone
    model.hour_month_year_zone_zone_tuples = Set(initialize=[(h, m, y, z, z1)
    for h in model.hour for m in model.month for y, z, z1 in model.year_zone_zone_tuples])
    model.month_year_zone_tuples = model.month * model.year * model.zone
    model.hour_month_year_tuples = model.hour * model.month * model.year
    model.hour_p_month_year_zone_tech_tuples =  model.hour_p * model.month * model.year * model.zone * model.tech
    
    # Create sets by type of technology.
    if 'storage' in para['type'].values():
        model.storage_tech = Set(initialize=[i for i,j in para['type'].items() if j=='storage'], ordered=True, doc='Set of storage technology')
    else:
        model.storage_tech = 0

    if 'nondispatchable' in para['type'].values():
        model.nondispatchable_tech = Set(initialize=[i for i,j in para['type'].items() if j=='nondispatchable'], ordered=True, doc='Set of nondispatchable technology')
    else:
        model.nondispatchable_tech = 0
        
    if 'dispatchable' in para['type'].values():
        model.dispatchable_tech = Set(initialize=[i for i,j in para['type'].items() if j=='dispatchable'], ordered=True, doc='Set of dispatchable technology')
    else:
        model.dispatchable_tech = 0
        
    if 'hydro' in para['type'].values():
        model.hydro_tech = Set(initialize=[i for i,j in para['type'].items() if j=='hydro'], ordered=True, doc='Set of hydro technology')
    else:
        model.hydro_tech = 0
    
    model.hour_month_year_zone_storage_tuples = model.hour * model.month * model.year * model.zone * model.storage_tech
    model.month_year_zone_storage_tuples = model.month * model.year * model.zone * model.storage_tech
    model.hour_p_month_year_zone_storage_tuples = model.hour_p * model.month * model.year * model.zone * model.storage_tech

    model.hour_month_year_zone_nondispatchable_tuples = model.hour * model.month * model.year * model.zone * model.nondispatchable_tech

    # Define decision variables and intermediate variables.
    model.cost = Var(within=NonNegativeReals, doc='total cost of system [RMB]')
    model.cost_var = Var(within=NonNegativeReals, doc='Variable O&M costs [RMB]')
    model.cost_newtech = Var(within=NonNegativeReals, doc='Investment costs of new technology [RMB]')
    model.cost_fix = Var(within=NonNegativeReals, doc='Fixed O&M costs [RMB/MW/year]')
    model.cost_newline = Var(within=NonNegativeReals, doc='Investment costs of new transmission lines [RMB]')
    model.income = Var(within=NonNegativeReals, doc='total income of withdraw water [RMB]')

    model.cap_existing = Var(model.year_zone_tech_tuples,
                             within=NonNegativeReals, doc='Capacity of existing technology [MW]')
    model.cap_newtech = Var(model.year_zone_tech_tuples,
                            within=NonNegativeReals, doc='Capacity of newbuild technology [MW]')
    model.cap_newline = Var(model.year_zone_zone_tuples,
                            within=NonNegativeReals, doc='Capacity of new transmission lines [MW]')
    model.cap_lines_existing = Var(model.year_zone_zone_tuples,
                                   within=NonNegativeReals, doc='Capacity of existing transmission line [MW]')
    model.carbon = Var(model.year, within=NonNegativeReals,
                       doc='Total carbon dioxide emission in each years [tonne]')
    model.carbon_capacity = Var(model.year_zone_tuples, within=NonNegativeReals,
                                doc='Carbon dioxide emission in each year and each zone [tonne]')
    model.gen = Var(model.hour_month_year_zone_tech_tuples, within=NonNegativeReals,
                    doc='Output of each technology in each year, each zone and each time period [MWh]')
    model.storage = Var(model.hour_p_month_year_zone_tech_tuples, within=NonNegativeReals,
                        doc='Storage of energy technology in each year, each zone and each time period [MW]')
    model.charge = Var(model.hour_month_year_zone_tech_tuples, within=NonNegativeReals,
                       doc='Storage in each year, each zone and each time period [MWh]')
    model.trans_export = Var(model.hour_month_year_zone_zone_tuples,
                             within=NonNegativeReals,
                             doc='Transfer output from zone A to zone B (A is not \
                                 equals to B)in each year and each time period [MWh]')
    model.trans_import = Var(model.hour_month_year_zone_zone_tuples, within=NonNegativeReals,
                             doc='Transfer output from zone B to zone A (A is not equals to B) \
                                       in each year and each time period [MWh]')
    model.remaining_technology = Var(model.year_zone_tech_tuples, within=NonNegativeReals,
                                     doc='remaining technology [MW]')

    # Define objective funtion: Minimize total costs
    def cost_rule(model):
        return model.cost_var + model.cost_newtech + model.cost_fix + model.cost_newline - model.income

    model.total_cost = Objective(rule=cost_rule, sense=minimize, doc='Minimize the sum of all cost types)')

    # Define constraints
    def var_cost_rule(model):
        """ Return total fuel cost of technologies and variable 
        Operation and maintenance (O&M) cost of technologies and transmission lines.
        """
        var_OM_tech_cost = sum([para['varcost'][te,y] * model.gen[h, m, y, z, te] * para['dt'] * \
                                para['var_factor'][y]
                                for h, m, y, z, te in model.hour_month_year_zone_tech_tuples])/para['weight']
        fuel_cost = sum([para['fuelprice'][te,y] * model.gen[h, m, y, z, te] * para['dt'] * \
                         para['var_factor'][y]
                         for h, m, y, z, te in model.hour_month_year_zone_tech_tuples])/para['weight']
        var_OM_line_cost = 0.5 * sum([para['varcost_lines'][z, z1] * model.trans_export[h, m, y, z, z1] * 
                                      para['var_factor'][y]  
                                      for h, m, y, z, z1 in model.hour_month_year_zone_zone_tuples])/para['weight']
        return model.cost_var == var_OM_tech_cost + fuel_cost + var_OM_line_cost

    def newtech_cost_rule(model):
        """Return total investment cost of new technologies.
        """
        return model.cost_newtech == sum(para['invcost'][te, y] * model.cap_newtech[y, z, te] * \
                                         para['inv_factor'][te,y]
                                         for y, z, te in model.year_zone_tech_tuples)

    def newline_cost_rule(model):
        """Return total investment cost of new transmission lines.
        """
        return model.cost_newline == 0.5 * sum(para['invline'][z, z1] * model.cap_newline[y, z, z1] * \
                                               para['distance'][z, z1] * \
                                               para['trans_inv_factor'][y]
                                               for y, z, z1 in model.year_zone_zone_tuples)

    def fix_cost_rule(model):
        """Return fixed O&M cost of technologies and transmission lines.
        """
        fix_cost_tech = sum(para['fixcost'][te,y] * model.cap_existing[y, z, te]
                                     * para['fix_factor'][y]
                                     for y, z, te in model.year_zone_tech_tuples)
        fix_cost_line = 0.5 * sum(para['fixcost_lines'][z, z1] * model.cap_lines_existing[y, z, z1]
                  * para['fix_factor'][y]
                  for y, z1, z in model.year_zone_zone_tuples)
        return model.cost_fix == fix_cost_tech + fix_cost_line

    def remaining_capacity_rule(model, y, z, te):
        """Lifetime restrictions. 
        In modelled year y, the available technology consists of two parts: 
            1. the remaining in-service installed capacity from the initial technology and 
            2. the remaining in-service installed capacity from newly built technology in the previous modelled years. 
        """
        Year = para['year_sets']
        new_tech = sum([model.cap_newtech[yy, z, te] for yy in Year[:Year.index(y) + 1]
             if y - yy < para['lifetime'][te,y]])
        return model.cap_existing[y, z, te] == model.remaining_technology[y, z, te] + new_tech

    def emission_limit_rule(model, y):
        """Carbon emission restrictions.
        """
        # return sum(para['carbon'][te, y] * model.gen[h, m, y, z, te] * para['dt'] 
        #        for h, m, te in model.hour_month_tech_tuples 
        #        for z in model.zone) <= para['carbon_limit'][y]
        return model.carbon[y] <= para['carbon_limit'][y]

    def emission_calc_rule(model, y):
        return model.carbon[y] == sum(model.carbon_capacity[y, z] for z in model.zone)

    def emission_calc_by_zone_rule(model, y, z):
        return model.carbon_capacity[y, z] == sum(para['carbon'][te, y] *
                                                  model.gen[h, m, y, z, te] * para['dt']
                                                  for h, m, te in model.hour_month_tech_tuples)

    def power_balance_rule(model, h, m, y, z):
        """Power balance constraints. 
        Total electricity demand of each time period in each zone z should be met by 
            1. the sum of imported power energy from other zones and 
            2. generation from zone z minus 
            3. the sum of exported power energy from zone z to other zones and 
            4. the charging power energy of storage technologies in zone z.
        """
        imp_z = sum([model.trans_import[h, m, y, z1, z]  for z1 in model.zone if (z != z1 and not np.isnan(para['transmission'][z,z1]))])
        exp_z = sum([model.trans_export[h, m, y, z, z1]  for z1 in model.zone if (z != z1 and not np.isnan(para['transmission'][z,z1]))])
        gen_z = sum([model.gen[h, m, y, z, te] for te in model.tech])
        charge_z = sum([model.charge[h, m, y, z, te] for te in model.storage_tech])
        demand_z = para['demand'][z, y, m, h]
        return demand_z == imp_z - exp_z + gen_z - charge_z

    model.power_balance_cons = Constraint(model.hour_month_year_zone_tuples,
                                          rule=power_balance_rule,
                                          doc='Power balance')
    
    def trans_capacity_rule(model, y, z, z1):
        Year = para['year_sets']
        remaining_capacity_line = para['transmission'][z,z1]
        new_capacity_line = sum(model.cap_newline[yy, z, z1] for yy in Year[:Year.index(y) + 1])
        return model.cap_lines_existing[y, z, z1] == remaining_capacity_line + new_capacity_line

    model.trans_capacity_cons = Constraint(model.year_zone_zone_tuples,
                                           rule=trans_capacity_rule,
                                           doc='Trans capacity')
    def trans_physical_rule(model, y, z, z1):
        return model.cap_newline[y, z, z1] == model.cap_newline[y, z1, z]

    model.trans_physical_cons = Constraint(model.year_zone_zone_tuples,
                                           rule=trans_physical_rule,
                                           doc='Two-way trans capacity equals')
    def trans_balance_rule(model, h, m, y, z, z1):
        eff = para['trans_effi'][z, z1]
        return eff * model.trans_export[h, m, y, z, z1] == model.trans_import[h, m, y, z, z1]
    model.trans_balance_cons = Constraint(model.hour_month_year_zone_zone_tuples,
                                          rule=trans_balance_rule,
                                          doc='Trans balance')
    def trans_up_bound_rule(model, h, m, y, z, z1):
        """Transmission restrictions.
        """
        return model.trans_export[h, m, y, z, z1] <= model.cap_lines_existing[y, z, z1]
    model.trans_up_bound_cons = Constraint(model.hour_month_year_zone_zone_tuples,
                                           rule=trans_up_bound_rule,
                                           doc='Trans upper bound')
    
    def gen_up_bound_rule(model, h, m, y, z, te):
        """Maximum output constraint
        """
        return model.gen[h, m, y, z, te] <= model.cap_existing[y, z, te]
    model.gen_up_bound_cons = Constraint(model.hour_month_year_zone_tech_tuples,
                                         rule=gen_up_bound_rule,
                                         doc='Maximum output constraint')

    def tech_up_bound_rule(model, y, z, te):
        """ Upper bound of  investment capacity
        """
        if para['tech_upper'][te, z] == np.Inf:
            return Constraint.Skip
        else:
            return model.cap_existing[y, z, te] <= para['tech_upper'][te, z]
    def new_tech_up_bound_rule(model, y, z, te):
        if para['newtech_upper'][te, z] == np.Inf:
            return Constraint.Skip
        else:
            return model.cap_newtech[y, z, te] <= para['newtech_upper'][te, z]
    def new_tech_low_bound_rule(model, y, z, te):
        return model.cap_newtech[y, z, te] >= para['newtech_lower'][te, z]
    
    model.tech_up_bound_cons = Constraint(model.year_zone_tech_tuples,
                                          rule=tech_up_bound_rule,
                                          doc='technology upper bound')
    model.new_tech_up_bound_cons = Constraint(model.year_zone_tech_tuples,
                                              rule=new_tech_up_bound_rule,
                                              doc='new technology upper bound')
    model.new_tech_low_bound_cons = Constraint(model.year_zone_tech_tuples,
                                               rule=new_tech_low_bound_rule,
                                               doc='new technology lower bound')

    if model.nondispatchable_tech != 0:
        def renew_gen_rule(model, h, m, y, z, te):
            """Nondispatchable energy output
            """
            return model.gen[h, m, y, z, te] <= para['capacity_factor'][te, z, m, h] * model.cap_existing[y, z, te] * para['dt']
        model.renew_gen_cons = Constraint(model.hour_month_year_zone_nondispatchable_tuples,
                                                rule=renew_gen_rule,
                                                doc='define renewable output')
    
    def tech_lifetime_rule(model, y, z, te):
        """Lifetime.
        """
        lifetime = para['lifetime'][te,y]
        service_time = y - para['year_sets'][0]
        remaining_time = int(lifetime - service_time)
        if remaining_time <= 1:
            return model.remaining_technology[y, z, te] == 0
        else:
            return model.remaining_technology[y, z, te] == sum([para['age_'][z, te, a] for a in range(1,remaining_time)])
    model.tech_lifetime_cons = Constraint(model.year_zone_tech_tuples,
                                                rule=tech_lifetime_rule,
                                                doc='Remaining technology')

    if model.storage_tech != 0:
        def energy_storage_balance_rule(model, h, m, y, z, te):
            """Storage
            """
            return (model.storage[h, m, y, z, te] == model.storage[h-1, m, y, z, te] - 
                    model.gen[h, m, y, z, te] * para['efficiency-out'][te, y]*para['dt'] + 
                    model.charge[h, m, y, z, te] * para['efficiency-in'][te, y]*para['dt'])

        def init_energy_storage_rule(model, m, y, z, te):
            return (model.storage[0, m, y, z, te] == para['storage_level'][te, z] * 
                   model.cap_existing[y, z, te] * para['ep'][te])

        def end_energy_storage_rule(model, m, y, z, te):
            return model.storage[para['hour_sets'][-1], m, y, z, te] == model.storage[0, m, y, z, te]

        def energy_storage_up_bound_rule(model, h, m, y, z, te):
            return model.storage[h, m, y, z, te] <= model.cap_existing[y, z, te] *  para['ep'][te]

        def energy_storage_gen_rule(model, h, m, y, z, te):
            return model.gen[h, m, y, z, te] * para['efficiency-out'][te, y] * para['dt'] <= model.storage[h-1, m, y, z, te]

        model.energy_storage_balance_cons = Constraint(model.hour_month_year_zone_storage_tuples,
                                                    rule=energy_storage_balance_rule,
                                                    doc='Storage constraint')
        model.init_energy_storage_cons = Constraint(model.month_year_zone_storage_tuples,
                                                    rule=init_energy_storage_rule,
                                                    doc='Init Storage')
        model.end_energy_storage_cons = Constraint(model.month_year_zone_storage_tuples,
                                                    rule=end_energy_storage_rule,
                                                    doc='End storage == Init Storage')
        model.energy_storage_up_bound_cons = Constraint(model.hour_month_year_zone_storage_tuples,
                                                    rule=energy_storage_up_bound_rule,
                                                    doc='Storage bound')
        model.energy_storage_gen_cons = Constraint(model.hour_month_year_zone_storage_tuples,
                                                    rule=energy_storage_gen_rule,
                                                    doc='Storage bound')

    ##################################  Ramping ####################################
    def ramping_up_rule(model, h, m, y, z, te):
        if h > 1 and para['ramp_up'][te] * para['dt'] < 1:
            return model.gen[h, m, y, z, te] - model.gen[h-1, m, y, z, te] <= para['ramp_up'][te] * para['dt'] * model.cap_existing[y, z, te]
        else:
            return Constraint.Skip
    def ramping_down_rule(model, h, m, y, z, te):
        if h > 1 and para['ramp_down'][te] * para['dt'] < 1:
            return model.gen[h-1, m, y, z, te] - model.gen[h, m, y, z, te] <= para['ramp_down'][te] * para['dt'] * model.cap_existing[y, z, te]
        else:
            return Constraint.Skip
    model.ramping_up_cons = Constraint(model.hour_month_year_zone_tech_tuples,
                                                rule=ramping_up_rule,
                                                doc='Ramping up constraint')
    model.ramping_down_cons = Constraint(model.hour_month_year_zone_tech_tuples,
                                                rule=ramping_down_rule,
                                                doc='Ramping down constraint')

   #  add constarints
    model.cost_var_cons = Constraint(rule=var_cost_rule, doc='Variable O&M cost and fuel cost')
    model.newtech_cost_cons = Constraint(rule=newtech_cost_rule, doc='Investment costs of new technology')
    model.newline_cost_cons = Constraint(rule=newline_cost_rule,
                                         doc='Investment costs of new transmission lines')
    model.fix_cost_cons = Constraint(rule=fix_cost_rule,
                                     doc='Fix O&M costs of new transmission lines')
    model.remaining_capacity_cons = Constraint(model.year, model.zone, model.tech,
                                               rule=remaining_capacity_rule,
                                               doc='Capacity increasment of technology')
    model.emission_limit_cons = Constraint(model.year,
                                           rule=emission_limit_rule,
                                           doc='Carbon dioxide emission limit')
    model.emission_calc_cons = Constraint(model.year,
                                          rule=emission_calc_rule,
                                          doc='Carbon dioxide emission of each year')
    model.emission_calc_by_zone_cons = Constraint(model.year_zone_tuples,
                                                rule=emission_calc_by_zone_rule,
                                                doc='Carbon dioxide emission of each year')
    if para['ishydro'] == 1:
        model = add_hydro(model, para)
    else:
        # not consider hydropower curtailment
        def hydro_output_rule(model, h, m, y, z):
            return model.gen[h, m, y, z, [i for i,j in para['type'].items() if j == 'hydro'][0]] <= float(para['hydro_output']['Hydro', z, m, h]) * para['dt']

        model.hydro_output_cons = Constraint(model.hour_month_year_zone_tuples,
                                             rule=hydro_output_rule,
                                             doc='define hydropower output')
        model.income_cons = Constraint(expr=model.income==0)

    return model

def add_hydro(model, para):

    Hour = para['hour_sets']
    Hour_period = [0] + para['hour_sets']  # storage

    model.station = Set(initialize=para['stcd_sets'], ordered=True, doc='Set of hydropower plants')

    model.station_hour_month_year_tuples = model.station * model.hour * model.month * model.year
    model.station_month_year_tuples = model.station * model.month * model.year
    model.station_hour_p_month_year_tuples = model.station * model.hour_p * model.month * model.year

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
                                                doc='Initialqq storage Constraints')
    model.end_storage_cons = Constraint(model.station_month_year_tuples,
                                                rule=end_storage_rule,
                                                doc='Terminal storage Constraints')
    model.income_cons = Constraint(expr=model.income==sum([model.withdraw[s, h, m, y]*3600*para['dt']*para['price'] 
                                                           for s,h,m,y in model.station_hour_month_year_tuples]))
    # hydropower not curtailment
    def hydro_output_rule(model, h, m, y, z):
        hydro_output = 0
        for s in model.station:
            if para['static']['zone',s] == z:
                hydro_output += model.output[s, h, m, y] * para['dt']
        return model.gen[h, m, y, z, [i for i,j  in para['type'].items() if j == 'hydro'][0]] == hydro_output

    model.hydro_output_cons = Constraint(model.hour_month_year_zone_tuples,
                                                rule=hydro_output_rule,
                                                doc='define hydropower output')
    
    return model
