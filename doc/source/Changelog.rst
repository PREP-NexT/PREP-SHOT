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


Version 1.3.1 - May 2, 2026
-------------------------------

Security / dependency hygiene release. Bumps declared dependency floors
to clear known CVEs in the previously pinned old releases (the
v0.1.x-era pins were 2-4 years old).

Changed
+++++++

* ``pyproject.toml`` and ``requirements.txt`` floors raised to:

  * ``numpy>=1.26.0,<2.0``
  * ``scipy>=1.11.4``
  * ``pandas>=1.5.3,<2.0``
  * ``xarray>=2023.4.0,<2024``
  * ``openpyxl>=3.1.2``
  * ``xlsxwriter>=3.1.0``

* ``pandas`` and ``numpy`` are temporarily capped below 2.0 because
  pandas 2.x's ``DataFrame.unstack`` no longer accepts duplicate
  column-level values (which the wide input format relies on). The
  cap will be lifted in a future release once ``read_excel`` is
  rewritten to not rely on ``unstack``.

Tested with
+++++++++++

* numpy 1.26.4, scipy 1.13.1, pandas 1.5.3, xarray 2023.12.0,
  openpyxl 3.1.5, xlsxwriter 3.2.9, pyoptinterface 0.2.5,
  highsbox 1.7.0. Full test suite (13 tests) passes.

Migration notes
+++++++++++++++

* Existing environments should run ``pip install -U -r requirements.txt``
  (or ``pip install -e .`` if you use the editable install) to pick up
  the bumped dependency versions.


Version 1.3.2 - May 2, 2026
-------------------------------

Continuous-integration release. The full unit-test suite now runs
automatically on every push and pull request via GitHub Actions.

Added
+++++

* ``.github/workflows/test.yml``: matrix-tests on Python 3.9 / 3.10 /
  3.11. Runs the fast unit tests (schema, optional inputs, utils) on
  every push and PR; runs the slow end-to-end regression test only on
  pushes to ``main`` to keep PR feedback fast.

The fast tests give contributors a quick green/red signal on every PR;
the regression test on ``main`` catches any change that would alter the
model's optimal objective on the canonical ``input/`` dataset.


Version 1.4.0 - May 2, 2026
-------------------------------

PREP-SHOT now supports long-format ("tidy") CSV inputs as a parallel
option to the wide-Excel format. New parameters can be born long-format
without disturbing existing wide-format inputs; existing parameters can
migrate one at a time when convenient.

Why long-format
+++++++++++++++

Adding a dimension to a long-format file is a non-breaking column add,
not a reshape. This eliminates the recurring "the bound files were
reshaped from (tech, zone) to (zone, tech, year)" class of breakage,
which historically required migrating every existing input directory.

Long-format is the canonical input shape used by OSeMOSYS, GenX,
Switch, and PyPSA -- researchers familiar with those tools will find
the convention intuitive.

Added
+++++

* ``prepshot/load_data.py::read_long_csv`` -- new reader for tidy CSVs.
  Convention: dimension columns first, value column last. Output dict
  shape matches what the wide-format reader produces for the same
  parameter (scalar keys for 1 dim, tuple keys for 2+ dims), so model
  code is unchanged regardless of which format is on disk.
* ``params.json`` entries support a new ``"format": "long"`` key.
  When set, the loader looks for ``<file_name>.csv`` instead of
  ``<file_name>.xlsx``, and skips the wide-format-specific keys
  (``index_cols``, ``header_rows``, ``unstack_levels``,
  ``first_col_only``).
* ``tests/test_long_format.py`` -- 7 unit tests covering 1-dim, 2-dim,
  and 3-dim CSV reading; NaN-row dropping; format dispatch in
  ``load_excel_data``; and the optional-input fallback for long-format.

Changed
+++++++

* ``carbon_tax`` migrated from wide-Excel to long-CSV as the working
  demonstration of the new format. ``input/carbon_tax.csv`` and
  ``southeast_asia/carbon_tax.csv`` replace the corresponding
  ``carbon_tax.xlsx`` files. The data and model behavior are identical
  -- the regression test passes unchanged at ``1.879e+11`` objective.

Migration notes
+++++++++++++++

* No action needed for existing input directories that are not based
  on the canonical ``input/`` -- their wide-format files keep working.
