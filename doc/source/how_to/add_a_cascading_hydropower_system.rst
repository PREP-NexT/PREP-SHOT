Add a cascading hydropower system
=================================

**Goal.** Introduce a multi-station hydropower cascade (e.g. a new
river basin) into a scenario, with per-station reservoir physics and
inter-station water-delay routing.

This is the heaviest "add a tech" recipe because hydropower stations
are first-class techs in PREP-SHOT (not aggregated). Each station is
its own row in ``tech_registry.csv`` AND has its own reservoir-
parameter rows across ~10 reservoir-specific files. See the
shipped Lower Mekong scenario (``examples/southeast_asia``, 57
stations) and the Thailand scenario (``examples/thailand``, 13
stations) for fully-worked examples.

Steps
-----

**1. Pick station slugs.** No spaces; dots stripped. Example for a
3-station cascade:

.. code-block:: text

    Upper_Dam, Middle_Dam, Lower_Dam

**2. Register each as a hydro tech.** In ``tech_registry.csv``:

.. code-block:: text

    tech,name,carrier,is_storage
    Upper_Dam,Upper Dam,hydro,False
    Middle_Dam,Middle Dam,hydro,False
    Lower_Dam,Lower Dam,hydro,False

The ``carrier='hydro'`` is special-cased; the model loads the
reservoir-physics constraint stack for these techs.

**3. Map each station to a zone.** In ``reservoir_zone.csv``:

.. code-block:: text

    tech,unit,zone
    Upper_Dam,zone_code,BA1
    Middle_Dam,zone_code,BA1
    Lower_Dam,zone_code,BA2

**4. Populate per-station reservoir parameters.** Each of these
files needs one row per station:

.. code-block:: text

    reservoir_capacity_max.csv         (MW, generator nameplate)
    reservoir_capacity_min.csv         (MW, usually 0)
    reservoir_outflow_max.csv          (m^3/s)
    reservoir_outflow_min.csv          (m^3/s, environmental flow)
    reservoir_generation_flow_max.csv  (m^3/s through turbines)
    reservoir_head.csv                 (m, designed)
    reservoir_coefficient.csv          (efficiency, typically ~8.5)

**5. Time-varying inputs.** ``reservoir_inflow.csv`` needs an entry
per ``(station, year, month, hour)``; same for
``reservoir_storage_max.csv`` and ``reservoir_storage_min.csv``
(though these are usually constant within a month). Endpoint
volumes go in ``reservoir_initial_storage_level.csv`` and
``reservoir_final_storage_level.csv``.

**6. Cascade routing.** Define water travel time between connected
stations in ``reservoir_water_delay_time.csv``:

.. code-block:: text

    upstream_tech,downstream_tech,delay
    Upper_Dam,Middle_Dam,2
    Middle_Dam,Lower_Dam,4

Delay is in hours. Stations with no downstream entry are terminal
(water leaves the modeled system).

**7. Piecewise functions.** Two more files describe the non-linear
hydropower physics, both in long-format with per-station rows:

* ``reservoir_forebay_level_volume_function.csv`` -- forebay
  elevation as a function of reservoir volume.
* ``reservoir_tailrace_level_discharge_function.csv`` -- tailrace
  elevation as a function of total discharge.

PREP-SHOT linearizes these inside the head-iteration loop.

**8. Existing capacity (optional).** If the cascade is partly
already built:

.. code-block:: text

    tech,zone,commission_year,unit,capacity
    Upper_Dam,BA1,2020,MW,150
    Middle_Dam,BA1,2020,MW,200

**9. Per-tech files.** Don't forget the eight non-reservoir per-tech
files (lifetime, fuel_price, emission_factor, fixed_OM_cost,
variable_OM_cost, investment_cost, ramp_up, ramp_down) -- each
station needs a row, even if mostly zeros (no fuel, no emissions).

Verify
------

.. code-block:: python

    import xarray as xr
    ds = xr.open_dataset("output/year.nc")

    cascade = ["Upper_Dam", "Middle_Dam", "Lower_Dam"]
    print("Installed:")
    print(ds["install"].sel(tech=cascade).to_pandas())

    print("\nGeneration (sum over time):")
    print(ds["gen"].sel(tech=cascade).sum(["hour", "month", "zone"]).to_pandas())

    # Reservoir trajectories (only when isinflow=true)
    print("\nGeneration flow (sum over hours, by month, year):")
    print(ds["genflow"].sel(station=cascade).sum("hour").to_pandas())

Common pitfalls
---------------

* **Slug consistency.** The same station name must appear in every
  CSV that mentions it: ``tech_registry``, ``reservoir_zone``, all
  the ``reservoir_*`` files, and the per-tech files. Mistyping
  one breaks the load.
* **Cascade direction.** ``upstream_tech`` is always the station the
  water leaves; ``downstream_tech`` is the next station downstream.
  Reversing them silently produces nonsense.
* **Inflow data shape.** ``reservoir_inflow.csv`` is per-(station,
  year, month, hour). With config ``hour=8760, month=1``, that's
  8760 rows per station -- big but unavoidable. Reduce hour count
  during development.
* **Constraints can make the model infeasible.** If
  ``reservoir_outflow_min`` exceeds ``reservoir_outflow_max`` at any
  station, or if the demanded generation exceeds ``capacity_max``
  for too many hours, the LP will be reported infeasible by HiGHS
  with no slack indication. Check your bounds.

Looking at ``examples/southeast_asia/input/`` is the fastest way to
see what a complete 57-station cascade dataset looks like.
