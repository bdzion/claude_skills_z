---
name: watershed-model-calibration
description: Set up, calibrate, validate and evaluate process-based watershed models — IMWEBs, SWAT/ArcSWAT/SWAT+, SWAT-CUP (SUFI-2), HSPF-type models — for flow, sediment and nutrients in tile-drained agricultural watersheds, and compare BMP, land-use and climate scenarios. Covers warm-up and calibration/validation period design, parameter selection and ranges, NSE, KGE, PBIAS, RSR and FDC diagnostics with Moriasi ratings, baseflow separation, equifinality and uncertainty, and reporting scenario reductions at field and outlet scales. Use whenever the user mentions model calibration, goodness of fit, SWAT-CUP output, poor NSE, parameter sensitivity, model validation, or BMP scenario results, even if they only paste a hydrograph or a metrics table.
---

# Watershed model calibration and scenario evaluation

A calibrated model is a hypothesis about how a watershed works. The goal is a parameter
set that reproduces the right flow pathways for the right reasons, so that BMP and
climate scenarios built on it are credible. A high NSE with wrong pathways (for example
tile flow carried as surface runoff) makes scenario results wrong while looking right.

## Workflow

1. **State the setup** (assumptions block below) before touching parameters: model and
   version, spatial discretization, inputs and their sources, simulation, warm-up,
   calibration and validation periods, time step of evaluation, gauges and constituents.
2. **Design the periods.** Warm-up long enough for soil water and nutrient pools to
   stabilize (commonly 2–5 years for nutrients; state the choice and its basis).
   Calibration and validation periods should each span wet and dry years. Use
   multi-site and multi-variable calibration where data allow, and a differential
   split-sample test when the scenario involves conditions outside the calibration
   period (climate change, land-use change).
3. **Calibrate in order of process:** water balance and flow partitioning (surface,
   lateral, tile, groundwater) first, then sediment, then nutrients. A nutrient fit on
   wrong flow pathways does not transfer to BMP scenarios. Check the annual water
   balance and the tile/baseflow share against independent estimates
   (`scripts/baseflow.py`, published tile-flow fractions for the region) before trusting
   daily fits.
4. **Choose parameters deliberately.** Start from a sensitivity analysis, keep ranges
   physically plausible, and record each change with its reason.
   [references/parameters.md](references/parameters.md) lists common SWAT parameters by
   process. For IMWEBs, use the parameter names and ranges of the user's model version and
   documentation; ask for them rather than mapping SWAT names onto IMWEBs.
5. **Evaluate with several metrics and diagnostics** using `scripts/model_metrics.py`
   (NSE, log-NSE, KGE and KGE′ with components, PBIAS, RSR, R², FDC segment biases).
   Report the time step the metrics refer to: Moriasi et al. (2007) ratings are for
   monthly values and are guidelines. Look at the hydrograph, the FDC and event peaks;
   a good NSE can hide poor low flows (log-NSE, FLV) or biased peaks (FHV).
6. **Quantify uncertainty.** With SWAT-CUP SUFI-2 report the p-factor and r-factor and the
   95PPU band, not only the best simulation. Acknowledge equifinality (Beven & Binley
   1992): several parameter sets fit equally well and can give different scenario results;
   run key scenarios across the behavioural sets where feasible.
7. **Run scenarios on the calibrated model** and compare with `scripts/bmp_scenarios.py`.
   See [references/scenarios.md](references/scenarios.md) for design and reporting rules.

## Assumptions block

```
Model / version: ...                 Discretization: n subbasins, n HRUs/fields, thresholds
Inputs: DEM (source, resolution), soils, land use / crop rotations, management, tile drainage
        representation, weather (stations or gridded product; period)
Periods: warm-up ... ; calibration ... ; validation ...
Evaluation: gauge(s), constituents, time step (daily / monthly), units (m3/s, t, kg)
Calibration tool and objective function: ...
```

## Diagnosing a poor fit

Before adjusting parameters, rule out input problems: weather station representativeness
(snow and freeze–thaw in Ontario winters), missing or mistimed management operations,
tile drainage not represented, point sources, reservoir or wetland storage, and observed
data quality (ice-affected flow estimates, load estimates from sparse grab samples; see
the water-quality-analysis skill). Many "parameter" problems are input problems.

## Reporting

- Give metrics for calibration and validation separately, with periods, time step and n.
- State the PBIAS sign convention (the script uses positive = underestimation).
- Distinguish the model's performance from the scenario's credibility: say which
  processes the scenario depends on and how well those were tested.
- Separate established findings, contested ones, and your own inference.

Sources with verified DOIs are in [references/sources.md](references/sources.md). Do not
cite from memory.
