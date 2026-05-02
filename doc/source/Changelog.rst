Changelog
=========

Here, you'll find notable changes for each version of PREP-SHOT.

Version 0.1.0 - Jun 24, 2024
--------------------------------

* PREP-SHOT model is released with basic functionality for energy expansion planning.
* Linear programming optimization model for energy systems with multiple zones.
* Support for solvers such as Gurobi, CPLEX, MOSEK, and GLPK via `Pyomo <https://pyomo.readthedocs.io/en/stable/solving_pyomo_models.html>`_.
* Input and output handling with `pandas` and `Xarray`.

Version 0.1.1 - Jul 11, 2024
-------------------------------

Added
+++++

* Add an example, expansion of Southeast Asia Mainland power system considering hydropower of Lower Mekong River.
* Update the documentation with a docstring for each function and class.
* Add the `Semantic Versioning Specification <https://semver.org>`_.

Fixed
+++++

Changed
+++++++

* Support for solvers such as GUROBI (Commercial), COPT (Commercial), MOSEK (Commercial), and HiGHS (Open source) via `PyOptInterface <https://github.com/metab0t/PyOptInterface>`_.
* Change default solver to HiGHS.
* Change the code comment style to `NumPy <https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_numpy.html>`_.
* Change the code style to `PEP8 <https://pep8.org>`_.
* Categorize constraint definitions based on type (co2, cost, demand, generation, hydro, investment, nondispatchable, storage, transmission) for better organization.
* Split `rule.py` class into serveral smaller, focused classes according to categorized constraint definitions.
* Simplify model by replacing intermediate constraints with direct expressions.
* Extract new modules `solver.py`, `output_data.py`, and `set_up.py` from `run.py` and `utils.py`.
* Remove `parameters.py` into `set_up.py`.
* Refactor and improve comments and function names for clarity and conciseness.

Deprecated
++++++++++

* Removed dependency on `Pyomo <https://pyomo.readthedocs.io/en/stable/solving_pyomo_models.html>`_ due to high memory usage and slow performance for large-scale models. `For you reference <https://metab0t.github.io/PyOptInterface/benchmark.html>`_.


Version 0.1.2 - Jul 22, 2024
-------------------------------

Added
++++++

* Added mathematical notations to the constraint module.
* Added a test script for `prepshot.utils`.

Fixed
++++++

* Fixed the format of the API reference.
* Fix code blocks of documentation.
* Updated `Contribution.rst` to include context on running tests and code style checks.
* Defined explicit data types for inputs and outputs of functions for better type checking and readability.
* Added `pyoptinterface._src.core_ext` to Pylint's extension package allow list to resolve cpp-extension-no-member warning.

Changed
++++++++

* Updated `model.py` to keep necessary decision variables and use expressions for intermediate variables instead of direct determination.
* Refactored `extract_results_non_hydro` in `output_data.py` to extract common features for different variables, simplifying the code.
* Removed definitions of complex sets and opted for simple sets wherever possible to streamline the code.
* Refactor: Organize import order of modules according to PEP 8 guidelines: (1) Grouped standard library imports at the top; (2) Followed by third-party library imports; (3) Local application/library imports at the bottom.


Version 1.0 - Jul 21, 2025
-------------------------------

