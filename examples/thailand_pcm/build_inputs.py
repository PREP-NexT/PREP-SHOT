#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Build PREP-SHOT inputs from the Thai PCM dataset.

Source data lives in
``/Users/energy/01-doing/PREP-SHOT-tutorial/production-cost-model-main``
(Thai grid PCM, ~472 buses, ~615 lines, ~168 thermal units +
30 VRE + 14 hydro stations, full 8760-hour 2023 load profile).

This script does NO spatial aggregation -- every bus stays a separate
PREP-SHOT zone, every thermal unit stays a separate tech, every hydro
station stays a separate tech. PREP-SHOT only practically solves a
problem of this size in PCM rolling-horizon mode (24-hour windows;
see ``prepshot.pcm``).

Outputs land in ``examples/thailand_pcm/input/`` in PREP-SHOT's
v1.5+ long-format CSV schema, plus a capacity-source CSV consumed
by ``--cap-source`` of the PCM driver.

Run:

    python examples/thailand_pcm/build_inputs.py
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[2]
SRC = Path('/Users/energy/01-doing/PREP-SHOT-tutorial/production-cost-model-main/input')
OUT = REPO / 'examples' / 'thailand_pcm' / 'input'
OUT.mkdir(parents=True, exist_ok=True)

YEAR = 2023
LIFETIME_YEARS = 100  # blanket value: all thermal/VRE/hydro stays in service


# ---------- helpers ------------------------------------------------------


