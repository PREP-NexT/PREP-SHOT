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

Each subdirectory of ``examples/`` is a self-contained scenario
(``config.json`` + ``params.json`` + ``input/``). Pick one and run from
inside it:

.. code:: bash

    cd examples/three_zone
    python -m prepshot

Equivalent entry points (after ``pip install -e .``):

.. code:: bash

    prepshot                       # console script (any cwd)
    python /path/to/run.py .       # explicit path

Three scenarios ship with the repo: ``three_zone`` (synthetic 3-zone,
used by :ref:`Quickstart`), ``southeast_asia`` (Lower Mekong,
5 countries, 57 reservoirs), and ``thailand`` (single-zone with
13 Mekong-basin reservoirs).

PREP-SHOT default solve models using open-source solver `HiGHS <https://highs.dev/>`_. It also support commercial solvers, including `Gurobi <https://www.gurobi.com/features/academic-named-user-license/>`_, `COPT <https://www.copt.de/>`_ and `MOSEK <https://www.mosek.com/>`_. They offer academic licenses. To use these solvers, you need to install them and modify the ``solver`` field in the scenario's ``config.json`` file.


Step 4: Run your own model
+++++++++++++++++++++++++++

To run your own scenario, copy one of the ``examples/`` directories as
a starting template, edit its ``input/`` CSV files, and tweak its
``config.json`` (number of representative hours/months, solver
choice, hydropower convergence threshold). Then run from inside it:

.. code:: bash

    cp -r examples/three_zone examples/my_scenario
    # ... edit examples/my_scenario/input/*.csv and config.json ...
    cd examples/my_scenario
    python -m prepshot

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

Input formats: long CSV (default) and wide Excel (legacy)
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

As of v1.5.0, almost all input parameters are read from long-format
("tidy") CSV files. A long-format CSV places the dimension columns
first and the value column last. For example, ``carbon_tax`` is
shipped as:

.. code:: text

    zone,year,value
    BA1,2020,0
    BA1,2025,0
    BA2,2020,0

Each ``params.json`` entry declares its format. Long-format entries
are minimal:

.. code:: json

    "carbon_tax": {
        "file_name": "carbon_tax",
        "format": "long",
        "drop_na": true,
        "required": false,
        "default": 0
    }

Four "Group 3" inherently table-shaped lookups (``water_delay_time``,
``reservoir_characteristics``, ``reservoir_tailrace_level_discharge_function``,
``reservoir_forebay_level_volume_function``) remain in wide-Excel
format pending the v1.6.0 release.

Migrating an existing input directory
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you have a custom input directory inherited from v1.4.x or earlier,
run the migration tool once to convert the wide-Excel files to long
CSV:

.. code:: bash

    python tools/migrate_to_long.py /path/to/your/input_dir

After migration the loader will accept the directory under the v1.5.0
schema (``_schema_version: 2``).