First v1.0 release. Aggregates all changes since v0.1.2 (PRs #23-#34). See
the GitHub release notes for the full list. Notable highlights:

* Bug fixes and refinements to constraint definitions.
* Documentation improvements and added publications.
* Stabilized PyOptInterface integration.


Version 1.1.0 - May 2, 2026
-------------------------------

.. note::
   **v1.x is a rapid-evolution series.** Breaking input-format changes may
   occur on minor version bumps. API and input-schema stability will be
   promised with v2.0.0. See the Stability page.

Added
+++++

* Time-varying capacity bounds: ``technology_upper_bound``,
  ``technology_lower_bound``, ``new_technology_upper_bound``, and
  ``new_technology_lower_bound`` are now indexed by ``(zone, tech, year)``.
* Re-introduced ``technology_lower_bound`` constraint on ``cap_existing``.
* Carbon market:

  * ``carbon_offset[y, z]`` decision variable.
  * ``carbon_tax`` cost term in the objective.
  * ``carbon_offset_price`` cost term in the objective.
  * Fractional ``carbon_offset_limit`` constraint
    (``offset <= rate * raw zonal emissions``).
  * ``carbon_capacity[y, z]`` now nets out purchased offsets.

* ``southeast_asia/`` dataset migrated to the new schema.
* ``params.json`` now stamps ``_schema_version: 1``.

Changed (Breaking)
++++++++++++++++++

* Bound input files reshaped from ``(tech, zone)`` to ``(zone, tech, year)``.
* Four new required input files: ``technology_lower_bound``,
  ``carbon_tax``, ``carbon_offset_price``, ``carbon_offset_limit``. The
  shipped defaults are zero-filled, which keeps the carbon-market feature
  dormant.
* ``params.json`` files without ``_schema_version`` are rejected by the
  loader.


Version 1.1.1 - May 2, 2026
-------------------------------

Added
+++++

* ``prepshot.load_data.CURRENT_SCHEMA`` constant and a ``check_schema()``
  guard that validates ``params.json`` carries a compatible
  ``_schema_version`` before any input is loaded.
* ``tests/test_schema_version.py`` covering the happy path plus
  rejection of missing, older, and newer schema stamps.

Changed
+++++++

* ``process_data`` now filters out keys beginning with ``_`` (such as
  ``_schema_version``) before iterating the parameter list, so metadata
  stamps cannot accidentally be treated as input files.

Fixed
+++++

* Legacy ``params.json`` files (pre-v1.1.0, no ``_schema_version`` stamp)
  now produce a clear migration hint instead of a downstream
  ``KeyError`` / ``FileNotFoundError``.


Version 1.1.2 - May 2, 2026
-------------------------------

Added
+++++

* ``tests/test_regression.py``: end-to-end regression test that runs the
  full ``python run.py`` flow on the canonical ``input/`` dataset and
  locks in the final-iteration objective (``1.8793771299e+11``) with a
  1 % tolerance. Set ``PREPSHOT_SKIP_SLOW=1`` to skip it (about 150 s).

Fixed
+++++

* ``prepshot/set_up.py`` now skips underscore-prefixed metadata keys
  (e.g. ``_schema_version``) when iterating ``params.json`` to build the
  argparse list. Without this fix v1.1.1 raised ``TypeError: 'int' object
  is not subscriptable`` at the start of ``initialize_environment``,
  breaking ``python run.py`` end-to-end despite the schema guard inside
  ``process_data`` working in isolation.


Version 1.2.0 - May 2, 2026
-------------------------------

PREP-SHOT is now installable as a Python package.

Added
+++++

* ``pyproject.toml`` at the repo root, declaring ``prepshot`` as an
  installable package with pinned-but-flexible dependency floors. Allows
  ``pip install -e .`` for local development and ``pip install prepshot``
  once published to PyPI.
* ``prepshot/cli.py`` -- ``main()`` entry point that looks for
  ``config.json`` and ``params.json`` in the current working directory.
* ``prepshot/__main__.py`` -- enables ``python -m prepshot`` invocation.
* Console-script entry point ``prepshot`` (declared in
  ``[project.scripts]``).

Changed
+++++++

* ``run.py`` is now a thin backward-compatible shim that delegates to
  ``prepshot.cli.main``. It preserves the legacy file-relative path
  behavior (``config.json`` / ``params.json`` next to ``run.py``), so
  existing ``python run.py`` workflows continue to work unchanged.

Migration notes
+++++++++++++++

* New: ``pip install -e .`` from the repo root, then run ``prepshot``
  (or ``python -m prepshot``) from any directory containing
  ``config.json`` and ``params.json``.
* Existing: ``python run.py`` still works as before -- no action needed.


Version 1.3.0 - May 2, 2026
-------------------------------

Features can now ship with optional input files. New parameters declared
``"required": false`` in ``params.json`` no longer force every existing
input directory to provide a matching Excel file -- a sensible default
is used when the file is absent.

Added
+++++

* ``params.json`` entries support two new keys:

  * ``"required"`` (bool, default ``true``): when ``false``, a missing
    input file is tolerated.
  * ``"default"`` (any, default ``{}``): the value substituted when an
    optional input file is missing. Scalar defaults are wrapped in a
    ``defaultdict`` so model-side tuple-key lookups
    (``params['foo'][z, y]``) keep working unchanged.

* ``tests/test_optional_inputs.py`` covers required-missing-terminates,
  optional-missing-uses-scalar-default, and optional-missing-no-default
  (empty dict).

Changed
+++++++

* The four carbon-market / technology_lower_bound entries in
  ``params.json`` are now marked ``"required": false, "default": 0``,
  so input directories that pre-date v1.1.0 (or any future input dir
  that does not use these features) no longer need to ship the
  zero-filled Excel files.
* ``README.md`` now documents the editable-install path
  (``pip install -e .``) and the ``prepshot`` / ``python -m prepshot``
  console-script entry points introduced in v1.2.0.
* ``doc/source/Installation.rst`` extended with a "Use PREP-SHOT as a
  Python library" section that shows both the high-level
  ``prepshot.cli.main(root_dir=...)`` entry point and the low-level
  ``initialize_environment`` / ``create_model`` / ``solve_model`` flow
  for downstream code that imports PREP-SHOT programmatically.

Removed
+++++++

* ``tests/test_prepshot.py`` -- removed. It exercised the legacy
  ``load_data``, ``read_four_dims``, ``read_three_dims`` etc. APIs
  that were replaced in v0.1.1 by the generic ``read_excel`` helper.
  The test file had been a silent import error since then.

Migration notes
+++++++++++++++

* Existing input directories are unaffected -- the carbon-market files
  shipped in v1.1.0 still load if present.
* When adding new features in the future, prefer ``"required": false,
  "default": ...`` so users only need to prepare files for features they
  actually use. See ``prepshot/load_data.py::load_excel_data``.