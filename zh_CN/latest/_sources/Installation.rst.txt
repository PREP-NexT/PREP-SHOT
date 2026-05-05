.. _Installation:

Installation
============

This page covers PREP-SHOT setup and library use. For a hands-on first
solve, see :doc:`Quickstart`.


Step 1: Download
++++++++++++++++

Clone the repository:

.. code-block:: bash

    git clone https://github.com/PREP-NexT/PREP-SHOT.git

Or download a `zip archive <https://github.com/PREP-NexT/PREP-SHOT/archive/refs/heads/main.zip>`__.


Step 2: Install
+++++++++++++++

A dedicated `conda environment
<https://conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html>`_
is recommended so the optimization-solver dependencies stay isolated:

.. code-block:: bash

    cd PREP-SHOT
    conda create -n prep-shot python=3.11 -y
    conda activate prep-shot
    pip install -e .

``pip install -e .`` installs PREP-SHOT itself in editable mode AND
pulls in every runtime dependency declared in ``pyproject.toml``. The
default solver `HiGHS <https://highs.dev/>`_ is installed
automatically as a wheel; commercial solvers need a separate install
and a ``solver`` change in the scenario's ``config.json``.

.. tabs::

   .. tab:: HiGHS (default)

      No extra install needed -- ``pip install -e .`` already pulled
      in ``highsbox``, which ships HiGHS as a wheel. Confirm with:

      .. code-block:: bash

         python -c "import highsbox; print('OK')"

      In ``config.json``:

      .. code-block:: json

         "solver_parameters": {"solver": "highs"}

   .. tab:: Gurobi

      Install Gurobi from `gurobi.com
      <https://www.gurobi.com/features/academic-named-user-license/>`_
      and obtain an academic license. Then:

      .. code-block:: bash

         pip install gurobipy

      In ``config.json``:

      .. code-block:: json

         "solver_parameters": {"solver": "gurobi"}

   .. tab:: COPT

      Install COPT from `copt.de <https://www.copt.de/>`_; academic
      licenses are free. Then:

      .. code-block:: bash

         pip install coptpy

      In ``config.json``:

      .. code-block:: json

         "solver_parameters": {"solver": "copt"}

   .. tab:: MOSEK

      Install MOSEK from `mosek.com <https://www.mosek.com/>`_; an
      academic license is free. Then:

      .. code-block:: bash

         pip install mosek

      In ``config.json``:

      .. code-block:: json

         "solver_parameters": {"solver": "mosek"}

Optional dependency groups:

.. code-block:: bash

    pip install -e .[notebook]   # jupyterlab, matplotlib, h5netcdf
    pip install -e .[dev,docs]   # pytest, sphinx

A PyPI release (``pip install prepshot``) is planned alongside the v2.0
stability promise. To pin a specific version meanwhile, install
directly from GitHub:

.. code-block:: bash

    pip install git+https://github.com/PREP-NexT/PREP-SHOT@v1.10.0


Step 3: Run a scenario
++++++++++++++++++++++

Each subdirectory of ``examples/`` is a self-contained scenario. Pick
one and run from inside it; see :doc:`Quickstart` for a hands-on
walkthrough on the ``three_zone`` dataset.

.. code-block:: bash

    cd examples/three_zone   # or southeast_asia, thailand
    python -m prepshot

Three scenarios ship with the repo: ``three_zone`` (synthetic 3-zone,
used by :doc:`Quickstart`), ``southeast_asia`` (Lower Mekong, 5
countries, 57 reservoirs), and ``thailand`` (single-zone with 13
Mekong-basin reservoirs).

To run your own scenario, copy ``examples/three_zone/`` as a starting
template and edit ``input/*.csv`` + ``config.json``.


Step 4: Use PREP-SHOT as a Python library
+++++++++++++++++++++++++++++++++++++++++

After ``pip install -e .``, PREP-SHOT can be imported and driven
directly from your own Python code. The simplest entry point is
``prepshot.cli.main``, which mirrors the ``prepshot`` console script
and runs a full build-solve-save cycle on a directory containing
``config.json`` and ``params.json``:

.. code-block:: python

    from prepshot.cli import main

    solved = main(root_dir="/path/to/my/scenario")
    if not solved:
        raise RuntimeError("PREP-SHOT did not reach optimality")

For finer-grained control -- multiple scenarios in the same Python
process, inspecting the model after solving, skipping the default
Excel output -- use the lower-level functions:

.. code-block:: python

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
surface for downstream code that depends on PREP-SHOT. See
:doc:`Stability` for the full stability policy.