* Users with custom ``carbon_tax.xlsx`` files who pull v1.4.0 should
  convert them to ``carbon_tax.csv`` (zone, year, value columns) and
  drop the old xlsx, since ``params.json`` now declares carbon_tax as
  long-format.
* Future features should prefer long-format from the start.


Version 1.5.0 - May 2, 2026
-------------------------------

.. note::
   **Schema bump 1 -> 2.** This is a breaking input-format change.
   Existing input directories must be migrated. See migration notes
   below.

Every input is now a CSV. The unstack-based wide-Excel code path is
no longer used by the loader at runtime, though ``read_excel`` remains
in ``prepshot/load_data.py`` for the migration tool's benefit (a full
v1.4.x -> v1.5.0 migration tool is on the v1.6.0 roadmap).

The ``pandas<2.0`` cap from v1.3.1 is *still in place* in v1.5.0 because
``read_excel`` (used by the migration tool) calls ``unstack``. Once the
migration tool no longer needs ``read_excel`` (v1.6.0), the cap will
be lifted.

Added
+++++

* ``tools/migrate_to_long.py`` -- runnable migration script that
  converts a directory of wide-format Excel inputs to long-format CSVs
  using the legacy params.json spec for shape information. Run as::

      python tools/migrate_to_long.py /path/to/your/input_dir

* Tailored schema-1 -> schema-2 migration hint in ``check_schema``:
  users feeding a v1.4.x or earlier params.json now get a clear
  pointer at ``tools/migrate_to_long.py`` instead of a generic version
  mismatch error.

Changed (Breaking)
++++++++++++++++++

* ``params.json`` schema bumped to ``_schema_version: 2``. Files with
  ``_schema_version: 1`` are rejected with a migration hint.
* All Group-1/2 parameters in ``input/`` and ``southeast_asia/`` have
  been converted from wide ``.xlsx`` to long ``.csv``:

  - Capacity / cost: ``technology_*``, ``transmission_line_*``,
    ``capacity_factor``, ``new_technology_*_bound``, ``lifetime``,
    ``fuel_price``, ``technology_portfolio``, ``technology_type``,
    ``historical_capacity``, ``initial_energy_storage_level``,
    ``charge_efficiency``, ``discharge_efficiency``,
    ``energy_to_power_ratio``, ``ramp_up``, ``ramp_down``.
  - Time-series / spatial: ``demand``, ``inflow``,
    ``predefined_hydropower``, ``distance``,
    ``reservoir_storage_upper_bound``, ``reservoir_storage_lower_bound``,
    ``initial_reservoir_storage_level``,
    ``final_reservoir_storage_level``.
  - Domain: ``carbon_emission_limit``, ``emission_factor``,
    ``carbon_offset_price``, ``carbon_offset_limit``, ``discount_factor``.

* ``params.json`` entries for migrated parameters now declare just
  ``"format": "long"`` plus ``drop_na`` (and ``required``/``default``
  if optional). The wide-format-specific keys (``index_cols``,
  ``header_rows``, ``unstack_levels``, ``first_col_only``) are dropped.

Annotation columns
++++++++++++++++++

Long-format CSVs now support **annotation columns** -- human-readable
metadata that lives alongside the data but is ignored by the model
loader. Following the TransitionZero convention:

* Every long CSV has a ``unit`` column (e.g. ``MWh``, ``USD/tonneCO2``,
  ``m3/s``).
* The eight per-field reservoir CSVs additionally have a ``name``
  column with the human-readable station name (e.g. "Grand Coulee")
  alongside the ``stcd`` ID.

The loader filters out columns whose name (case-insensitive) is in
the annotation set ``{unit, units, name, commodity, comment, comments,
description, desc, note, notes, label}``, or that ends in ``_name``
(``zone_name``, ``tech_name``, etc.). These columns never appear in
the dim-key tuples, so model code is unaffected.

Two new unit tests cover annotation handling:
``test_unit_column_filtered`` and
``test_name_and_other_annotation_columns_filtered``.

Column renames for clarity
++++++++++++++++++++++++++

Several cryptic abbreviations have been replaced with self-describing
names across the input CSVs and model code:

* ``stcd`` (and ``station`` for params that previously used that name)
  -> ``station_id`` everywhere -- inputs, ``model.station``,
  ``params['station_id']``, local variables.
