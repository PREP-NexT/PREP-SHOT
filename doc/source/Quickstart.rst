.. _Quickstart:

Quickstart (30 minutes)
=======================

Goal: take a fresh checkout of PREP-SHOT, solve the shipped example,
read the results, change one input, and re-solve -- all in about
half an hour. No prior knowledge of capacity-expansion modeling is
assumed; everything happens against the ``input/`` folder that comes
with the repo.

If anything in this page does not work for you, please open a `GitHub
issue <https://github.com/PREP-NexT/PREP-SHOT/issues>`_ -- we read
every report and a broken Quickstart is the bug we most want to know
about.


Step 1 -- Install (5 minutes)
-----------------------------

PREP-SHOT requires Python 3.9 or newer. Conda is recommended so the
optimization-solver dependencies stay isolated::

  conda create -n prep-shot python=3.11 -y
  conda activate prep-shot

  git clone https://github.com/PREP-NexT/PREP-SHOT.git
  cd PREP-SHOT
  pip install -e .

The default solver is the open-source `HiGHS
<https://highs.dev/>`_, installed automatically as a wheel. To use a
commercial solver (Gurobi, COPT, MOSEK) instead, set ``solver`` in
``config.json`` -- see :ref:`Model_input_output`.


Step 2 -- Solve the shipped example (5 minutes)
-----------------------------------------------

The repo ships a self-contained 3-zone, 11-year example in
``input/``. Solve it with::

  python run.py

You will see the solver log scroll by; on commodity hardware the
default settings (48 hours, 1 representative month, 3 head
iterations) finish in around 2 minutes. The last line should
report::

  Objective value : 1.8809...e+11

and ``output/year.nc`` will appear. That NetCDF file is the result
artifact -- everything in the rest of this page reads from it.

If the solve does not finish within a few minutes, lower
``hour`` to ``24`` and ``iteration_number`` to ``1`` in
``config.json`` to get a quicker (less accurate) sanity solve.


Step 3 -- Open the results (10 minutes)
---------------------------------------

PREP-SHOT writes results in `xarray <https://docs.xarray.dev>`_'s
NetCDF format, so any tool that reads NetCDF can consume them. From
Python::

  import xarray as xr
  ds = xr.open_dataset("output/year.nc")
  print(ds.data_vars)

You will see entries like ``gen``, ``install``, ``charge``,
``trans_export``, ``cost_newtech_breakdown``,
``shadow_price_demand``, etc. Full list and units in
:ref:`Model_input_output`.

**Three things worth a first look:**

1. **Total cost.** A single number, the NPV of system cost over the
   planning horizon::

     print(f"Total cost: ${float(ds.cost):,.0f}")

2. **Installed capacity over time.** Which technologies expanded,
   in which zones, and when::

     install_by_year = ds["install"].sum("zone").to_pandas()
     print(install_by_year)         # rows: year, cols: tech

3. **Locational marginal prices (shadow prices on demand).**
   This is the dual of the power-balance constraint -- the
   marginal cost of one extra MWh of demand at each
   ``(hour, month, year, zone)``. Useful for diagnosing where
   the system is most stressed::

     # LMPs at zone BA1 in 2025, averaged over the modeled month:
     lmp = ds["shadow_price_demand"].sel(zone="BA1", year=2025).mean("month")
     print(lmp)                     # one value per hour

Values in ``shadow_price_demand`` are **NPV-discounted** dollars
per MWh. To recover undiscounted real-year prices, divide by the
year's variable-cost factor (computed in
``prepshot.load_data.compute_cost_factors``).

A minimal generation-mix chart::

  import matplotlib.pyplot as plt
  gen_by_tech = (
      ds["gen"]
      .sum(["hour", "month", "zone"])  # sum over time and space
      .to_pandas()                     # rows=year, cols=tech
  )
  gen_by_tech.plot.area(figsize=(8, 4))
  plt.ylabel("Generation (MWh)")
  plt.title("Generation mix over the planning horizon")
  plt.tight_layout()
  plt.savefig("gen_mix.png", dpi=120)


Step 4 -- Change one input and re-solve (5 minutes)
---------------------------------------------------

Every input is a CSV under ``input/``. To see how the model
responds to a change, try one of these single-file edits.

**Option A -- bump demand 20% in one zone.** Open
``input/demand.csv`` (long format: ``zone, year, month, hour, unit,
value``) and multiply the BA1 column by 1.2 in your editor of
choice. Then::

  python run.py

The objective will rise -- the model has to build more capacity or
import more from neighboring zones to serve the extra load.
``shadow_price_demand`` at BA1 should also increase in the most
constrained hours.

**Option B -- introduce a carbon tax.** Open
``input/policy_carbon_tax.csv`` and replace the ``value`` column
with a non-zero number (e.g. ``50`` USD/tonneCO2). Re-run; the
generation mix should shift away from coal and gas toward zero-
carbon technologies, raising ``cost_carbon`` in the breakdown.

**Tip -- run scenarios without overwriting your baseline.** Save
your modified file as ``input/demand_high.csv`` and run::

  python run.py --demand=high

PREP-SHOT appends the suffix to the file name, so the baseline
``demand.csv`` is left untouched. Output goes to
``output/year_high.nc``.


Step 5 -- Where to next
-----------------------

* :ref:`Model_input_output` -- full input / output reference, including
  optional carbon-market and finance modules.
* :ref:`Tutorial` -- the same shipped example, with more context on
  the modeled scenario (3 balancing authorities, 15 hydropower
  stations, 2020-2030 zero-carbon pathway).
* :doc:`Mathematical_notations` -- the underlying linear program.
* :doc:`Changelog` -- what's new in each release.

If you used PREP-SHOT in published work, please cite it -- see
:ref:`citation`. And if you ran into something rough, the fastest
fix is to file an issue on `GitHub
<https://github.com/PREP-NexT/PREP-SHOT/issues>`_.
