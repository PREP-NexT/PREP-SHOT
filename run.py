import logging
from os import path, makedirs
from prepshot.load_data import load_json, get_required_config_data, load_data
from prepshot.logs import setup_logging, log_parameter_info
from prepshot.model import create_model
from prepshot.parameters import parse_arguments
from prepshot.solver import build_solver, solve_model
from prepshot.utils import extract_result, update_output_filename

# Name of the configuration file and parameters file in root directory.
CONFIG_FILENAME = 'config.json'
PARAMS_FILENAME = 'params.json'

def setup(params_data, args):
    """
    Load data and set up logging.

    Args:
        params_data (dict): Dictionary of parameters data.
        args (argparse.Namespace): Arguments parsed by argparse.

    Returns:
        tuple: A tuple containing the parameters dictionary and the output filename.
    """
    # Load configuration data
    config_data = load_json(CONFIG_FILENAME)
    required_config_data = get_required_config_data(config_data)
    required_config_data.update({'price': args.price})

    # Get the path to input folder.
    filepath = path.dirname(path.abspath(__file__))
    input_filename = str(config_data['general_parameters']['input_folder'])
    input_filepath = path.join(filepath, input_filename)

    # update command-line arguments to set different scenarios easily.
    for param in params_data.keys():
        if getattr(args, param) is None:
            pass
        else:
            params_data[param]["file_name"] = params_data[param]["file_name"] + f"_{getattr(args, param)}"

    # Load parameters data
    parameters = load_data(params_data, input_filepath)

    # Combine the configuration data and parameters data.
    parameters.update(required_config_data)

    # Set up logging
    setup_logging()
    log_parameter_info(config_data)
    
    # Get the output folder.
    output_folder = './' + str(config_data['general_parameters']['output_folder'])
    if not path.exists(output_folder):
        makedirs(output_folder)
        logging.warning(f"Folder {output_folder} created")

    # Get the output filename.
    output_filename =  output_folder + '/' + str(config_data['general_parameters']['output_filename'])

    return parameters, output_filename


def run_model(parameters, output_filename, args):
    """
    Create and solve the model.

    Args:
        parameters (dict): Dictionary of parameters for the model.
        output_filename (str): The name of the output file.
        args (argparse.Namespace): Arguments parsed by argparse.

    Returns:
        None
    """
    model = create_model(parameters)
    output_filename = update_output_filename(output_filename, args)
    solver = build_solver(parameters)
    solved = solve_model(model, solver, parameters)
    if solved:
        ds = extract_result(model, ishydro=parameters['ishydro'])
        ds.to_netcdf(f'{output_filename}.nc')
        logging.info("Results are written to %s.nc", output_filename)


def main():
    """
    The main function of the PREP-SHOT model.

    Args:
        None

    Returns:
        None
    """
    # Load parameters data.
    params_data = load_json(PARAMS_FILENAME)
    params_list = [params_data[key]["file_name"] for key in params_data]
    args = parse_arguments(params_list)

    # Set up model.
    parameters, output_filename = setup(params_data, args)

    # Run model.
    run_model(parameters, output_filename, args)

if __name__ == "__main__":
    main()
