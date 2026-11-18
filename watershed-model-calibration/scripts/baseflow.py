#!/usr/bin/env python3
"""Baseflow separation with the Eckhardt (2005) two-parameter recursive digital filter.

  b_t = [(1 - BFImax) * a * b_{t-1} + (1 - a) * BFImax * Q_t] / (1 - a * BFImax),  b_t <= Q_t

a     recession constant for a daily time step; estimate it from recession analysis of the
      user's own record where possible (0.98 is a common starting value, not a default to
      report without checking).
BFImax  maximum baseflow index; Eckhardt (2005) suggests 0.80 for perennial streams on
      porous aquifers, 0.50 for ephemeral streams on porous aquifers, 0.25 for perennial
      streams on hard-rock aquifers. Tile-drained clay-till catchments do not fit these
      classes cleanly: drain flow is fast subsurface flow that a filter partly counts as
      baseflow, so report BFI as filter-dependent, with sensitivity to BFImax.

Usage:
  python baseflow.py flow.csv --date date --q Q_m3s [--a 0.98] [--bfimax 0.5] [--out bf.csv]
  python baseflow.py --selftest
Input: daily mean flow (m3/s), no gaps (gaps are reported and the filter restarts after them).
"""
from __future__ import annotations

import argparse
import sys

import numpy as np
import pandas as pd


def eckhardt(q: np.ndarray, a: float = 0.98, bfimax: float = 0.5) -> np.ndarray:
    q = np.asarray(q, float)
    b = np.empty_like(q)
    b[0] = q[0] * bfimax  # initial condition; discard a warm-up period in interpretation
    for t in range(1, len(q)):
        if not np.isfinite(q[t]):
            b[t] = np.nan; continue
        prev = b[t - 1] if np.isfinite(b[t - 1]) else q[t] * bfimax
        b[t] = min(((1 - bfimax) * a * prev + (1 - a) * bfimax * q[t]) / (1 - a * bfimax), q[t])
    return b


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("csv", nargs="?"); ap.add_argument("--date", default="date"); ap.add_argument("--q")
    ap.add_argument("--a", type=float, default=0.98); ap.add_argument("--bfimax", type=float, default=0.5)
    ap.add_argument("--out"); ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if not (a.csv and a.q):
        ap.error("csv and --q are required")
    df = pd.read_csv(a.csv, parse_dates=[a.date]).sort_values(a.date)
    gaps = df[a.q].isna().sum()
    df["baseflow"] = eckhardt(df[a.q].to_numpy(), a.a, a.bfimax)
    ok = df[a.q].notna()
    bfi = df.loc[ok, "baseflow"].sum() / df.loc[ok, a.q].sum()
    print(f"# Eckhardt filter: a={a.a}, BFImax={a.bfimax}; daily flow units as input; {gaps} missing days")
    print(f"BFI = {bfi:.3f}")
    for bm in (0.25, 0.5, 0.8):
        b = eckhardt(df[a.q].to_numpy(), a.a, bm)
        print(f"  sensitivity BFImax={bm}: BFI = {np.nansum(b[ok]) / df.loc[ok, a.q].sum():.3f}")
    if a.out:
        df.to_csv(a.out, index=False)
    return 0


def selftest() -> int:
    q = np.full(400, 2.0)
    b = eckhardt(q, 0.98, 0.5)
    assert np.all(b <= q + 1e-12)
    assert abs(b[-1] - 1.0) < 0.01           # constant flow converges to BFImax * Q
    rng = np.random.default_rng(0)
    storm = 1 + np.abs(rng.normal(0, 3, 365)) * (rng.random(365) < 0.1)
    bs = eckhardt(storm, 0.98, 0.8)
    assert np.all(bs <= storm + 1e-12) and 0 < bs.sum() / storm.sum() < 0.8 + 1e-9
    print("baseflow selftest passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
