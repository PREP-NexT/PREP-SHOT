from pyomo.environ import SolverFactory
import configparser
import time
import argparse
import pandas as pd

from prepshot import load_data
from prepshot import updatedata
from prepshot import create_hydro_model
from prepshot import utils

# carbon emission scenario
parser = argparse.ArgumentParser(description='scenario approach')
parser.add_argument('--carbon', type=int, help='carbon emission limits scenario')
parser.add_argument('--price', type=float, default=0.01, help='withdraw water price [RMB/m**3]')
parser.add_argument('--inflow', type=float, default=0, help='inflow scenarios')
parser.add_argument('--demand', type=int, default=0, help='demand scenarios')
parser.add_argument('--invcost', type=int, default=0, help='investment cost scenarios')
args = parser.parse_args()

# default paths
inputpath = './input/'
outputpath = './output/'
logpath = './log/'
logtime = time.strftime("%Y-%m-%d-%H-%M-%S")
logfile = logpath + "main_%s.log"%logtime

utils.write(logfile, "Starting load parameters ...")
start_time = time.time()

# load global parameters
config = configparser.RawConfigParser(inline_comment_prefixes="#")
config.read('global.properties')
basic_para = dict(config.items('global parameters'))
solver_para = dict(config.items('solver parameters'))
hydro_para = dict(config.items('hydro parameters'))

# global parameters
time_length = int(basic_para['hour'])
month = int(basic_para['month'])
dt = int(basic_para['dt'])
# Fraction of One Year of Modeled Timesteps
weight = (month * time_length * dt) / 8760
input_filename = inputpath + basic_para['inputfile']
output_filename = outputpath + basic_para['outputfile']

# hydro parameters
ishydro = bool(int(hydro_para['ishydro']))
error_threshold = float(hydro_para['error_threshold'])
iteration_number = int(hydro_para['iteration_number'])

# solver config
solver = SolverFactory(basic_para['solver'], solver_io='python')
solver.options['TimeLimit'] = int(solver_para['timelimit'])
solver.options['LogToConsole'] = 0
solver.options['LogFile'] = logfile

utils.write(logfile, "Set parameter solver to value %s"%basic_para['solver'])
utils.write(logfile, "Set parameter timelimit to value %s"%int(solver_para['timelimit']))
utils.write(logfile, "Set parameter input_filename to value %s"%input_filename)
utils.write(logfile, "Set parameter output_filename to value %s.nc"%output_filename)
utils.write(logfile, "Set parameter time_length to value %s"%basic_para['hour'])
utils.write(logfile, "Parameter loading completed, taking %s minutes"%(round((time.time() - start_time)/60,2)))

utils.write(logfile, "\n=========================================================")
utils.write(logfile, "Starting load data ...")
start_time = time.time()
# load data
para  = load_data(input_filename, month, time_length)
utils.write(logfile, "Data loading completed, taking %s minutes"%(round((time.time() - start_time)/60,2)))


para['inputpath'] = inputpath
para['time_length'] = time_length
para['month'] = month
para['dt'] = dt
para['logfile'] = logfile

# update parameters according to scenarios (update para)
para['price'] = args.price
para['carbon_scenario'] = (args.carbon, 'carbon.xlsx')
para['inflow_scenario'] = (args.inflow, 'inflow.xlsx')
para['invcost_scenario'] = (args.invcost, 'invcost.xlsx')
para['demand_scenario'] = (args.demand, 'demand.xlsx')

# update year
para['year_sets'] = [2018]

# change Yunnan demand to Guangxi demand because Yunnan hydropower can meet demand
for m in para['month_sets']:
    for h in para['hour_sets']:
        para['demand']['Yunnan', 2018, m, h] = para['demand']['Guangdong', 2018, m, h]

para = updatedata(para)
# Validation data
# TODO

# Create a model
model = create_hydro_model(para)

state = utils.run_model_iteration(model, solver, para, iteration_log=logfile,
            error_threshold=error_threshold, iteration_number=iteration_number)
# Outout results
def get_value(dic):
    mux = pd.MultiIndex.from_tuples(dic.keys())
    output = pd.DataFrame(list(dic.values()), index=mux)
    return output
idx = pd.IndexSlice
gen_hydro = get_value(model.gen.extract_values())[0].unstack().swaplevel(0,1).droplevel(level=2)
gen_hydro = gen_hydro.sort_index(level=[0,1], axis=0, ascending=True).round(3)
import numpy as np
line = pd.DataFrame({i:np.nan for i in gen_hydro.columns}, index=pd.MultiIndex.from_tuples([('month','hour')]))
gen_hydro = pd.concat([line, gen_hydro])
gen_hydro.columns = pd.MultiIndex.from_tuples([('Hydro', i) for i in gen_hydro.columns])
gen_hydro.columns.names = ('tech','zone')
gen_hydro.to_excel('./input/scenario/hydro_inflow%s.xlsx'%args.inflow)
