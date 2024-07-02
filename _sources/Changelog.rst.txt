Changelog
=========

Here, you'll find notable changes for each version of PREP-SHOT.

Version 0.1.0 - Jun 24, 2024
--------------------------------

* PREP-SHOT model is released with basic functionality for energy expansion planning.
* Linear programming optimization model for energy systems with multiple zones.
* Support for solvers such as Gurobi, CPLEX, MOSEK, and GLPK via `Pyomo <https://pyomo.readthedocs.io/en/stable/solving_pyomo_models.html>`_.
* Input and output handling with `pandas` and `Xarray`.

Version 0.1.1 - Jun 24, 2024
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

Deprecated
++++++++++

* Removed dependency on `Pyomo <https://pyomo.readthedocs.io/en/stable/solving_pyomo_models.html>`_ due to high memory usage and slow performance for large-scale models. `For you reference <https://metab0t.github.io/PyOptInterface/benchmark.html>`_.
