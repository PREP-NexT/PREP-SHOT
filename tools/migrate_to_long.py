#!/usr/bin/env python3
"""Convert v1.4.x wide-format Excel inputs to v1.5.0 long-format CSV.

Usage::

    python tools/migrate_to_long.py <input_dir>

This handles three cases:

1. **Dict-shape wide xlsx -> long csv** (most params). Reads the file
   using the legacy v1.4.x params.json spec (hard-coded below), emits
   a long-format CSV with semantic dim column names from ``DIM_NAMES``.

2. **DataFrame-shape wide xlsx -> CSV (table format)**: water_delay_time
   and the two piecewise-function lookups (reservoir_tailrace_*,
   reservoir_forebay_*) are already 3-column long internally. Just
   resave the .xlsx as .csv.

3. **reservoir_characteristics -> 8 split CSVs** (one per field). The
   wide table is melted by field; only the model-used fields are kept
   (zone, coefficient, outflow_min/max, generation_flow_max,
   capacity_min/max, head). Descriptive fields (name, short_name, type)
   are dropped.

The script ships its OWN copy of the v1.4.x wide-format spec because
by the time a user runs it, params.json has already been overwritten
with the v1.5.0 long-format spec.
"""
import json
import os
import sys

import pandas as pd

# Hand-curated dimension-column names for each migrated parameter. The
# *order* must match the tuple-key order produced by the wide-format
# ``read_excel + unstack`` flow; column NAMES are for human readability
# only since the loader treats the last column as the value and all
# preceding ones as positional dimensions.
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

# NOTE: this script was originally written for the v1.4.x -> long-format
# migration where the in-tree params.json still carried wide-format
# specs. After v1.5.0 the on-disk params.json no longer holds those
# specs, so the script in its current form only handles parameters that
# are still declared with legacy wide keys (e.g. by users with their
# own pre-v1.5.0 params.json).
#
# A complete v1.4.x -> v1.5.0 migration tool is on the v1.6.0 roadmap.
# Until then, users moving from v1.4.x should either:
#   1. Ask in the issue tracker for help porting their custom inputs.
#   2. Pull a v1.4.x checkout, run this script, then upgrade. Or
#   3. Use the shipped input/ and southeast_asia/ directories as
#      reference shapes for the new long-format CSVs.
#
# Group 3 files now declare format:"table" or format:"long" in
# params.json; reservoir_characteristics has been split into eight
# reservoir_<field> CSVs.
DATAFRAME_FILES = {
    "water_delay_time",
    "reservoir_tailrace_level_discharge_function",
    "reservoir_forebay_level_volume_function",
}

# reservoir_characteristics is split into 8 single-field long CSVs
# in v1.5.0. Mapping from old wide-column name to new file suffix.
RESERVOIR_CHARACTERISTICS_FIELDS = {
    "zone": "zone",
    "coeff": "coefficient",
    "outflow_min": "outflow_min",
    "outflow_max": "outflow_max",
    "GQ_max": "generation_flow_max",
    "N_min": "capacity_min",
    "N_max": "capacity_max",
    "head": "head",
}


def _migrate_one(input_dir, key, spec):
    from prepshot.load_data import read_excel
    src = os.path.join(input_dir, f"{spec['file_name']}.xlsx")
    dst = os.path.join(input_dir, f"{spec['file_name']}.csv")
    if not os.path.exists(src):
        print(f"  {key}: skip (no .xlsx in {input_dir})")
        return False

    data = read_excel(
        src,
        spec["index_cols"], spec["header_rows"], spec["unstack_levels"],
        spec.get("first_col_only", False), spec.get("drop_na", True),
    )
    if not isinstance(data, dict):
        raise RuntimeError(
            f"{key}: read_excel returned {type(data).__name__}, not dict; "
            "this param looks Group-3 (table-shaped) and should be in KEEP_WIDE."
        )

    dim_names = DIM_NAMES.get(key)
    if dim_names is None:
        raise RuntimeError(f"{key}: missing DIM_NAMES entry; please add one.")

    rows = []
    for k, v in data.items():
        key_tuple = k if isinstance(k, tuple) else (k,)
        if len(key_tuple) != len(dim_names):
            raise RuntimeError(
                f"{key}: dim count mismatch -- key has {len(key_tuple)} "
                f"elements but DIM_NAMES has {len(dim_names)}: "
                f"{key_tuple} vs {dim_names}"
            )
        rows.append((*key_tuple, v))

    df = pd.DataFrame(rows, columns=[*dim_names, "value"])
    df.to_csv(dst, index=False)
    os.remove(src)
    print(f"  {key}: wrote {dst} ({len(df)} rows); removed {src}")
    return True


def main():
    if len(sys.argv) != 2:
        print("usage: python tools/migrate_to_long.py <input_dir>")
        sys.exit(2)
    input_dir = sys.argv[1]
    if not os.path.isdir(input_dir):
        print(f"error: {input_dir} is not a directory")
        sys.exit(2)

    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, repo_root)

    with open(os.path.join(repo_root, "params.json")) as f:
        params_info = json.load(f)

    print(f"Migrating wide xlsx -> long csv in {input_dir}/ ...")
    converted = 0
    for key, spec in params_info.items():
        if key.startswith("_"):
            continue
        if key in DATAFRAME_FILES:
            # These will be handled in v1.6.0's expanded migration tool.
            print(f"  {key}: skip (Group-3 DataFrame; manual migration for now)")
            continue
        if spec.get("format") == "long":
            print(f"  {key}: already long")
            continue
        if _migrate_one(input_dir, key, spec):
            converted += 1
    print(f"Done. Converted {converted} files in {input_dir}/.")


if __name__ == "__main__":
    main()