* ``POWER_ID`` / ``NEXTPOWER_ID`` (water_delay_time)
  -> ``upstream_station_id`` / ``downstream_station_id``.
* ``Z`` / ``Q`` / ``V`` in the piecewise-function lookups
  -> ``tailrace_level`` / ``discharge`` / ``forebay_level`` /
  ``volume`` (the same axis was being repurposed: ``Z`` meant
  tailrace level in one file and forebay level in the other).
* ``coeff`` -> ``coefficient``, ``GQ_max`` -> ``generation_flow_max``,
  ``N_min`` / ``N_max`` -> ``capacity_min`` / ``capacity_max`` for the
  per-field reservoir CSVs.

Group 3 migration
+++++++++++++++++

The four "table-shaped" parameters are now CSVs as well:

* ``water_delay_time``, ``reservoir_tailrace_level_discharge_function``,
  ``reservoir_forebay_level_volume_function`` -- already 3-column long
  internally; resaved as CSV and loaded via the new ``format: "table"``
  dispatch (returns a DataFrame for downstream ``groupby``/column
  access).
* ``reservoir_characteristics`` -- previously one wide table with ~13
  fields per station -- has been **split into 8 single-field long
  CSVs**, one per field the model actually uses:

  - ``reservoir_zone``, ``reservoir_coefficient``,
    ``reservoir_outflow_min``, ``reservoir_outflow_max``,
    ``reservoir_generation_flow_max``, ``reservoir_capacity_min``,
    ``reservoir_capacity_max``, ``reservoir_head``.

  Four field renames in the process (``coeff`` -> ``coefficient``,
  ``GQ_max`` -> ``generation_flow_max``, ``N_min`` -> ``capacity_min``,
  ``N_max`` -> ``capacity_max``) for clarity. The three descriptive
  fields (``name``, ``short_name``, ``type``) that the model never
  referenced have been dropped.

* ``params.json`` gains a new ``"format": "table"`` value alongside
  ``"format": "long"`` for parameters consumed as DataFrames rather
  than dicts.

Model code (9 sites in ``hydro.py`` / ``head_iteration.py`` /
``load_data.py``) updated to read from the new per-field params:
``params['reservoir_characteristics']['<field>', s]`` becomes
``params['reservoir_<field>'][s]``. The end-to-end regression test
confirms the model objective is unchanged after the refactor.

Migration notes
+++++++++++++++

The shipped ``input/`` and ``southeast_asia/`` directories are already
in v1.5.0 shape. For custom input directories (e.g. scenario forks
such as ``input_s100_baseline_*``):

* ``tools/migrate_to_long.py`` covers the dict-shape parameters; run::

      python tools/migrate_to_long.py /path/to/your/input_dir

* The four Group-3 parameters and ``reservoir_characteristics``'s
  field-split are not yet automated. Until the v1.6.0 expanded
  migration tool ships, use the shipped ``input/`` directory as a
  reference for the new file shapes, or open an issue if you need
  porting help.

Custom ``params.json`` files (i.e. anyone who has forked params.json)
will need to mirror the canonical v1.5.0 file shipped in this release:
metadata stamp ``"_schema_version": 2``, then minimal long-format
entries (``"format": "long"`` / ``"format": "table"``) without the
legacy wide-format keys.


Version 1.6.0 - May 3, 2026
-------------------------------

Cleanup release. The wide-Excel reading machinery is removed, the
migration tool is rewritten to work under pandas >= 2.0, and the
``pandas<2.0`` / ``numpy<2.0`` caps from v1.3.1 are lifted.

Removed
+++++++

* ``prepshot.load_data.read_excel`` -- deleted. Nothing in the runtime
  path used it after v1.5.0; the migration tool now has its own
  ``pd.read_excel`` call.

Changed
+++++++

* ``tools/migrate_to_long.py`` rewritten to be self-contained:

  - Bundles its own copy of the v1.4.x wide-format spec (since the
    on-disk ``params.json`` is now v1.5.0 long-format and no longer
    carries that information).
  - Uses a custom ``flatten_wide_to_dict`` helper that replicates the
    v1.4.x ``unstack``-based key ordering by direct cell iteration.
    Works under pandas >= 2.0 (which rejects ``unstack`` on
    DataFrames with duplicate column-level values).
  - Verified to produce byte-equivalent output to the shipped
    v1.5.0 ``input/`` CSVs (modulo annotation columns) for all 38
    dict-shape parameters.

