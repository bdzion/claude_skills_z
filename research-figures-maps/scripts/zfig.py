"""House style and recipes for publication figures in hydrology, water quality and
food-system papers. Import it from a paper's figure scripts:

    import sys; sys.path.insert(0, "<path to this scripts folder>")
    import zfig
    zfig.use_style()
    fig, ax = zfig.figure("single", height_mm=60)

Conventions (state them in the figure script's docstring):
  * widths follow common Elsevier column sizes (single 90 mm, 1.5 column 140 mm,
    double 190 mm); check the target journal's current artwork guide;
  * 8 pt text at final size (7 pt minimum), sans-serif, units in every axis label;
  * Okabe-Ito colour-blind-safe qualitative palette (Wong 2011); perceptually uniform
    sequential maps (viridis, cividis or Crameri maps) for continuous data, never jet/rainbow;
  * 600 dpi PNG for review, PDF/SVG vector for submission when the journal accepts it.
"""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

MM = 1 / 25.4
WIDTHS_MM = {"single": 90, "onehalf": 140, "double": 190}
OKABE_ITO = ["#000000", "#E69F00", "#56B4E9", "#009E73", "#F0E442", "#0072B2", "#D55E00", "#CC79A7"]
LDC_REGIMES = [(0, 10, "High\nflows"), (10, 40, "Moist\nconditions"), (40, 60, "Mid-range\nflows"),
               (60, 90, "Dry\nconditions"), (90, 100, "Low\nflows")]


def use_style(base_pt: float = 8.0):
    plt.rcParams.update({
        "font.family": "sans-serif", "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
        "font.size": base_pt, "axes.labelsize": base_pt, "axes.titlesize": base_pt,
        "xtick.labelsize": base_pt - 1, "ytick.labelsize": base_pt - 1, "legend.fontsize": base_pt - 1,
        "axes.linewidth": 0.6, "lines.linewidth": 1.0, "xtick.major.width": 0.6, "ytick.major.width": 0.6,
        "axes.spines.top": False, "axes.spines.right": False, "legend.frameon": False,
        "axes.prop_cycle": matplotlib.cycler(color=OKABE_ITO[1:] + OKABE_ITO[:1]),
        "savefig.dpi": 600, "savefig.bbox": "tight", "pdf.fonttype": 42, "svg.fonttype": "none",
    })


def figure(width="single", height_mm=60, **kw):
    w = WIDTHS_MM.get(width, width) if isinstance(width, str) else width
    return plt.subplots(figsize=(w * MM, height_mm * MM), **kw)


def save(fig, stem, formats=("png", "pdf")):
    paths = []
    for f in formats:
        p = f"{stem}.{f}"; fig.savefig(p); paths.append(p)
    plt.close(fig)
    return paths


def hydrograph_with_rain(ax, dates, q_obs, q_sim=None, rain=None, q_label="Discharge (m$^3$ s$^{-1}$)",
                         rain_label="Precipitation (mm d$^{-1}$)"):
    """Flow on the main axis, precipitation as inverted bars on a twin axis."""
    ax.plot(dates, q_obs, color=OKABE_ITO[0], lw=0.8, label="Observed")
    if q_sim is not None:
        ax.plot(dates, q_sim, color=OKABE_ITO[6], lw=0.8, label="Simulated")
    ax.set_ylabel(q_label)
    if rain is not None:
        qmax = np.nanmax([np.nanmax(q_obs)] + ([np.nanmax(q_sim)] if q_sim is not None else []))
        ax.set_ylim(0, qmax * 1.6)  # headroom so inverted rain bars do not cover flow peaks
        ax2 = ax.twinx()
        ax2.bar(dates, rain, color=OKABE_ITO[5], width=1.0, alpha=0.6, linewidth=0)
        ax2.set_ylim(np.nanmax(rain) * 3, 0)
        ax2.set_ylabel(rain_label); ax2.spines["right"].set_visible(True); ax2.spines["top"].set_visible(False)
    ax.legend(loc="center right")
    return ax


def exceedance(values):
    v = np.sort(np.asarray(values, float)[np.isfinite(values)])[::-1]
    p = 100 * np.arange(1, len(v) + 1) / (len(v) + 1)  # Weibull plotting position
    return p, v


def flow_duration(ax, series: dict, ylabel="Discharge (m$^3$ s$^{-1}$)", log=True):
    for i, (name, q) in enumerate(series.items()):
        p, v = exceedance(q)
        ax.plot(p, v, label=name, color=OKABE_ITO[i % len(OKABE_ITO)])
    if log:
        ax.set_yscale("log")
    ax.set_xlabel("Flow exceedance probability (%)"); ax.set_ylabel(ylabel); ax.set_xlim(0, 100)
    ax.legend()
    return ax


