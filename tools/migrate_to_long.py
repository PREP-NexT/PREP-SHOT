#!/usr/bin/env python3
"""Convert v1.4.x wide-format Excel inputs to v1.5.0+ long-format CSV.

Usage::

    python tools/migrate_to_long.py <input_dir>

This tool is for users with custom input directories that pre-date
v1.5.0 and still contain wide-format ``.xlsx`` files. The shipped
``input/`` and ``southeast_asia/`` directories were already migrated
in the v1.5.0 release.

The tool is **self-contained**: it bundles its own copy of the
v1.4.x wide-format spec (since by the time you run it, ``params.json``
has already been overwritten with the v1.5.0 long-format spec). It
also has its own flatten-to-dict implementation so it works under
pandas >= 2.0 (the v1.4.x ``read_excel`` relied on ``unstack`` which
no longer accepts duplicate column-level values in pandas 2.x).

Scope
-----
Handles **dict-shape** parameters automatically (the 38 params in
DIM_NAMES below). For each, reads ``<input_dir>/<param>.xlsx`` using
the bundled v1.4.x spec, emits ``<input_dir>/<param>.csv`` in long
format, and removes the original.

Three kinds of params NOT handled automatically:

1. The four **Group-3 table-shaped** lookups (water_delay_time,
   reservoir_tailrace_level_discharge_function,
   reservoir_forebay_level_volume_function) -- already 3-column long
   internally. To migrate, just rename the .xlsx to .csv (or open in
   Excel and Save As CSV).

2. **reservoir_characteristics** -- split into 8 single-field CSVs in
   v1.5.0. To migrate, see the shipped ``input/`` directory for the
   canonical shape (one CSV per used field: ``reservoir_zone``,
   ``reservoir_coefficient``, ``reservoir_capacity_max``, etc.).

3. **Annotation columns** (``unit``, ``name``) -- the v1.5.0 CSVs
   include human-readable annotation columns. The tool emits
   minimal CSVs without these; refer to the shipped directories
   to copy in unit / name annotations as desired.
"""
import json
import os
import sys

import pandas as pd


# --------------------------------------------------------------------
# v1.4.x wide-format spec (bundled here because the on-disk params.json
# is now v1.5.0 long-format and no longer carries this information).
# Each entry is (index_cols, header_rows, first_col_only, drop_na).
# unstack_levels was always "all of the row levels" (or null for
# table-shape entries), so it's implicit in flatten_wide_to_dict.
# --------------------------------------------------------------------
LEGACY_WIDE_SPEC = {
    "historical_capacity":               ([0],       [0, 1], False, True),
    "capacity_factor":                   ([0, 1, 2], [0, 1], False, True),
    "carbon_emission_limit":             ([0],       [0],    True,  True),
    "emission_factor":                   ([0],       [0],    False, True),
    "demand":                            ([0, 1, 2], [0],    False, True),
    "discount_factor":                   ([0],       [0],    True,  True),
    "distance":                          ([0],       [0],    False, True),
    "discharge_efficiency":              ([0],       [0],    False, True),
    "charge_efficiency":                 ([0],       [0],    False, True),
    "energy_to_power_ratio":             ([0],       [0],    True,  True),
    "fuel_price":                        ([0],       [0],    False, True),
    "predefined_hydropower":             ([0, 1, 2], [0, 1], False, True),
    "inflow":                            ([0, 1, 2], [0],    False, True),
    "initial_energy_storage_level":      ([0],       [0],    False, True),
    "lifetime":                          ([0],       [0],    False, True),
    "new_technology_lower_bound":        ([0],       [0, 1], False, True),
    "new_technology_upper_bound":        ([0],       [0, 1], False, True),
    "ramp_down":                         ([0],       [0],    True,  True),
    "ramp_up":                           ([0],       [0],    True,  True),
    "reservoir_storage_upper_bound":     ([0, 1],    [0],    False, True),
    "reservoir_storage_lower_bound":     ([0, 1],    [0],    False, True),
    "final_reservoir_storage_level":     ([0],       [0],    False, True),
    "initial_reservoir_storage_level":   ([0],       [0],    False, True),
    "technology_fixed_OM_cost":          ([0],       [0],    False, True),
    "technology_investment_cost":        ([0],       [0],    False, True),
    "technology_portfolio":              ([0],       [0],    False, True),
    "technology_upper_bound":            ([0],       [0, 1], False, True),
    "technology_lower_bound":            ([0],       [0, 1], False, True),
    "carbon_tax":                        ([0],       [0],    False, True),
    "carbon_offset_price":               ([0],       [0],    False, True),
    "carbon_offset_limit":               ([0],       [0],    False, True),
    "technology_variable_OM_cost":       ([0],       [0],    False, True),
    "transmission_line_existing_capacity": ([0],     [0],    False, True),
    "transmission_line_efficiency":      ([0],       [0],    False, True),
    "transmission_line_investment_cost": ([0],       [0],    False, True),
    "transmission_line_fixed_OM_cost":   ([0],       [0],    False, True),
    "transmission_line_variable_OM_cost":([0],       [0],    False, True),
    "transmission_line_lifetime":        ([0],       [0],    False, True),
    "technology_type":                   ([0],       [0],    True,  True),
}


