#!/usr/bin/env python3
"""Compare BMP scenario outputs against a baseline from the same calibrated model.

Input: a long-format CSV with one row per scenario x spatial unit (field, HRU, subbasin)
holding the simulated average annual load for the evaluation period:
  scenario, unit, area_ha, load_kg_yr [, cost_cad_yr] [, level]
`level` marks rows as "field" (edge-of-field / source) or "outlet" (routed to the
watershed outlet). The two are reported separately, never summed together, because
field-scale reductions shrink on the way to the outlet (in-stream processes, legacy
sources, lags).

Outputs per scenario and level: total load, reduction vs baseline (kg/yr and %),
reduction per treated hectare, and cost-effectiveness (CAD per kg reduced) when cost is
given. Units are those of the input; the script does not convert them.

Usage:
  python bmp_scenarios.py scenarios.csv --baseline baseline [--out summary.csv]
  python bmp_scenarios.py --selftest
"""
from __future__ import annotations

import argparse
import sys

import numpy as np
import pandas as pd


def compare(df: pd.DataFrame, baseline: str) -> pd.DataFrame:
    if "level" not in df:
        df = df.assign(level="outlet")
    if baseline not in set(df["scenario"]):
        raise SystemExit(f"baseline scenario {baseline!r} not found; scenarios: {sorted(set(df['scenario']))}")
    rows = []
    for level, d in df.groupby("level"):
        base = d[d["scenario"] == baseline].set_index("unit")["load_kg_yr"]
        for sc, s in d.groupby("scenario"):
            s = s.set_index("unit")
            common = s.index.intersection(base.index)
            if len(common) < len(s):
                print(f"# warning: {sc}/{level}: {len(s) - len(common)} units missing from the baseline were skipped")
            red = base.loc[common] - s.loc[common, "load_kg_yr"]
            treated = s.loc[common][red.abs() > 1e-9]
            row = dict(level=level, scenario=sc, load_kg_yr=s.loc[common, "load_kg_yr"].sum(),
                       reduction_kg_yr=red.sum(),
                       reduction_pct=100 * red.sum() / base.loc[common].sum() if base.loc[common].sum() else np.nan,
                       treated_area_ha=treated["area_ha"].sum() if "area_ha" in s else np.nan)
            row["reduction_kg_per_treated_ha"] = row["reduction_kg_yr"] / row["treated_area_ha"] if row["treated_area_ha"] else np.nan
            if "cost_cad_yr" in s:
                cost = s.loc[common, "cost_cad_yr"].sum()
                row["cost_cad_yr"] = cost
                row["cad_per_kg_reduced"] = cost / row["reduction_kg_yr"] if row["reduction_kg_yr"] > 0 else np.nan
            rows.append(row)
    out = pd.DataFrame(rows).sort_values(["level", "reduction_kg_yr"], ascending=[True, False])
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("csv", nargs="?"); ap.add_argument("--baseline", default="baseline"); ap.add_argument("--out")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if not a.csv:
        ap.error("csv is required")
    out = compare(pd.read_csv(a.csv), a.baseline)
    print("# loads as supplied (kg/yr); field and outlet levels reported separately")
    print(out.round(2).to_string(index=False))
    if a.out:
        out.to_csv(a.out, index=False)
    return 0


def selftest() -> int:
    df = pd.DataFrame({
        "scenario": ["baseline"] * 3 + ["cover_crop"] * 3,
        "unit": [1, 2, 3] * 2, "area_ha": [10, 20, 30] * 2,
        "load_kg_yr": [5, 10, 15, 4, 10, 12], "cost_cad_yr": [0, 0, 0, 500, 0, 1500]})
    out = compare(df, "baseline").set_index("scenario")
    cc = out.loc["cover_crop"]
    assert cc["reduction_kg_yr"] == 4 and abs(cc["reduction_pct"] - 400 / 30) < 1e-9
    assert cc["treated_area_ha"] == 40 and cc["cad_per_kg_reduced"] == 500
    print("bmp_scenarios selftest passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
