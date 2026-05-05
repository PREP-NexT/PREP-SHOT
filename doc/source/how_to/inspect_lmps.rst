Inspect locational marginal prices
==================================

**Goal.** Read PREP-SHOT's :term:`LMP` output and use it to diagnose
binding constraints, compare zones, and back-cast wholesale-price
trajectories.

LMPs are the dual of the nodal power-balance constraint -- the
marginal cost of one extra MWh of demand at each ``(hour, month,
year, zone)``. PREP-SHOT exposes them as ``shadow_price_demand``
in the result NetCDF since v1.9.1.

Recipe
------

.. code-block:: python

    import xarray as xr
    import pandas as pd

    ds = xr.open_dataset("output/year.nc")
    lmp = ds["shadow_price_demand"]   # dims: (hour, month, year, zone)

    # 1. Average LMP by zone and year
    lmp_avg = lmp.mean(["hour", "month"]).to_pandas()
    print(lmp_avg.round(4))

    # 2. Maximum hourly LMP per zone (the most-stressed hour)
    lmp_peak = lmp.max(["hour", "month"]).to_pandas()
    print("\nPeak LMP by zone:")
    print(lmp_peak.round(4))

    # 3. LMPs for a specific zone over a representative day
    profile = lmp.sel(zone="BA1", year=2025).mean("month").to_pandas()
    profile.plot(figsize=(8, 3), title="Hourly LMP at BA1, 2025")

Sign convention
---------------

LMPs in ``shadow_price_demand`` are **positive when serving more
demand is more expensive** -- the standard convention used by PyPSA,
Switch, and GenX. PREP-SHOT internally flips the raw HiGHS dual
(which is negative because the demand-balance constraint is posed as
``demand - supply == 0``) before writing the NetCDF.

NPV vs real-year prices
-----------------------

LMPs are written in **NPV-discounted USD per MWh**. To recover
undiscounted real-year prices, divide by the variable-cost factor
for that year and zone:

.. code-block:: python

    # var_factor[year, zone] = (1 + r)^(year_min - year) * (year_to_next - year)
    # PREP-SHOT writes it to a sidecar; reconstruct from inputs:
    discount = pd.read_csv("input/economic_discount_factor.csv")
    # ... or pull it back from the model's params dict if you ran it
    # programmatically.

For most analyses (relative-zone comparisons, peak-hour identification,
trend over the planning horizon), the NPV scaling is harmless and
keeps the cross-zone comparison meaningful.

Common pitfalls
---------------

* **MIP solves don't return duals.** If ``shadow_price_demand`` is
  missing from the NetCDF, the solve was a MIP (or infeasible). The
  v1.9.1 extraction is wrapped in try/except: a warning logs and the
  variable is omitted rather than crashing the run.
* **Storage zones distort short-horizon LMPs.** A binding storage
  state-of-charge constraint shows up as an LMP spike in one hour
  and a depression in another (energy-arbitrage). Don't read a
  single hour's LMP as "the price"; average over a day or week.
* **Demand profile shape matters.** PREP-SHOT samples representative
  hours/months. The LMPs you get reflect the sampled hours, not the
  full 8760-hour year. A handful of representative peak hours can
  dominate the average.

For the underlying constraint (``power_balance_cons`` in
``prepshot/_model/demand.py``), see :doc:`../Mathematical_notations`.
