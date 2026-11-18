#!/usr/bin/env python3
"""Monotonic trend tests for water-quality (or flow) time series.

Implements, with numpy/pandas/scipy only:
  * Mann-Kendall test with tie correction, optional Hamed & Rao (1998) variance
    correction for serial correlation;
  * Sen (1968) slope with a Gilbert-style confidence interval;
  * Seasonal Kendall test and seasonal Sen slope (Hirsch, Slack & Smith 1982),
    one value per season-year (median of samples in that season and year);
  * optional log-linear flow adjustment (residuals of ln C on ln Q) before testing;
  * censored values (below detection) re-censored at the highest detection limit and
    treated as ties (a conservative Kendall approach; see Helsel 2012). Sen slopes are
    not reported when more than 15 % of values are censored, because substituted values
    bias them; use an Akritas-Theil-Sen estimate (e.g. R package NADA2) instead.

Assumptions stated in every report: time unit = decimal years, slope units = input
concentration units per year; seasons = calendar months unless --season quarter.
The seasonal Kendall variance assumes independence between seasons (no Hirsch & Slack
1984 covariance correction).

Usage:
  python wq_trends.py data.csv --date date --value TP_mg_L [--censored TP_flag]
         [--flow Q_m3s --flow-adjust] [--seasonal --season month|quarter]
         [--hamed-rao] [--alpha 0.05]
  python wq_trends.py --selftest
The censored column holds True/1/'<' for values below the detection limit; the value
column then holds the detection limit.
"""
from __future__ import annotations

import argparse
import json
import sys

import numpy as np
import pandas as pd
from scipy import stats


def decimal_year(d: pd.Series) -> np.ndarray:
    d = pd.to_datetime(d)
    start = pd.to_datetime(d.dt.year.astype(str) + "-01-01")
    end = pd.to_datetime((d.dt.year + 1).astype(str) + "-01-01")
    return (d.dt.year + (d - start) / (end - start)).to_numpy(dtype=float)


def _s_and_ties(x: np.ndarray) -> tuple[float, float]:
    n = len(x)
    s = 0.0
    for i in range(n - 1):
        s += np.sign(x[i + 1:] - x[i]).sum()
    _, counts = np.unique(x, return_counts=True)
    tie = (counts * (counts - 1) * (2 * counts + 5)).sum()
    var = (n * (n - 1) * (2 * n + 5) - tie) / 18.0
    return s, var


def _z(s: float, var: float) -> float:
    if var <= 0:
        return 0.0
    return (s - np.sign(s)) / np.sqrt(var)


def sen_slope(t: np.ndarray, x: np.ndarray, var_s: float | None = None, alpha: float = 0.05):
    i, j = np.triu_indices(len(x), k=1)
    dt = t[j] - t[i]
    ok = dt != 0
    slopes = np.sort((x[j] - x[i])[ok] / dt[ok])
    if slopes.size == 0:
        return np.nan, (np.nan, np.nan)
    slope = float(np.median(slopes))
    ci = (np.nan, np.nan)
    if var_s is not None and var_s > 0:
        c = stats.norm.ppf(1 - alpha / 2) * np.sqrt(var_s)
        m1 = int(np.floor((slopes.size - c) / 2))
        m2 = int(np.ceil((slopes.size + c) / 2))
        if 0 <= m1 < slopes.size and 0 <= m2 < slopes.size:
            ci = (float(slopes[m1]), float(slopes[m2]))
    return slope, ci


def hamed_rao_factor(t: np.ndarray, x: np.ndarray, slope: float) -> float:
    """n/n* variance inflation from significant rank autocorrelations of the detrended series."""
    n = len(x)
    r = stats.rankdata(x - slope * t)
    r = r - r.mean()
    denom = (r ** 2).sum()
    acc = 0.0
    bound = stats.norm.ppf(0.975) / np.sqrt(n)
    for k in range(1, n - 2):
        rk = (r[:-k] * r[k:]).sum() / denom
        if abs(rk) > bound:
            acc += (n - k) * (n - k - 1) * (n - k - 2) * rk
    return max(1.0 + 2.0 / (n * (n - 1) * (n - 2)) * acc, 1e-6)


def mann_kendall(t, x, hamed_rao=False, alpha=0.05, report_slope=True):
    order = np.argsort(t)
    t, x = np.asarray(t, float)[order], np.asarray(x, float)[order]
    s, var = _s_and_ties(x)
    slope, _ = sen_slope(t, x)
    factor = hamed_rao_factor(t, x, slope) if hamed_rao else 1.0
    var_adj = var * factor
    z = _z(s, var_adj)
    p = 2 * (1 - stats.norm.cdf(abs(z)))
    slope, ci = sen_slope(t, x, var_adj, alpha) if report_slope else (np.nan, (np.nan, np.nan))
    tau = s / (0.5 * len(x) * (len(x) - 1))
    return dict(test="Mann-Kendall" + (" (Hamed-Rao)" if hamed_rao else ""), n=len(x), S=s,
                var_S=var_adj, variance_factor=factor, Z=z, p=p, tau=tau,
                sen_slope_per_year=slope, slope_ci=ci)


