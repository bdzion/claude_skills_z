# BMP, land-use and climate scenarios

## Design
- Use the same calibrated parameter set, inputs and period for baseline and scenarios;
  change only what the scenario represents, and list exactly what was changed (parameters,
  operations, areas) for each scenario.
- Represent each BMP by the mechanism the model has (e.g. filter strip efficiency, cover
  crop operations, reduced fertilizer rates, changed USLE_P). Say when the model lacks the
  mechanism and the representation is a proxy.
- Targeted vs random placement: when comparing targeting strategies (critical source
  areas, field-specific placement), hold the treated area or the budget constant across
  strategies so the comparison isolates placement.
- Climate scenarios: state the climate model ensemble, emission or warming level,
  downscaling and bias correction, and the period; report the spread across members, not
  only the ensemble mean.

## Reporting
- Report reductions at the field/edge-of-field level and at the outlet separately
  (`bmp_scenarios.py` keeps them apart). Outlet reductions are usually smaller.
- Give absolute (kg/yr) and relative (%) reductions, the treated area, and cost per kg
  reduced when costs are available (state the cost source, year and currency, CAD).
- Translate to targets where relevant (e.g. the 40 % spring TP and DRP load reduction
  targets for Lake Erie under the Great Lakes Water Quality Agreement Annex 4); check
  the target's exact definition and baseline year from the official source before using it.
- Note lags: modelled steady-state reductions can take years to decades to appear in
  monitoring data because of legacy sources and groundwater travel times (Meals et al. 2010).
- Do not report more precision than the calibration supports (e.g. 23 %, not 23.47 %).
