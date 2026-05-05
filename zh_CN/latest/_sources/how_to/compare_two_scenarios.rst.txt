Compare two scenarios
=====================

**Goal.** Quantify what changes between a baseline and a
counterfactual -- total cost, capacity mix, generation by carrier,
LMPs.

The result NetCDF makes side-by-side comparison easy: each file is
just an ``xarray.Dataset`` with the same variables, so subtraction
and `groupby` work directly.

Setup
-----

Run two scenarios using the suffix flag (see
:doc:`tighten_a_carbon_cap`):

.. code-block:: bash

    cd examples/southeast_asia
    python -m prepshot                           # -> output/baseline.nc
    python -m prepshot --carbon_emission_limit=tight  # -> output/baseline_tight.nc

Recipe
------

.. code-block:: python

    import xarray as xr
    import pandas as pd

    base = xr.open_dataset("output/baseline.nc")
    tight = xr.open_dataset("output/baseline_tight.nc")

    # 1. Headline cost delta
    cost_delta = float(tight.cost) - float(base.cost)
    cost_delta_pct = cost_delta / float(base.cost) * 100
    print(f"Cost delta: ${cost_delta:,.0f} ({cost_delta_pct:+.1f}%)")

    # 2. Capacity-mix shift in 2030 (the year the cap binds)
    registry = pd.read_csv("input/tech_registry.csv")
    tech_to_carrier = dict(zip(registry["tech"], registry["carrier"]))

    def by_carrier(ds, year):
        df = ds["install"].sel(year=year).to_dataframe().reset_index()
        df["carrier"] = df["tech"].map(tech_to_carrier)
        return df.groupby("carrier")["install"].sum()

    compare = pd.concat({
        "baseline": by_carrier(base, 2030),
        "tight":    by_carrier(tight, 2030),
    }, axis=1).fillna(0)
    compare["delta"] = compare["tight"] - compare["baseline"]
    compare = compare[compare.abs().max(axis=1) > 1]
    print(compare.sort_values("delta", ascending=False).round(0))

    # 3. LMP shift by zone
    lmp_base = base["shadow_price_demand"].mean(["hour", "month"]).to_pandas()
    lmp_tight = tight["shadow_price_demand"].mean(["hour", "month"]).to_pandas()
    lmp_delta = lmp_tight - lmp_base
    print("\nAverage LMP delta (USD/MWh, NPV):")
    print(lmp_delta.round(4))

Plot the capacity reshuffle
---------------------------

.. code-block:: python

    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(7, 4))
    compare["delta"].plot.barh(
        ax=ax,
        color=compare["delta"].apply(lambda v: "green" if v > 0 else "firebrick"),
    )
    ax.axvline(0, color="black", linewidth=0.5)
    ax.set_xlabel("Capacity change vs. baseline in 2030 (MW)")
    ax.set_title("Tighter carbon cap: capacity reshuffle")
    fig.tight_layout()
    plt.show()

Common pitfalls
---------------

* **Mismatched dimensions.** If you ran the two scenarios with
  different ``hour`` or ``month`` settings, ``ds_a - ds_b`` will
  fail with a broadcast error. Keep configs in lockstep when
  comparing.
* **NPV-discounted vs nominal.** ``ds.cost`` is NPV; ``ds.gen``
  is in MWh per timestep. Don't mix without dividing by
  ``var_factor[year, zone]`` for unit conversion.
* **One-hot scenarios.** For more than two variants, lift the
  pattern into a dict comprehension over a list of suffixes:
  ``{s: xr.open_dataset(f"output/baseline_{s}.nc") for s in suffixes}``.

For a worked end-to-end comparison see
:doc:`../examples/southeast_asia/SoutheastAsia` (the SoutheastAsia
notebook walks through this exact pattern in cells 18-20).