def seasonal_kendall(df: pd.DataFrame, season: str = "month", alpha=0.05, report_slope=True):
    d = pd.to_datetime(df["date"])
    df = df.assign(year=d.dt.year, season=d.dt.month if season == "month" else d.dt.quarter)
    g = df.groupby(["season", "year"], as_index=False)["value"].median()
    s_tot = var_tot = 0.0
    slopes = []
    n_used = 0
    for _, grp in g.groupby("season"):
        if len(grp) < 2:
            continue
        x = grp["value"].to_numpy(float); t = grp["year"].to_numpy(float)
        s, v = _s_and_ties(x)
        s_tot += s; var_tot += v; n_used += len(x)
        i, j = np.triu_indices(len(x), k=1)
        slopes.extend(((x[j] - x[i]) / (t[j] - t[i])).tolist())
    z = _z(s_tot, var_tot)
    p = 2 * (1 - stats.norm.cdf(abs(z)))
    slope = float(np.median(slopes)) if (slopes and report_slope) else np.nan
    return dict(test=f"Seasonal Kendall ({season})", n=n_used, S=s_tot, var_S=var_tot, Z=z, p=p,
                sen_slope_per_year=slope,
                note="one value per season-year (median); seasons treated as independent")


def prepare(df, date, value, censored=None, flow=None, flow_adjust=False):
    out = pd.DataFrame({"date": pd.to_datetime(df[date]), "value": pd.to_numeric(df[value], errors="coerce")})
    notes = []
    cens = np.zeros(len(out), bool)
    if censored:
        c = df[censored].astype(str).str.strip().str.lower()
        cens = c.isin(["true", "1", "<", "yes", "y"]).to_numpy()
        if cens.any():
            dl = out.loc[cens, "value"].max()
            below = out["value"] < dl
            recens = cens | below.to_numpy()
            out.loc[recens, "value"] = dl * 0.999  # all tied just below the highest DL
            notes.append(f"{cens.sum()} censored values; {recens.sum()} values re-censored at the highest detection limit ({dl}) and treated as ties")
            cens = recens
    if flow_adjust:
        if not flow:
            raise SystemExit("--flow-adjust needs --flow")
        q = pd.to_numeric(df[flow], errors="coerce")
        ok = (q > 0) & (out["value"] > 0)
        b = np.polyfit(np.log(q[ok]), np.log(out.loc[ok, "value"]), 1)
        out.loc[ok, "value"] = np.log(out.loc[ok, "value"]) - np.polyval(b, np.log(q[ok]))
        out = out[ok]
        cens = cens[ok.to_numpy()]
        notes.append(f"flow-adjusted: residuals of ln C = {b[1]:.3f} + {b[0]:.3f} ln Q; slopes are in ln units per year (x100 ~ % per year)")
    keep = out["value"].notna().to_numpy()
    out, cens = out[keep], cens[keep]
    return out.reset_index(drop=True), cens, notes


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("csv", nargs="?")
    ap.add_argument("--date", default="date"); ap.add_argument("--value")
    ap.add_argument("--censored"); ap.add_argument("--flow"); ap.add_argument("--flow-adjust", action="store_true")
    ap.add_argument("--seasonal", action="store_true"); ap.add_argument("--season", default="month", choices=["month", "quarter"])
    ap.add_argument("--hamed-rao", action="store_true"); ap.add_argument("--alpha", type=float, default=0.05)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if not (a.csv and a.value):
        ap.error("csv and --value are required")
    df = pd.read_csv(a.csv)
    data, cens, notes = prepare(df, a.date, a.value, a.censored, a.flow, a.flow_adjust)
    frac = float(cens.mean()) if len(cens) else 0.0
    report_slope = frac <= 0.15
    if not report_slope:
        notes.append(f"{frac:.0%} censored: Sen slope withheld (use Akritas-Theil-Sen, e.g. NADA2::ATS)")
    if a.seasonal:
        res = seasonal_kendall(data, a.season, a.alpha, report_slope)
    else:
        res = mann_kendall(decimal_year(data["date"]), data["value"].to_numpy(), a.hamed_rao, a.alpha, report_slope)
    res.update(period=f"{data['date'].min().date()} to {data['date'].max().date()}",
               units=f"{a.value} units per year", censored_fraction=round(frac, 3), notes=notes)
    print(json.dumps(res, indent=2, default=lambda o: None if (isinstance(o, float) and np.isnan(o)) else float(o) if isinstance(o, (np.floating,)) else str(o)))
    return 0


def selftest() -> int:
    rng = np.random.default_rng(42)
    dates = pd.date_range("2005-01-15", "2024-12-15", freq="MS") + pd.Timedelta(days=14)
    t = decimal_year(pd.Series(dates))
    season = 0.05 * np.sin(2 * np.pi * t)
    x = 0.10 + 0.002 * (t - t[0]) + season + rng.normal(0, 0.01, len(t))
    mk = mann_kendall(t, x)
    assert mk["p"] < 0.01 and abs(mk["sen_slope_per_year"] - 0.002) < 0.0007, mk
    assert mk["slope_ci"][0] < 0.002 < mk["slope_ci"][1], mk
    sk = seasonal_kendall(pd.DataFrame({"date": dates, "value": x}))
    assert sk["p"] < 0.001 and abs(sk["sen_slope_per_year"] - 0.002) < 0.0005, sk
    flat = 0.1 + rng.normal(0, 0.01, len(t))
    assert mann_kendall(t, flat)["p"] > 0.01
    # serial correlation inflates variance under Hamed-Rao
    ar = np.zeros(len(t))
    for k in range(1, len(t)):
        ar[k] = 0.8 * ar[k - 1] + rng.normal(0, 0.01)
    hr = mann_kendall(t, ar, hamed_rao=True)
    assert hr["variance_factor"] > 1.5, hr
    # tie correction: identical values give zero variance contribution
    s, v = _s_and_ties(np.array([1, 1, 1, 2.0]))
    assert s == 3 and abs(v - (4 * 3 * 13 - 3 * 2 * 11) / 18) < 1e-9
    print("wq_trends selftest passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
