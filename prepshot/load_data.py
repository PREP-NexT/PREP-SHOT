from .utils import Readin, invcost_factor, fixcost_factor, varcost_factor, write

def load_data(filename, month, time_length):

    Tech_existing = Readin('technology portfolio', filename, month, time_length)  # [MW]
    Distance = Readin('distance', filename, month, time_length)  # [km]

    # New transmission lines Can not be built in some areas without transmission lines
    Transmission = Readin('transline', filename, month, time_length)  # [MW]
    Trans_effi = Readin('transline efficiency', filename, month, time_length)
    DF = Readin('discount factor', filename, month, time_length)
    Cfix = Readin('technology fix cost', filename, month, time_length)  # [RMB/MW/y], O&M cost
    Cvar = Readin('technology variable cost', filename, month, time_length)  # [RMB/MWh]
    Cinv = Readin('technology investment cost', filename, month, time_length)  # [RMB/MW]
    Carbon_Content = Readin('carbon content', filename, month, time_length)  # [Ton/MWh]
    Fuel_price = Readin('fuel price', filename, month, time_length)  # [RMB/MWh]
    Efficiency_in = Readin('efficiency-in', filename, month, time_length)
    Efficiency_out = Readin('efficiency-out', filename, month, time_length)
    EP = Readin('EP', filename, month, time_length)
    Lifetime = Readin('lifetime', filename, month, time_length)

    Capacity_factor = Readin('capacity factor', filename, month, time_length)
    Demand = Readin('demand', filename, month, time_length)  # [MWh]

    Ramp_up = Readin('ramp_up', filename, month, time_length)
    Ramp_down = Readin('ramp_down', filename, month, time_length)
    Carbon = Readin('carbon', filename, month, time_length)  # [Ton] # * weight
    inv_budget = Readin('invest budget', filename, month, time_length)  # [RMB]
    Cinv_lines = Readin('transline investment cost', filename, month, time_length)  # [RMB/MW/km]

    # technology expantion limits
    tech_upper = Readin('technology upper bound', filename, month, time_length)  # [MW]
    newtech_upper = Readin('new technology upper bound', filename, month, time_length)  # [MW]
    newtech_lower = Readin('new technology lower bound', filename, month, time_length)  # [MW]

    # init storage level
    initstorage_level = Readin('init storage level', filename, month, time_length)  # [MW]

    # transmission line cost
    Cfix_lines = Readin('transline fix cost', filename, month, time_length)  # [RMB/MW/km/y]
    Cvar_lines = Readin('transline variable cost', filename, month, time_length)  # [RMB/MWh]
    lifetime_lines = Readin('transmission_line_lifetime', filename, month, time_length)  # [RMB/MWh]

    ZV = Readin('ZV', filename, month, time_length)
    ZQ = Readin('ZQ', filename, month, time_length)

    # type of technology
    tech_type =  Readin('type', filename)  # [MW]

    # age
    age = Readin('age', filename)  # [MW]

    df_invcost_factor = Cinv.copy()
    df_fixcost_factor = DF.copy()
    df_varcost_factor = DF.copy()
    trans_invcost_factor = DF.copy()
    
    # Sets
    # Srictly ascending order
    year_sets = list(DF.keys())
    hour_sets = list([i[3] for i in list(Demand.keys())[:time_length]])
    month_sets = [list(Demand.keys())[i*time_length][2] for i in range(month)]
    # No order
    zone_sets = list(set([i[0] for i in Demand.keys()]))
    tech_sets = list(tech_type.keys())
    
    
    y_min = min(year_sets)
    y_max = max(year_sets)
    # used to calculate cost
    for te in tech_sets:
        for y in year_sets:
            discount_rate = DF[y]
            next_modeled_year = y+1 if y == y_max else year_sets[
                year_sets.index(y) + 1]
            trans_invcost_factor[y] = invcost_factor(max(lifetime_lines.values()), interest_rate=discount_rate, discount_rate=discount_rate, year_built=y,  year_min=y_min, year_max=y_max)
            df_invcost_factor[te,y] = invcost_factor(Lifetime[te,y], interest_rate=discount_rate, discount_rate=discount_rate, year_built=y,  year_min=y_min, year_max=y_max)
            df_fixcost_factor[y] = varcost_factor(discount_rate=discount_rate, modeled_year=y,
                                                   year_min=y_min, next_modeled_year=next_modeled_year)
            df_varcost_factor[y] = fixcost_factor(discount_rate=discount_rate, modeled_year=y,
                                                   year_min=y_min, next_modeled_year=next_modeled_year)

    # hydropower
    df_static = Readin('static', filename, month, time_length)
    df_inflow = Readin('inflow', filename, month, time_length)
    df_storage_upbound = Readin('storage_upbound', filename, month, time_length)
    df_storage_downbound = Readin('storage_downbound', filename, month, time_length)
    df_storage_init = Readin('storage_init', filename, month, time_length)
    df_storage_end = Readin('storage_end', filename, month, time_length)
    df_hydro_output = Readin('hydropower', filename, month, time_length)
    df_connect = Readin('connect', filename, month, time_length)  # dataframe

    stcd_sets = list(set([i[1] for i in df_static.keys()]))

    para = {'technology': Tech_existing,
                                 'distance': Distance,
                                 'transmission': Transmission,
                                 'trans_effi': Trans_effi,
                                 'discount': DF,
                                 'fixcost': Cfix,
                                 'varcost': Cvar,
                                 'invcost': Cinv,
                                 'carbon': Carbon_Content,
                                 'fuelprice': Fuel_price,
                                 'efficiency-in': Efficiency_in,
                                 'efficiency-out': Efficiency_out,
                                 'ep': EP,
                                 'lifetime': Lifetime,
                                 'capacity_factor': Capacity_factor,
                                 'demand': Demand,
                                 'invline': Cinv_lines,
                                 'ramp_up': Ramp_up,
                                 'ramp_down': Ramp_down,
                                 'inv_budget': inv_budget,
                                 'carbon_limit': Carbon,
                                 'tech_upper': tech_upper,
                                 'newtech_upper': newtech_upper,
                                 'newtech_lower': newtech_lower,
                                 'storage_level': initstorage_level,
                                 'fixcost_lines': Cfix_lines,
                                 'varcost_lines': Cvar_lines,
                                 'lifetime_lines': lifetime_lines,
                                 'inv_factor': df_invcost_factor,
                                 'fix_factor': df_fixcost_factor,
                                 'var_factor': df_varcost_factor,
                                 'trans_inv_factor':trans_invcost_factor,
                                 'type':tech_type,
                                 'age_':age,
                                 'inflow': df_inflow,
                                'storageup': df_storage_upbound,
                                'storagedown': df_storage_downbound,
                                'storageinit': df_storage_init,
                                'storageend': df_storage_end,
                                'static':df_static,
                                'connect':df_connect,
                                'ZV':ZV,
                                'ZQ':ZQ,
                                'hydro_output':df_hydro_output,
                                'year_sets':year_sets,
                                'hour_sets':hour_sets,
                                'month_sets':month_sets,
                                'zone_sets':zone_sets,
                                'tech_sets':tech_sets,
                                'stcd_sets':stcd_sets}

    return para
