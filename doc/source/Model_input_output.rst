.. _Model_input_output:

Model Inputs/Outputs
=====================

PREP-SHOT loads its inputs from a folder of CSV files and writes its
results to a NetCDF file. ``params.json`` (in the repo root) maps each
model parameter to its CSV file name, declares whether the file is
required, and supplies a default value when an optional file is absent.

Input file format
-----------------

Since v1.5.0, all inputs are **long-format ("tidy") CSV** -- one
dimension column per index plus a single ``value`` column at the end.
Annotation columns named ``unit``, ``name``, ``commodity``, ``comment``,
``note``, ``label``, or any column ending in ``_name`` are treated as
documentation and ignored by the loader. A typical 2-dim file looks
like::

    zone,year,unit,value
    BA1,2020,USD/tonneCO2,0
    BA1,2025,USD/tonneCO2,5
    BA2,2020,USD/tonneCO2,0

Four "Group 3" lookups (carbon emission limits, expansion candidates,
piecewise reservoir functions, water delay matrix, technology registry)
remain wide tables loaded as DataFrames -- they have multiple value
columns and the model code slices them by name.

The current input-file schema version is stamped at the top of
``params.json`` as ``"_schema_version": 2``. See ``Stability.rst`` and
``Changelog.rst`` for migration notes from older releases.

File-name prefixes group inputs by domain:

* ``demand`` -- electricity demand
* ``economic_`` -- discount factors
* ``finance_`` -- (optional) WACC and public-debt accounting
* ``policy_`` -- carbon limits, taxes, offsets
* ``reservoir_`` -- per-station reservoir parameters
* ``storage_`` -- storage-tech parameters
* ``tech_`` -- technology registry, costs, capacity, profiles
* ``transmission_`` -- transmission-line parameters

Inputs
------

Required inputs
~~~~~~~~~~~~~~~

.. list-table::
  :widths: 22 56 22
  :header-rows: 1

  * - Parameter [Unit]
    - Description
    - Input file

  * - demand [MW]
    - Hourly electricity demand by zone, year, and month-hour. PREP-SHOT
      multiplies by ``dt`` internally to convert MW to MWh per timestep,
      matching ``gen`` and ``charge``.
    - demand
  * - economic discount factor [fraction]
    - Discount rate per zone and year. Used to discount fixed, variable,
      and (when finance is OFF) investment cash flows.
    - economic_discount_factor

  * - tech registry [N/A]
    - Per-technology metadata: ``tech``, ``name``, ``carrier`` (free-form
      string -- ``hydro`` is special-cased), ``is_storage`` (boolean
      flag). Drives the model's hydro / storage / dispatchable
      partitioning.
    - tech_registry
  * - tech existing fleet [MW]
    - One row per existing-capacity block: ``(tech, zone,
      commission_year, capacity)``. Sparse -- only non-zero entries
      listed. Replaced ``historical_capacity`` in v1.7.0.
    - tech_existing
  * - tech candidates [MW]
    - Buildable expansion options per ``(zone, tech, year)`` with
      ``capacity_min`` / ``capacity_max`` columns. Absence of an entry
      means "this combination cannot be expanded".
    - tech_candidates
  * - tech capacity max [MW]
    - Upper bound on total installed capacity per ``(zone, tech, year)``.
      ``inf`` disables the cap.
    - tech_capacity_max
  * - tech lifetime [yr]
    - Per-tech, per-vintage lifetime. Looked up at the commissioning
      year, so a unit built in ``cy`` retires at ``cy + lifetime[te,
      cy]``. (Bug fixed in v1.8.1.)
    - tech_lifetime

  * - tech investment cost [dollar/MW]
    - Overnight investment cost per tech and year.
    - tech_investment_cost
  * - tech fixed OM cost [dollar/MW/yr]
    - Fixed O&M cost per tech and year.
    - tech_fixed_OM_cost
  * - tech variable OM cost [dollar/MWh]
    - Variable O&M cost per tech and year.
    - tech_variable_OM_cost
  * - tech fuel price [dollar/MWh]
    - Fuel price per tech and year.
    - tech_fuel_price
  * - tech emission factor [tCO2/MWh]
    - Emission factor per tech, year, and zone.
    - tech_emission_factor
  * - tech ramp up / ramp down [1/MW]
    - Hourly ramp limits per tech and year.
    - tech_ramp_up,
      tech_ramp_down

  * - storage charge / discharge efficiency [fraction]
    - Round-trip efficiency of storage technologies.
    - storage_charge_efficiency,
      storage_discharge_efficiency
  * - storage energy-to-power ratio [MWh/MW]
    - Energy capacity per unit of power capacity for storage
      technologies.
    - storage_energy_to_power_ratio
  * - storage initial level [fraction]
    - Initial state of charge of storage technologies (fraction of
      energy capacity).
    - storage_initial_level

  * - transmission existing [MW]
    - Existing transmission-line capacity per ``(zone1, zone2,
      commission_year)``. Lifetime-driven retirements via
      ``transmission_lifetime``. Symmetric to ``tech_existing``.
    - transmission_existing
  * - transmission candidates [MW]
    - Buildable transmission options per ``(zone1, zone2, year)`` with
      ``capacity_min`` / ``capacity_max`` columns.
    - transmission_candidates
  * - transmission distance [km]
    - Inter-zone distance (drives investment cost).
    - transmission_distance
  * - transmission efficiency [fraction]
    - Per-line transmission efficiency.
    - transmission_efficiency
  * - transmission investment cost [dollar/MW/km]
    - Per-line investment cost (multiplied by distance).
    - transmission_investment_cost
  * - transmission fixed / variable OM cost
    - Per-line fixed and variable O&M costs.
    - transmission_fixed_OM_cost,
      transmission_variable_OM_cost
  * - transmission lifetime [yr]
    - Per-line lifetime; controls retirements of the existing fleet.
    - transmission_lifetime

