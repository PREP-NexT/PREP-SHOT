import datetime
import logging

import numpy as np
import pandas as pd
import xarray as xr
from pyomo.opt import SolverStatus, TerminationCondition
from scipy import interpolate


########################################################################
############# 1. Set configuration and read data from file #############
########################################################################

# Investment cost factor formula


def invcost_factor(dep_prd, interest_rate, discount_rate, year_built,
                   year_min, year_max):
    """
    Evaluates the factor multiplied to the invest costs for depreciation duration and interest rate.
    Args:
        dep_prd: depreciation period or lifetime (years)
        interest_rate: interest rate or weighted average cost of capital (WACC) (e.g. 0.06 means 6 %)
        year_built: year utility is built
        discount_rate: discount rate for intertemporal planning (convert future value to net present value)
        year_min: starting year of intertemporal planning
        year_max: ending year of intertemporal planning
    """
    # Assertions to check input values
    assert (dep_prd > 0) & (interest_rate > 0) & (year_built > 0) & (year_min > 0) \
        & (year_max > 0) & (year_max > year_min) & (year_max >= year_built) & (year_built >= year_min)

    # Calculate investment cost factor
    m = year_built - year_min
    k = year_max - year_built + 1
    i = interest_rate
    n = dep_prd
    r = discount_rate

    return i / (1 - (1 + i) ** (-n)) * (1 - (1 + r) ** (-min(n, k))) / (r * (1 + r) ** m)

# Variable cost factor formula


def varcost_factor(discount_rate, modeled_year, year_min, next_modeled_year):
    """
    Evaluates the factor multiplied to the invest costs of modeled year.
    Args:
        discount_rate: discount rate for intertemporal planning (convert future value to net present value)
        modeled_year: current modeled year
        year_min: starting year of intertemporal planning
        next_modeled_year: adjacent next year of intertemporal planning
    """
    # Assertions to check input values
    assert (discount_rate > 0) & (modeled_year > 0) & (year_min > 0) \
        & (next_modeled_year > 0) & (next_modeled_year >= modeled_year)

    # Calculate variable cost factor
    m = modeled_year - year_min
    k = next_modeled_year - modeled_year
    r = discount_rate

    return (1 - (1 + r) ** (-k)) / (r * (1 + r) ** (m - 1))

# Fixed cost factor formula (same as variable cost factor)


def fixcost_factor(discount_rate, modeled_year, year_min, next_modeled_year):
    return varcost_factor(discount_rate, modeled_year, year_min, next_modeled_year)

def read_five_dims(filename):
    df = pd.read_excel(io=filename, index_col=[0, 1, 2], header=[0, 1])
    df = df.unstack(level=[0, 1, 2]).dropna().to_dict()
    return df

def read_four_dims(filename):
    df = pd.read_excel(io=filename, index_col=[0, 1], header=[0, 1])
    df = df.unstack(level=[0, 1]).dropna().to_dict()
    return df

def read_four_dims_three_index_one_col(filename):
    df = pd.read_excel(io=filename, index_col=[0, 1, 2], header=[0])
    df = df.unstack(level=[0, 1, 2]).dropna().to_dict()
    return df

def read_three_dims(filename):
    df = pd.read_excel(io=filename, index_col=[0, 1], header=[0])
    df = df.unstack(level=[0, 1]).dropna().to_dict()
    return df


def read_three_dims_one_idx_two_col(filename):
    df = pd.read_excel(io=filename, index_col=[0], header=[0, 1])
    df = df.unstack(level=[0]).dropna().to_dict()
    return df


def read_two_dims(filename):
    df = pd.read_excel(io=filename, index_col=[0], header=[0])
    df = df.unstack(level=[0]).dropna().to_dict()
    return df


def read_one_dims(filename):
    df = pd.read_excel(io=filename, index_col=[0], header=[0])
    df = df.iloc[:, 0].dropna().to_dict()
    return df


def read_break_point(filename):
    df = pd.read_excel(filename, header=0)
    return df


def read_lag_time(filename):
    df = pd.read_excel(filename, index_col=None, header=0)
    return df


def read_hydro_static(filename):
    df = pd.read_excel(filename, index_col=0, header=0).unstack()
    return df.to_dict()


def get_Z_by_Q(name, Q, ZQ):
    try:
        ZQ_temp = ZQ[(ZQ.name == int(name)) | (ZQ.name == str(name))]  
    except:
        ZQ_temp = ZQ[ZQ.name == str(name)]
    f_ZQ = interpolate.interp1d(ZQ_temp.Q, ZQ_temp.Z, fill_value='extrapolate')
    Z = f_ZQ(Q)
    return Z