def updatedata(para):
    # update carbon emission scenarios
    write(para['logfile'], 'update carbon emission: %s'%para['carbon_scenario'][0])
    para['carbon_limit'] = Readin(str(para['carbon_scenario'][0]), para['inputpath']+'scenario/'+para['carbon_scenario'][1], para['month'], para['time_length'])
    if para['inflow_scenario'][0] != 0:
        # update inflow
        write(para['logfile'], 'update inflow and fixed hydropower output emission: %s'%para['inflow_scenario'][0])
        para['inflow'] = Readin(str(para['inflow_scenario'][0]), para['inputpath']+'scenario/'+para['inflow_scenario'][1], para['month'], para['time_length'])
        para['hydro_output'] = Readin(str(para['hydropower_scenario'][0]), para['inputpath']+'scenario/'+para['hydropower_scenario'][1], para['month'], para['time_length'])
    if para['demand_scenario'][0] != 0:
        # update demand
        write(para['logfile'], 'update demand emission: %s'%para['demand_scenario'][0])
        para['demand'] = Readin(str(para['demand_scenario'][0]), para['inputpath']+'scenario/'+para['demand_scenario'][1], para['month'], para['time_length'])
    if para['invcost_scenario'][0] != 0:
        # update invcost
        write(para['logfile'], 'update invcost emission: %s'%para['invcost_scenario'][0])
        para['invcost'] = Readin(str(para['invcost_scenario'][0]), para['inputpath']+'scenario/'+para['invcost_scenario'][1], para['month'], para['time_length'])
    return para