Hydropower inputs (active when ``isinflow=true`` in ``config.json``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Hydro plants are first-class technologies (``carrier='hydro'`` in
``tech_registry``); these per-station reservoir parameters tie them to
the rest of the model.

.. list-table::
  :widths: 22 56 22
  :header-rows: 1

  * - Parameter [Unit]
    - Description
    - Input file

  * - reservoir zone
    - Maps each hydro station to its home zone.
    - reservoir_zone
  * - reservoir inflow [m**3/s]
    - Hourly inflow per station.
    - reservoir_inflow
  * - reservoir water delay time [N/A]
    - Travel time matrix between connected reservoirs (table format).
    - reservoir_water_delay_time
  * - reservoir coefficient
    - Power-generation coefficient per station.
    - reservoir_coefficient
  * - reservoir head [m]
    - Designed water head per station.
    - reservoir_head
  * - reservoir capacity max / min [MW]
    - Installed-capacity bounds per station.
    - reservoir_capacity_max,
      reservoir_capacity_min
  * - reservoir outflow max / min, generation flow max [m**3/s]
    - Outflow and generation-flow constraints per station, hour, month.
    - reservoir_outflow_max,
      reservoir_outflow_min,
      reservoir_generation_flow_max
  * - reservoir storage max / min [m**3]
    - Volume bounds per station, month, hour.
    - reservoir_storage_max,
      reservoir_storage_min
  * - reservoir initial / final storage level [m**3]
    - Volume of each station at the start / end of each year.
    - reservoir_initial_storage_level,
      reservoir_final_storage_level
  * - reservoir tailrace level-discharge function [m and m**3/s]
    - Piecewise lookup of tailrace level as a function of total discharge
      (table format).
    - reservoir_tailrace_level_discharge_function
  * - reservoir forebay level-volume function [m and m**3]
    - Piecewise lookup of forebay level as a function of volume (table
      format).
    - reservoir_forebay_level_volume_function

Optional inputs (skipped when absent)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
  :widths: 22 56 22
  :header-rows: 1

  * - Parameter [Unit]
    - Description (default when absent)
    - Input file

  * - tech max gen profile [fraction]
    - Time-varying upper bound on dispatch (PyPSA-style ``p_max_pu``).
      Default: ``1`` (no cap below installed capacity). Replaced
      ``capacity_factor`` in v1.8.0.
    - tech_max_gen_profile
  * - tech min gen profile [fraction]
    - Time-varying lower bound on dispatch (``p_min_pu``). Default:
      ``0``. Subsumes the legacy "must-run" behavior.
    - tech_min_gen_profile
  * - tech capacity min [MW]
    - Floor on total installed capacity per ``(zone, tech, year)``.
      Default: ``0``.
    - tech_capacity_min

  * - policy carbon emission limit [tCO2]
    - Cap on net emissions per limit-region (rows carry a comma-separated
      ``zones`` field; one row per region per year). Wide-table format.
    - policy_carbon_emission_limit
  * - policy carbon tax [dollar/tCO2]
    - Per-zone, per-year carbon tax on net emissions. Default: ``0``.
    - policy_carbon_tax
  * - policy carbon offset price [dollar/tCO2]
    - Per-zone, per-year offset price. Default: ``0``.
    - policy_carbon_offset_price
  * - policy carbon offset limit [tCO2]
    - Per-zone, per-year limit on offsets that may be purchased.
      Default: ``0``.
    - policy_carbon_offset_limit

  * - finance public / private debt ratio [fraction]
    - Per-tech share of project capital financed by public and private
      debt. Equity ratio is the residual ``1 - public - private``.
      Activates the v1.9.0 finance module.
    - finance_public_debt_ratio,
      finance_private_debt_ratio
  * - finance cost of public / private debt, private equity [fraction]
    - Per-(tech, zone) cost of each financing tranche. Combined into a
      project-level WACC that discounts construction outlays.
    - finance_cost_of_public_debt,
      finance_cost_of_private_debt,
      finance_cost_of_private_equity
  * - finance public debt max system / zone [dollar]
    - System-wide and per-zone caps on public debt taken in each year.
      ``inf`` (or a missing entry) disables the cap.
    - finance_public_debt_max_system,
      finance_public_debt_max_zone

.. note::

  * ``inf`` in a value cell means "no upper bound" -- the model skips
    the corresponding constraint.
  * Empty cells (NaN) are dropped by the loader for files declared with
    ``"drop_na": true``.
  * The finance module is OFF unless ``finance_public_debt_ratio.csv``
    is provided. With finance OFF, ``inv_factor`` falls back to the
    zonal discount rate -- so a fresh deployment without finance inputs
    matches the v1.8.x objective exactly.

Outputs
-------

Results are written to a NetCDF file (``year.nc`` by default; see
``output_filename`` in ``config.json``). Use `xarray
<https://docs.xarray.dev/en/stable/>`_ to read it; this `tutorial
<https://xiaoganghe.github.io/python-climate-visuals/chapters/data-analytics/xarray-basic.html>`_
is a good entry point.

.. list-table:: Output Variables
  :widths: 26 14 60
  :header-rows: 1

  * - Variable name
    - Unit
    - Description

  * - trans_export
    - MWh per timestep
    - Power dispatched from ``zone1`` toward ``zone2`` in each
      ``(hour, month, year)``, before transmission losses.
  * - gen
    - MWh per timestep
    - Generation per ``(tech, zone, hour, month, year)``.
  * - install
    - MW
    - Total installed capacity per ``(year, zone, tech)`` after
      additions and retirements.
  * - charge
    - MWh per timestep
    - Storage charging energy per ``(tech, zone, hour, month, year)``.
  * - carbon, carbon_breakdown
    - tCO2
    - Total emissions per year, and the per-(year, zone, tech)
      breakdown.
  * - cost
    - dollar
    - Net present value of total system cost over the planning horizon.
  * - cost_var, cost_var_breakdown
    - dollar
    - Variable O&M + fuel cost (total and per-(year, zone, tech)).
  * - cost_fix, cost_fix_breakdown
    - dollar
    - Fixed O&M cost (total and per-(year, zone, tech)).
  * - cost_newtech, cost_newtech_breakdown
    - dollar
    - Discounted investment cost of new tech additions (total and
      per-(year, zone, tech)).
  * - cost_newline, cost_newline_breakdown
    - dollar
    - Discounted investment cost of new transmission lines (total and
      per-(year, zone1, zone2)).
  * - public_debt_newtech [#opt]_
    - dollar
    - Discounted public-debt obligation incurred by new-tech
      investments. Emitted only when the v1.9.0 finance module is
      active.
  * - income
    - dollar
    - Discounted income from water-withdrawal services (only when
      ``isinflow=true``).
  * - genflow, spillflow
    - m**3/s
    - Per-station hydro generation flow and spill flow (only when
      ``isinflow=true``).

.. [#opt] Optional output -- present in the NetCDF file only when
   ``finance_public_debt_ratio.csv`` is provided.

Running scenarios
-----------------

You can swap any single input file at the command line via
``--<param_key> <suffix>``. PREP-SHOT appends the suffix to the
parameter's ``file_name`` and loads the resulting CSV instead. For
example, to run a "low demand" scenario, prepare a
``demand_low.csv`` file in the input folder and invoke::

  python run.py --demand=low

CLI flags are registered by **param key** (the dict key in
``params.json``), not by file name -- the two can diverge after a
file rename.

Setting global parameters
-------------------------

``config.json`` (in the repo root) holds the model-wide settings:

.. list-table::
   :widths: 30 70
   :header-rows: 1
   :align: left

   * - Setting
     - Description

   * - input_folder
     - Folder containing the input CSVs (relative to the repo root).
   * - output_filename
     - Name of the NetCDF results file written under ``output/``.
   * - hour
     - Number of representative hours per period.
   * - month
     - Number of representative months per period.
   * - dt
     - Hours per timestep. ``demand`` is in MW; the balance constraint
       multiplies by ``dt`` to convert to MWh per timestep.
   * - hours_in_year
     - Hours-per-year scalar used for cost rollups (typically 8760).
   * - isinflow
     - Toggles the hydropower / reservoir constraints. With ``false``,
       the model skips all reservoir math.
   * - error_threshold
     - Convergence threshold for the hydropower head-iteration loop.
   * - iteration_number
     - Maximum head-iteration count.
   * - solver
     - Optimization solver: ``highs``, ``gurobi``, ``copt``, ``mosek``,
       etc. (passed through to PyOptInterface).
   * - solver_path
     - Path to the solver's dynamic library; only needed when auto-
       detection fails. See the
       `PyOptInterface setup notes <https://metab0t.github.io/PyOptInterface/getting_started.html#setup-of-optimizers>`_.
   * - solver_parameters
     - Solver-specific options for `mosek
       <https://docs.mosek.com/latest/capi/parameters.html>`_, `gurobi
       <https://www.gurobi.com/documentation/11.0/refman/parameters.html>`_,
       `highs <https://ergo-code.github.io/HiGHS/dev/options/definitions/>`_,
       and `copt <https://guide.coap.online/copt/en-doc/parameter.html>`_.

After tuning ``config.json``, run the model as described in
:ref:`installation`. The shipped ``input/`` folder is a working
self-contained example.
