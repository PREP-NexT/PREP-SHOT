Add a new technology
====================

**Goal.** Introduce a new generation tech (e.g. ``Geothermal``) into
an existing scenario.

A tech is a row in ``tech_registry.csv`` plus rows in every per-tech
input file. Adding one is mostly mechanical CSV editing; no code
changes.

Steps
-----

**1. Pick a slug and register the tech.** Open
``examples/<scenario>/input/tech_registry.csv`` and add a row:

.. code-block:: text

    tech,name,carrier,is_storage
    Geothermal,Geothermal,geothermal,False

The ``tech`` column is the slug used everywhere else (no spaces, no
dots). The ``carrier`` is a free-form string; pick something
meaningful (``geothermal``, ``nuclear``, ``hydrogen``).

**2. Add rows to every per-tech input file.** The model loads the
following per-tech files; each needs a row for the new tech:

.. code-block:: text

    tech_lifetime.csv             tech_fuel_price.csv
    tech_emission_factor.csv      tech_investment_cost.csv
    tech_fixed_OM_cost.csv        tech_variable_OM_cost.csv
    tech_ramp_up.csv              tech_ramp_down.csv
    tech_capacity_max.csv         tech_capacity_min.csv

For example in ``tech_lifetime.csv``:

.. code-block:: text

    tech,year,unit,value
    Geothermal,2020,years,30

If the new tech has time-varying availability (like solar / wind),
add it to ``tech_max_gen_profile.csv`` as well.

**3. Optionally: existing capacity.** If some Geothermal is already
built before the planning horizon starts, add it to
``tech_existing.csv``:

.. code-block:: text

    tech,zone,commission_year,unit,capacity
    Geothermal,BA1,2020,MW,150

**4. Optionally: expansion candidates.** To allow the optimizer to
build new Geothermal, add rows to ``tech_candidates.csv`` with
non-zero ``capacity_max``:

.. code-block:: text

    zone,tech,year,unit,capacity_min,capacity_max
    BA1,Geothermal,2020,MW,0,inf
    BA1,Geothermal,2025,MW,0,inf

A missing entry means "this combination cannot be expanded";
``capacity_max=0`` has the same effect.

**5. Re-run.**

.. code-block:: bash

    cd examples/<scenario>
    python -m prepshot

Verify
------

Open the output NetCDF and confirm the new tech appears:

.. code-block:: python

    import xarray as xr
    ds = xr.open_dataset("output/year.nc")
    print("Geothermal" in ds.tech.values)        # True
    print(ds["install"].sel(tech="Geothermal"))  # capacity over time

Common pitfalls
---------------

* **Typo in the slug.** Slugs must match exactly across all CSV files
  and ``tech_registry.csv``. The loader raises a ``KeyError`` mid-
  build if any per-tech file is missing the new slug.
* **Forgetting ``tech_capacity_max``.** Missing rows result in a
  ``KeyError``. Use ``inf`` for unbounded.
* **Storage techs need extra files.** If ``is_storage=True`` in the
  registry, also populate ``storage_charge_efficiency.csv``,
  ``storage_discharge_efficiency.csv``,
  ``storage_energy_to_power_ratio.csv``, and
  ``storage_initial_level.csv``.

For hydropower (``carrier='hydro'``), see
:doc:`add_a_cascading_hydropower_system` -- the reservoir physics
adds another ~10 files per tech.
