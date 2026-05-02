#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Command-line entry point for PREP-SHOT.

Run as a console script after ``pip install``::

    prepshot

Or as a Python module::

    python -m prepshot

Both forms look for ``config.json`` and ``params.json`` in the current
working directory by default. The legacy entry point (``python run.py``)
remains supported and reads those files relative to ``run.py`` instead.
"""
import os

from prepshot.set_up import initialize_environment
from prepshot.model import create_model
from prepshot.solver import solve_model
from prepshot.output_data import save_result

CONFIG_FILENAME = 'config.json'
PARAMS_FILENAME = 'params.json'


def main(root_dir : str = None) -> bool:
    """Run a full PREP-SHOT solve.

    Parameters
    ----------
    root_dir : str, optional
        Directory containing ``config.json`` and ``params.json``. Defaults
        to the current working directory.

    Returns
    -------
    bool
        ``True`` if the model solved to optimality and results were saved,
        ``False`` otherwise.
    """
    if root_dir is None:
        root_dir = os.getcwd()
    config_files = {
        "filepath": root_dir,
        "config_filename": os.path.join(root_dir, CONFIG_FILENAME),
        "params_filename": os.path.join(root_dir, PARAMS_FILENAME),
    }
    parameters = initialize_environment(config_files)
    model = create_model(parameters)
    solved = solve_model(model, parameters)
    if solved:
        save_result(model)
    return solved


if __name__ == "__main__":
    main()
