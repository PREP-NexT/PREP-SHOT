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