* ``pyproject.toml`` and ``requirements.txt`` floors raised:

  - ``numpy>=1.26.0`` (no upper cap)
  - ``pandas>=2.0.0`` (no upper cap)
  - ``xarray>=2023.10.0`` (no upper cap)

* Tested with numpy 2.0.2, pandas 2.3.3, xarray 2024.7.0; full
  test suite passes (22 tests, end-to-end regression objective
  unchanged at 1.879e+11).

Fixed
+++++

* ``np.Inf`` references in ``prepshot/_model/investment.py`` and
  ``prepshot/_model/co2.py`` replaced with ``np.inf`` (``np.Inf``
  was removed in numpy 2.0).


Version 1.7.0 - May 3, 2026
-------------------------------

Data-model cleanup ahead of the v1.8.0 PyPSA-style API. The
existing-fleet representation is reshaped from an awkward
``(zone, tech, age)`` "historical capacity" table to a tidy
``(tech, zone, commission_year)`` "existing fleet" table, and the
single-purpose ``technology_type`` file is renamed to ``technologies``
so it can grow into a per-tech registry.

Added
+++++

* ``input/existing_fleet.csv`` and ``southeast_asia/existing_fleet.csv``
  -- one row per existing-capacity block (tech, zone, commission year,
  capacity). Sparse representation: only non-zero entries are listed.
* ``technologies.csv`` (replaces ``technology_type.csv``) with columns
  ``tech`` and ``type``. Designed to grow into a richer per-tech
  registry (e.g. ``description``, ``category``, ``co2_intensity_class``)
  alongside the v1.8.0 API work.

Removed
+++++++

* ``historical_capacity.csv`` -- replaced by ``existing_fleet.csv``.
  The ``age`` dimension is gone; capacity blocks now record an
  explicit ``commission_year``, which is unambiguous and survives
  schedule shifts.
* ``technology_portfolio.csv`` -- file existed in the schema but was
  never referenced by any model rule (all values were 0 in the
  shipped data). Dead code; deleted.
* ``technology_type.csv`` -- renamed to ``technologies.csv`` (see
  Added).

Changed
+++++++

* ``prepshot/_model/investment.py::tech_lifetime_rule`` rewritten:

  - **Before:** sum ``historical_capacity[zone, tech, age]`` for
    ``age`` in ``[0, lifetime - service_time)``.
  - **After:** sum ``existing_fleet[tech, zone, commission_year]``
    for all commission years where
    ``commission_year <= y < commission_year + lifetime``.

  The two formulations are mathematically equivalent for the shipped
  data; the regression test confirms the model objective is unchanged
  at ``1.879e+11``.

* ``prepshot/load_data.py::extract_sets`` derives the ``tech`` set
  from ``technologies`` (was ``technology_type``).
* ``prepshot/model.py::define_basic_sets`` reads tech categories from
  ``technologies`` (was ``technology_type``).
* ``prepshot/_model/hydro.py`` reads the hydro-tech list from
  ``technologies`` (was ``technology_type``).


Version 1.8.0 - May 3, 2026
-------------------------------

PyPSA-style data model. The fixed ``resource_type`` enum is replaced
with a free-form ``carrier`` string plus boolean per-tech behavior
flags; any tech can now bound its dispatch with time-varying
``p_max_pu`` / ``p_min_pu`` profiles, removing the need for separate
``capacity_factor`` and ``must_run`` paths. Hydro plants are first-class
techs (carrier ``hydro``) instead of an aggregate ``Hydro``. Input
files gain consistent domain prefixes (``tech_``, ``reservoir_``,
``transmission_``, ``storage_``, ``policy_``, ``economic_``) and
adopt ``max`` / ``min`` instead of mixed ``upper_bound`` / ``lower_bound``.
Existing capacity and candidates are now structured symmetrically for
both plants and transmission lines.

The regression test confirms the model objective is unchanged at
``1.880e+11`` for the canonical ``input/`` dataset across all
intermediate refactors.

Added
+++++

* ``input/tech_registry.csv`` (was ``technologies.csv``) -- per-tech
  registry with columns ``tech``, ``name``, ``carrier``, ``is_storage``.
  Replaces the rigid ``resource_type`` enum.
