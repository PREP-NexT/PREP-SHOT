#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""This module contains functions for loading and processing data from JSON
and Excel files.
"""

import json
import sys
import logging
from collections import defaultdict
from os import path

import pandas as pd

from prepshot.utils import (
    calc_inv_cost_factor, calc_cost_factor, calc_interest_rate,
)


# The input-file schema version this PREP-SHOT release expects. Bumped
# whenever a breaking change to the params.json / input/ shape lands. See
# doc/source/Stability.rst and doc/source/Changelog.rst for the migration
# story across versions.
#
# Schema 1 (v1.1.0): wide-format xlsx with hierarchical headers.
# Schema 2 (v1.5.0): long-format CSV (tidy) is the default; only the
#     four "Group 3" table-shaped lookups remain wide.
CURRENT_SCHEMA = 2


# Column names treated as annotations / metadata in long-format CSVs.
# The loader filters them out before keying so they never appear in the
# dim tuples. Any column whose name (case-insensitive) is in this set,
# or that ends in "_name" (e.g. zone_name, tech_name, station_name),
# is treated as a comment column rather than a dimension.
_LONG_CSV_META_COLS = frozenset({
    "unit", "units",
    "name",
    "commodity",
    "comment", "comments",
    "description", "desc",
    "note", "notes",
    "label",
})


def check_schema(params_info : dict) -> None:
    """Validate that ``params.json`` declares a compatible ``_schema_version``.

    Raises a :class:`RuntimeError` with a clear migration hint if the file
    is missing the stamp or carries a different version than this release
    supports.

    Parameters
    ----------
    params_info : dict
        Parsed contents of ``params.json``.
    """
    stamped = params_info.get("_schema_version")
    if stamped is None:
        raise RuntimeError(
            "params.json is missing '_schema_version'. This file was likely "
            "written for an older PREP-SHOT release (pre-v1.1.0). Add "
            f"'\"_schema_version\": {CURRENT_SCHEMA}' as the first key in "
            "params.json, and make sure your input directory matches the "
            f"v{CURRENT_SCHEMA} schema. See doc/source/Changelog.rst and "
            "doc/source/Stability.rst."
        )
    if stamped != CURRENT_SCHEMA:
        if stamped == 1 and CURRENT_SCHEMA >= 2:
            raise RuntimeError(
                "params.json declares _schema_version=1, which used wide "
                "Excel inputs. Schema 2 (v1.5.0+) uses long-format CSV. "
                "Run 'python tools/migrate_to_long.py <input_dir>' to "
                "convert your input files, then bump _schema_version to "
                f"{CURRENT_SCHEMA} in params.json. See "
                "doc/source/Changelog.rst for full migration notes."
            )
        raise RuntimeError(
            f"params.json declares _schema_version={stamped}, but this "
            f"PREP-SHOT release requires _schema_version={CURRENT_SCHEMA}. "
            "Migrate your input directory and update the stamp; see "
            "doc/source/Changelog.rst for the migration story."
        )


def load_json(file_path : str) -> dict:
    """Load data from a JSON file.

    Parameters
    ----------
    file_path : str
        Path to the JSON file.

    Returns
    -------
    dict
        Dictionary containing data from the JSON file.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def extract_config_data(config_data : dict) -> dict:
    """Extract necessary data from configuration settings.

    Parameters
    ----------
    config_data : dict
        Configuration data for the model.

    Returns
    -------
    dict
        Dictionary containing necessary configuration data.
    """
    # Extract parameters from configuration data.
    hour = int(config_data['general_parameters']['hour'])
    month = int(config_data['general_parameters']['month'])
    dt = int(config_data['general_parameters']['dt'])
    hours_in_year = int(config_data['general_parameters']['hours_in_year'])
    price = float(config_data['general_parameters']['price'])
    includes_hydrological_constraints =                                       \
        config_data['hydro_parameters']['isinflow']
    error_threshold = float(
        config_data['hydro_parameters']['error_threshold']
    )
    iteration_number = int(
        config_data['hydro_parameters']['iteration_number']
    )
    # Reserve module is opt-in. Missing section -> disabled, preserves
    # behavior of any pre-reserve config.json.
    is_reserve = bool(
        config_data.get('reserve_parameters', {}).get('is_reserve', False)
    )

    # Create dictionary with necessary configuration data.
    required_config_data = {
        'dt': dt,
        'price': price,
        'weight': (month * hour * dt) / hours_in_year,
        'solver': config_data['solver_parameters'],
        'isinflow': includes_hydrological_constraints,
        'error_threshold': error_threshold,
        'iteration_number': iteration_number,
        'is_reserve': is_reserve,
    }

    return required_config_data


