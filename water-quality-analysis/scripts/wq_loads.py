#!/usr/bin/env python3
"""Annual (or seasonal) constituent loads from daily flow and discrete samples.

Three estimators, reported side by side because they disagree most when sampling is
sparse or storm-biased, and that disagreement is itself a result worth reporting:
  * interpolation: concentration linearly interpolated between sample dates, times daily
    flow (sensitive to whether storms were sampled);
  * FWMC: flow-weighted mean concentration of the samples in the period, times the
    period's total flow volume;
  * Beale ratio estimator with finite-population correction (bias-corrected ratio of
    sample-day loads to sample-day flows, scaled by the mean daily flow of the period).
For regression/WRTDS loads with flow normalisation, use R EGRET (Hirsch & De Cicco 2015).

Units (stated in every output): flow in m3/s (daily mean), concentration in mg/L,
load in kg; kg/day = mg/L x m3/s x 86.4. Periods are water years (1 Oct - 30 Sep,
labelled by the year in which they end) unless --period calendar.

Usage:
  python wq_loads.py --flow flow.csv --flow-date date --flow-col Q_m3s \
                     --samples wq.csv --sample-date date --conc-col TP_mg_L \
                     [--period water|calendar] [--min-samples 12] [--out loads.csv]
  python wq_loads.py --selftest
"""
from __future__ import annotations

import argparse
import sys

import numpy as np
import pandas as pd

KG_PER_DAY = 86.4  # (mg/L) * (m3/s) -> kg/day


def period_label(dates: pd.Series, kind: str) -> pd.Series:
    d = pd.to_datetime(dates)
    return (d.dt.year + (d.dt.month >= 10).astype(int)) if kind == "water" else d.dt.year


def beale(q_all: np.ndarray, q_s: np.ndarray, c_s: np.ndarray) -> float:
    """Daily-mean load (kg/day) by the Beale ratio estimator with finite-population correction."""
    n, big_n = len(q_s), len(q_all)
    l_s = c_s * q_s * KG_PER_DAY
    mq, ml, muq = q_s.mean(), l_s.mean(), q_all.mean()
    if n < 2 or mq == 0:
        return np.nan
    f = 1.0 / n - 1.0 / big_n
    s_lq = np.cov(l_s, q_s, ddof=1)[0, 1]
    s_qq = np.var(q_s, ddof=1)
    return muq * (ml / mq) * (1 + f * s_lq / (ml * mq)) / (1 + f * s_qq / mq ** 2)


def compute(flow: pd.DataFrame, samples: pd.DataFrame, kind="water", min_samples=12) -> pd.DataFrame:
    flow = flow.dropna().sort_values("date").drop_duplicates("date")
    samples = samples.dropna().sort_values("date")
    samples = samples.groupby("date", as_index=False)["conc"].mean()  # same-day replicates
    merged = samples.merge(flow, on="date", how="inner")
    unmatched = len(samples) - len(merged)
    daily = flow.set_index("date")
    interp = merged.set_index("date")["conc"].reindex(daily.index).interpolate("time").ffill().bfill()
    daily = daily.assign(conc_interp=interp, period=period_label(daily.index.to_series(), kind).to_numpy())
    merged = merged.assign(period=period_label(merged["date"], kind).to_numpy())
    rows = []
    for p, d in daily.groupby("period"):
        s = merged[merged["period"] == p]
        expected = 366 if (pd.Timestamp(f"{p}-02-28") + pd.Timedelta(days=1)).day == 29 else 365
        row = dict(period=p, flow_days=len(d), complete=len(d) >= expected, n_samples=len(s),
                   flow_volume_m3=d["Q"].sum() * 86400,
                   load_interp_kg=(d["conc_interp"] * d["Q"] * KG_PER_DAY).sum())
        if len(s) >= 1 and s["Q"].sum() > 0:
            fwmc = (s["conc"] * s["Q"]).sum() / s["Q"].sum()
            row.update(fwmc_mg_L=fwmc, load_fwmc_kg=fwmc * d["Q"].sum() * KG_PER_DAY)
        row["load_beale_kg"] = beale(d["Q"].to_numpy(), s["Q"].to_numpy(), s["conc"].to_numpy()) * len(d) if len(s) >= 2 else np.nan
        flags = []
        if not row["complete"]:
            flags.append("incomplete flow record")
        if len(s) < min_samples:
            flags.append(f"fewer than {min_samples} samples")
        if len(s) and s["Q"].quantile(0.9) < d["Q"].quantile(0.9):
            flags.append("high flows (top 10 %) not represented in samples")
        row["flags"] = "; ".join(flags)
        rows.append(row)
    out = pd.DataFrame(rows)
    out.attrs["unmatched_samples"] = unmatched
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--flow"); ap.add_argument("--flow-date", default="date"); ap.add_argument("--flow-col")
    ap.add_argument("--samples"); ap.add_argument("--sample-date", default="date"); ap.add_argument("--conc-col")
    ap.add_argument("--period", default="water", choices=["water", "calendar"])
    ap.add_argument("--min-samples", type=int, default=12); ap.add_argument("--out")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if not all([a.flow, a.flow_col, a.samples, a.conc_col]):
        ap.error("--flow, --flow-col, --samples and --conc-col are required")
    f = pd.read_csv(a.flow)
    flow = pd.DataFrame({"date": pd.to_datetime(f[a.flow_date]).dt.normalize(), "Q": pd.to_numeric(f[a.flow_col], errors="coerce")})
    s = pd.read_csv(a.samples)
    samples = pd.DataFrame({"date": pd.to_datetime(s[a.sample_date]).dt.normalize(), "conc": pd.to_numeric(s[a.conc_col], errors="coerce")})
    out = compute(flow, samples, a.period, a.min_samples)
    print(f"# units: flow m3/s daily mean; concentration mg/L; loads kg per {a.period} year")
    if out.attrs["unmatched_samples"]:
        print(f"# {out.attrs['unmatched_samples']} sample dates had no daily flow and were dropped")
    print(out.round(3).to_string(index=False))
    if a.out:
        out.to_csv(a.out, index=False)
    return 0


def selftest() -> int:
    dates = pd.date_range("2018-10-01", "2020-09-30", freq="D")
    rng = np.random.default_rng(1)
    q = np.exp(rng.normal(0, 1, len(dates)))
    flow = pd.DataFrame({"date": dates, "Q": q})
    idx = np.arange(0, len(dates), 14)
    samples = pd.DataFrame({"date": dates[idx], "conc": 0.1})
    out = compute(flow, samples)
    truth = flow.assign(p=period_label(flow["date"], "water")).groupby("p")["Q"].sum().to_numpy() * 0.1 * KG_PER_DAY
    for col in ["load_interp_kg", "load_fwmc_kg", "load_beale_kg"]:
        assert np.allclose(out[col].to_numpy(), truth, rtol=1e-9), (col, out[col].to_numpy(), truth)
    assert list(out["period"]) == [2019, 2020] and out["complete"].all()
    # concentration rising with flow: FWMC > arithmetic mean concentration
    samples2 = pd.DataFrame({"date": dates[idx], "conc": 0.05 * q[idx]})
    out2 = compute(flow, samples2)
    assert (out2["fwmc_mg_L"] > samples2["conc"].mean() * 0.9).all()
    print("wq_loads selftest passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