* ``input/tech_max_gen_profile.csv`` and
  ``input/tech_min_gen_profile.csv`` -- optional time-varying upper /
  lower bounds on dispatch (PyPSA's ``p_max_pu`` / ``p_min_pu``).
  Subsumes the ``capacity_factor`` and ``must_run`` paths.
* ``input/transmission_candidates.csv`` -- symmetric counterpart to
  ``tech_candidates.csv`` for new transmission lines, with columns
  ``zone1, zone2, year, unit, capacity_min, capacity_max``.
* ``input/transmission_existing.csv`` -- now keyed by
  ``(zone1, zone2, commission_year)`` and respects ``transmission_lifetime``,
  matching the existing-fleet structure for plants.
* Per-zone discount factor: ``input/economic_discount_factor.csv`` is
  keyed by ``(zone, year)``; cost factors propagate through ``cost.py``.
* Custom carbon-emission-limit regions in
  ``input/policy_carbon_emission_limit.csv``: each row carries a
  comma-separated ``zones`` field, allowing arbitrary multi-zone
  caps without per-zone duplication.

Removed
+++++++

* ``prepshot/_model/nondispatchable.py`` -- subsumed by the unified
  ``gen_up_bound_rule`` / ``gen_low_bound_rule`` in
  ``prepshot/_model/generation.py``.
* ``predefined_hydropower.csv`` and the ``must_run`` else-branch in
  ``hydro.py`` -- replaced by ``tech_min_gen_profile.csv``.
* ``capacity_factor.csv`` -- replaced by ``tech_max_gen_profile.csv``.

Changed
+++++++

* **Naming sweep:** all ``upper_bound`` / ``lower_bound`` files,
  param keys, and DataFrame columns renamed to ``max`` / ``min``:

  - ``tech_upper_bound.csv`` -> ``tech_capacity_max.csv``
  - ``tech_lower_bound.csv`` -> ``tech_capacity_min.csv``
  - ``reservoir_storage_upper_bound.csv`` -> ``reservoir_storage_max.csv``
  - ``reservoir_storage_lower_bound.csv`` -> ``reservoir_storage_min.csv``
  - ``tech_candidates.csv`` columns ``lower_bound`` / ``upper_bound``
    -> ``capacity_min`` / ``capacity_max``
  - ``transmission_candidates.csv`` columns: same rename.

* **File prefixes:** input files regrouped by domain.
  ``hydro_inflow.csv`` -> ``reservoir_inflow.csv``;
  ``charge_efficiency.csv`` -> ``storage_charge_efficiency.csv``;
  ``carbon_tax.csv`` -> ``policy_carbon_tax.csv``;
  ``discount_factor.csv`` -> ``economic_discount_factor.csv``; etc.
* **Hydro plants are first-class techs.** Each plant appears in
  ``tech_registry.csv`` with ``carrier='hydro'``; reservoir
  parameters are keyed per station (no ``main_hydro`` aggregation).
* **Demand units.** ``demand.csv`` now carries instantaneous power
  in MW (PyPSA convention). The nodal balance constraint multiplies
  by ``dt`` to convert to MWh per timestep, matching ``gen`` /
  ``charge`` which were already in MWh.
* ``prepshot/model.py::define_basic_sets`` derives ``hydro_tech``,
  ``storage_tech``, and ``dispatchable_tech`` from the registry's
  ``carrier`` and ``is_storage`` columns rather than a fixed enum.
* ``prepshot/_model/generation.py`` defines a single pair of
  generation bound rules using ``p_max_pu`` / ``p_min_pu`` lookups,
  replacing the per-resource-type branches.
* ``prepshot/_model/transmission.py`` builds existing transmission
  capacity by summing over ``(zone1, zone2, commission_year)`` entries
  still in service, mirroring ``tech_lifetime_rule``.


Version 1.8.1 - May 3, 2026
-------------------------------

Fixed
+++++

* ``prepshot/_model/investment.py``: retirement check now looks up
  ``lifetime`` at the commissioning year, not the current modeled
  year, so units built at vintage ``cy`` retire after
  ``cy + lifetime[te, cy]`` regardless of any later parameter
  changes. Bug present in two locations:

  - ``tech_lifetime_rule`` (existing-fleet retirement, introduced
    by the v1.7.0 refactor): ``lifetime[te, y]`` -> ``lifetime[te, cy]``.
  - ``remaining_capacity_rule`` (new-build retirement, original
    PR #47 by Quan YUAN): ``lt[te, y]`` -> ``lt[te, yy]``.

  The shipped ``input/tech_lifetime.csv`` has constant lifetime
  across years for every tech, so the regression objective is
  unchanged at ``1.880e+11``. The bug only manifests when users
  supply time-varying lifetimes (e.g. modeling tech improvement).


Version 1.9.0 - May 3, 2026
-------------------------------

Optional finance module: weighted-average cost of capital (WACC) for
new-build investment, plus public-debt accounting and caps.
Backported from the dev branch (commit ``bfd9de6``, "add finance
module") and adapted to the v1.8.x long-format / per-zone /
``max``-naming conventions. The feature is OFF by default; the
regression objective is unchanged at ``1.880e+11`` for the canonical
``input/`` dataset.

Added
+++++

* ``prepshot/_model/finance.py`` with ``AddFinanceConstraints``:

  - ``public_debt_newtech[y, z, te]`` -- discounted public-debt
    obligation incurred by each new-tech investment, exported in
    the ``year.nc`` results.
  - System-wide cap: ``sum over (z, te) of public_debt_newtech[y, z, te]
    <= public_debt_max_system[y]``. Skipped when missing or
    ``+inf``.
  - Per-zone cap: ``sum over te of public_debt_newtech[y, z, te]
    <= public_debt_max_zone[z, y]``. Same skip behavior.

* ``prepshot/utils.py::calc_interest_rate`` -- weighted-average cost
  of capital from public-debt / private-debt / equity tranches.
* Seven new optional inputs (all ``required: false``):
  ``finance_public_debt_ratio.csv`` (per-tech),
  ``finance_private_debt_ratio.csv`` (per-tech),
  ``finance_cost_of_public_debt.csv`` (per-tech, per-zone),
  ``finance_cost_of_private_debt.csv`` (per-tech, per-zone),
  ``finance_cost_of_private_equity.csv`` (per-tech, per-zone),
  ``finance_public_debt_max_system.csv`` (per-year),
  ``finance_public_debt_max_zone.csv`` (per-zone, per-year).

Changed
+++++++

* ``prepshot/load_data.py::compute_cost_factors`` -- when finance
  inputs are present, ``inv_factor[tech, year, zone]`` discounts
  the construction outlay at the project-level WACC instead of the
  zonal discount rate. Fixed/variable/transmission factors continue
  to use the zonal discount rate. With finance OFF (no inputs),
  ``WACC == discount_rate`` and the legacy behavior is preserved.
* ``prepshot/model.py::create_model`` -- ``AddFinanceConstraints``
  is wired in only when ``params['public_debt_ratio']`` is
  populated, so users without finance inputs see no extra
  variables, constraints, or output variables.
* ``prepshot/output_data.py::extract_results_non_hydro`` -- emits
  ``public_debt_newtech`` only when finance is enabled.

Notes
+++++

* The dev-branch commit used wide-Excel inputs and ``np.Inf``;
  this backport uses long-format CSV, ``np.inf``, and the
  v1.8.0 ``max``/``min`` naming convention (e.g.
  ``public_debt_max_system`` rather than
  ``public_debt_upper_bound_system``).
* Cap rules treat both missing entries and ``+inf`` as "no
  constraint", matching the candidates / carbon-emission-limit
  conventions elsewhere in the model.


Version 1.9.1 - May 3, 2026
-------------------------------

Added
+++++

* New output variable ``shadow_price_demand`` -- the dual of the
  nodal power-balance constraint, exposing the locational marginal
  price (LMP) at each ``(hour, month, year, zone)``. Sign is
  flipped from the raw dual so positive values mean "more
  expensive to serve more demand", matching the convention used by
  PyPSA / Switch / GenX. Discounted to NPV; divide by
  ``var_factor[year, zone]`` to recover undiscounted real-year
  prices.
* ``prepshot/output_data.py::create_data_array`` gained an
  ``extractor`` parameter so the same helper can lift either primal
  values (``model.get_value``, the default) or duals
  (``model.get_constraint_dual``) out of a tupledict.

Notes
+++++

* The shadow-price extraction is wrapped in a try/except: if the
  solver does not return duals (e.g. for a MIP solve, or after an
  infeasible run), a warning is logged and the variable is omitted
  from the NetCDF file rather than aborting the run.