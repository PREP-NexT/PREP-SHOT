
__version__ = "1.0.0"
__author__ = "Zhanwei Liu"
__email__ = "liuzhanwei@u.nus.edu"
__license__ = "MIT"
__url__ = "https://github.com/PREP-NexT/PREP-SHOT"
__description__ = "Pathways for Renewable Energy Planning coupling Short-term Hydropower OperaTion (PREP-SHOT)"

from .model import create_model
from .load_data import load_data
from .utils import run_model_iteration, extract_result