def long_demand() -> pd.DataFrame:
    """8760-hour x 472-bus load -> long format (zone, year, month, hour, unit, value).

    Source ``load_demand.csv`` is wide: rows are timestamps, columns are
    bus IDs. We treat the 472 columns as 472 PREP-SHOT zones, leave the
    hourly values in MW.
    """
    df = pd.read_csv(SRC / 'load_demand.csv')
    ts_col = df.columns[0]
    df['ts'] = pd.to_datetime(df[ts_col])
    df['hour'] = ((df['ts'] - df['ts'].iloc[0]).dt.total_seconds() // 3600).astype(int) + 1
    df = df.drop(columns=[ts_col, 'ts'])
    long = df.melt(id_vars='hour', var_name='zone', value_name='value')
    long['year'] = YEAR
    long['month'] = 1
    long['unit'] = 'MW'
    return long[['zone', 'year', 'month', 'hour', 'unit', 'value']]


def thermal_units() -> pd.DataFrame:
    """One row per thermal unit: name, node, max_capacity, fuel_type, etc."""
    return pd.read_excel(SRC / 'generators.xlsx', 'Thermal')


def renewable_units() -> pd.DataFrame:
    return pd.read_excel(SRC / 'generators.xlsx', 'Renewable')


def hydro_units() -> pd.DataFrame:
    return pd.read_excel(SRC / 'hydropower.xlsx', 'Sheet2')


def grid_topology() -> pd.DataFrame:
    return pd.read_csv(SRC / 'grid_topology.csv')


# ---------- main builders ------------------------------------------------


def build_zones_and_techs():
    """Collect the master zone / tech sets."""
    # Zones = every bus that appears in the load file (472 of them).
    demand = pd.read_csv(SRC / 'load_demand.csv')
    zones = sorted(c for c in demand.columns if c.startswith('bus'))

    # Techs: each plant is its own. Use the plant's name as the tech.
    tt = thermal_units()
    rt = renewable_units()
    ht = hydro_units()

    # Some thermal units have weird characters in names. Normalise to
    # something CSV / Excel-sheet-name-friendly: keep the original
    # `name` since it appears in the source as ASCII-ish.
    thermal_names = list(tt['name'].astype(str))
    renew_names = list(rt['name'].astype(str))
    hydro_names = list(ht['short_name'].fillna(ht['name']).astype(str))

    tech_registry = []
    for n in thermal_names:
        carrier = tt.loc[tt['name'] == n, 'fuel_type'].iloc[0]
        tech_registry.append({'tech': n, 'name': n, 'carrier': carrier, 'is_storage': False})
    for n in renew_names:
        carrier = rt.loc[rt['name'] == n, 'tech'].iloc[0]
        tech_registry.append({'tech': n, 'name': n, 'carrier': carrier, 'is_storage': False})
    # Hydro stations: carrier = 'hydro', and they need a station_id for
    # the per-station hydro module too.
    for _, h in ht.iterrows():
        n = str(h.get('short_name') or h['name'])
        tech_registry.append({'tech': n, 'name': n, 'carrier': 'hydro', 'is_storage': False})

    return zones, thermal_names, renew_names, hydro_names, tt, rt, ht, tech_registry


def build_tech_existing(tt, rt, ht, hydro_names):
    """Capacity-by-zone-tech-commission_year for the existing fleet."""
    rows = []
    for _, r in tt.iterrows():
        rows.append({
            'tech': r['name'], 'zone': r['node'], 'commission_year': YEAR,
            'unit': 'MW', 'capacity': float(r['max_capacity']),
        })
    for _, r in rt.iterrows():
        rows.append({
            'tech': r['name'], 'zone': r['node_id'], 'commission_year': YEAR,
            'unit': 'MW', 'capacity': float(r['p_nom']),
        })
    for n, (_, r) in zip(hydro_names, ht.iterrows()):
        rows.append({
            'tech': n, 'zone': r['node_id'], 'commission_year': YEAR,
            'unit': 'MW', 'capacity': float(r['N(MW)']),
        })
    df = pd.DataFrame(rows, columns=['tech', 'zone', 'commission_year', 'unit', 'capacity'])
    return df


def build_capacity_factor(rt):
    """Per-renewable hourly capacity factor for tech_max_gen_profile.csv.

    The renewable plant CFs in capacity_factor.csv are keyed by plant
    name (csv column). Map each column to the matching renewable
    tech name; emit one row per (tech, zone, year, month, hour).
    """
    cf = pd.read_csv(SRC / 'capacity_factor.csv')
    cf['ts'] = pd.to_datetime(cf['time'])
    cf['hour'] = ((cf['ts'] - cf['ts'].iloc[0]).dt.total_seconds() // 3600).astype(int) + 1
    cf = cf.drop(columns=['time', 'ts'])
    plant_cols = [c for c in cf.columns if c != 'hour']
    # Map plant -> (tech_name, zone). Most names in capacity_factor.csv
    # match the Renewable sheet's `name`. Build a quick lookup.
    rt_idx = rt.set_index('name')
    rows = []
    skipped = []
    for plant in plant_cols:
        if plant not in rt_idx.index:
            skipped.append(plant)
            continue
        zone = str(rt_idx.loc[plant, 'node_id'])
        for _, r in cf.iterrows():
            rows.append({
                'tech': plant, 'zone': zone, 'year': YEAR,
                'month': 1, 'hour': int(r['hour']),
                'unit': 'fraction', 'value': float(r[plant]),
            })
    if skipped:
        print(f'  (skipped {len(skipped)} CF columns with no Renewable-sheet match: '
              f'{skipped[:5]}{"..." if len(skipped) > 5 else ""})')
    return pd.DataFrame(rows, columns=['tech', 'zone', 'year', 'month', 'hour', 'unit', 'value'])


def build_inflow(ht, hydro_names):
    """Hourly natural inflow per hydro station, in m^3/s.

    Source ``inflow.csv`` covers 2016-2019; the target dispatch year
    is 2023 (load data only goes that far). We re-use 2019 as the
    inflow proxy and re-stamp the timestamps onto target-year hours
    1..8760. Common modelling shortcut when an exactly-matching
    inflow year isn't available.
    """
    inf = pd.read_csv(SRC / 'inflow.csv')
    inf['ts'] = pd.to_datetime(inf['time'])
    proxy_year = 2019
    inf = inf[inf['ts'].dt.year == proxy_year].copy().reset_index(drop=True)
    inf['hour'] = (inf.index + 1).astype(int)
    # Source CSV has columns "1" through "17" (sequential indices,
    # NOT stcd) plus "18_import" through "25_import" (import nodes
    # from neighbouring countries). The 14 hydro stations in
    # hydropower.xlsx map to columns "1".."14" by row order.
    rows = []
    skipped = []
    for i, name in enumerate(hydro_names, start=1):
        col = str(i)
        if col not in inf.columns:
            skipped.append((col, name))
            continue
        for _, r in inf.iterrows():
            rows.append({
                'tech': name, 'year': YEAR, 'month': 1,
                'hour': int(r['hour']),
                'unit': 'm3/s', 'value': float(r[col]),
            })
    if skipped:
        print(f'  (skipped {len(skipped)} hydro stations with no inflow column)')
    return pd.DataFrame(rows, columns=['tech', 'year', 'month', 'hour', 'unit', 'value'])


def build_transmission(gt):
    """transmission_existing.csv (both directions) + susceptance.

    The grid_topology.csv has 615 directed edges; PREP-SHOT's
    transport model already expects both directions so we leave them
    as-is.
    """
    rows = []
    for _, r in gt.iterrows():
        s, k = str(r['source']), str(r['sink'])
        # Source uses -1 as a sentinel for "no user override; use the
        # computed thermal limit". Handle explicitly rather than via
        # `or`, which would select -1 because it's truthy in Python.
        ulc = float(r.get('user_line_cap', 0) or 0)
        cap = ulc if ulc > 0 else float(r.get('thermal_limit') or 0)
        if cap <= 0:
            continue
        rows.append({
            'zone1': s, 'zone2': k, 'commission_year': YEAR,
            'unit': 'MW', 'value': cap,
        })
        # Add the reverse direction with same capacity, mirroring
        # the existing PREP-SHOT examples' convention.
        rows.append({
            'zone1': k, 'zone2': s, 'commission_year': YEAR,
            'unit': 'MW', 'value': cap,
        })
    df = pd.DataFrame(rows, columns=['zone1', 'zone2', 'commission_year', 'unit', 'value'])

    # Susceptance: one row per UNORDERED pair, so the dc_flow module
    # creates one constraint per electrical line.
    susc_rows = []
    seen_pairs = set()
    for _, r in gt.iterrows():
        a, b = sorted([str(r['source']), str(r['sink'])])
        if (a, b) in seen_pairs:
            continue
        seen_pairs.add((a, b))
        b_pu = float(r.get('user_susceptance') or 0)
        # Source uses -1 sentinel for "compute from reactance / km".
        # We use the b_pu when positive; else fall back to a default.
        if b_pu <= 0:
            # Default: 2 * cap_MW per radian -- matches the heuristic
            # we use in southeast_asia. Saturates the line at ~0.5 rad.
            cap = float(r.get('user_line_cap') or r.get('thermal_limit') or 0)
            b_pu = max(2.0 * cap, 1000.0) if cap > 0 else 1000.0
        susc_rows.append({'zone1': a, 'zone2': b, 'unit': 'MW/rad', 'value': b_pu})
    susc = pd.DataFrame(susc_rows, columns=['zone1', 'zone2', 'unit', 'value'])
    return df, susc


# ---------- entry point --------------------------------------------------


def main():
    print(f'Reading source: {SRC}')
    print(f'Writing PREP-SHOT inputs to: {OUT}')

    zones, thermal_names, renew_names, hydro_names, tt, rt, ht, tech_registry = (
        build_zones_and_techs()
    )
    print(f'  zones (= bus ids): {len(zones)}')
    print(f'  thermal techs: {len(thermal_names)}')
    print(f'  renewable techs: {len(renew_names)}')
    print(f'  hydro techs: {len(hydro_names)}')

    # 1. tech_registry.csv
    pd.DataFrame(tech_registry, columns=['tech', 'name', 'carrier', 'is_storage']).to_csv(
        OUT / 'tech_registry.csv', index=False
    )
    # 2. tech_existing.csv -- the fixed fleet (PCM has no expansion).
    fleet = build_tech_existing(tt, rt, ht, hydro_names)
    fleet.to_csv(OUT / 'tech_existing.csv', index=False)
    # 3. tech_existing_pcm.csv -- the same data reshaped as the
    #    cap-source CSV consumed by `python -m prepshot.pcm
    #    --cap-source ...`. Cols: zone, tech, year, capacity.
    cap_source = fleet.rename(columns={'commission_year': 'year'})[
        ['zone', 'tech', 'year', 'capacity']
    ]
    cap_source.to_csv(OUT / 'capacity_pcm.csv', index=False)
    print(f'  tech_existing.csv: {len(fleet)} rows')

    # 4. demand.csv -- the big one (~4.1M rows).
    dem = long_demand()
    dem.to_csv(OUT / 'demand.csv', index=False)
    print(f'  demand.csv: {len(dem):,} rows')

    # 5. transmission_existing.csv + transmission_susceptance.csv
    gt = grid_topology()
    trans, susc = build_transmission(gt)
    trans.to_csv(OUT / 'transmission_existing.csv', index=False)
    susc.to_csv(OUT / 'transmission_susceptance.csv', index=False)
    print(f'  transmission_existing.csv: {len(trans)} rows ({len(susc)} pairs)')

    # 6. tech_max_gen_profile.csv -- VRE capacity factors.
    cf = build_capacity_factor(rt)
    cf.to_csv(OUT / 'tech_max_gen_profile.csv', index=False)
    print(f'  tech_max_gen_profile.csv: {len(cf):,} rows')

    # 7. reservoir_inflow.csv -- hydro natural inflow.
    inf = build_inflow(ht, hydro_names)
    inf.to_csv(OUT / 'reservoir_inflow.csv', index=False)
    print(f'  reservoir_inflow.csv: {len(inf):,} rows')

    # 8. Hydro per-station static / per-station-month tables.
    #    ht has all the params we need: head, coeff, V_max/min,
    #    outflow_max/min, downstream, delay_hours.
    pd.DataFrame({
        'tech': hydro_names, 'unit': 'm', 'head': ht['head'].astype(float).values,
    }).to_csv(OUT / 'reservoir_head.csv', index=False)
    pd.DataFrame({
        'tech': hydro_names, 'unit': 'MW/(m*m3/s)',
        'coefficient': ht['coeff'].astype(float).values,
    }).to_csv(OUT / 'reservoir_coefficient.csv', index=False)
    pd.DataFrame({
        'tech': hydro_names, 'unit': 'MW',
        'capacity_max': ht['N_max'].astype(float).values,
    }).to_csv(OUT / 'reservoir_capacity_max.csv', index=False)
    pd.DataFrame({
        'tech': hydro_names, 'unit': 'MW',
        'capacity_min': ht['N_min'].fillna(0).astype(float).values,
    }).to_csv(OUT / 'reservoir_capacity_min.csv', index=False)
    pd.DataFrame({
        'tech': hydro_names, 'unit': 'm3/s',
        'generation_flow_max': ht['GQ_max'].astype(float).values,
    }).to_csv(OUT / 'reservoir_generation_flow_max.csv', index=False)
    pd.DataFrame({
        'tech': hydro_names, 'unit': 'm3/s',
        'outflow_max': ht['outflow_max'].astype(float).values,
    }).to_csv(OUT / 'reservoir_outflow_max.csv', index=False)
    pd.DataFrame({
        'tech': hydro_names, 'unit': 'm3/s',
        'outflow_min': ht['outflow_min'].fillna(0).astype(float).values,
    }).to_csv(OUT / 'reservoir_outflow_min.csv', index=False)
    # Per-month-hour storage bounds: ship constant V_min / V_max
    # (the source has no time variation). PREP-SHOT keys
    # ``reservoir_storage_max[s, year=1, month=1..H]`` so we emit one
    # row per (tech, year=1, month=h) for h in 1..8760.
    H = 8760
    rows_min = []
    rows_max = []
    for n, vmin, vmax in zip(hydro_names, ht['V_min'].fillna(0).values, ht['V_max'].values):
        for h in range(1, H + 1):
            rows_min.append({'tech': n, 'year': 1, 'month': h, 'unit': 'm3', 'value': float(vmin)})
            rows_max.append({'tech': n, 'year': 1, 'month': h, 'unit': 'm3', 'value': float(vmax)})
    pd.DataFrame(rows_min).to_csv(OUT / 'reservoir_storage_min.csv', index=False)
    pd.DataFrame(rows_max).to_csv(OUT / 'reservoir_storage_max.csv', index=False)
    # Initial / final storage at half-full (matches the v1.17 SE Asia
    # convention for stable rolling-horizon).
    init_storage = (ht['V_max'].astype(float) * 0.5).values
    pd.DataFrame({
        'tech': hydro_names, 'unit': 'm3', 'value': init_storage,
    }).to_csv(OUT / 'reservoir_initial_storage_level.csv', index=False)
    pd.DataFrame({
        'tech': hydro_names, 'unit': 'm3', 'value': init_storage,
    }).to_csv(OUT / 'reservoir_final_storage_level.csv', index=False)
    # Cascade topology: use `downstream` and `delay_hours` from the
    # hydro sheet to build water_delay_time.csv.
    wdt_rows = []
    for n, ds, dly in zip(
        hydro_names, ht['downstream'].fillna('').values,
        ht['delay_hours'].fillna(0).values,
    ):
        if not ds or str(ds).strip() == '' or str(ds).lower() == 'nan':
            continue
        # `downstream` is the stcd of the downstream station; map it
        # to a tech name.
        ds_int = None
        try:
            ds_int = int(float(ds))
        except (TypeError, ValueError):
            continue
        match = ht[ht['stcd'].astype(int) == ds_int]
        if match.empty:
            continue
        downstream_name = str(match['short_name'].iloc[0] or match['name'].iloc[0])
        wdt_rows.append({
            'upstream_tech': n, 'downstream_tech': downstream_name,
            'delay': int(float(dly)),
        })
    pd.DataFrame(
        wdt_rows or [], columns=['upstream_tech', 'downstream_tech', 'delay'],
    ).to_csv(OUT / 'reservoir_water_delay_time.csv', index=False)
    # reservoir_zone.csv: which zone owns each station.
    pd.DataFrame({
        'tech': hydro_names,
        'zone': [str(z) for z in ht['node_id'].values],
    }).to_csv(OUT / 'reservoir_zone.csv', index=False)
    # Empty Z(Q,V) lookup tables -- iteration_number=1 will skip them.
    pd.DataFrame(columns=['tech', 'tailrace_level', 'discharge']).to_csv(
        OUT / 'reservoir_tailrace_level_discharge_function.csv', index=False
    )
    pd.DataFrame(columns=['tech', 'forebay_level', 'volume']).to_csv(
        OUT / 'reservoir_forebay_level_volume_function.csv', index=False
    )

    # 9. tech_lifetime.csv -- everyone gets a 100-year lifetime so
    #    the existing fleet stays in service for all modelled years.
    rows = []
    for n in thermal_names + renew_names + hydro_names:
        rows.append({'tech': n, 'year': YEAR, 'unit': 'years', 'value': LIFETIME_YEARS})
    pd.DataFrame(rows).to_csv(OUT / 'tech_lifetime.csv', index=False)

    # 10. Variable cost = thermal operation_cost; renewables / hydro
    #     get 0. Used by the flat-rate fuel-cost path.
    var_cost = []
    for _, r in tt.iterrows():
        var_cost.append({
            'tech': r['name'], 'year': YEAR, 'unit': 'dollar/MWh',
            'value': float(r['operation_cost']),
        })
    for n in renew_names + hydro_names:
        var_cost.append({'tech': n, 'year': YEAR, 'unit': 'dollar/MWh', 'value': 0.0})
    pd.DataFrame(var_cost).to_csv(OUT / 'tech_variable_OM_cost.csv', index=False)

    # Fuel price = 0 (operation_cost above already includes fuel for
    # the source dataset). Setting fuel_price=0 keeps PREP-SHOT's
    # fuel_cost_breakdown contribution at zero so we don't double
    # count.
    fuel_price = pd.DataFrame([
        {'tech': n, 'year': YEAR, 'unit': 'dollar/MWh', 'value': 0.0}
        for n in thermal_names + renew_names + hydro_names
    ])
    fuel_price.to_csv(OUT / 'tech_fuel_price.csv', index=False)

    # 11. tech_fixed_OM_cost = fixed_cost from Thermal sheet, 0 for
    #     others.
    fix = []
    for _, r in tt.iterrows():
        fix.append({
            'tech': r['name'], 'year': YEAR, 'unit': 'dollar/MW/yr',
            'value': float(r.get('fixed_cost') or 0.0),
        })
    for n in renew_names + hydro_names:
        fix.append({'tech': n, 'year': YEAR, 'unit': 'dollar/MW/yr', 'value': 0.0})
    pd.DataFrame(fix).to_csv(OUT / 'tech_fixed_OM_cost.csv', index=False)

    # 12. Investment cost = 0 (PCM has no expansion). cap_newtech
    #     gets locked to 0 by the PCM driver.
    inv = pd.DataFrame([
        {'tech': n, 'year': YEAR, 'unit': 'dollar/MW',  'value': 0.0}
        for n in thermal_names + renew_names + hydro_names
    ])
    inv.to_csv(OUT / 'tech_investment_cost.csv', index=False)

    # 13. tech_capacity_max / _min: bound cap_newtech to 0 implicitly.
    #     Set capacity_max = the existing fleet's MW so the model's
    #     own bound matches what cap_existing already has.
    fleet_by_zt = fleet.set_index(['zone', 'tech'])['capacity']
    rows_max = []
    rows_min = []
    for z in zones:
        for n in thermal_names + renew_names + hydro_names:
            cap = float(fleet_by_zt.get((z, n), 0.0))
            rows_max.append({
                'zone': z, 'tech': n, 'year': YEAR,
                'unit': 'MW', 'value': cap,
            })
            rows_min.append({
                'zone': z, 'tech': n, 'year': YEAR,
                'unit': 'MW', 'value': 0.0,
            })
    pd.DataFrame(rows_max).to_csv(OUT / 'tech_capacity_max.csv', index=False)
    pd.DataFrame(rows_min).to_csv(OUT / 'tech_capacity_min.csv', index=False)

    # 14. Other minimal-but-required scalar tables. Carbon: ship `inf`
    #     so it's non-binding. Same for the offset machinery.
    pd.DataFrame([{
        'limit_id': 'system_cap', 'year': YEAR, 'unit': 'tonneCO2',
        'value': float('inf'), 'zones': ','.join(zones),
    }]).to_csv(OUT / 'policy_carbon_emission_limit.csv', index=False)
    for nm in (
        'policy_carbon_offset_limit', 'policy_carbon_offset_price',
        'policy_carbon_tax',
    ):
        # Per-(zone, year) zero rows.
        pd.DataFrame([
            {'zone': z, 'year': YEAR, 'unit': 'fraction', 'value': 0.0}
            for z in zones
        ]).to_csv(OUT / f'{nm}.csv', index=False)

    # Emission factor: thermal carries its fuel's emission factor;
    # renewables / hydro = 0. Numbers from NREL ATB ballpark.
    emit_kg_per_mwh = {
        'coal': 900.0, 'gas': 400.0, 'fuel_oil': 700.0,
        'biomass': 0.0, 'biogas': 0.0, 'solid_waste': 0.0,
    }
    rows = []
    for _, r in tt.iterrows():
        rows.append({
            'tech': r['name'], 'year': YEAR, 'unit': 'tonneCO2/MWh',
            'value': emit_kg_per_mwh.get(str(r['fuel_type']), 0.0) / 1000.0,
        })
    for n in renew_names + hydro_names:
        rows.append({'tech': n, 'year': YEAR, 'unit': 'tonneCO2/MWh', 'value': 0.0})
    pd.DataFrame(rows).to_csv(OUT / 'tech_emission_factor.csv', index=False)

    # 15. Discount factor: shipped year-by-zone, ratio 1.0 = no
    #     discounting (PCM is single-year, NPV doesn't matter).
    pd.DataFrame([
        {'zone': z, 'year': YEAR, 'unit': 'fraction', 'value': 1.0}
        for z in zones
    ]).to_csv(OUT / 'economic_discount_factor.csv', index=False)

    # 16. Ramp rates -- pass-through from Thermal sheet.
    rows_up = []
    rows_dn = []
    for _, r in tt.iterrows():
        rate = float(r.get('ramp_rate') or 1.0)
        # Source ramp_rate is fraction-of-cap-per-hour; PREP-SHOT
        # expects fraction-of-cap-per-dt-step. With dt=1 hour they
        # match.
        rows_up.append({'tech': r['name'], 'unit': 'fraction', 'ramp_up': rate})
        rows_dn.append({'tech': r['name'], 'unit': 'fraction', 'ramp_down': rate})
    for n in renew_names + hydro_names:
        rows_up.append({'tech': n, 'unit': 'fraction', 'ramp_up': 1.0})
        rows_dn.append({'tech': n, 'unit': 'fraction', 'ramp_down': 1.0})
    pd.DataFrame(rows_up).to_csv(OUT / 'tech_ramp_up.csv', index=False)
    pd.DataFrame(rows_dn).to_csv(OUT / 'tech_ramp_down.csv', index=False)

    # 17. Transmission line auxiliary tables: efficiency = 0.95,
    #     lifetime = 100 years, candidates = 0 (no expansion in PCM).
    pd.DataFrame([
        {'zone1': r['zone1'], 'zone2': r['zone2'], 'unit': 'fraction', 'value': 0.95}
        for _, r in trans.iterrows()
    ]).to_csv(OUT / 'transmission_line_efficiency.csv', index=False)
    pd.DataFrame([
        {'zone1': r['zone1'], 'zone2': r['zone2'], 'year': YEAR,
         'unit': 'years', 'value': LIFETIME_YEARS}
        for _, r in trans.iterrows()
    ]).to_csv(OUT / 'transmission_lifetime.csv', index=False)
    pd.DataFrame([
        {'zone1': r['zone1'], 'zone2': r['zone2'], 'year': YEAR,
         'unit': 'MW', 'capacity_max': 0.0, 'capacity_min': 0.0}
        for _, r in trans.iterrows()
    ]).to_csv(OUT / 'transmission_candidates.csv', index=False)
    pd.DataFrame([
        {'zone1': r['zone1'], 'zone2': r['zone2'], 'year': YEAR,
         'unit': 'dollar/MW', 'value': 0.0}
        for _, r in trans.iterrows()
    ]).to_csv(OUT / 'transmission_investment_cost.csv', index=False)
    pd.DataFrame([
        {'zone1': r['zone1'], 'zone2': r['zone2'], 'year': YEAR,
         'unit': 'dollar/MW/yr', 'value': 0.0}
        for _, r in trans.iterrows()
    ]).to_csv(OUT / 'transmission_fixed_OM_cost.csv', index=False)
    pd.DataFrame([
        {'zone1': r['zone1'], 'zone2': r['zone2'], 'year': YEAR,
         'unit': 'dollar/MWh', 'value': 0.0}
        for _, r in trans.iterrows()
    ]).to_csv(OUT / 'transmission_variable_OM_cost.csv', index=False)
    pd.DataFrame([
        {'zone1': r['zone1'], 'zone2': r['zone2'], 'unit': 'km',
         'value': float(gt[(gt['source']==r['zone1']) & (gt['sink']==r['zone2'])]['distance'].iloc[0])
                  if not gt[(gt['source']==r['zone1']) & (gt['sink']==r['zone2'])].empty else 0.0}
        for _, r in trans.iterrows()
    ]).to_csv(OUT / 'transmission_distance.csv', index=False)

    # 18. tech_max_gen_profile defaults to 1 if a tech is not listed
    # (PREP-SHOT convention). Same for tech_min_gen_profile.
    pd.DataFrame(
        columns=['tech', 'zone', 'year', 'month', 'hour', 'unit', 'value'],
    ).to_csv(OUT / 'tech_min_gen_profile.csv', index=False)

    # 19. Storage scaffolding: empty. We have no batteries in the
    # source. Provide empty CSVs so PREP-SHOT's loader is happy.
    pd.DataFrame(columns=['tech', 'unit', 'value']).to_csv(
        OUT / 'storage_initial_level.csv', index=False
    )
    pd.DataFrame(columns=['tech', 'unit', 'value']).to_csv(
        OUT / 'storage_discharge_efficiency.csv', index=False
    )

    # 20. tech_candidates.csv -- PCM has no expansion, but the loader
    # expects this file. Empty rows = no candidates.
    pd.DataFrame(columns=['zone', 'tech', 'year', 'unit', 'capacity_max', 'capacity_min']).to_csv(
        OUT / 'tech_candidates.csv', index=False
    )

    print()
    print(f'Done. Inputs in: {OUT}')
    print(f'PCM cap-source CSV: {OUT / "capacity_pcm.csv"}')


if __name__ == '__main__':
    main()
