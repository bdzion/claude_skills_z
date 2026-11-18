#!/usr/bin/env python3
"""Transparent shock-propagation model for food-system stress tests: early vs delayed action.

Purpose: make the logic of a stress test explicit and inspectable (which node is hit,
how buffers absorb it, how shortfalls pass downstream, and how much a response at day t
avoids), not to forecast. Every parameter lives in a JSON scenario file; outputs are
labelled ILLUSTRATIVE unless the scenario marks every parameter as sourced.

Model (daily step, one commodity flow measured in a common unit, e.g. tonnes/day):
  * each node has demand d (units/day), production capacity c, a stock buffer of
    `buffer_days` x d, and optional inputs from upstream nodes;
  * production_t = c * (1 - shock_t) * min over inputs of the input's delivery ratio on
    day t-1 (fixed-proportion dependency: a processor cannot run without its inputs);
  * deliveries_t = min(d, stock_{t-1} + production_t); stock_t = stock_{t-1} + production_t - deliveries_t
    (capped at the buffer size); delivery ratio = deliveries / d; shortfall = d - deliveries;
  * shocks: a node's capacity drops by `severity` from `start_day` for `duration` days,
    then recovers linearly over `recovery_days`;
  * responses (applied from `start_day`, ramping in over `ramp_days`):
      capacity_boost      adds magnitude x c (substitution, imports, rerouting)
      severity_reduction  multiplies the remaining shock by (1 - magnitude) (containment)
      demand_reduction    reduces demand by magnitude x d (rationing, substitution by consumers)
The comparison reruns the scenario with the response starting on each day listed in
`response_start_days`, and reports avoided shortfall = shortfall(no action) - shortfall(action at t).

Usage:
  python shock_scenarios.py scenario.json [--out results/]
  python shock_scenarios.py --selftest
Outputs: summary table (stdout), timeseries.csv (scenario, day, node, delivery_ratio,
stock_days, shortfall) and avoided_loss.csv for dashboards.
"""
from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd


def _shock_factor(day, s):
    t0, dur, rec = s["start_day"], s["duration"], s.get("recovery_days", 0)
    if day < t0:
        return 0.0
    if day < t0 + dur:
        return s["severity"]
    if rec and day < t0 + dur + rec:
        return s["severity"] * (1 - (day - t0 - dur + 1) / rec)
    return 0.0


def _ramp(day, r):
    if day < r["start_day"]:
        return 0.0
    ramp = max(r.get("ramp_days", 0), 1)
    return min(1.0, (day - r["start_day"] + 1) / ramp)


def simulate(sc: dict, responses: list | None = None) -> pd.DataFrame:
    nodes = {n["id"]: n for n in sc["nodes"]}
    order = _topo_order(nodes)
    days = sc["days"]
    stock = {k: n.get("buffer_days", 0) * n["demand"] for k, n in nodes.items()}
    ratio_prev = {k: 1.0 for k in nodes}
    rows = []
    for t in range(days):
        ratio_today = {}
        for k in order:
            n = nodes[k]
            shock = sum(_shock_factor(t, s) for s in sc.get("shocks", []) if s["node"] == k)
            boost = dem_cut = 0.0
            for r in responses or []:
                if r["node"] != k:
                    continue
                w = _ramp(t, r)
                if r["type"] == "severity_reduction":
                    shock *= 1 - w * r["magnitude"]
                elif r["type"] == "capacity_boost":
                    boost += w * r["magnitude"]
                elif r["type"] == "demand_reduction":
                    dem_cut += w * r["magnitude"]
            shock = min(max(shock, 0.0), 1.0)
            inputs = n.get("inputs", [])
            input_ratio = min([ratio_prev[i] for i in inputs], default=1.0)
            prod = n["capacity"] * ((1 - shock) * input_ratio + boost)
            demand = n["demand"] * (1 - min(dem_cut, 1.0))
            deliv = min(demand, stock[k] + prod)
            cap = n.get("buffer_days", 0) * n["demand"]
            stock[k] = min(stock[k] + prod - deliv, cap)
            ratio = deliv / n["demand"]  # against original demand: demand cuts are a cost too
            ratio_today[k] = deliv / demand if demand > 0 else 1.0
            rows.append(dict(day=t, node=k, delivery_ratio=ratio, stock_days=stock[k] / n["demand"],
                             shortfall=n["demand"] - deliv))
        ratio_prev = ratio_today
    return pd.DataFrame(rows)


