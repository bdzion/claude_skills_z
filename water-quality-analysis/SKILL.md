---
name: water-quality-analysis
description: Analyze long-term stream and tributary water-quality monitoring data (total and soluble reactive phosphorus, nitrate, TSS, chloride, E. coli) together with flow — data audits, concentration–discharge behaviour, annual and seasonal loads, flow-weighted concentrations, Mann-Kendall, seasonal Kendall and Sen slope trends, censored (<DL) values, and machine-learning models of concentration with SHAP. Use whenever the user shares grab-sample or sensor water-quality data, conservation-authority or PWQMN records, Great Lakes tributary datasets, or asks about loads, trends, flow-adjusted concentrations, nutrient export or ML on water-quality records, even if they never say "trend test".
---

# Water-quality analysis

Long monitoring records answer management questions only when the analysis respects how
they were collected: grab samples cluster in some flows and seasons, laboratories change
methods and detection limits, and concentration, flow and load can move in different
directions. This skill turns such records into defensible numbers, with the assumptions
written next to every result.

## Workflow

1. **Audit before analysis.** Run the checklist in [references/data-audit.md](references/data-audit.md)
   and write the *assumptions block* (below) before any test or model. Most wrong answers
   in this field come from units, censoring or flow pairing, not from the statistics.
2. **Match the method to the question** with the decision table in
   [references/methods.md](references/methods.md). Say which question the result answers
   (concentration trend, flow-normalized trend, load trend, or event behaviour), because
   they are not interchangeable.
3. **Compute with the bundled scripts** where they fit, so results are reproducible:
   - `scripts/wq_trends.py`: Mann-Kendall (optional Hamed–Rao correction), Sen slope with
     confidence interval, seasonal Kendall, log-linear flow adjustment, censoring by
     re-censoring at the highest detection limit.
   - `scripts/wq_loads.py`: annual loads by interpolation, flow-weighted mean concentration
     and the Beale ratio estimator, side by side, with flags for incomplete flow records,
     few samples, and unsampled high flows.
   Run `python <script> --help` for arguments, and `--selftest` once in a new environment.
   For WRTDS flow normalization or censored regression, write R code with EGRET or NADA2
   instead of approximating them in Python, and say so.
4. **Report** effect size with units and period (e.g. "TP decreased by 0.004 mg/L per
   year, 95 % CI 0.001–0.007, 2005–2024, seasonal Kendall p = 0.01"), not p-values alone.
   Report every station's result when several are tested, and control the false-discovery
   rate (Benjamini–Hochberg) across stations.
5. **Separate three kinds of statement** in the write-up: what the data show, what the
   literature establishes, and your inference (e.g. attributing a trend to BMP adoption).
   Attribution needs evidence beyond the trend itself; name the alternative explanations
   (flow regime, land-use change, sampling change, legacy P).

## Assumptions block

Put this at the top of every analysis output, filled in:

```
Stations / period: ...            Sampling: grab | composite | sensor; frequency ...
Units: concentration mg/L (as P / as N?); flow m3/s daily mean (source: WSC HYDAT station ...)
Time step: daily flow; samples paired to same-day mean flow; time zone ...
Year definition: water year Oct–Sep | calendar
Censoring: n below DL, DL values and changes, method used
Excluded data and why: ...
```

## Machine learning on water-quality records

Use ML for prediction or for exploring drivers, not as proof of cause.
- Split by time (blocked or forward-chaining) or by station, never at random: random
  splits leak autocorrelated information and inflate skill (Roberts et al. 2017).
- Compare against a simple baseline (seasonal mean or ln C–ln Q regression); report the
  ML gain over it.
- SHAP values describe the model, not the watershed (Lundberg et al. 2020). Phrase
  results as "the model associates higher TP with ..."; correlated predictors share
  credit unpredictably.
- State feature lags and aggregation windows (e.g. 3-day antecedent precipitation) with units.

## Python conventions

Python first, commented, reproducible: fixed random seeds, explicit file paths, package
versions printed at the top of a run, and the assumptions block repeated as a docstring.
Keep units in column names (`TP_mg_L`, `Q_m3s`).

## References

[references/methods.md](references/methods.md) holds the equations and sources; every DOI
there was checked against Crossref. Do not add a citation from memory: check it, or say
the source still needs to be found.
