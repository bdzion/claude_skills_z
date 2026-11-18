#!/usr/bin/env python3
"""Goodness-of-fit metrics for simulated vs observed watershed model output.

Metrics: NSE (Nash & Sutcliffe 1970), log-NSE, KGE (Gupta et al. 2009) and KGE'
(Kling et al. 2012) with their components, PBIAS and RSR (Moriasi et al. 2007), R2,
and flow-duration-curve segment biases (Yilmaz et al. 2008): high-flow volume bias
(top 2 %), mid-segment slope bias (20-70 % exceedance) and low-flow bias (bottom 30 %).

Sign convention (Moriasi et al. 2007): PBIAS = 100 * sum(obs - sim) / sum(obs);
positive = model underestimates, negative = overestimates. Stated in every output
because the literature uses both conventions.

Ratings: Moriasi et al. (2007) general performance ratings for a MONTHLY time step
(NSE, RSR, PBIAS by constituent). They are guidelines, not tests; Moriasi et al. (2015)
gives revised criteria by variable, scale and time step; take those values from the
paper itself rather than from memory.

Usage:
  python model_metrics.py run.csv --date date --obs Q_obs --sim Q_sim
         [--constituent flow|sediment|nutrient] [--monthly mean|sum]
         [--start 2012-01-01 --end 2018-12-31] [--warmup-end 2011-12-31]
  python model_metrics.py --selftest
"""
from __future__ import annotations

import argparse
import json
import sys

import numpy as np
import pandas as pd

# Moriasi et al. (2007), Table 4: monthly time step. NSE > bound; RSR <= bound; |PBIAS| < bound.
RATINGS = {
    "NSE": [(0.75, "very good"), (0.65, "good"), (0.50, "satisfactory")],
    "RSR": [(0.50, "very good"), (0.60, "good"), (0.70, "satisfactory")],
    "PBIAS": {"flow": [(10, "very good"), (15, "good"), (25, "satisfactory")],
              "sediment": [(15, "very good"), (30, "good"), (55, "satisfactory")],
              "nutrient": [(25, "very good"), (40, "good"), (70, "satisfactory")]},
}


def _clean(obs, sim):
    o, s = np.asarray(obs, float), np.asarray(sim, float)
    ok = np.isfinite(o) & np.isfinite(s)
    return o[ok], s[ok]


def nse(obs, sim):
    o, s = _clean(obs, sim)
    return 1 - np.sum((o - s) ** 2) / np.sum((o - o.mean()) ** 2)


def log_nse(obs, sim, eps=None):
    o, s = _clean(obs, sim)
    eps = eps if eps is not None else 0.01 * o.mean()  # avoids log(0); stated in output
    return nse(np.log(o + eps), np.log(s + eps))


def kge(obs, sim, modified=False):
    o, s = _clean(obs, sim)
    r = np.corrcoef(o, s)[0, 1]
    beta = s.mean() / o.mean()
    if modified:  # KGE' (Kling et al. 2012): coefficient-of-variation ratio
        g = (s.std() / s.mean()) / (o.std() / o.mean())
    else:         # KGE (Gupta et al. 2009): standard-deviation ratio
        g = s.std() / o.std()
    val = 1 - np.sqrt((r - 1) ** 2 + (g - 1) ** 2 + (beta - 1) ** 2)
    return val, dict(r=r, bias_ratio=beta, **({"cv_ratio": g} if modified else {"alpha_sd_ratio": g}))


def pbias(obs, sim):
    o, s = _clean(obs, sim)
    return 100 * np.sum(o - s) / np.sum(o)


def rsr(obs, sim):
    o, s = _clean(obs, sim)
    return np.sqrt(np.sum((o - s) ** 2)) / np.sqrt(np.sum((o - o.mean()) ** 2))


def r2(obs, sim):
    o, s = _clean(obs, sim)
    return np.corrcoef(o, s)[0, 1] ** 2


def fdc_biases(obs, sim):
    """Yilmaz et al. (2008) FDC signatures, in % (positive = simulated higher)."""
    o, s = _clean(obs, sim)
    o, s = np.sort(o)[::-1], np.sort(s)[::-1]
    n = len(o)
    p = (np.arange(1, n + 1) - 0.5) / n
    hi = p <= 0.02
    fhv = 100 * (s[hi] - o[hi]).sum() / o[hi].sum()
    i20, i70 = np.searchsorted(p, 0.2), np.searchsorted(p, 0.7)
    mid = lambda q: np.log(max(q[i20], 1e-9)) - np.log(max(q[i70], 1e-9))
    fms = 100 * (mid(s) - mid(o)) / mid(o) if mid(o) != 0 else np.nan
    lo = p >= 0.7
    lo_o, lo_s = np.log(np.maximum(o[lo], 1e-9)), np.log(np.maximum(s[lo], 1e-9))
    qo = np.sum(lo_o - lo_o.min()); qs = np.sum(lo_s - lo_s.min())
    flv = -100 * (qs - qo) / qo if qo != 0 else np.nan
    return dict(FHV_pct=fhv, FMS_pct=fms, FLV_pct=flv)


