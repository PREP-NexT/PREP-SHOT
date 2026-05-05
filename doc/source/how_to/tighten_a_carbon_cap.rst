Tighten a carbon cap
====================

**Goal.** Run a counterfactual with a stricter system-wide CO2 cap
without overwriting the baseline.

PREP-SHOT registers a CLI flag for every input file in
``params.json``. Pass ``--<param>=<suffix>`` and PREP-SHOT loads
``<file>_<suffix>.csv`` instead of ``<file>.csv``. Output names get
the same suffix.

Steps
-----

**1. Copy the baseline policy file as a new variant.** From inside
``examples/<scenario>/input/``:

.. code-block:: bash

    cd examples/southeast_asia/input
    cp policy_carbon_emission_limit.csv policy_carbon_emission_limit_tight.csv

**2. Edit the new file's 2030 cap.** The schema is
``(limit_id, year, unit, value, zones)``. Open in your editor and
change the cap from ``146000000`` (baseline) to ``80000000`` (about
55% of baseline):

.. code-block:: text

    limit_id,year,unit,value,zones
    system_cap,2020,tonneCO2,inf,"Cambodia,Laos,Myanmar,Thailand,Vietnam"
    system_cap,2030,tonneCO2,80000000.0,"Cambodia,Laos,Myanmar,Thailand,Vietnam"

**3. Re-run with the variant flag.**

.. code-block:: bash

    cd examples/southeast_asia
    python -m prepshot --carbon_emission_limit=tight

Output goes to ``output/baseline_tight.nc`` (or whatever your
``output_filename`` is, with ``_tight`` appended).

Verify
------

Compare baseline vs tight by total cost and by 2030 emissions:

.. code-block:: python

    import xarray as xr

    base = xr.open_dataset("output/baseline.nc")
    tight = xr.open_dataset("output/baseline_tight.nc")

    print(f"Cost delta:       ${float(tight.cost) - float(base.cost):,.0f}")
    print(f"2030 emissions baseline: {float(base.carbon.sel(year=2030)):,.0f} tCO2")
    print(f"2030 emissions tight:    {float(tight.carbon.sel(year=2030)):,.0f} tCO2")

The tight cap forces the model to either build more zero-carbon
capacity, dispatch existing zero-carbon capacity harder, or import
clean power from neighboring zones -- whichever is cheapest.

Custom cap regions
------------------

The ``zones`` column accepts any comma-separated subset. For a
Vietnam-only cap:

.. code-block:: text

    limit_id,year,unit,value,zones
    vietnam_cap,2030,tonneCO2,40000000.0,Vietnam

Multiple ``limit_id`` rows for the same year stack as additional
constraints.

Common pitfalls
---------------

* **Quote the zones string.** A comma inside an unquoted CSV cell
  splits the column. Always wrap multi-zone lists in double quotes.
* **The CLI suffix must be a valid filename suffix.**
  ``--carbon_emission_limit=tight`` looks for
  ``policy_carbon_emission_limit_tight.csv``, NOT
  ``policy_carbon_emission_limit-tight.csv``.
* **All cap regions must use existing zone names.** A typo
  silently produces a constraint that's vacuously satisfied (no
  zones contribute), giving you the wrong answer rather than an
  error. Double-check zone spelling against ``demand.csv``.
