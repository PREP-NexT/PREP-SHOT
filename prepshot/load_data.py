import json
from os import path
from prepshot.utils import read_data, inv_cost_factor, cost_factor

def load_json(file):
    """
    Load data from a json file.
    
    Args:
        file (str): Path to the json file.

    Returns:
        dict: Dictionary containing data from the json file.
    """
    with open(file, "r") as f:
        return json.load(f)


def get_required_config_data(config_data):
    """
    Get required data from loaded configuration data.
    
    Args:
        config_data (dict): Configuration data for the model.

    Returns:
        dict: Dictionary containing required data from the loaded configuration data.
    """
    # Extract data from configuration file.
    hour = int(config_data['general_parameters']['hour'])
    month = int(config_data['general_parameters']['month'])
    dt = int(config_data['general_parameters']['dt'])
    hours_in_year = int(config_data['general_parameters']['hours_in_year'])
    price = float(config_data['general_parameters']['price'])
    includes_hydrological_constraints = config_data['hydro_parameters']['isinflow']
    error_threshold = float(config_data['hydro_parameters']['error_threshold'])
    iteration_number = int(config_data['hydro_parameters']['iteration_number'])
    solver = str(config_data['solver_parameters']['solver'])
    timelimit = str(config_data['solver_parameters']['timelimit'])

    # Create dictionary containing required data from configuration file.
    required_config_data = {
        'dt': dt,
        'price': price,
        'weight': (month * hour * dt) / hours_in_year,
        'solver': solver,
        'timelimit': timelimit,
        'isinflow': includes_hydrological_constraints,
        'error_threshold': error_threshold,
        'iteration_number': iteration_number
    }

    return required_config_data


def load_input_params(input_filepath, params_data, para):
    """
    Load input data into its respective parameter.
    
    Args:
        input_filepath (str): Path to the input folder.
        params_data (dict): Dictionary containing parameters.
        para (dict): Dictionary to store input data of parameters.

    Returns:
        None
    """
    # Load input data into parameters dictionary.
    for key, value in params_data.items():
        filename = path.join(input_filepath, f"{value['file_name']}.xlsx")
        para[key] = read_data(filename, 
                              value["index_cols"], 
                              value["header_rows"], 
                              value["unstack_levels"], 
                              value["first_col_only"], 
                              value["drop_na"])


def get_attr(para):
    """
    Extract attributes from parameters.
    
    Args:
        para (dict): Dictionary containing parameters.

    Returns:
        None
    """
    para["year"] = sorted(list(para["discount_factor"].keys()))
    if "static" in para.keys():
        para["stcd"] = list({i[1] for i in para["static"].keys()})
    para["hour"] = sorted({i[3] for i in para["demand"].keys() if isinstance(i[3], int)})
    para["month"] = sorted({i[2] for i in para["demand"].keys() if isinstance(i[2], int)})
    para["zone"] = list({i[0] for i in para["demand"].keys()})
    para["tech"] = list(para["type"].keys())


def calculate_cost_factors(para):
    """
    Calculate cost factors for transmission investment, investment, fixed and variable costs.

    Args:
        para (dict): Dictionary containing parameters.

    Returns:
        None
    """
    # Initialize dictionaries for computed cost factors.
    para["trans_inv_factor"] = dict()
    para["inv_factor"] = dict()
    para["fix_factor"] = dict()
    para["var_factor"] = dict()

    # Initialize parameters for cost factor calculations.
    trans_line_lifetime = max(para["transmission_line_lifetime"].values())
    lifetime = para["lifetime"]
    y_min, y_max = min(para["year"]), max(para["year"])

    # Calculate cost factors
    for tech in para["tech"]:
        for year in para["year"]:
            discount_rate = para["discount_factor"][year]
            next_year = year+1 if year == y_max else para["year"][para["year"].index(year) + 1]
            para["trans_inv_factor"][year] = inv_cost_factor(trans_line_lifetime, discount_rate, year, discount_rate, y_min, y_max)
            para["inv_factor"][tech, year] = inv_cost_factor(lifetime[tech, year], discount_rate, year, discount_rate, y_min, y_max)
            para["fix_factor"][year] = cost_factor(discount_rate, year, y_min, next_year)
            para["var_factor"][year] = cost_factor(discount_rate, year, y_min, next_year)


def load_data(params_data, input_filepath):
    """
    Loads data from provided file path and processes it according to parameters from params.json.

    Args:
        params_data (dict): Dictionary of parameters data.
        input_filename (str): Name of input folder.

    Returns:
        dict: Dictionary containing processed parameters.
    """
    # Initialize dictionary for parameters to store input data.
    para = dict()

    # Load input data into parameters dictionary.
    load_input_params(input_filepath, params_data, para)

    # Extract attributes from parameters.
    get_attr(para)

    # Calculate cost factors for the parameters.
    calculate_cost_factors(para)

    return para
