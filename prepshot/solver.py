from pyomo.environ import SolverFactory
from pyomo.opt import SolverStatus, TerminationCondition
from prepshot.logs import timer
from prepshot.utils import run_model_iteration

def build_solver(parameters):
    """
    Build the solver for PREP-SHOT model.

    Args:
        parameters (dict): Dictionary of parameters for the model.

    Returns:
        pyomo.solvers.plugins.solvers: Solver for the model.
    """
    solver = SolverFactory(parameters['solver'], solver_io='python')
    solver.options['timelimit'] = parameters['timelimit']
    return solver


@timer
def solve_model_with_hydro(model, solver, parameters):
    """
    Solve the model with hydrological constraints.

    Args:
        model (pyomo.core.base.PyomoModel.ConcreteModel): Model to be solved.
        solver (pyomo.solvers.plugins.solvers): Solver for the model.
        parameters (dict): Dictionary of parameters for the model.

    Returns:
        bool: True if the model is solved, False otherwise.
    """
    error_threshold = parameters['error_threshold']
    iteration_number = parameters['iteration_number']
    return run_model_iteration(model, solver, parameters, error_threshold, iteration_number)


@timer
def solve_model_without_hydro(model, solver):
    """
    Solve the model without hydrological constraints.

    Args:
        model (pyomo.core.base.PyomoModel.ConcreteModel): Model to be solved.
        solver (pyomo.solvers.plugins.solvers): Solver for the model.
    
    Returns:
        bool: True if the model is solved, False otherwise.
    """
    results = solver.solve(model, tee=True)
    if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
        return True
    else:
        return False


def solve_model(model, solver, parameters):
    """
    Solve the model.

    Args:
        model (pyomo.core.base.PyomoModel.ConcreteModel): Model to be solved.
        solver (pyomo.solvers.plugins.solvers): Solver for the model.
        parameters (dict): Dictionary of parameters for the model.

    Returns:
        bool: True if the model is solved, False otherwise.
    """
    if parameters['isinflow']:
        return solve_model_with_hydro(model, solver, parameters)
    else:
        return solve_model_without_hydro(model, solver)
