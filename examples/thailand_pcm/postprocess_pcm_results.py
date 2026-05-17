#!/usr/bin/env python3
"""Post-process Thailand PCM parquet outputs into Excel tables and PNG charts."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

import pandas as pd

os.environ.setdefault("MPLCONFIGDIR", "/private/tmp/matplotlib-cache")
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


DEFAULT_SCENARIO = Path(__file__).resolve().parent
DEFAULT_RESULT = DEFAULT_SCENARIO / "output" / "baseline_pcm"
DEFAULT_OUT = DEFAULT_SCENARIO / "output" / "baseline_pcm_processed"

CARRIER_COLORS = {
    "coal": "#5b5b5b",
    "gas": "#4c78a8",
    "hydro": "#2f9eaa",
    "solar": "#f2c94c",
    "wind": "#6fcf97",
    "biomass": "#8d6e63",
    "import": "#9b51e0",
    "storage": "#56ccf2",
    "other": "#bdbdbd",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenario-dir", type=Path, default=DEFAULT_SCENARIO)
    parser.add_argument("--result-dir", type=Path, default=DEFAULT_RESULT)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--excel-name", default="PCM_Results_baseline_pcm.xlsx")
    parser.add_argument(
        "--max-line-columns",
        type=int,
        default=2000,
        help="Maximum line-flow columns to write into Excel.",
    )
    parser.add_argument(
        "--voll",
        type=float,
        default=10000.0,
        help="Value of lost load used to price load shedding in summary tables.",
    )
    return parser.parse_args()


def read_parquet(result_dir: Path, name: str) -> pd.DataFrame:
    path = result_dir / f"{name}.parquet"
    if not path.exists():
        return pd.DataFrame()
    return pd.read_parquet(path)


def snapshot_from_hour(hours: pd.Series, year: int = 2023) -> pd.Series:
    start = pd.Timestamp(year=year, month=1, day=1)
    return start + pd.to_timedelta(hours.astype(int) - 1, unit="h")


def read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)


def tech_label(tech: str) -> str:
    if tech.lower().startswith("h") and tech[1:].isdigit():
        return f"Hydro_{tech[1:]}"
    return tech


def line_label(zone1: str, zone2: str) -> str:
    return f"{zone1}->{zone2}"


def physical_line_key(zone1: str, zone2: str) -> tuple[str, str]:
    a, b = str(zone1), str(zone2)
    return (a, b) if a <= b else (b, a)


def physical_line_label(zone1: str, zone2: str) -> str:
    a, b = physical_line_key(zone1, zone2)
    return f"{a}<->{b}"


def write_excel(
    out_path: Path,
    tables: dict[str, pd.DataFrame],
) -> None:
    with pd.ExcelWriter(out_path, engine="xlsxwriter") as writer:
        for sheet, df in tables.items():
            safe = sheet[:31]
            df.to_excel(writer, sheet_name=safe, index=False)
            ws = writer.sheets[safe]
            ws.freeze_panes(1, 1)
            ws.autofilter(0, 0, max(len(df), 1), max(len(df.columns) - 1, 0))
            for i, col in enumerate(df.columns[:20]):
                width = min(max(len(str(col)) + 2, 12), 28)
                ws.set_column(i, i, width)


def make_wide(
    df: pd.DataFrame,
    index_col: str,
    column_col: str,
    value_col: str = "value",
) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["snapshot"])
    wide = (
        df.pivot_table(
            index=index_col,
            columns=column_col,
            values=value_col,
            aggfunc="sum",
            fill_value=0.0,
        )
        .sort_index()
        .reset_index()
    )
    wide.columns.name = None
    return wide


def save_fig(path: Path) -> None:
    plt.tight_layout()
    plt.savefig(path, dpi=220, bbox_inches="tight")
    plt.close()


def stack_png(path: Path, hourly_carrier: pd.DataFrame) -> None:
    carriers = [c for c in hourly_carrier.columns if c != "hour"]
    if not carriers:
        plt.figure(figsize=(12, 5))
        plt.text(0.1, 0.5, "No generation data")
        save_fig(path)
        return
    xvals = hourly_carrier["hour"]
    y = hourly_carrier[carriers].clip(lower=0)
    colors = [CARRIER_COLORS.get(c, CARRIER_COLORS["other"]) for c in carriers]
    plt.figure(figsize=(15, 6.8))
    plt.stackplot(xvals, [y[c].to_numpy() for c in carriers], labels=carriers, colors=colors, alpha=0.9)
    plt.title("System Total Generation Stack")
    plt.xlabel("Hour")
    plt.ylabel("Generation (MWh/h)")
    plt.xlim(float(xvals.min()), float(xvals.max()))
    plt.legend(loc="center left", bbox_to_anchor=(1.01, 0.5), frameon=False)
    plt.grid(axis="y", alpha=0.25)
    save_fig(path)


def pie_png(path: Path, totals: pd.Series) -> None:
    totals = totals[totals > 1e-6].sort_values(ascending=False)
    total = float(totals.sum())
    plt.figure(figsize=(8.5, 7.2))
    if total <= 0:
        plt.text(0.1, 0.5, "No generation data")
        save_fig(path)
        return
    colors = [CARRIER_COLORS.get(str(c), CARRIER_COLORS["other"]) for c in totals.index]
    labels = [f"{c} ({v / total * 100:.1f}%)" for c, v in totals.items()]
    plt.pie(totals.to_numpy(), labels=labels, colors=colors, startangle=90, counterclock=False)
    plt.title("Generation Mix")
    save_fig(path)


def line_png(
    path: Path,
    series_df: pd.DataFrame,
    title: str,
    y_label: str,
    max_series: int = 12,
) -> None:
    cols = [c for c in series_df.columns if c != "hour"]
    plt.figure(figsize=(15, 6.8))
    if not cols:
        plt.text(0.1, 0.5, "No data")
        save_fig(path)
        return
    xvals = series_df["hour"] if "hour" in series_df.columns else series_df.index
    palette = plt.get_cmap("tab20")
    for j, col in enumerate(cols[:max_series]):
        plt.plot(xvals, series_df[col].astype(float), label=str(col), linewidth=1.5, color=palette(j % 20))
    plt.title(title)
    plt.xlabel("Hour")
    plt.ylabel(y_label)
    plt.grid(axis="y", alpha=0.25)
    plt.legend(loc="center left", bbox_to_anchor=(1.01, 0.5), frameon=False)
    save_fig(path)


def bar_png(path: Path, values: pd.Series, title: str, x_label: str) -> None:
    values = values.sort_values(ascending=True).tail(10)
    plt.figure(figsize=(14, 8))
    if values.empty:
        plt.text(0.1, 0.5, "No data")
        save_fig(path)
        return
    labels = [str(x)[:42] for x in values.index]
    plt.barh(labels, values.astype(float), color="#4c78a8")
    plt.title(title)
    plt.xlabel(x_label)
    plt.grid(axis="x", alpha=0.25)
    save_fig(path)


def build_tables(
    scenario_dir: Path,
    result_dir: Path,
    max_line_columns: int,
    voll: float,
) -> tuple[dict[str, pd.DataFrame], dict[str, pd.DataFrame]]:
    input_dir = scenario_dir / "input"
    tech_registry = read_csv(input_dir / "tech_registry.csv")
    carrier_map = dict(zip(tech_registry["tech"].astype(str), tech_registry["carrier"].astype(str)))

    gen = read_parquet(result_dir, "gen")
    lns = read_parquet(result_dir, "lns")
    lmp = read_parquet(result_dir, "lmp")
    trans = read_parquet(result_dir, "trans_export")
    genflow = read_parquet(result_dir, "genflow")
    spillflow = read_parquet(result_dir, "spillflow")

    year = int(gen["year"].iloc[0]) if not gen.empty else 2023
    hours = pd.DataFrame({"hour": sorted(gen["hour"].unique() if not gen.empty else [])})
    hours["snapshot"] = snapshot_from_hour(hours["hour"], year)

    gen2 = gen.copy()
    gen2["tech_label"] = gen2["tech"].astype(str).map(tech_label)
    gen_wide = make_wide(gen2, "hour", "tech_label").merge(hours, on="hour", how="left")
    gen_wide = gen_wide[["snapshot"] + [c for c in gen_wide.columns if c not in ("snapshot", "hour")]]

    demand = read_csv(input_dir / "demand.csv")
    demand = demand[demand["year"].astype(int) == year].copy()
    demand_wide = make_wide(demand, "hour", "zone").merge(hours, on="hour", how="left")
    demand_wide = demand_wide[["snapshot"] + [c for c in demand_wide.columns if c not in ("snapshot", "hour")]]

    if not trans.empty:
        trans2 = trans.copy()
        trans2["line"] = [line_label(a, b) for a, b in zip(trans2["zone1"], trans2["zone2"])]
        line_totals = trans2.groupby("line")["value"].apply(lambda s: s.abs().sum()).sort_values(ascending=False)
        keep_lines = set(line_totals.head(max_line_columns).index)
        trans2 = trans2[trans2["line"].isin(keep_lines)]
        line_wide = make_wide(trans2, "hour", "line").merge(hours, on="hour", how="left")
        line_wide = line_wide[["snapshot"] + [c for c in line_wide.columns if c not in ("snapshot", "hour")]]
    else:
        line_wide = pd.DataFrame(columns=["snapshot"])

    hydro_outflow = pd.concat(
        [
            genflow.assign(kind="turbine"),
            spillflow.assign(kind="spillage"),
        ],
        ignore_index=True,
    )
    turbine_wide = make_wide(genflow.assign(station_label=genflow["station"].astype(str).str.replace("h", "", regex=False) + "_turbine"), "hour", "station_label")
    spill_wide = make_wide(spillflow.assign(station_label=spillflow["station"].astype(str).str.replace("h", "", regex=False) + "_spillage"), "hour", "station_label")
    outflow_sum = hydro_outflow.groupby(["hour", "station"], as_index=False)["value"].sum()
    outflow_sum["station_label"] = outflow_sum["station"].astype(str).str.replace("h", "", regex=False) + "_outflow_gate"
    outflow_wide = make_wide(outflow_sum, "hour", "station_label")

    reservoir_level = reconstruct_reservoir_level(input_dir, genflow, spillflow, year)
    for df in (reservoir_level, outflow_wide, turbine_wide, spill_wide):
        if "hour" in df.columns:
            df.insert(1, "snapshot", snapshot_from_hour(df["hour"], year))
            df.drop(columns=["hour"], inplace=True)
        elif len(df):
            df.insert(0, "snapshot", [])

    lns_total = float(lns["value"].sum()) if not lns.empty else 0.0
    lmp_avg = float(lmp["value"].mean()) if not lmp.empty else 0.0
    carrier_summary = build_carrier_summary(input_dir, gen, carrier_map, year)
    import_generation, import_summary = build_import_tables(
        input_dir, gen, carrier_map, hours, year
    )
    line_congestion_top10, line_congestion_series = build_line_congestion_tables(input_dir, trans, hours)
    total_generation_cost = (
        float(carrier_summary["generation_cost"].sum()) if not carrier_summary.empty else 0.0
    )
    load_shedding_cost = lns_total * float(voll)
    total_system_cost = total_generation_cost + load_shedding_cost
    summary = pd.DataFrame(
        [
            ("System: Total Load (MWh)", float(demand["value"].sum())),
            ("System: Total Generation (MWh)", float(gen["value"].sum()) if not gen.empty else 0.0),
            ("System: Total Generation Cost", total_generation_cost),
            ("System: Load Shedding (MWh)", lns_total),
            ("System: VOLL ($/MWh)", float(voll)),
            ("System: Load Shedding Cost", load_shedding_cost),
            ("System: Total System Cost incl. Load Shedding", total_system_cost),
            ("System: Peak Load (MW)", float(demand.groupby("hour")["value"].sum().max())),
            ("System: Average LMP", lmp_avg),
            ("System: Simulated Hours", int(demand["hour"].nunique())),
        ],
        columns=["Metric", "Value"],
    )

    tables = {
        "Generation": gen_wide,
        "Load": demand_wide,
        "Line_Flow": line_wide,
        "Reservoir_Level": reservoir_level,
        "Hydro_Outflow": outflow_wide,
        "Hydro_Turbine": turbine_wide,
        "Hydro_Spillage": spill_wide,
        "LNS": make_wide(lns, "hour", "zone").merge(hours, on="hour", how="left")[["snapshot"] + sorted(lns["zone"].unique().tolist())] if not lns.empty else pd.DataFrame(),
        "LMP": make_wide(lmp, "hour", "zone").merge(hours, on="hour", how="left")[["snapshot"] + sorted(lmp["zone"].unique().tolist())] if not lmp.empty else pd.DataFrame(),
        "Carrier_Summary": carrier_summary,
        "Import_Generation": import_generation,
        "Import_Summary": import_summary,
        "Line_Congestion_Top10": line_congestion_top10,
        "Line_Congestion_Top10_Series": line_congestion_series,
        "Summary": summary,
    }

    gen_carrier = gen.copy()
    gen_carrier["carrier"] = gen_carrier["tech"].astype(str).map(carrier_map).fillna("other")
    hourly_carrier = gen_carrier.groupby(["hour", "carrier"], as_index=False)["value"].sum().pivot(index="hour", columns="carrier", values="value").fillna(0).reset_index()
    hourly_carrier.columns.name = None

    renew = build_renewable_curtailment(input_dir, gen, carrier_map, year)
    congestion = (
        line_congestion_top10.set_index("line")["mean_utilization_pct"]
        if not line_congestion_top10.empty
        else pd.Series(dtype=float)
    )
    reservoir_plot = reservoir_level.copy()
    if not reservoir_plot.empty:
        reservoir_plot.insert(0, "hour", range(1, len(reservoir_plot) + 1))
        reservoir_plot = reservoir_plot[["hour"] + [c for c in reservoir_plot.columns if c not in ("hour", "snapshot")]]
    import_plot = import_generation.copy()
    if not import_plot.empty:
        import_plot.insert(0, "hour", range(1, len(import_plot) + 1))
        import_plot = import_plot[["hour"] + [c for c in import_plot.columns if c not in ("hour", "snapshot")]]

    plots = {
        "hourly_carrier": hourly_carrier,
        "generation_mix": hourly_carrier.drop(columns=["hour"], errors="ignore").sum(),
        "renewable_curtailment": renew,
        "congestion": congestion,
        "import_dispatch": import_plot,
        "reservoir": reservoir_plot,
    }
    return tables, plots


def reconstruct_reservoir_level(input_dir: Path, genflow: pd.DataFrame, spillflow: pd.DataFrame, year: int) -> pd.DataFrame:
    if genflow.empty:
        return pd.DataFrame(columns=["snapshot"])
    init = read_csv(input_dir / "reservoir_initial_storage_level.csv")
    init_map = dict(zip(init["tech"].astype(str), init["value"].astype(float)))
    inflow = read_csv(input_dir / "reservoir_inflow.csv")
    inflow = inflow[(inflow["year"].astype(int) == year)][["tech", "hour", "value"]].copy()
    inflow["tech"] = inflow["tech"].astype(str)
    flow = genflow.groupby(["station", "hour"], as_index=False)["value"].sum()
    flow = flow.rename(columns={"station": "tech", "value": "genflow"})
    spill = spillflow.groupby(["station", "hour"], as_index=False)["value"].sum()
    spill = spill.rename(columns={"station": "tech", "value": "spillflow"})
    df = inflow.merge(flow, on=["tech", "hour"], how="left").merge(spill, on=["tech", "hour"], how="left")
    df[["genflow", "spillflow"]] = df[["genflow", "spillflow"]].fillna(0.0)
    out = []
    for tech, grp in df.sort_values(["tech", "hour"]).groupby("tech"):
        storage = init_map.get(str(tech), 0.0)
        for _, row in grp.iterrows():
            storage += 3600.0 * (float(row["value"]) - float(row["genflow"]) - float(row["spillflow"]))
            out.append({"hour": int(row["hour"]), "station": f"{str(tech).replace('h', '')}_store", "value": storage / 1000.0})
    wide = pd.DataFrame(out).pivot_table(index="hour", columns="station", values="value", aggfunc="last").reset_index()
    wide.columns.name = None
    return wide


def build_renewable_curtailment(input_dir: Path, gen: pd.DataFrame, carrier_map: dict[str, str], year: int) -> pd.DataFrame:
    renewable = {t for t, c in carrier_map.items() if c in {"solar", "wind"}}
    if not renewable:
        return pd.DataFrame(columns=["hour", "available", "generation", "curtailment"])
    cap = read_csv(input_dir / "capacity_pcm.csv")
    cap = cap[(cap["year"].astype(int) == year) & (cap["tech"].astype(str).isin(renewable))]
    pmax = read_csv(input_dir / "tech_max_gen_profile.csv")
    pmax = pmax[(pmax["year"].astype(int) == year) & (pmax["tech"].astype(str).isin(renewable))]
    avail = pmax.merge(cap[["zone", "tech", "capacity"]], on=["zone", "tech"], how="inner")
    avail["available"] = avail["value"].astype(float) * avail["capacity"].astype(float)
    avail_h = avail.groupby("hour", as_index=False)["available"].sum()
    gen_h = gen[gen["tech"].astype(str).isin(renewable)].groupby("hour", as_index=False)["value"].sum().rename(columns={"value": "generation"})
    out = avail_h.merge(gen_h, on="hour", how="left").fillna(0.0)
    out["curtailment"] = (out["available"] - out["generation"]).clip(lower=0.0)
    return out


def add_generation_cost_columns(
    input_dir: Path,
    gen: pd.DataFrame,
    carrier_map: dict[str, str],
) -> pd.DataFrame:
    if gen.empty:
        return pd.DataFrame()

    df = gen[["zone", "tech", "year", "value"]].copy()
    df["tech"] = df["tech"].astype(str)
    df["zone"] = df["zone"].astype(str)
    df["year"] = df["year"].astype(int)
    df["carrier"] = df["tech"].map(carrier_map).fillna("other")
    df = df.rename(columns={"value": "generation_mwh"})

    var_om = read_cost_file(input_dir / "tech_variable_OM_cost.csv", "variable_om_cost_per_mwh")
    fuel = read_cost_file(input_dir / "tech_fuel_price.csv", "fuel_cost_per_mwh")
    emission = read_cost_file(input_dir / "tech_emission_factor.csv", "emission_tonne_per_mwh")
    carbon_tax = read_zone_year_file(input_dir / "policy_carbon_tax.csv", "carbon_tax")

    df = df.merge(var_om, on=["tech", "year"], how="left")
    df = df.merge(fuel, on=["tech", "year"], how="left")
    df = df.merge(emission, on=["tech", "year"], how="left")
    df = df.merge(carbon_tax, on=["zone", "year"], how="left")
    df[
        [
            "variable_om_cost_per_mwh",
            "fuel_cost_per_mwh",
            "emission_tonne_per_mwh",
            "carbon_tax",
        ]
    ] = df[
        [
            "variable_om_cost_per_mwh",
            "fuel_cost_per_mwh",
            "emission_tonne_per_mwh",
            "carbon_tax",
        ]
    ].fillna(0.0)

    df["variable_om_cost"] = df["generation_mwh"] * df["variable_om_cost_per_mwh"]
    df["fuel_cost"] = df["generation_mwh"] * df["fuel_cost_per_mwh"]
    df["carbon_cost"] = df["generation_mwh"] * df["emission_tonne_per_mwh"] * df["carbon_tax"]
    df["generation_cost"] = df["variable_om_cost"] + df["fuel_cost"] + df["carbon_cost"]
    return df


def build_import_tables(
    input_dir: Path,
    gen: pd.DataFrame,
    carrier_map: dict[str, str],
    hours: pd.DataFrame,
    year: int,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    import_techs = {t for t, c in carrier_map.items() if c == "import"}
    columns = [
        "tech",
        "zone",
        "capacity_mw",
        "generation_mwh",
        "max_hourly_import_mw",
        "capacity_factor_pct",
        "variable_om_cost",
        "fuel_cost",
        "carbon_cost",
        "generation_cost",
        "average_cost_per_mwh",
    ]
    if gen.empty or not import_techs:
        return pd.DataFrame(columns=["snapshot"]), pd.DataFrame(columns=columns)

    import_gen = gen[gen["tech"].astype(str).isin(import_techs)].copy()
    if import_gen.empty:
        return pd.DataFrame(columns=["snapshot"]), pd.DataFrame(columns=columns)

    import_gen["tech"] = import_gen["tech"].astype(str)
    generation = make_wide(import_gen, "hour", "tech").merge(hours, on="hour", how="left")
    generation = generation[["snapshot"] + [c for c in generation.columns if c not in ("snapshot", "hour")]]
    tech_cols = [c for c in generation.columns if c != "snapshot"]
    generation["Total_Import"] = generation[tech_cols].sum(axis=1) if tech_cols else 0.0

    costed = add_generation_cost_columns(input_dir, import_gen, carrier_map)
    summary = (
        costed.groupby(["tech", "zone"], as_index=False)[
            [
                "generation_mwh",
                "variable_om_cost",
                "fuel_cost",
                "carbon_cost",
                "generation_cost",
            ]
        ]
        .sum()
        .sort_values("generation_mwh", ascending=False)
    )
    peak = import_gen.groupby(["tech", "zone"], as_index=False)["value"].max()
    peak = peak.rename(columns={"value": "max_hourly_import_mw"})
    cap = read_csv(input_dir / "capacity_pcm.csv")
    cap = cap[(cap["year"].astype(int) == year) & (cap["tech"].astype(str).isin(import_techs))]
    cap = cap.rename(columns={"capacity": "capacity_mw"})
    summary = summary.merge(peak, on=["tech", "zone"], how="left")
    summary = summary.merge(cap[["tech", "zone", "capacity_mw"]], on=["tech", "zone"], how="left")
    simulated_hours = max(int(hours["hour"].nunique()), 1) if "hour" in hours.columns else 1
    denom = summary["capacity_mw"].where(summary["capacity_mw"].fillna(0.0) > 0.0)
    summary["capacity_factor_pct"] = (summary["generation_mwh"] / (denom * simulated_hours) * 100.0).fillna(0.0)
    summary["average_cost_per_mwh"] = (
        summary["generation_cost"] / summary["generation_mwh"].where(summary["generation_mwh"].abs() > 1e-9)
    ).fillna(0.0)
    return generation, summary[columns]


def build_carrier_summary(
    input_dir: Path,
    gen: pd.DataFrame,
    carrier_map: dict[str, str],
    year: int,
) -> pd.DataFrame:
    columns = [
        "carrier",
        "generation_mwh",
        "variable_om_cost",
        "fuel_cost",
        "carbon_cost",
        "generation_cost",
        "average_cost_per_mwh",
    ]
    if gen.empty:
        return pd.DataFrame(columns=columns)

    df = add_generation_cost_columns(input_dir, gen, carrier_map)
    out = (
        df.groupby("carrier", as_index=False)[
            [
                "generation_mwh",
                "variable_om_cost",
                "fuel_cost",
                "carbon_cost",
                "generation_cost",
            ]
        ]
        .sum()
        .sort_values("generation_mwh", ascending=False)
    )
    out["average_cost_per_mwh"] = (
        out["generation_cost"] / out["generation_mwh"].where(out["generation_mwh"].abs() > 1e-9)
    ).fillna(0.0)
    return out[columns]


def read_cost_file(path: Path, column: str) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame(columns=["tech", "year", column])
    df = read_csv(path)
    return df.assign(
        tech=df["tech"].astype(str),
        year=df["year"].astype(int),
        **{column: df["value"].astype(float)},
    )[["tech", "year", column]]


def read_zone_year_file(path: Path, column: str) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame(columns=["zone", "year", column])
    df = read_csv(path)
    return df.assign(
        zone=df["zone"].astype(str),
        year=df["year"].astype(int),
        **{column: df["value"].astype(float)},
    )[["zone", "year", column]]


def build_physical_line_utilization(input_dir: Path, trans: pd.DataFrame) -> pd.DataFrame:
    columns = ["hour", "line", "zone1", "zone2", "capacity_mw", "net_flow_mw", "abs_flow_mw", "utilization_pct"]
    if trans.empty:
        return pd.DataFrame(columns=columns)

    cap = read_csv(input_dir / "transmission_existing.csv")
    cap[["physical_zone1", "physical_zone2"]] = pd.DataFrame(
        [physical_line_key(a, b) for a, b in zip(cap["zone1"], cap["zone2"])],
        index=cap.index,
    )
    cap = cap.groupby(["physical_zone1", "physical_zone2"], as_index=False)["value"].max()
    cap = cap.rename(columns={"value": "capacity_mw"})

    df = trans.copy()
    df[["physical_zone1", "physical_zone2"]] = pd.DataFrame(
        [physical_line_key(a, b) for a, b in zip(df["zone1"], df["zone2"])],
        index=df.index,
    )
    df["signed_flow_mw"] = df["value"].astype(float)
    reverse = df["zone1"].astype(str) != df["physical_zone1"].astype(str)
    df.loc[reverse, "signed_flow_mw"] *= -1.0

    net = (
        df.groupby(["hour", "physical_zone1", "physical_zone2"], as_index=False)["signed_flow_mw"]
        .sum()
        .rename(columns={"signed_flow_mw": "net_flow_mw"})
    )
    net = net.merge(cap, on=["physical_zone1", "physical_zone2"], how="left")
    net = net[net["capacity_mw"].fillna(0.0) > 0.0].copy()
    if net.empty:
        return pd.DataFrame(columns=columns)

    net["abs_flow_mw"] = net["net_flow_mw"].abs()
    net["utilization_pct"] = (net["abs_flow_mw"] / net["capacity_mw"] * 100.0).clip(upper=100.0)
    net["zone1"] = net["physical_zone1"]
    net["zone2"] = net["physical_zone2"]
    net["line"] = [physical_line_label(a, b) for a, b in zip(net["zone1"], net["zone2"])]
    return net[columns]


def build_line_congestion_tables(
    input_dir: Path,
    trans: pd.DataFrame,
    hours: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    columns = [
        "rank",
        "line",
        "zone1",
        "zone2",
        "capacity_mw",
        "max_abs_flow_mw",
        "max_utilization_pct",
        "mean_utilization_pct",
        "hour_of_max",
    ]
    series_columns = ["snapshot"]
    if trans.empty:
        return pd.DataFrame(columns=columns), pd.DataFrame(columns=series_columns)

    df = build_physical_line_utilization(input_dir, trans)
    if df.empty:
        return pd.DataFrame(columns=columns), pd.DataFrame(columns=series_columns)

    idx = df.groupby("line")["utilization_pct"].idxmax()
    top = df.loc[idx, ["line", "zone1", "zone2", "hour", "capacity_mw", "abs_flow_mw", "utilization_pct"]].copy()
    mean_util = df.groupby("line")["utilization_pct"].mean().rename("mean_utilization_pct")
    top = top.merge(mean_util, left_on="line", right_index=True, how="left")
    top = top.sort_values("mean_utilization_pct", ascending=False).head(10).reset_index(drop=True)
    top.insert(0, "rank", top.index + 1)
    top = top.rename(
        columns={
            "abs_flow_mw": "max_abs_flow_mw",
            "utilization_pct": "max_utilization_pct",
            "hour": "hour_of_max",
        }
    )

    series = df[df["line"].isin(top["line"])].pivot_table(
        index="hour",
        columns="line",
        values="utilization_pct",
        aggfunc="mean",
        fill_value=0.0,
    ).sort_index().reset_index()
    series.columns.name = None
    series = series.merge(hours, on="hour", how="left")
    series = series[["snapshot"] + top["line"].tolist()]
    return top[columns], series


def main() -> None:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    tables, plots = build_tables(args.scenario_dir, args.result_dir, args.max_line_columns, args.voll)
    write_excel(args.out_dir / args.excel_name, tables)
    stack_png(args.out_dir / "System_Total_Stack.png", plots["hourly_carrier"])
    pie_png(args.out_dir / "Generation_Mix_Pie.png", plots["generation_mix"])
    line_png(args.out_dir / "Renewable_Curtailment.png", plots["renewable_curtailment"], "Renewable Curtailment", "MWh/h")
    line_png(args.out_dir / "Import_Dispatch.png", plots["import_dispatch"], "Import Dispatch", "MWh/h", max_series=20)
    bar_png(args.out_dir / "Transmission_Congestion.png", plots["congestion"], "Transmission Congestion", "Mean utilization (%)")
    line_png(args.out_dir / "Reservoir_Scheduling.png", plots["reservoir"], "Reservoir Scheduling", "10^3 m3")
    print(f"Wrote results to {args.out_dir}")


if __name__ == "__main__":
    main()