def get_Z_by_S(name, S, ZV):
    try:
        ZV_temp = ZV[(ZV.name == int(name)) | (ZV.name == str(name))]  
    except:
        ZV_temp = ZV[ZV.name == str(name)]
    f_ZV = interpolate.interp1d(ZV_temp.V, ZV_temp.Z, fill_value='extrapolate')
    Z = f_ZV(S)
    return Z


# def write(file, message):
#     print(message)
#     with open(file, "a") as f:
#         f.write(message)
#         f.write("\n")


def run_model_iteration(model, solver, para, error_threshold=0.001, iteration_number=5):
    logging.info('Starting iteration recorded at %s.' %(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

    Year = para['year']
    Hour = para['hour']
    Month = para['month']
    stations = para['stcd']

    # Iterative Head Modeling
    # initial water head
    old_waterhead = pd.DataFrame(index=stations,
                                 columns=pd.MultiIndex.from_product([Year, Month, Hour], names=['year', 'month', 'hour']))
    new_waterhead = old_waterhead.copy(deep=True)

    for s in stations:
        old_waterhead.loc[s, :] = [para['static']
                                   ['head', s]]*(len(Hour)*len(Month)*len(Year))
    # Initialization error
    error = 1
    iterations = 1
    errors = []

    idx = pd.IndexSlice
    while error >= error_threshold and iterations <= iteration_number:
        alpha = 1/iterations

        for s, h, m, y in model.station_hour_month_year_tuples:
            model.head_para[s, h, m, y] = old_waterhead.loc[s, idx[y, m, h]]

        results = solver.solve(model, tee=True)
        if (results.solver.status == SolverStatus.ok) and \
                (results.solver.termination_condition == TerminationCondition.optimal):
            # Do nothing when the solution in optimal and feasible
            pass
        elif (results.solver.termination_condition == TerminationCondition.infeasible):
            # Exit programming when model in infeasible
            logging.info("Error: Model is in infeasible!")
            return
        else:
            # Something else is wrong
            logging.info("Solver Status: %s" % results.solver.status)
        outflow_v = model.outflow.extract_values()
        storage_v = model.storage_hydro.extract_values()

        # Obtain the new water head after solution
        for stcd in stations:
            stcd = str(stcd)
            tail = np.array([[[outflow_v[int(stcd), h, m, y]
                            for h in Hour] for m in Month] for y in Year])
            s = np.array([[[storage_v[int(stcd), h, m, y]
                         for h in model.hour_p] for m in Month] for y in Year])
            # interpolation
            tail = get_Z_by_Q(stcd, tail, para['zq'])
            s = get_Z_by_S(stcd, s, para['zv'])
            fore = (s[:, :, :Hour[-1]] + s[:, :, 1:])/2
            H = fore - tail
            H[H <= 0] = 0
            new_waterhead.loc[int(stcd), :] = H.ravel()
        # Calculate iteration error
        new_waterhead[new_waterhead <= 0] = 1
        error = (abs(new_waterhead-old_waterhead) /
                 new_waterhead).mean(axis='columns').mean()
        errors.append(error)
        logging.info('water head error: {:.2%}'.format(error))
        # Update water head
        old_waterhead = old_waterhead + alpha*(new_waterhead - old_waterhead)

        iterations += 1

    logging.info('Ending iteration recorded at %s.' %
          (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    return 0


def extract_result(model, ishydro=True):
    Hour = model.hour
    Month = model.month
    Year = model.year
    Zone = model.zone
    Tech = model.tech

    trans_import = model.trans_import.extract_values()
    trans_export = model.trans_export.extract_values()
    gen = model.gen.extract_values()
    carbon = model.carbon.extract_values()
    cap_existing = model.cap_existing.extract_values()
    cost_var = model.cost_var.extract_values()[None]
    cost_fix = model.cost_fix.extract_values()[None]
    cost_newtech = model.cost_newtech.extract_values()[None]
    cost_newline = model.cost_newline.extract_values()[None]
    income = model.income.extract_values()[None]
    charge = model.charge.extract_values()

    trans_import_v = xr.DataArray(data=[[[[[trans_import[h, m, y, z1, z2] / 1e6
                                            if (h, m, y, z1, z2) in model.hour_month_year_zone_zone_tuples else np.nan
                                            for h in Hour]
                                        for m in Month] for y in Year]
                                        for z1 in Zone] for z2 in Zone],
                                  dims=['zone2', 'zone1',
                                        'year', 'month', 'hour'],
                                  coords={'month': Month,
                                          'hour': Hour,
                                          'year': Year,
                                          'zone1': Zone,
                                          'zone2': Zone},
                                  attrs={'unit': 'TWh'})
    trans_export_v = xr.DataArray(data=[[[[[trans_export[h, m, y, z1, z2] / 1e6
                                            if (h, m, y, z1, z2) in model.hour_month_year_zone_zone_tuples else np.nan
                                            for h in Hour]
                                        for m in Month] for y in Year]
                                        for z2 in Zone] for z1 in Zone],
                                  dims=['zone2', 'zone1',
                                        'year', 'month', 'hour'],
                                  coords={'month': Month,
                                          'hour': Hour,
                                          'year': Year,
                                          'zone1': Zone,
                                          'zone2': Zone},
                                  attrs={'unit': 'TWh'})
    gen_v = xr.DataArray(data=[[[[[gen[h, m, y, z, te] / 1e6 for h in Hour]
                                for m in Month] for y in Year]
                                for z in Zone] for te in Tech],
                         dims=['tech', 'zone', 'year', 'month', 'hour'],
                         coords={'month': Month,
                                 'hour': Hour,
                                 'year': Year,
                                 'zone': Zone,
                                 'tech': Tech},
                         attrs={'unit': 'TWh'})
    install_v = xr.DataArray(data=[[[cap_existing[y, z, te] for y in Year] for z in Zone] for te in Tech],
                             dims=['tech', 'zone', 'year'],
                             coords={'zone': Zone, 'tech': Tech, 'year': Year},
                             attrs={'unit': 'MW'})
    carbon_v = xr.DataArray(data=[carbon[y] for y in Year],
                            dims=['year'],
                            coords={'year': Year},
                            attrs={'unit': 'Ton'})
    cost_v = xr.DataArray(data=cost_var + cost_fix +
                          cost_newtech + cost_newline - income)
    cost_var_v = xr.DataArray(data=cost_var)
    cost_fix_v = xr.DataArray(data=cost_fix)
    cost_newtech_v = xr.DataArray(data=cost_newtech)
    cost_newline_v = xr.DataArray(data=cost_newline)
    income_v = xr.DataArray(data=income)
    charge_v = xr.DataArray(data=[[[[[charge[h, m, y, z, te] for h in Hour] for m in Month]
                                    for y in Year] for z in Zone] for te in Tech],
                            dims=['tech', 'zone', 'year', 'month', 'hour'],
                            coords={'tech': Tech, 'zone': Zone,
                                    'year': Year, 'month': Month, 'hour': Hour},
                            attrs={'unit': 'MW'})

    if ishydro:
        stations = model.station
        genflow = model.genflow.extract_values()
        spillflow = model.spillflow.extract_values()
        genflow_v = xr.DataArray(data=[[[[genflow[s, h, m, y] for h in Hour] for m in Month]
                                        for y in Year] for s in stations],
                                 dims=['station', 'year', 'month', 'hour'],
                                 coords={'station': stations, 'year': Year,
                                         'month': Month, 'hour': Hour},
                                 attrs={'unit': 'm**3s**-1'})
        spillflow_v = xr.DataArray(data=[[[[spillflow[s, h, m, y] for h in Hour] for m in Month]
                                          for y in Year] for s in stations],
                                   dims=['station', 'year', 'month', 'hour'],
                                   coords={'station': stations, 'year': Year,
                                           'month': Month, 'hour': Hour},
                                   attrs={'unit': 'm**3s**-1'})
        ds = xr.Dataset(data_vars={'trans_import_v': trans_import_v,
                                   'trans_export_v': trans_export_v,
                                   'gen_v': gen_v,
                                   'carbon_v': carbon_v,
                                   'install_v': install_v,
                                   'carbon_v': carbon_v,
                                   'cost_v': cost_v,
                                   'cost_var_v': cost_var_v,
                                   'cost_fix_v': cost_fix_v,
                                   'charge_v': charge_v,
                                   'genflow_v': genflow_v,
                                   'spillflow_v': spillflow_v,
                                   'cost_newtech_v': cost_newtech_v,
                                   'cost_newline_v': cost_newline_v,
                                   'income_v': income_v})
    else:
        ds = xr.Dataset(data_vars={'trans_import_v': trans_import_v,
                                   'trans_export_v': trans_export_v,
                                   'gen_v': gen_v,
                                   'carbon_v': carbon_v,
                                   'install_v': install_v,
                                   'carbon_v': carbon_v,
                                   'cost_v': cost_v,
                                   'cost_var_v': cost_var_v,
                                   'cost_fix_v': cost_fix_v,
                                   'charge_v': charge_v,
                                   'cost_newtech_v': cost_newtech_v,
                                   'cost_newline_v': cost_newline_v,
                                   'income_v': income_v})
    return ds