def _topo_order(nodes):
    seen, order = set(), []
    def visit(k, stack=()):
        if k in stack:
            raise SystemExit(f"cycle in node inputs at {k!r}")
        if k in seen:
            return
        for i in nodes[k].get("inputs", []):
            if i not in nodes:
                raise SystemExit(f"node {k!r} lists unknown input {i!r}")
            visit(i, stack + (k,))
        seen.add(k); order.append(k)
    for k in nodes:
        visit(k)
    return order


def compare(sc: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    base = simulate(sc).assign(scenario="no_action")
    series = [base]
    value = sc.get("value_per_unit")  # e.g. CAD per tonne; optional
    focus = sc.get("report_nodes") or [n["id"] for n in sc["nodes"]]
    base_short = base[base.node.isin(focus)].shortfall.sum()
    rows = [dict(response_start_day=None, scenario="no_action", total_shortfall=base_short, avoided_shortfall=0.0)]
    for t0 in sc.get("response_start_days", []):
        resp = copy.deepcopy(sc.get("responses", []))
        for r in resp:
            r["start_day"] = t0
        s = simulate(sc, resp).assign(scenario=f"act_day_{t0}")
        series.append(s)
        tot = s[s.node.isin(focus)].shortfall.sum()
        rows.append(dict(response_start_day=t0, scenario=f"act_day_{t0}", total_shortfall=tot,
                         avoided_shortfall=base_short - tot))
    summ = pd.DataFrame(rows)
    if value:
        summ["avoided_value"] = summ["avoided_shortfall"] * value
    return pd.concat(series, ignore_index=True), summ


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("scenario", nargs="?"); ap.add_argument("--out"); ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if not a.scenario:
        ap.error("scenario JSON is required")
    sc = json.loads(Path(a.scenario).read_text())
    ts, summ = compare(sc)
    sourced = sc.get("parameters_sourced", False)
    label = "SOURCED PARAMETERS (see scenario file)" if sourced else "ILLUSTRATIVE: parameters are assumptions, not estimates"
    print(f"# {sc.get('name', 'scenario')} | units: {sc.get('unit', 'units')}/day | {label}")
    print(summ.round(1).to_string(index=False))
    if a.out:
        o = Path(a.out); o.mkdir(parents=True, exist_ok=True)
        ts.to_csv(o / "timeseries.csv", index=False); summ.to_csv(o / "avoided_loss.csv", index=False)
        print(f"# wrote {o/'timeseries.csv'} and {o/'avoided_loss.csv'}")
    return 0


def selftest() -> int:
    sc = {"days": 120, "nodes": [
        {"id": "farm", "demand": 100, "capacity": 100, "buffer_days": 0},
        {"id": "plant", "demand": 100, "capacity": 100, "buffer_days": 5, "inputs": ["farm"]},
        {"id": "retail", "demand": 100, "capacity": 100, "buffer_days": 7, "inputs": ["plant"]}]}
    calm = simulate(sc)
    assert calm.shortfall.abs().max() < 1e-9, "no shock must give no shortfall"
    sc["shocks"] = [{"node": "farm", "start_day": 10, "duration": 30, "severity": 0.5, "recovery_days": 20}]
    hit = simulate(sc)
    first_retail_short = hit[(hit.node == "retail") & (hit.shortfall > 1e-9)].day.min()
    first_farm_short = hit[(hit.node == "farm") & (hit.shortfall > 1e-9)].day.min()
    assert first_retail_short > first_farm_short, "buffers must delay downstream shortfall"
    sc["responses"] = [{"node": "farm", "type": "severity_reduction", "magnitude": 0.6, "ramp_days": 7}]
    sc["response_start_days"] = [5, 15, 30, 60]
    sc["report_nodes"] = ["retail"]
    _, summ = compare(sc)
    av = summ.dropna(subset=["response_start_day"]).avoided_shortfall.to_numpy()
    assert np.all(np.diff(av) <= 1e-9) and av[0] > av[-1] >= 0, f"earlier action must avoid at least as much: {av}"
    print("shock_scenarios selftest passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