def load_duration(ax, q_daily, sample_q, sample_conc, target_conc, conc_units="mg L$^{-1}$"):
    """Load duration curve: allowable load = target concentration x flow x 86.4 (kg/d),
    observed sample loads plotted at the exceedance of their sampling-day flow."""
    p, v = exceedance(q_daily)
    ax.plot(p, target_conc * v * 86.4, color=OKABE_ITO[0], label=f"Target ({target_conc} {conc_units})")
    sq = np.asarray(sample_q, float); sc = np.asarray(sample_conc, float)
    qs = np.sort(np.asarray(q_daily, float)[np.isfinite(q_daily)])
    ps = 100 * (1 - np.searchsorted(qs, sq, side="right") / (len(qs) + 1))
    exceed = sc > target_conc
    ax.scatter(ps[~exceed], (sc * sq * 86.4)[~exceed], s=8, color=OKABE_ITO[5], label="Sample load ≤ target", zorder=3)
    ax.scatter(ps[exceed], (sc * sq * 86.4)[exceed], s=8, color=OKABE_ITO[6], label="Sample load > target", zorder=3)
    ax.set_yscale("log"); ax.set_xlim(0, 100)
    for lo, hi, lab in LDC_REGIMES:
        ax.axvline(hi, color="0.7", lw=0.5)
        ax.text((lo + hi) / 2, 0.98, lab, transform=ax.get_xaxis_transform(), ha="center", va="top", fontsize=6, color="0.35")
    ax.set_xlabel("Flow exceedance probability (%)"); ax.set_ylabel("Load (kg d$^{-1}$)")
    ax.legend(loc="lower left")
    return ax


def obs_vs_sim(ax, obs, sim, units="m$^3$ s$^{-1}$", label="Discharge"):
    o, s = np.asarray(obs, float), np.asarray(sim, float)
    ax.scatter(o, s, s=6, color=OKABE_ITO[5], alpha=0.7)
    lim = [0, np.nanmax([o.max(), s.max()]) * 1.05]
    ax.plot(lim, lim, color="0.4", lw=0.6, ls="--", label="1:1")
    ax.set_xlim(lim); ax.set_ylim(lim); ax.set_aspect("equal")
    ax.set_xlabel(f"Observed {label.lower()} ({units})"); ax.set_ylabel(f"Simulated {label.lower()} ({units})")
    ax.legend(loc="upper left")
    return ax


def scenario_bars(ax, names, reductions_pct, lo=None, hi=None, ylabel="TP load reduction (%)"):
    x = np.arange(len(names))
    err = None if lo is None else [np.asarray(reductions_pct) - np.asarray(lo), np.asarray(hi) - np.asarray(reductions_pct)]
    ax.bar(x, reductions_pct, color=OKABE_ITO[3], yerr=err, capsize=2, error_kw=dict(lw=0.6))
    ax.set_xticks(x, names); ax.set_ylabel(ylabel); ax.axhline(0, color="0.3", lw=0.6)
    return ax


def selftest() -> int:
    import os
    import tempfile
    use_style()
    rng = np.random.default_rng(5)
    days = np.arange("2020-01-01", "2021-01-01", dtype="datetime64[D]")
    q = np.exp(rng.normal(0, 1, days.size)); rain = rng.gamma(0.3, 8, days.size)
    d = tempfile.mkdtemp()
    fig, ax = figure("double", 70); hydrograph_with_rain(ax, days, q, q * 0.9, rain); p1 = save(fig, f"{d}/hydro")
    fig, ax = figure("single", 60); flow_duration(ax, {"Observed": q, "Simulated": q * 1.1}); p2 = save(fig, f"{d}/fdc")
    idx = rng.choice(days.size, 40, replace=False)
    fig, ax = figure("single", 60); load_duration(ax, q, q[idx], 0.02 + 0.02 * q[idx], 0.03); p3 = save(fig, f"{d}/ldc")
    fig, ax = figure("single", 80); obs_vs_sim(ax, q, q * 0.9); p4 = save(fig, f"{d}/obs_sim")
    fig, ax = figure("single", 55); scenario_bars(ax, ["CC", "NT", "CC+NT"], [12, 8, 18], [9, 5, 14], [15, 11, 23]); p5 = save(fig, f"{d}/bars")
    for p in p1 + p2 + p3 + p4 + p5:
        assert os.path.getsize(p) > 2000, p
    w, _ = plt.imread(p2[0]).shape[1], None
    assert abs(w / 600 * 25.4 - 90) < 15, w  # about 90 mm at 600 dpi (tight bbox trims a little)
    print("zfig selftest passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(selftest())
