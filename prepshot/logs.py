import logging
import time
from pathlib import Path
import tracemalloc

def setup_logging():
    """
    Set up logging file to log model run.

    Args:
        None

    Returns:
        None
    """
    # Create a directory for the log file if it doesn't exist.
    Path('log').parent.mkdir(parents=True, exist_ok=True)

    # Create a log file with a timestamp.
    log_dir = Path('log')
    log_time = time.strftime("%Y-%m-%d-%H-%M-%S")
    log_file = log_dir / f'main_{log_time}.log'
    
    logging.basicConfig(filename=log_file, 
                        level=logging.INFO,
                        format='%(asctime)s %(levelname)s: %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s', '%Y-%m-%d %H:%M:%S'))
    logging.getLogger().addHandler(console)


def timer(func):
    """
    Decorator to log the start and end of a function, and how long it took to run.

    Args:
        func (function): The function to be decorated.

    Returns:
        function: The decorated function.
    """
    def wrapper(*args, **kwargs):
        # logging.info("Start solving model ...")
        start_time = time.time()
        tracemalloc.start()
        result = func(*args, **kwargs)
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        run_time = time.time() - start_time
        logging.info(
            "Finished %s in %.2f seds", repr(func.__name__),
            run_time
        )
        logging.info(
            "Memory used %s in %.2f MB", repr(func.__name__),
            peak / 10**6
        )
        return result
    return wrapper


def log_parameter_info(config_data):
    """
    Log the parameters used for the model.

    Args:
        Config_data (dict): Dictionary containing configuration data for the model.

    Returns:
        None
    """
    logging.info(f"Set parameter solver to value {config_data['solver_parameters']['solver']}")
    logging.info(f"Set parameter input folder to value {config_data['general_parameters']['input_folder']}")
    logging.info(f"Set parameter output_filename to value {config_data['general_parameters']['output_filename']}.nc")
    logging.info(f"Set parameter time_length to value {config_data['general_parameters']['hour']}")
