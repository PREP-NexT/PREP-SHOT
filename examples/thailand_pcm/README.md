# Thailand PCM example

Full-nodal Thai grid example for PREP-SHOT's **PCM mode**:

- **472 buses** (each = a PREP-SHOT zone — no spatial aggregation)
- **615 transmission lines** with reactance / susceptance from
  `grid_topology.csv`
- **168 thermal units** kept individual (each unit = its own tech)
- **30 VRE plants** with hourly capacity factors
- **14 hydro stations** with cascade topology and per-station
  reservoir physics
- **8760-hour 2023 load profile**

This dataset comes from the Thai PCM repo at
`production-cost-model-main/`. The `build_inputs.py` script in this
directory converts it to PREP-SHOT's v1.5+ long-format CSV schema.

## Why PCM mode?

A single-pass full-year LP at this scale is intractable
(~880 M `gen` variables before any storage / reserve / UC). The
intended workflow is **rolling-horizon PCM**:

```bash
cd examples/thailand_pcm
python -m prepshot.pcm . \
    --year 2023 \
    --horizon 24 --step 24 \
    --cap-source input/capacity_pcm.csv
```

Each 24-hour window is small enough to solve quickly; the driver
solves 365 windows sequentially with hydro storage + cascade
state carried over.

## Files

- `build_inputs.py` — reads `production-cost-model-main/input/` and
  emits PREP-SHOT long-format CSVs into `input/`
- `input/capacity_pcm.csv` — `--cap-source` input for the PCM
  driver. Same data as `tech_existing.csv` but reshaped to
  `(zone, tech, year, capacity)`.
- `config.json` — defaults to PCM rolling-horizon mode (24h /
  24h step). DC flow / N-1 / UC / multi-product reserves all
  available but disabled by default at this scale.
- `params.json` — optional inputs marked `required: false` so
  the loader silently uses zero/empty defaults for things like
  finance tables, reserve files, and storage scaffolding.

## Knobs to flip on for higher fidelity

In `config.json`:

- `dc_parameters.is_dc_flow: true` — Kirchhoff voltage law on the
  615-line network. Stays LP.
- `dc_parameters.is_n1_secure: true` — N-1 SCDC OPF (preventive
  policy). Multiplies LP size by `1 + N_contingencies`. Add lines
  to `input/transmission_contingencies.csv` (currently empty).
- `cost_parameters.is_piecewise_heat_rate: true` — convex
  piecewise-linear heat rates. Stays LP. Source thermal units
  already have a `heat_rate` column; you can derive segments
  from it and edit `input/tech_heat_rate.csv`.
- `uc_parameters.is_uc: true` — clustered UC. With 168 thermal
  units, full integer MILP across the year is **not** routinely
  practical -- pair with `--horizon 24 --step 24` so each window
  is its own MILP.

## Status

**The data conversion is complete and the inputs validate against
PREP-SHOT's loader.** Running the full PCM solve does **not**
complete in reasonable time on the current PREP-SHOT codebase: at
472 zones x 212 techs x 24 hours per window, PoI's
``make_tupledict`` Python-level iteration during ``create_model``
takes 20+ minutes per window before HiGHS even sees the LP. The
bottleneck is PREP-SHOT's constraint-construction overhead, not
the underlying HiGHS solver.

Two paths to actually run this:

1. **Aggregate buses** to a smaller zone set before running --
   defeats the "no aggregation" point but makes the model
   tractable.
2. **Profile + accelerate** ``model.py`` / ``hydro.py`` constraint
   construction (Cython, Numba, or just batched ``add_linear_
   constraint`` calls). This is the right fix; it would lift
   PREP-SHOT closer to PowNet / PyPSA scale-handling.

Until either lands, this example is shipped as a **data-conversion
artefact** demonstrating how to plug an existing nodal PCM dataset
into PREP-SHOT's input schema. The ``input/`` directory is a
working PREP-SHOT scenario; you can run the loader, build the
fleet vectors, and inspect them with pandas without invoking the
full LP build.

## Caveats

- Hydro inflow is from 2019 (closest year in the source CSV) re-
  stamped onto 2023 hours. Source `inflow.csv` only covers
  2016-2019 while `load_demand.csv` is 2023; one of them is the
  proxy.
- The 8 import nodes from `import.csv` are **not** modelled in
  this conversion. Add them as fixed-injection rows in
  `demand.csv` (negative load) if you want them included.
- `operation_cost` from the Thermal sheet already bundles fuel
  cost + variable O&M; we ship `tech_fuel_price = 0` and put the
  whole number in `tech_variable_OM_cost` to avoid double-
  counting.

## Source attribution

This example uses input data from the Thai PCM repo at
`production-cost-model-main/`. Original developers' attribution
applies. The conversion script and the PREP-SHOT integration
itself are part of PREP-SHOT.