def rate(metric, value, constituent="flow"):
    if not np.isfinite(value):
        return "n/a"
    if metric == "NSE":
        for bound, label in RATINGS["NSE"]:
            if value > bound:  # Moriasi 2007: e.g. good = 0.65 < NSE <= 0.75
                return label
        return "unsatisfactory"
    if metric == "RSR":
        for bound, label in RATINGS["RSR"]:
            if value <= bound:
                return label
        return "unsatisfactory"
    if metric == "PBIAS":
        for bound, label in RATINGS["PBIAS"][constituent]:
            if abs(value) < bound:
                return label
        return "unsatisfactory"
    return "n/a"


def evaluate(obs, sim, constituent="flow", monthly=False):
    k, kc = kge(obs, sim)
    k2, k2c = kge(obs, sim, modified=True)
    res = dict(n=int(np.sum(np.isfinite(np.asarray(obs, float)) & np.isfinite(np.asarray(sim, float)))),
               NSE=nse(obs, sim), logNSE=log_nse(obs, sim), KGE=k, KGE_components=kc,
               KGE_prime=k2, KGE_prime_components=k2c, PBIAS_pct=pbias(obs, sim),
               RSR=rsr(obs, sim), R2=r2(obs, sim), **fdc_biases(obs, sim),
               pbias_convention="100*sum(obs-sim)/sum(obs); positive = underestimation",
               kge_benchmark_note="KGE = -0.41 corresponds to using the observed mean as predictor (Knoben et al. 2019)")
    if monthly:
        res["ratings_Moriasi2007_monthly"] = dict(NSE=rate("NSE", res["NSE"]), RSR=rate("RSR", res["RSR"]),
                                                  PBIAS=rate("PBIAS", res["PBIAS_pct"], constituent))
    else:
        res["ratings_note"] = "Moriasi et al. (2007) ratings are for monthly values; rerun with --monthly to apply them"
    return res


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("csv", nargs="?"); ap.add_argument("--date", default="date")
    ap.add_argument("--obs"); ap.add_argument("--sim")
    ap.add_argument("--constituent", default="flow", choices=["flow", "sediment", "nutrient"])
    ap.add_argument("--monthly", choices=["mean", "sum"], help="aggregate to months first: mean for flow/concentration, sum for loads")
    ap.add_argument("--start"); ap.add_argument("--end"); ap.add_argument("--warmup-end")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if not (a.csv and a.obs and a.sim):
        ap.error("csv, --obs and --sim are required")
    df = pd.read_csv(a.csv, parse_dates=[a.date]).set_index(a.date)[[a.obs, a.sim]].astype(float)
    if a.warmup_end:
        df = df[df.index > pd.Timestamp(a.warmup_end)]
    if a.start:
        df = df[df.index >= pd.Timestamp(a.start)]
    if a.end:
        df = df[df.index <= pd.Timestamp(a.end)]
    if a.monthly:
        # only months where every day has both values, so partial months do not bias sums
        full = df.dropna().groupby(pd.Grouper(freq="MS")).filter(lambda m: len(m) == m.index[0].days_in_month)
        df = getattr(full.groupby(pd.Grouper(freq="MS")), a.monthly)().dropna()
    res = evaluate(df[a.obs], df[a.sim], a.constituent, monthly=bool(a.monthly))
    res["period"] = f"{df.index.min().date()} to {df.index.max().date()}"
    res["time_step"] = f"monthly ({a.monthly})" if a.monthly else "as supplied"
    print(json.dumps(res, indent=2, default=float))
    return 0


def selftest() -> int:
    rng = np.random.default_rng(3)
    o = np.exp(rng.normal(1, 0.8, 1000))
    assert abs(nse(o, o) - 1) < 1e-12 and abs(kge(o, o)[0] - 1) < 1e-12 and abs(pbias(o, o)) < 1e-12
    assert abs(nse(o, np.full_like(o, o.mean()))) < 1e-12           # mean predictor -> NSE 0
    assert abs(kge(o, o * 0 + o.mean() + 1e-9 * rng.normal(size=o.size))[0] - (1 - np.sqrt(2))) < 0.05
    assert pbias(o, 0.8 * o) > 0                                      # underestimation -> positive
    assert abs(pbias(o, 0.8 * o) - 20) < 1e-9
    assert abs(rsr(o, o * 1.1) - np.sqrt(np.sum((0.1 * o) ** 2) / np.sum((o - o.mean()) ** 2))) < 1e-12
    assert rate("NSE", 0.75) == "good" and rate("NSE", 0.80) == "very good" and rate("NSE", 0.55) == "satisfactory" and rate("NSE", 0.4) == "unsatisfactory"
    assert rate("PBIAS", -12, "flow") == "good" and rate("PBIAS", 50, "nutrient") == "satisfactory"
    f = fdc_biases(o, 1.2 * o)
    assert f["FHV_pct"] > 19 and abs(f["FMS_pct"]) < 1e-6
    print("model_metrics selftest passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
