#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Production-cost-model (PCM) mode with rolling horizon.

Companion mode to the default capacity-expansion (CEM) flow in
``run.py``. PCM takes a fixed fleet (from a prior CEM solve, or a
user-supplied capacity CSV) and solves *only* dispatch over a chosen
year, hour-by-hour, in overlapping windows -- the same machinery that
PowNet and PyPSA's ``optimize_with_rolling_horizon`` use.

.. note::

   **v1.14.1 status (alpha).** The rolling driver is wired end-to-end
   with single-window solves working cleanly. Multi-window rolling
   has TWO known limitations:

   1. **Cascading hydro cross-window state**: at the start of any
      non-first window, downstream stations see only their natural
      (incremental) inflow because the upstream's outflow during the
      lookback period (``hour[0] - delay .. hour[0]``) is in the
      previous window's solve and is not yet carried forward. When
      the downstream's ``min_outflow`` exceeds its natural inflow,
      water balance can drain storage below ``storage_min`` -> the
      sub-problem is infeasible. v1.15+ will add cross-window cascade
      state (carry the upstream's last ``max_delay`` outflow values
      into the next window's ``inflow_rule`` lookup).
   2. **Carbon cap rescaling**: the cap from ``policy_carbon_emission_
      limit.csv`` is annual (full-year tonneCO2) but each window
      only covers a fraction of the year. The naive filter applies
      the full annual cap to a 48-hour window -- not binding for our
      small examples but wrong on principle. Will rescale by
      ``window_hours / hours_in_year`` in v1.15.

   For now, recommend ``--horizon == --step == period_length``
   (single-window PCM = fixed-capacity dispatch validation).
   Multi-window rolling works on scenarios *without* binding
   min-outflow constraints on cascaded hydro.

Why rolling horizon?
====================

Solving dispatch on the full 8760-hour annual MILP/LP at once is
intractable for realistic networks. Rolling horizon decomposes the
problem into a sequence of short, overlapping subproblems:

  while t < 8760:
      build LP for hours [t, t + horizon)
      pin initial state (storage SOC, hydro reservoir level) from the
        previous window's terminal solution
      solve
      persist dispatch decisions for [t, t + step)
      advance t by step

Each window's lookahead (``horizon - step``) absorbs the end-of-window
distortion. PowNet uses ``horizon = 48 h, step = 24 h``; we default to
the same.

Capacity source
===============

Two formats are accepted via ``--cap-source PATH``:

* ``.nc`` -- a CEM ``baseline.nc`` written by ``run.py``. The
  ``install`` data array (dims ``year x zone x tech``) is selected
  for the chosen year.
* ``.csv`` -- a tidy table with columns ``zone, tech, year, capacity``
  (MW). Useful when running PCM standalone, no CEM needed.

If neither is supplied, the existing fleet from
``tech_existing.csv`` is used as-is (no expansion). This is the
"validate-the-existing-build" mode.

Config
======

Add a ``pcm_parameters`` block to ``config.json``::

    "pcm_parameters": {
        "horizon_h": 48,
        "step_h": 24,
        "year": 2030,
        "total_h": 168
    }

Or pass as CLI flags. CLI overrides config.

``total_h`` (optional) caps how many hours from ``hour[0]`` are
simulated -- useful as a smoke test on large nodal models, where a
single 48 h window can take tens of minutes to build. Omit (or set
``null``) to run the full year.

Output
======

PCM dispatch lands in ``output/baseline_pcm/`` -- one Parquet
sidecar per output variable (``gen.parquet``, ``trans_export.parquet``,
``lns.parquet``, ...), keyed in long format so the file size scales
with non-zero entries (not the dense (h, m, y, z, ...) product).
A ``manifest.json`` next to the Parquets records the schema. The
companion CEM ``baseline.nc`` is left untouched.

CLI
===

::

    cd examples/three_zone
    python -m prepshot.pcm --year 2025 --horizon 48 --step 24

    # smoke test: only the first 48 h, one window
    python -m prepshot.pcm --year 2025 --horizon 48 --step 48 --total-h 48

Or programmatically::

    from prepshot.pcm import run_pcm
    run_pcm('examples/three_zone', year=2025)
    run_pcm('examples/three_zone', year=2025, total_h=48)
"""
import argparse
import json
import logging
from pathlib import Path
from typing import Optional

import pandas as pd
import xarray as xr

from prepshot.set_up import initialize_environment
from prepshot.solver import solve_model
from prepshot.model import create_model
from prepshot.logs import setup_logging, timer


# ---------- capacity loaders ---------------------------------------------


def load_fixed_capacity(
    source: Path, target_year: int, scenario_dir: Path
) -> dict:
    """Return ``{(zone, tech): capacity_MW}`` for ``target_year``.

    ``source`` may be a path to:

    * a CEM ``baseline.nc`` (xarray dataset with an ``install`` array
      indexed by ``year x zone x tech``), or
    * a tidy CSV with columns ``zone, tech, year, capacity``.

    Relative paths are resolved against ``scenario_dir``.
    """
    path = Path(source)
    if not path.is_absolute():
        path = scenario_dir / path
    if not path.exists():
        raise FileNotFoundError(f"Capacity source not found: {path}")

    if path.suffix == '.nc':
        ds = None
        last_err = None
        for engine in ('netcdf4', 'h5netcdf'):
            try:
                ds = xr.open_dataset(path, engine=engine)
                break
            except (OSError, ImportError, RuntimeError, ValueError) as exc:
                # netCDF backends fail in a variety of ways across
                # platforms (missing native lib, format mismatch, etc.);
                # we just want to fall through to the next engine.
                last_err = exc
        if ds is None:
            raise RuntimeError(
                f"Could not open {path}: {last_err}"
            )
        if 'install' not in ds.data_vars:
            raise ValueError(
                f"{path} has no 'install' data var; not a CEM baseline."
            )
        arr = ds['install'].sel(year=target_year)
        cap = {}
        for z in arr['zone'].values:
            for t in arr['tech'].values:
                cap[(str(z), str(t))] = float(arr.sel(zone=z, tech=t).item())
        return cap

    if path.suffix == '.csv':
        df = pd.read_csv(path)
        df_yr = df[df['year'].astype(int) == int(target_year)]
        if df_yr.empty:
            raise ValueError(
                f"{path} has no rows for year={target_year}; "
                f"available years: {sorted(df['year'].unique())}"
            )
        return {
            (str(r['zone']), str(r['tech'])): float(r['capacity'])
            for _, r in df_yr.iterrows()
        }

    raise ValueError(
        f"Unrecognized capacity source extension: {path.suffix}. "
        f"Use .nc or .csv."
    )


# ---------- per-window plumbing ------------------------------------------


def _lock_no_expansion(model) -> None:
    """Pin ``cap_newtech`` to zero so the model is dispatch-only.

    Must be called *after* ``create_model`` -- it sets the upper bound
    on each ``cap_newtech`` variable to 0, which presolve folds away.
    """
    import pyoptinterface as poi
    for y in model.year:
        for z in model.zone:
            for te in model.tech:
                v = model.cap_newtech[y, z, te]
                model.set_variable_attribute(
                    v, poi.VariableAttribute.UpperBound, 0.0
                )


def _override_existing_fleet(params: dict, cap_lookup: dict) -> None:
    """Replace ``params['existing_fleet']`` so ``cap_existing`` for
    the chosen year collapses to the user-supplied capacity.

    investment.py reads ``params['existing_fleet']`` (dict keyed
    ``(tech, zone, commission_year) -> MW``) during model construction;
    each entry contributes capacity for years where ``commission_year
    <= y < commission_year + lifetime[tech, commission_year]``. By
    rewriting the dict to a single entry per (zone, tech) commissioned
    at the first model year, we guarantee the chosen year sees exactly
    the user-supplied capacity (and no other).

    Also clears the precomputed ``active_zt`` set so it's recomputed
    against the overridden fleet on the next ``create_model`` call.
    """
    cy = params['year'][0]  # commission at the first model year so
                            # the lifetime lookup is defined.
    new_fleet = {}
    for (z, te), cap_mw in cap_lookup.items():
        if cap_mw > 0:
            new_fleet[(te, z, cy)] = float(cap_mw)
    params['existing_fleet'] = new_fleet
    # Drop precomputed sparse index so create_model recomputes it
    # against the overridden fleet.
    for k in ('active_zt', 'tech_zones', 'zone_techs', 'active_zt_storage'):
        params.pop(k, None)


def _build_window_params(
    full_params: dict,
    year: int,
    window_hours: list,
    state: dict,
) -> dict:
    """Slice ``full_params`` down to a single year + window of hours.

    A SHALLOW copy of ``full_params`` -- the big dicts (demand,
    max_gen_profile, inflow, ...) are reused by reference because
    they're never mutated per window. Only the small set of keys we
    actually overwrite below get fresh values; the dicts we update
    in place (e.g. ``initial_energy_storage_level``) are explicitly
    one-level copied so we don't bleed state into ``full_params``.

    Replaces the previous full ``deepcopy(full_params)`` which on
    Thai PCM (4 M demand entries + 0.3 M VRE-CF entries) cost
    ~10 s per window -- ~20x more than ``create_model`` itself.
    """
    p = dict(full_params)  # shallow copy
    p['hour'] = list(window_hours)
    p['year'] = [int(year)]
    p['skip_end_storage'] = True  # interior windows: terminal SOC is free
    # Switch hydro from cyclic-wrap to non-cyclic-rolling. With cyclic
    # off, the cascade upstream's outflow at hours before the window
    # start is dropped from the downstream's inflow expression -- the
    # approximation that lets each window stand alone, instead of
    # implicitly looping its end back into its beginning.
    p['cyclic_hydro'] = False
    # Recompute weight for the smaller window so cost / income terms
    # scale correctly (weight is in the income denominator).
    if 'hours_in_year' in p:
        p['weight'] = (
            len(p['month']) * len(window_hours) * p['dt']
        ) / p['hours_in_year']
    # Filter year-keyed lookups down to {year}. The CEM model iterates
    # over rows of the policy / fleet tables and indexes year-keyed
    # variables; keeping rows for years outside the window triggers
    # KeyError when those variables don't exist in this subproblem.
    cel = p.get('carbon_emission_limit')
    if cel is not None and hasattr(cel, 'iterrows'):
        p['carbon_emission_limit'] = cel[cel['year'] == int(year)].copy()
    # set per-station initial storage from carried-over state
    if state.get('hydro_storage'):
        p['initial_reservoir_storage_level'] = dict(state['hydro_storage'])
    if state.get('prior_outflow'):
        # Cross-window cascade state, consumed by hydro.inflow_rule
        # when the delayed hour falls before this window's hour[0].
        p['prior_outflow'] = dict(state['prior_outflow'])
    if state.get('battery_storage'):
        # Merge: keep the dataset's default SOC for any (te, z) that
        # the previous window didn't write (e.g. zero-capacity slots).
        merged = dict(p.get('initial_energy_storage_level') or {})
        merged.update(state['battery_storage'])
        p['initial_energy_storage_level'] = merged
    # Force the head-iteration off in PCM windows -- per-window head
    # iteration would multiply the solve count by 3x with no extra
    # accuracy on a single window.
    p['iteration_number'] = 1
    return p


def _extract_window_state(
    model, full_params: dict, terminal_hour: int
) -> dict:
    """Read storage levels + cascade outflows at end of the committed
    window to seed the next window.

    Hydro storage is clamped a small fraction inside ``[storage_min,
    storage_max]`` so floating-point boundary values from the LP
    optimum don't accidentally violate the next window's bounds.

    Battery SOC is converted from absolute MWh (the form held by
    ``model.storage``) to the per-unit-of-capacity fraction that
    ``params['initial_energy_storage_level']`` expects, using the
    same ``esl * cap * epr * dt`` relation as the
    ``init_energy_storage_rule``.

    **Prior outflow state (v1.17+).** For each upstream station with a
    delay ``D``, the next window's first ``D`` hours of downstream
    inflow refer back to the upstream's outflow over hours
    ``[terminal_hour - D + 1, terminal_hour]``. We extract those
    values now and stash them as a flat
    ``{(station, hour, month, year) -> m**3/s}`` lookup that the
    next window's ``hydro.inflow_rule`` will consult when ``t <
    hour[0]``. Without this, downstream stations would see only
    natural inflow at window boundaries -- often infeasible when
    ``min_outflow > natural_inflow``.
    """
    state = {
        'hydro_storage': {},
        'battery_storage': {},
        'prior_outflow': {},
    }
    if full_params.get('isinflow') and hasattr(model, 'storage_reservoir'):
        smin = full_params.get('reservoir_storage_min') or {}
        smax = full_params.get('reservoir_storage_max') or {}
        for s in model.station:
            # storage_*[s, m, h] -- pick m=h=1 as a per-station bound
            # (these CSVs in shipped examples are flat across the
            # representative period). PCM v1.14.1 will resolve per-hour
            # bounds properly.
            lo = float(smin.get((s, 1, 1), 0.0))
            hi = float(smax.get((s, 1, 1), float('inf')))
            margin = max(0.0, (hi - lo) * 1e-3)  # 0.1 % buffer
            for m in model.month:
                for y in model.year:
                    val = float(model.get_value(
                        model.storage_reservoir[s, terminal_hour, m, y]
                    ))
                    val = min(max(val, lo + margin), hi - margin)
                    state['hydro_storage'][s] = val

        # Prior outflow lookup: for every upstream-of-anyone station
        # ``s`` and every absolute hour ``h_abs`` in
        # ``[terminal_hour - max_delay + 1, terminal_hour]``, stash
        # ``outflow[s, h_abs, m, y]``. The next window's
        # ``hydro.inflow_rule`` keys this dict when ``t < hour[0]``.
        wdt_df = full_params.get('water_delay_time')
        if (
            wdt_df is not None
            and hasattr(wdt_df, 'iterrows')
            and not wdt_df.empty
            and not wdt_df['delay'].isna().all()
        ):
            upstream_stations = set(wdt_df['upstream_tech'].astype(str))
            max_delay = int(wdt_df['delay'].max())
        else:
            upstream_stations = set()
            max_delay = 0
        for s in upstream_stations:
            if s not in set(model.station):
                continue
            for offset in range(max_delay):
                h_abs = terminal_hour - offset
                if h_abs not in set(model.hour):
                    continue
                for m in model.month:
                    for y in model.year:
                        try:
                            v = float(model.get_value(
                                model.outflow[s, h_abs, m, y]
                            ))
                        except (KeyError, TypeError):
                            continue
                        state['prior_outflow'][(s, h_abs, m, y)] = v

    if hasattr(model, 'storage') and getattr(model, 'storage_tech', None):
        epr_lookup = full_params.get('energy_to_power_ratio') or {}
        dt = full_params['dt']
        for z in model.zone:
            for te in model.storage_tech:
                # Compose cap_existing for this (year, zone, tech). Use
                # the FIRST year in the window (PCM only models one).
                year = model.year[0]
                cap_mw = float(model.get_value(
                    model.cap_existing[year, z, te]
                )) if hasattr(model.cap_existing, '__getitem__') else 0.0
                epr = float(epr_lookup.get(te, 0.0))
                denom = cap_mw * epr * dt
                if denom <= 0:
                    # No installed storage in this (z, te) slot --
                    # skip; the next window's init lookup defaults to 0.
                    continue
                for m in model.month:
                    val_mwh = float(model.get_value(
                        model.storage[terminal_hour, m, year, z, te]
                    ))
                    esl = val_mwh / denom
                    # Clamp into [0, 1] -- LP feasibility guarantees
                    # storage stays in [0, cap*epr*dt], but
                    # floating-point noise can push the ratio just
                    # outside.
                    esl = min(max(esl, 0.0), 1.0)
                    state['battery_storage'][te, z] = esl
    return state


def _extract_window_dispatch(
    model, commit_hours: list, year: int
) -> dict:
    """Pull the dispatch decisions for ``commit_hours`` out of a solved
    window model. Returns a dict of arrays keyed like the CEM output."""
    out = {'gen': [], 'charge': [], 'trans_export': [], 'genflow': [],
           'spillflow': [], 'reserve_up': [], 'reserve_down': [],
           'lns': [], 'lmp': []}
    months = list(model.month)
    zones = list(model.zone)
    techs = list(model.tech)
    stations = list(model.station) if hasattr(model, 'station') else []

    storage_set = set(getattr(model, 'storage_tech', []) or [])
    zone_techs = getattr(model, 'zone_techs', None) or {
        z: list(techs) for z in zones
    }
    out_neighbours = getattr(model, 'out_neighbours', None) or {
        z: list(zones) for z in zones
    }

    for h in commit_hours:
        for m in months:
            for z in zones:
                for te in zone_techs.get(z, []):
                    out['gen'].append({
                        'hour': h, 'month': m, 'year': year,
                        'zone': z, 'tech': te,
                        'value': float(model.get_value(
                            model.gen[h, m, year, z, te]
                        )),
                    })
                    if hasattr(model, 'charge') and te in storage_set:
                        out['charge'].append({
                            'hour': h, 'month': m, 'year': year,
                            'zone': z, 'tech': te,
                            'value': float(model.get_value(
                                model.charge[h, m, year, z, te]
                            )),
                        })
                    if hasattr(model, 'reserve_up'):
                        out['reserve_up'].append({
                            'hour': h, 'month': m, 'year': year,
                            'zone': z, 'tech': te,
                            'value': float(model.get_value(
                                model.reserve_up[h, m, year, z, te]
                            )),
                        })
                        out['reserve_down'].append({
                            'hour': h, 'month': m, 'year': year,
                            'zone': z, 'tech': te,
                            'value': float(model.get_value(
                                model.reserve_down[h, m, year, z, te]
                            )),
                        })
                # Load-not-served: per-(h, m, y, z), populated only
                # when allow_load_shedding is on.
                if hasattr(model, 'lns'):
                    out['lns'].append({
                        'hour': h, 'month': m, 'year': year,
                        'zone': z,
                        'value': float(model.get_value(
                            model.lns[h, m, year, z]
                        )),
                    })
            for z in zones:
                for z2 in out_neighbours.get(z, []):
                    out['trans_export'].append({
                        'hour': h, 'month': m, 'year': year,
                        'zone1': z, 'zone2': z2,
                        'value': float(model.get_value(
                            model.trans_export[h, m, year, z, z2]
                        )),
                    })
            for s in stations:
                out['genflow'].append({
                    'hour': h, 'month': m, 'year': year,
                    'station': s,
                    'value': float(model.get_value(
                        model.genflow[s, h, m, year]
                    )),
                })
                out['spillflow'].append({
                    'hour': h, 'month': m, 'year': year,
                    'station': s,
                    'value': float(model.get_value(
                        model.spillflow[s, h, m, year]
                    )),
                })

    # LMP: dual of the nodal power-balance constraint, scaled to
    # real-year USD/MWh. The constraint is posed as
    # ``demand - supply == 0`` so the raw dual is the negative of the
    # marginal cost of one more MWh of demand -- flip the sign to
    # follow the convention. The objective discounts every cost term
    # by ``var_factor[y, z] / weight``; multiplying the dual by
    # ``weight / var_factor`` undoes that and gives a real-year
    # marginal price. Skipped silently if the solver did not return
    # duals (e.g. infeasible).
    # Pick the right per-backend dual-extractor once.  PoI 0.4's
    # ``get_constraint_attribute(c, ConstraintAttribute.Dual)`` raises
    # ``AttributeError: Quadratric`` (sic) on linear constraints in
    # both backends, so we go through the raw native name instead:
    # Gurobi exposes the shadow price as ``Pi``, HiGHS as ``dual``.
    def _make_dual_extractor():
        probe = next(iter(model.power_balance_cons.values()), None)
        if probe is None:
            return None
        for raw_name in ('Pi', 'dual'):
            try:
                model.get_constraint_raw_attribute_double(probe, raw_name)
                return lambda c, n=raw_name: float(
                    model.get_constraint_raw_attribute_double(c, n)
                )
            except Exception:
                continue
        return None
    extract_dual = _make_dual_extractor()
    if extract_dual is None:
        logging.warning("could not extract LMP duals: backend exposes no Pi / dual")
    else:
        weight = model.params['weight']
        vf = model.params['var_factor']
        for h in commit_hours:
            for m in months:
                for z in zones:
                    c = model.power_balance_cons[h, m, year, z]
                    dual = extract_dual(c)
                    out['lmp'].append({
                        'hour': h, 'month': m, 'year': year,
                        'zone': z,
                        'value': -dual * weight / float(vf[year, z]),
                    })
    return out


# ---------- aggregation + write ------------------------------------------


def _aggregate(window_outs: list) -> dict:
    """Concatenate per-window dispatch dicts into one per-key list."""
    merged = {k: [] for k in window_outs[0].keys()}
    for w in window_outs:
        for k, rows in w.items():
            merged[k].extend(rows)
    return merged


def _save_pcm_netcdf(merged: dict, out_path: Path) -> None:
    """Save per-variable result tables.

    For sparse-by-construction outputs (``gen`` / ``charge`` /
    ``trans_export``: only ``active_zt`` or ``active_lines`` cells
    populated), pivoting to a dense ``(hour, month, year, zone, ...)``
    xarray creates a NaN-padded array that's orders of magnitude
    larger than the data. On a full-year Thai PCM run that's
    8760 x 472 x 472 = 1.95 B cells just for ``trans_export`` (~16
    GB), which overflows the NetCDF3 32-bit size field.

    Strategy: write each variable as a long-format Parquet sidecar
    next to ``out_path`` (in ``out_path`` with the ``.nc`` suffix
    swapped for a directory). Parquet is compressed, columnar, and
    natively sparse. A small ``manifest.json`` records the schema.
    """
    out_dir = out_path.with_suffix('')
    out_dir.mkdir(parents=True, exist_ok=True)
    schema = {}
    for key, rows in merged.items():
        if not rows:
            continue
        df = pd.DataFrame(rows)
        df.to_parquet(out_dir / f'{key}.parquet', compression='zstd')
        schema[key] = list(df.columns)
    (out_dir / 'manifest.json').write_text(
        json.dumps({'variables': schema, 'format': 'parquet'}, indent=2)
    )
    logging.info(
        'PCM dispatch written to %s/ (%d Parquet variables)',
        out_dir, len(schema),
    )


# ---------- main entry ---------------------------------------------------


@timer
def run_pcm(
    scenario_dir,
    *,
    year: Optional[int] = None,
    horizon_h: int = 48,
    step_h: int = 24,
    cap_source: Optional[str] = None,
    total_h: Optional[int] = None,
    allow_load_shedding: Optional[bool] = None,
    voll: Optional[float] = None,
) -> None:
    """Solve PCM dispatch over one year with rolling horizon.

    Parameters
    ----------
    scenario_dir : path-like
        Directory containing ``config.json``, ``params.json``, ``input/``.
    year : int, optional
        Which model year to dispatch. Defaults to the first year of
        the config's planning horizon.
    horizon_h : int
        Window length in hours. Defaults to 48.
    step_h : int
        Window advance in hours (committed segment). Defaults to 24.
    cap_source : str, optional
        Path to a CEM ``baseline.nc`` or capacity CSV. If omitted,
        the CEM-shipped existing fleet is used unchanged.
    total_h : int, optional
        Cap on the number of hours simulated from ``hour[0]``. Useful
        as a smoke test on large nodal models where the full year is
        intractable. Defaults to ``None`` (run all hours).
    allow_load_shedding : bool, optional
        Allow non-negative slack (``lns``) on every nodal power
        balance, priced at ``voll`` in the objective. Lets PCM
        windows complete even when the dispatch can't physically meet
        demand at some (hour, zone). Overrides
        ``reliability_parameters.allow_load_shedding`` from
        ``config.json`` when set.
    voll : float, optional
        Value of lost load (USD/MWh) for the load-shedding penalty.
        Overrides ``reliability_parameters.voll`` from
        ``config.json`` when set. Defaults to 10000.
    """
    setup_logging()
    scenario_dir = Path(scenario_dir).resolve()

    cfg = {
        'filepath': str(scenario_dir),
        'config_filename': str(scenario_dir / 'config.json'),
        'params_filename': str(scenario_dir / 'params.json'),
    }
    # initialize_environment registers an argparse parser with one flag
    # per scenario parameter (carbon_tax, demand, ...). Our CLI flags
    # (--year, --horizon, ...) would collide with that parser when
    # invoked via "python -m prepshot.pcm ...". Strip our flags by
    # presenting initialize_environment a clean argv -- we've already
    # captured what we need from the user.
    import sys as _sys
    _saved_argv = _sys.argv
    _sys.argv = [_saved_argv[0]]
    try:
        full_params = initialize_environment(cfg)
    finally:
        _sys.argv = _saved_argv
    pcm_block = json.loads(
        (scenario_dir / 'config.json').read_text()
    ).get('pcm_parameters') or {}

    if year is None:
        year = pcm_block.get('year', full_params['year'][0])
    horizon_h = horizon_h or pcm_block.get('horizon_h', 48)
    step_h = step_h or pcm_block.get('step_h', 24)
    cap_source = cap_source or pcm_block.get('cap_source')
    if total_h is None:
        total_h = pcm_block.get('total_h')

    # Load-shedding overrides: CLI / kwarg wins over config; config
    # wins over the default. We stamp the merged value back into
    # full_params so every per-window deepcopy picks it up.
    if allow_load_shedding is not None:
        full_params['allow_load_shedding'] = bool(allow_load_shedding)
    if voll is not None:
        full_params['voll'] = float(voll)
    if full_params.get('allow_load_shedding'):
        logging.info(
            'PCM: load shedding enabled (VOLL=%.0f $/MWh)',
            full_params.get('voll', 10000.0),
        )

    if cap_source:
        cap_lookup = load_fixed_capacity(
            Path(cap_source), int(year), scenario_dir
        )
        logging.info(
            'PCM: loaded fixed capacity for year %s from %s (%d entries)',
            year, cap_source, len(cap_lookup),
        )
    else:
        cap_lookup = None
        logging.info(
            'PCM: no cap-source given; using existing fleet from CEM inputs'
        )

    # Initial state: per-station / per-battery starting storage.
    state = {
        'hydro_storage': dict(
            full_params.get('initial_reservoir_storage_level') or {}
        ),
        'battery_storage': {},
    }

    full_hours = list(full_params['hour'])
    n_hours = len(full_hours)
    if total_h is not None:
        n_hours = min(n_hours, int(total_h))
        logging.info(
            'PCM: total_h=%d -- simulating only hours [%d..%d] '
            '(of %d available)',
            total_h, full_hours[0], full_hours[n_hours - 1],
            len(full_hours),
        )
    window_outs = []
    t = 0
    while t < n_hours:
        wh_end_idx = min(t + horizon_h, n_hours)
        commit_end_idx = min(t + step_h, n_hours)
        window_hours = full_hours[t:wh_end_idx]
        commit_hours = full_hours[t:commit_end_idx]

        win_params = _build_window_params(
            full_params, int(year), window_hours, state
        )
        if cap_lookup is not None:
            _override_existing_fleet(win_params, cap_lookup)
        m = create_model(win_params)
        _lock_no_expansion(m)
        ok = solve_model(m, win_params)
        if not ok:
            raise RuntimeError(
                f'PCM window hours {window_hours[0]}..{window_hours[-1]} '
                f'failed to solve to optimality.'
            )

        window_outs.append(
            _extract_window_dispatch(m, commit_hours, int(year))
        )
        state = _extract_window_state(m, win_params, commit_hours[-1])

        logging.info(
            'PCM window [%d..%d] solved; committed [%d..%d]; advancing.',
            window_hours[0], window_hours[-1],
            commit_hours[0], commit_hours[-1],
        )
        t += step_h

    merged = _aggregate(window_outs)
    out_path = scenario_dir / 'output' / 'baseline_pcm.nc'
    _save_pcm_netcdf(merged, out_path)


def main() -> None:
    """CLI entry point: ``python -m prepshot.pcm``."""
    p = argparse.ArgumentParser(prog='python -m prepshot.pcm')
    p.add_argument(
        'scenario', type=Path, default=Path.cwd(), nargs='?',
        help='Scenario directory (defaults to cwd).',
    )
    p.add_argument('--year', type=int, default=None)
    p.add_argument('--horizon', type=int, default=48,
                   help='Window length in hours.')
    p.add_argument('--step', type=int, default=24,
                   help='Window advance in hours.')
    p.add_argument('--cap-source', default=None,
                   help='Path to a CEM baseline.nc or capacity CSV.')
    p.add_argument('--total-h', type=int, default=None,
                   help='Cap simulated hours from hour[0]; smoke-test '
                        'knob for large nodal models.')
    p.add_argument('--allow-load-shedding', action='store_true',
                   default=None,
                   help='Allow non-negative load-not-served slack on '
                        'every (h, m, y, z) priced at VOLL.')
    p.add_argument('--voll', type=float, default=None,
                   help='Value of lost load in $/MWh (default 10000).')
    args = p.parse_args()
    run_pcm(
        args.scenario,
        year=args.year,
        horizon_h=args.horizon,
        step_h=args.step,
        cap_source=args.cap_source,
        total_h=args.total_h,
        allow_load_shedding=args.allow_load_shedding,
        voll=args.voll,
    )


if __name__ == '__main__':
    main()