# v1.5.0 long-CSV column order (last column is the value).
DIM_NAMES = {
    "historical_capacity": ["zone", "tech", "age"],
    "capacity_factor": ["tech", "zone", "year", "month", "hour"],
    "carbon_emission_limit": ["year"],
    "emission_factor": ["tech", "year"],
    "demand": ["zone", "year", "month", "hour"],
    "discount_factor": ["year"],
    "distance": ["zone1", "zone2"],
    "discharge_efficiency": ["tech", "year"],
    "charge_efficiency": ["tech", "year"],
    "energy_to_power_ratio": ["tech"],
    "fuel_price": ["tech", "year"],
    "predefined_hydropower": ["tech", "zone", "month", "hour", "year_offset"],
    "inflow": ["station_id", "year", "month", "hour"],
    "initial_energy_storage_level": ["tech", "zone"],
    "lifetime": ["tech", "year"],
    "new_technology_lower_bound": ["zone", "tech", "year"],
    "new_technology_upper_bound": ["zone", "tech", "year"],
    "ramp_down": ["tech"],
    "ramp_up": ["tech"],
    "reservoir_storage_upper_bound": ["station_id", "year", "month"],
    "reservoir_storage_lower_bound": ["station_id", "year", "month"],
    "final_reservoir_storage_level": ["station_id", "year"],
    "initial_reservoir_storage_level": ["station_id", "year"],
    "technology_fixed_OM_cost": ["tech", "year"],
    "technology_investment_cost": ["tech", "year"],
    "technology_portfolio": ["tech", "zone"],
    "technology_upper_bound": ["zone", "tech", "year"],
    "technology_lower_bound": ["zone", "tech", "year"],
    "carbon_tax": ["zone", "year"],
    "carbon_offset_price": ["zone", "year"],
    "carbon_offset_limit": ["zone", "year"],
    "technology_variable_OM_cost": ["tech", "year"],
    "transmission_line_existing_capacity": ["zone1", "zone2"],
    "transmission_line_efficiency": ["zone1", "zone2"],
    "transmission_line_investment_cost": ["zone1", "zone2"],
    "transmission_line_fixed_OM_cost": ["zone1", "zone2"],
    "transmission_line_variable_OM_cost": ["zone1", "zone2"],
    "transmission_line_lifetime": ["zone1", "zone2"],
    "technology_type": ["tech"],
}


def flatten_wide_to_dict(df, dropna=True):
    """Replicate the v1.4.x behavior of
    ``df.unstack(level=[all row levels]).dropna().to_dict()`` using
    direct cell iteration. Works under pandas >= 2.0 (the legacy
    ``unstack`` rejects duplicate column-level values in 2.x).

    The output dict keys are (existing_col_levels..., row_levels...);
    a 1-element tuple is unwrapped to its scalar value to match the
    legacy convention for single-dim params.
    """
    cols_multi = isinstance(df.columns, pd.MultiIndex)
    rows_multi = isinstance(df.index, pd.MultiIndex)
    result = {}
    for col_pos in range(df.shape[1]):
        col = df.columns[col_pos]
        col_tuple = tuple(col) if cols_multi else (col,)
        series = df.iloc[:, col_pos]
        for row_idx, value in series.items():
            if dropna and pd.isna(value):
                continue
            row_tuple = tuple(row_idx) if rows_multi else (row_idx,)
            full_key = (*col_tuple, *row_tuple)
            if len(full_key) == 1:
                full_key = full_key[0]
            result[full_key] = value
    return result


def _migrate_one(input_dir, key):
    """Migrate one parameter's xlsx -> csv. Returns True if converted."""
    spec = LEGACY_WIDE_SPEC.get(key)
    if spec is None:
        return False
    idx, hdr, first_col_only, dropna = spec
    src = os.path.join(input_dir, f"{key}.xlsx")
    dst = os.path.join(input_dir, f"{key}.csv")
    if not os.path.exists(src):
        return False

    df = pd.read_excel(src, index_col=idx, header=hdr)

    if first_col_only:
        # Single-column data; the row index is the only dim.
        s = df.iloc[:, 0]
        if dropna:
            s = s.dropna()
        data = s.to_dict()
    else:
        data = flatten_wide_to_dict(df, dropna=dropna)

    dim_names = DIM_NAMES.get(key)
    if dim_names is None:
        raise RuntimeError(f"{key}: missing DIM_NAMES entry")

    rows = []
    for k, v in data.items():
        kt = k if isinstance(k, tuple) else (k,)
        if len(kt) != len(dim_names):
            raise RuntimeError(
                f"{key}: dim mismatch -- key {kt} has {len(kt)} elements but "
                f"DIM_NAMES has {len(dim_names)}: {dim_names}"
            )
        rows.append((*kt, v))

    out = pd.DataFrame(rows, columns=[*dim_names, "value"])
    out.to_csv(dst, index=False)
    os.remove(src)
    print(f"  {key}: wrote {dst} ({len(out)} rows); removed {src}")
    return True


def main():
    if len(sys.argv) != 2:
        print("usage: python tools/migrate_to_long.py <input_dir>")
        sys.exit(2)
    input_dir = sys.argv[1]
    if not os.path.isdir(input_dir):
        print(f"error: {input_dir} is not a directory")
        sys.exit(2)

    print(f"Migrating wide xlsx -> long csv in {input_dir}/ ...")
    converted = 0
    for key in LEGACY_WIDE_SPEC:
        if _migrate_one(input_dir, key):
            converted += 1
    print(f"Done. Converted {converted} dict-shape parameters in {input_dir}/.")
    print()
    print("Manual steps still required (see file docstring for details):")
    print(f"  - Group-3 table-shape lookups in {input_dir}/")
    print(f"    (water_delay_time, reservoir_*_level_*_function): rename .xlsx to .csv")
    print(f"  - {input_dir}/reservoir_characteristics.xlsx: split into 8 reservoir_<field>.csv")
    print(f"  - Optional: copy unit/name annotation columns from the shipped input/")


if __name__ == "__main__":
    main()
