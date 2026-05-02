.. _Installation:

Installation
============

This page provides instructions on how to install and use PREP-SHOT. The installation process is divided into the following steps:

Step 1: Download PREP-SHOT
++++++++++++++++++++++++++

Ensure you have downloaded the PREP-SHOT model from the `GitHub repository <https://github.com/PREP-NexT/PREP-SHOT>`_.

You may either clone the repository using the command:

.. code-block:: bash

    git clone https://github.com/PREP-NexT/PREP-SHOT.git

or download the repository as a zip file `here <https://github.com/PREP-NexT/PREP-SHOT/archive/refs/heads/main.zip>`__.

Step 2: Install dependencies
++++++++++++++++++++++++++++++

Assuming you have already `installed Python <https://www.python.org/downloads/>`_, the ``requirements.txt`` file contains all the dependencies for the project (default install open-source solver `HiGHS`). I also recommend `create a new environment <https://conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html>`_ for PREP-SHOT and installing the dependencies within the new environement. This approach isolates the project and its dependencies, helping to prevent conflicts with other Python projects.

.. code:: bash

    cd PREP-SHOT
    conda create -n prep-shot python=3.9
    conda activate prep-shot
    pip install -r requirements.txt

Alternatively, install PREP-SHOT itself as an editable Python package
(this also pulls in the dependencies declared in ``pyproject.toml``):

.. code:: bash

    pip install -e .

A PyPI release (``pip install prepshot``) is planned alongside the v2.0
stability promise. Until then, to pin a specific version in another
project, install directly from GitHub:

.. code:: bash

    pip install git+https://github.com/PREP-NexT/PREP-SHOT@v1.3.0

Step 3: Run an example (Optional)
++++++++++++++++++++++++++++++++++

Once the environment is activated, you can run an example of :ref:`Tutorial` with the following command:

.. code:: bash

    python run.py

If you used ``pip install -e .`` in Step 2 you also have two additional,
equivalent entry points that work from any directory containing a
``config.json`` and ``params.json``:

.. code:: bash

    prepshot
    # or
    python -m prepshot

You can also run examples using Jupyter notebooks located in the `./example/` directory.

PREP-SHOT default solve models using open-source solver `HiGHS <https://highs.dev/>`_. also support commercial solvers, including `Gurobi <https://www.gurobi.com/features/academic-named-user-license/>`_, `COPT <https://www.copt.de/>`_ and `MOSEK <https://www.mosek.com/>`_. They offer academic licenses. To use these solvers, you need to install them and modify the solver in the `config.json` file.


Step 4: Run your own model
+++++++++++++++++++++++++++

You can prepare your input data referring to the example in the `input` and `southeast` folder. The detailed input data are introduced in the :ref:`Tutorial`. After preparing the input data, you can modify the `config.json` file to set the solver and other parameters. Then you can run your model with the following command:

.. code:: bash

    python run.py

Step 5: Use PREP-SHOT as a Python library
+++++++++++++++++++++++++++++++++++++++++++

After ``pip install -e .`` (or ``pip install prepshot`` once PyPI ships),
PREP-SHOT can be imported and driven directly from your own Python code.

The simplest entry point is ``prepshot.cli.main``, which mirrors the
behaviour of the ``prepshot`` console script and runs a full
build-solve-save cycle on a directory containing ``config.json`` and
``params.json``:

.. code:: python

    from prepshot.cli import main

    solved = main(root_dir="/path/to/my/scenario")
    if not solved:
        raise RuntimeError("PREP-SHOT did not reach optimality")

For finer-grained control -- for example, to run multiple scenarios in
the same Python process, inspect the model after solving, or skip the
default Excel output -- use the lower-level functions:

.. code:: python

    from prepshot.set_up import initialize_environment
    from prepshot.model import create_model
    from prepshot.solver import solve_model

    parameters = initialize_environment({
        "filepath": "/path/to/scenario",
        "config_filename": "/path/to/scenario/config.json",
        "params_filename": "/path/to/scenario/params.json",
    })

    model = create_model(parameters)
    solved = solve_model(model, parameters)
    print("objective:", model.get_value(model.cost))

The Python API is stable across the v1.x series; it is the recommended
surface for downstream code that depends on PREP-SHOT. See the Stability
page for the full stability policy.

Input formats: wide Excel and long CSV
+++++++++++++++++++++++++++++++++++++++

Most input parameters are read from wide-format Excel files (one
spreadsheet per parameter, with hierarchical row/column headers
encoding the dimensions). As of v1.4.0, parameters can also be read
from long-format ("tidy") CSVs via a ``"format": "long"`` flag in
``params.json``.

A long-format CSV places dimension columns first, value column last.
For example, ``carbon_tax`` is shipped as a long CSV:

.. code:: text

    zone,year,value
    BA1,2020,0
    BA1,2025,0
    BA2,2020,0

Both formats produce the same internal dictionary shape, so model
code (``params['carbon_tax'][zone, year]``) is unchanged regardless
of which format the file is on disk. New parameters can be born
long-format without disturbing existing wide-format inputs.