def load_excel_data(
    input_folder : str, params_info : dict, data_store : dict
) -> None:
    """Load input data based on the provided parameters.

    The function dispatches on ``"format"``:

    * ``"format": "long"`` (default) -- load from a ``.csv`` file in tidy
      form (dimension columns first, value column last). See
      :func:`read_long_csv`.
    * ``"format": "table"`` -- load from a ``.csv`` file with multiple
      value columns, returned as a DataFrame so consumers can use
      ``groupby``, column-by-name access, etc.

    Each entry may also declare ``"required": false`` and a ``"default"``
    value. If the file for an optional parameter is missing, the loader
    silently substitutes the default (or an empty dict if none is given)
    and logs a debug message. Required parameters with missing files
    still terminate the process.

    The legacy function name is kept for backwards-compatible imports;
    despite the ``_excel_`` in the name, all on-disk inputs are CSV as
    of v1.5.0.

    Parameters
    ----------
    input_folder : str
        Path to the input folder.
    params_info : dict
        Dictionary containing parameter names and their corresponding file
        information.
    data_store : dict
        Dictionary to store loaded data.
    """
    for key, value in params_info.items():
        fmt = value.get("format", "long")
        ext = "csv"
        filename = path.join(input_folder, f"{value['file_name']}.{ext}")
        required = value.get("required", True)
        try:
            if fmt == "long":
                data_store[key] = read_long_csv(
                    filename,
                    dropna=value.get("drop_na", True),
                )
            elif fmt == "table":
                # Inherently table-shaped data (e.g. piecewise-function
                # lookups, delay matrices). Loaded as a DataFrame so the
                # consumer can slice by columns / groupby.
                data_store[key] = pd.read_csv(filename)
            else:
                raise ValueError(
                    f"Unknown format {fmt!r} for parameter {key}; expected "
                    "'long' or 'table'."
                )
        except FileNotFoundError as e:
            if required:
                logging.error("Error loading %s data: %s", value["file_name"], e)
                sys.exit(1)
            default = value.get("default", {})
            if not isinstance(default, dict):
                # Scalar default: wrap in a defaultdict so any tuple-key
                # lookup (e.g. params['carbon_tax'][z, y]) returns the
                # scalar without the model code needing to know whether
                # the file was loaded or not.
                scalar = default
                default = defaultdict(lambda: scalar)
            data_store[key] = default
            logging.debug(
                "Optional input '%s' not found at %s; using default.",
                key, filename,
            )


def read_long_csv(filename : str, dropna : bool = True) -> dict:
    """Read a long-format ("tidy") CSV input file.

    The convention is: dimension columns first, value column last. For
    example a 2-dim input ``carbon_tax`` looks like::

        zone,year,value
        BA1,2020,0
        BA1,2025,5
        BA2,2020,0

    The returned dict matches the shape produced by the wide-format
    reader for the same parameter:

    * 1 dimension column -> ``{key: value}`` (scalar keys)
    * 2+ dimension columns -> ``{(d1, d2, ...): value}`` (tuple keys)

    The ORDER of the dimension columns in the CSV determines the order
    of elements in the output keys, so model-side lookups work
    unchanged regardless of which format the file is in on disk.

    Parameters
    ----------
    filename : str
        Path to the CSV file.
    dropna : bool
        If True, rows with any NaN are dropped before keying.

    Returns
    -------
    dict
        Mapping from dimension key (or tuple of keys) to the value.
    """
    df = pd.read_csv(filename)
    # Drop documentation-only annotation columns. These are
    # human-readable annotations stored alongside the data (the
    # TransitionZero pattern: an ID column paired with a friendly name
    # column, plus per-row unit/commodity tags). The loader treats them
    # as informational so they never appear in the dim-key tuples.
    meta_cols = [
        c for c in df.columns
        if c.strip().lower() in _LONG_CSV_META_COLS
        or c.strip().lower().endswith("_name")
    ]
    if meta_cols:
        df = df.drop(columns=meta_cols)
    if dropna:
        df = df.dropna()
    cols = list(df.columns)
    if len(cols) < 2:
        raise ValueError(
            f"Long-format CSV {filename} needs at least one dimension column "
            f"plus a value column; got columns {cols}."
        )
    dim_cols = cols[:-1]
    value_col = cols[-1]

    # Cell-level type coercion. When a CSV value column mixes numeric and
    # string entries (e.g. reservoir_characteristics has both "Grand
    # Coulee" and 6765 in its value column), pandas reads the whole
    # column as strings. Try float per cell so numeric values come back
    # as numbers; non-numeric strings are passed through unchanged.
    def _coerce(v):
        if isinstance(v, str):
            try:
                return float(v)
            except ValueError:
                return v
        return v

    values = [_coerce(v) for v in df[value_col]]

    if len(dim_cols) == 1:
        return dict(zip(df[dim_cols[0]], values))
    keys = list(zip(*(df[c] for c in dim_cols)))
    return dict(zip(keys, values))


