"""
This module is an energy capacity expansion optimization tool.
It takes command-line arguments for different scenarios to solve
the optimization problem with various constraints.
"""

import argparse
import configparser
import time
import logging

from pyomo.environ import SolverFactory
from pyomo.opt import SolverStatus, TerminationCondition

from prepshot import create_model, load_data, utils

# from copt_pyomo import *

# Constants
INPUT_FILE_PARAMS = [
    "technology_portfolio",
    "distance",
    "discount_factor",
    "transline",
    "transline_efficiency",
    "technology_fix_cost",
    "technology_variable_cost",
    "technology_investment_cost",
    "carbon_content",
    "fuel_price",
    "efficiency_in",
    "efficiency_out",
    "energy_power_ratio",
    "lifetime",
    "capacity_factor",
    "demand",
    "ramp_up",
    "ramp_down",
    "carbon",
    "transline_investment_cost",
    "technology_upper_bound",
    "new_technology_upper_bound",
    "new_technology_lower_bound",
    "init_storage_level",
    "transline_fix_cost",
    "transline_variable_cost",
    "transmission_line_lifetime",
    "zv",
    "zq",
    "type",
    "age",
    "storage_upbound",
    "storage_downbound",
    "storage_init",
    "storage_end",
    "hydropower",
    "inflow",
    "connect",
    "static"
]
CONFIG_FILENAME = 'global.properties'


def setup_logging(logfile):
    """
    Set up logging configuration.

    :param logfile: str, path to the log file
    """
    logging.basicConfig(filename=logfile, level=logging.INFO,
                        format='%(asctime)s %(levelname)s: %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s', '%Y-%m-%d %H:%M:%S'))
    logging.getLogger().addHandler(console)


def process_arguments():
    """
    Process command-line arguments for different scenarios.

    :return: argparse.Namespace, parsed command-line arguments
    """
    parser = argparse.ArgumentParser(description='filename')
    for param in INPUT_FILE_PARAMS:
        parser.add_argument(f'--{param}', type=str, default=None,
                            help=f'The suffix of input paramemeters: {param}')
    parser.add_argument(f'--price', type=float, default=0.01,
                        help='The value of price paramemeters')
    return parser.parse_args()


def generate_input_filenames(args):
    """
    Generate input file names based on provided command-line arguments.

    :param args: argparse.Namespace, parsed command-line arguments
    :return: dict, mapping of parameter names to input file names
    """
    input_filenames = {}

    for param in INPUT_FILE_PARAMS:
        if getattr(args, param) is None:
            input_filenames[param] = f"{param}.xlsx"
        else:
            input_filenames[param] = f"{param}_{args[param]}.xlsx"
    return input_filenames


def build_solver(solver_name, solver_config):
    """
    Build a solver based on the provided solver name and configuration.

    :param solver_name: str, name of the solver
    :param config: dict, solver configuration
    :return: pyomo.opt.base.solvers.OptSolver, solver instance
    """
    solver = SolverFactory(solver_name, solver_io='python')
    for option, value in solver_config.items():
        solver.options[option] = value
    return solver


def solve_model(model, solver, para, ishydro, error_threshold, iteration_number):
    """
    Solve the optimization model using the given solver.

    :param model: The optimization model to be solved
    :param solver: The solver to be used
    :param ishydro: Boolean, whether the model includes hydrological constraints
    :param error_threshold: The error threshold for the iterative solution process
    :param iteration_number: The maximum number of iterations for the iterative solution process
    :return: The solution status (0: optimal, 1: infeasible, others: error)
    """
    if ishydro:
        logging.info("Start solving model ...")
        start_time = time.time()
        state = utils.run_model_iteration(model, solver, para, error_threshold=error_threshold,
                                          iteration_number=iteration_number)
        logging.info(
            f"Solving model completed, taking {round((time.time() - start_time) / 60, 2)} minutes")
    else:
        logging.info("Start solving model ...")
        start_time = time.time()
        results = solver.solve(model, tee=True)
        logging.info(
            f"Solving model completed, taking {round((time.time() - start_time) / 60, 2)} minutes")

        if (results.solver.status == SolverStatus.ok) and \
                (results.solver.termination_condition == TerminationCondition.optimal):
            # Do nothing when the solution in optimal and feasible
            state = 0
        elif (results.solver.termination_condition == TerminationCondition.infeasible):
            # Exit programming when model in infeasible
            logging.info("Error: Model is in infeasible!")
            state = 1
        else:
            # Something else is wrong
            logging.info("Solver Status: ", results.solver.status)
            state = 2

    return state


def load_parameters(config_filename):
    config = configparser.RawConfigParser(inline_comment_prefixes="#")
    config.read(config_filename)
    basic_para = dict(config.items('global parameters'))
    solver_para = dict(config.items('solver parameters'))
    hydro_para = dict(config.items('hydro parameters'))

    return basic_para, solver_para, hydro_para


def initialize_parameters(basic_para, hydro_para, args, para):
    time_length = int(basic_para['hour'])
    month = int(basic_para['month'])
    assert time_length == len(para["hour"])
    assert month == len(para["month"])
    dt = int(basic_para['dt'])
    weight = (month * time_length * dt) / 8760

    ishydro = bool(int(hydro_para['ishydro']))
    error_threshold = float(hydro_para['error_threshold'])
    iteration_number = int(hydro_para['iteration_number'])

    return {
        'dt': dt,
        'weight': weight,
        'ishydro': ishydro,
        'error_threshold': error_threshold,
        'iteration_number': iteration_number,
        'price': args.price,
    }


def log_parameter_info(basic_para, input_filename, output_filename):
    logging.info("Set parameter solver to value %s" % basic_para['solver'])
    logging.info("Set parameter input_filename to value %s" % input_filename)
    logging.info("Set parameter output_filename to value %s.nc" %
                 output_filename)
    logging.info("Set parameter time_length to value %s" % basic_para['hour'])


def read_config_file(config_file):
    config = configparser.ConfigParser()
    config.read(config_file)

    # Create a dictionary to store all parameters
    parameters = {}

    for section in config.sections():
        for key, value in config.items(section):
            parameters[key] = value

    return parameters


def main():
    """
    The main function of the energy capacity expansion optimization tool.
    """
    args = process_arguments()
    input_filenames = generate_input_filenames(args)

    log_time = time.strftime("%Y-%m-%d-%H-%M-%S")
    log_file = f'./log/main_{log_time}.log'
    setup_logging(log_file)

    basic_para, solver_para, hydro_para = load_parameters(CONFIG_FILENAME)

    input_path = './input/'
    output_path = './output/'
    input_filename = input_path + basic_para['inputfile'] # TODO
    output_filename = output_path + basic_para['outputfile']

    log_parameter_info(basic_para, input_filename, output_filename)

    solver_name = basic_para['solver']
    solver = build_solver(solver_name, solver_para)

    parameters = load_data(filepath=input_path,
                           filename=input_filenames)

    params = initialize_parameters(basic_para, hydro_para, args, parameters)
    parameters.update(params)

    model = create_model(parameters)
    
    output_filename = output_filename + \
        '_'.join(f'{key}_{value}' for key, value in vars(args).items() if value != None)

    state = solve_model(
        model, solver, parameters, parameters['ishydro'], parameters['error_threshold'],
        parameters['iteration_number']
    )

    if state == 0:
        logging.info("Start writing results ...")
        ds = utils.extract_result(model, ishydro=parameters['ishydro'])
        ds.to_netcdf(f'{output_filename}.nc')
    logging.info("Finish!")


if __name__ == "__main__":
    main()
