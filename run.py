from pyomo.environ import SolverFactory
from pyomo.opt import SolverStatus, TerminationCondition
import configparser
import pandas as pd
import time

from prepshot import load_data
from prepshot import create_model
from prepshot import utils

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



# Scenario
carbon_limits = pd.read_excel(inputpath + 'scenario/carbon.xlsx', index_col=0)

# global parameters
time_length = int(basic_para['hour'])
month = int(basic_para['month'])
# Fraction of One Year of Modeled Timesteps
weight = (month * time_length) / 8760
dt = int(basic_para['dt'])
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
# Validation data
# TODO
utils.write(logfile, "\n=========================================================")
utils.write(logfile, "Start creating model ...")
# Create a model
model = create_model(para, dt, weight, ishydro)
utils.write(logfile, "Data creating completed, taking %s minutes"%(round((time.time() - start_time)/60,2)))
utils.write(logfile, "\n=========================================================")
for s in carbon_limits.columns:
    # Update output file name by carbon scenario
    output_filename = outputpath +'c%s'%s+ basic_para['outputfile']
    # set mutable parameters
    for h,m,y,z,te in model.hour_month_year_zone_nondispatchable_tuples:
        model.capacity_factor[h,m,y,z,te] = para['capacity_factor'][te, z, m, h]
    for y,te in model.year_tech_tuples:
        model.invcost[y, te] = para['invcost'][te, y]
    for h,m,y,z in model.hour_month_year_zone_tuples:
        model.demand_para[h, m, y, z] = para['demand'][z, y, m, h]
    for y in model.year:
        model.carbon_up_bound_para[y] = float(carbon_limits[s][y])

    if ishydro:
        for s,h,m,y in model.station_hour_month_year_tuples:
            model.inflow_para[s, h, m, y] = para['inflow'][s, m, h]
        utils.write(logfile, "Start solving model ...")
        start_time = time.time()
        state = utils.run_model_iteration(model, solver, para, iteration_log=logfile,
                error_threshold=error_threshold, iteration_number=iteration_number)
        utils.write(logfile, "Solving model completed, taking %s minutes"%(round((time.time() - start_time)/60,2)))
    else:
        for h,m,y,z in model.hour_month_year_zone_tuples:
            model.hydro_output_para[h, m, y, z] = float(para['hydro_output']['Hydro', z, m, h])
        utils.write(logfile, "Start solving model ...")
        start_time = time.time()
        results = solver.solve(model, tee=True)
        utils.write(logfile, "Solving model completed, taking %s minutes"%(round((time.time() - start_time)/60,2)))
        if (results.solver.status == SolverStatus.ok) and \
        (results.solver.termination_condition == TerminationCondition.optimal):
            # Do nothing when the solution in optimal and feasible
            state = 0
        elif (results.solver.termination_condition == TerminationCondition.infeasible):
            # Exit programming when model in infeasible
            utils.write(logfile, "Error: Model is in infeasible!")
            state = 1
        else:
            # Something else is wrong
            utils.write(logfile, "Solver Status: ",  results.solver.status)

    if state == 0:
        utils.write(logfile, "\n=========================================================")
        utils.write(logfile, "Start writing results ...")
        utils.saveresult(model, output_filename, ishydro=ishydro)
utils.write(logfile, "Finish!")