def extract_sets(data_store : dict) -> None:
    """Extract simple sets from loaded parameters.
    
    Parameters
    ----------
    data_store : dict
        Dictionary containing loaded parameters.
    """
    # discount_factor is now keyed by (zone, year) -- extract the year
    # set from the second element of each tuple key.
    data_store["year"] = sorted({y for (_, y) in data_store["discount_factor"].keys()})
    if "reservoir_zone" in data_store.keys():
        # reservoir_zone is keyed by hydro plant tech name (single-dim
        # long format). station_id is kept as an alias for back-compat
        # with code that referred to the old separate-station concept.
        data_store["station_id"] = list(data_store["reservoir_zone"].keys())
    data_store["hour"] = sorted({
        i[3] for i in data_store["demand"].keys() if isinstance(i[3], int)
    })
    data_store["month"] = sorted({
        i[2] for i in data_store["demand"].keys() if isinstance(i[2], int)
    })
    data_store["zone"] = list({i[0] for i in data_store["demand"].keys()})
    data_store["tech"] = data_store["technologies"]["tech"].tolist()


def compute_cost_factors(data_store : dict) -> None:
    """Calculate cost factors for various transmission investment and 
    operational costs.

    Parameters
    ----------
    data_store : dict
        Dictionary containing loaded parameters.
    """
    # Cost factors are computed per-zone because the discount rate can
    # differ by region (different cost of capital). Indices:
    #   trans_inv_factor[year, zone]
    #   inv_factor[tech, year, zone]
    #   fix_factor[year, zone]
    #   var_factor[year, zone]
    data_store["trans_inv_factor"] = {}
    data_store["inv_factor"] = {}
    data_store["fix_factor"] = {}
    data_store["var_factor"] = {}

    trans_line_lifetime = max(data_store["transmission_line_lifetime"].values())
    lifetime = data_store["lifetime"]
    y_min, y_max = min(data_store["year"]), max(data_store["year"])

    # Optional WACC: when the user supplies a finance model
    # (public_debt_ratio + cost-of-capital tables), inv_factor
    # discounts the construction outlay at a project-level WACC; fixed
    # / variable / transmission factors keep using the zonal discount
    # rate. With finance disabled, WACC == discount_rate, preserving
    # the v1.8.x objective.
    have_finance = bool(data_store.get("public_debt_ratio"))
    for zone in data_store["zone"]:
        for tech in data_store["tech"]:
            for year in data_store["year"]:
                discount_rate = data_store["discount_factor"][zone, year]
                next_year = year + 1 if year == y_max                          \
                    else data_store["year"][data_store["year"].index(year) + 1]
                if have_finance:
                    interest_rate = calc_interest_rate(
                        data_store["public_debt_ratio"][tech],
                        data_store["private_debt_ratio"][tech],
                        data_store["cost_of_public_debt"][tech, zone],
                        data_store["cost_of_private_equity"][tech, zone],
                        data_store["cost_of_private_debt"][tech, zone],
                    )
                else:
                    interest_rate = discount_rate
                data_store["trans_inv_factor"][year, zone] = calc_inv_cost_factor(
                    trans_line_lifetime, discount_rate, year, discount_rate,
                    y_min, y_max
                )
                data_store["inv_factor"][tech, year, zone] = calc_inv_cost_factor(
                    lifetime[tech, year], interest_rate, year, discount_rate,
                    y_min, y_max
                )
                data_store["fix_factor"][year, zone] = calc_cost_factor(
                    discount_rate, year, y_min, next_year
                )
                data_store["var_factor"][year, zone] = calc_cost_factor(
                    discount_rate, year, y_min, next_year
                )


def process_data(
    params_info : dict, input_folder : str
) -> dict:
    """Load and process data from input folder based on parameters settings.

    Parameters
    ----------
    params_info : dict
        Dictionary containing parameters information.
    input_folder : str
        Path to the input folder.

    Returns
    -------
    dict
        Dictionary containing processed parameters.
    """
    check_schema(params_info)
    file_params = {
        k: v for k, v in params_info.items() if not k.startswith("_")
    }
    data_store = {}
    load_excel_data(input_folder, file_params, data_store)
    extract_sets(data_store)
    compute_cost_factors(data_store)

    return data_store
