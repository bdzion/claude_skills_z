# Methods: choosing and reporting

## Decision table

| Question | Method | Notes |
|---|---|---|
| Is concentration changing over time? | Mann-Kendall + Sen slope; seasonal Kendall when seasonality is strong | One value per season-year for seasonal Kendall; Hamed–Rao correction if residual autocorrelation |
| Is concentration changing after removing flow variation? | Flow-adjusted concentration (residuals of ln C on ln Q) then Kendall; or WRTDS flow-normalized concentration | Flow adjustment answers a different question from the raw trend; report both |
| Is the load changing? | Annual loads (several estimators) then trend on loads; or WRTDS flow-normalized flux | Loads are dominated by flow; a load trend can reverse a concentration trend |
| How much was exported this year? | Interpolation, FWMC, Beale ratio; regression/WRTDS when sampling is sparse | Report the spread between estimators as uncertainty |
| How does concentration respond to flow? | ln C–ln Q slope (b); hysteresis on event data | b ≈ 0 chemostatic, b > 0 mobilization, b < 0 dilution |
| Which drivers explain variation? | Regression or tree ensembles with SHAP, time-blocked validation | Association, not causation |
| Many values below detection | Re-censor at highest DL + Kendall; Akritas–Theil–Sen; ROS / MLE for summaries | Avoid DL/2 substitution for trends |

## Equations

**Load conversion.** L (kg/day) = C (mg/L) × Q (m³/s) × 86.4.

**Mann-Kendall.** S = Σ_{i<j} sgn(x_j − x_i);
Var(S) = [n(n−1)(2n+5) − Σ_t t(t−1)(2t+5)] / 18 over tie groups of size t;
Z = (S − sgn S)/√Var(S).

**Sen slope.** Median of (x_j − x_i)/(t_j − t_i) over all i < j, in units per year.

**Seasonal Kendall.** S = Σ_k S_k and Var(S) = Σ_k Var(S_k) over seasons k, assuming
independence among seasons; seasonal slope = median of within-season pairwise slopes.

**Hamed–Rao correction.** Var*(S) = Var(S) · n/n*, with
n/n* = 1 + 2/[n(n−1)(n−2)] Σ_{k} (n−k)(n−k−1)(n−k−2) ρ_k over significant lag-k
autocorrelations ρ_k of the ranks of the detrended series.

**Flow-weighted mean concentration.** FWMC = Σ C_i Q_i / Σ Q_i over samples.

**Beale ratio estimator** (daily-mean load, finite-population form):
μ̂_L = μ_Q (m_l/m_q) [1 + f s_lq/(m_l m_q)] / [1 + f s_q²/m_q²], f = 1/n − 1/N,
where m_l, m_q are sample means of daily load and flow on sample days, s_lq and s_q² their
covariance and variance, μ_Q the mean of all N daily flows.

## Verified sources (checked against Crossref, 18 Nov 2026)

- Hirsch, R.M., Slack, J.R., Smith, R.A. (1982). Techniques of trend analysis for monthly water quality data. *Water Resources Research* 18(1), 107–121. https://doi.org/10.1029/WR018i001p00107
- Sen, P.K. (1968). Estimates of the regression coefficient based on Kendall's tau. *J. Am. Stat. Assoc.* 63, 1379–1389. https://doi.org/10.1080/01621459.1968.10480934
- Hamed, K.H., Rao, A.R. (1998). A modified Mann-Kendall trend test for autocorrelated data. *J. Hydrology* 204, 182–196. https://doi.org/10.1016/S0022-1694(97)00125-X
- Yue, S., Pilon, P., Phinney, B., Cavadias, G. (2002). The influence of autocorrelation on the ability to detect trend in hydrological series. *Hydrological Processes* 16, 1807–1829. https://doi.org/10.1002/hyp.1095
- Hirsch, R.M., Moyer, D.L., Archfield, S.A. (2010). Weighted Regressions on Time, Discharge, and Season (WRTDS). *JAWRA* 46(5), 857–880. https://doi.org/10.1111/j.1752-1688.2010.00482.x
- Hirsch, R.M., De Cicco, L.A. (2015). User guide to EGRET and dataRetrieval. USGS Techniques and Methods 4-A10. https://doi.org/10.3133/tm4A10
- Helsel, D.R. (2011). *Statistics for Censored Environmental Data Using Minitab and R*, 2nd ed. Wiley. https://doi.org/10.1002/9781118162729
- Helsel, D.R., Hirsch, R.M., Ryberg, K.R., Archfield, S.A., Gilroy, E.J. (2020). Statistical methods in water resources. USGS Techniques and Methods 4-A3. https://doi.org/10.3133/tm4A3
- Meals, D.W., Dressing, S.A., Davenport, T.E. (2010). Lag time in water quality response to best management practices: a review. *J. Environ. Qual.* 39, 85–96. https://doi.org/10.2134/jeq2009.0108
- Jarvie, H.P. et al. (2013). Phosphorus mitigation to control river eutrophication: murky waters, inconvenient truths, and "postnormal" science. *J. Environ. Qual.* 42, 295–304. https://doi.org/10.2134/jeq2012.0085
- Roberts, D.R. et al. (2017). Cross-validation strategies for data with temporal, spatial, hierarchical, or phylogenetic structure. *Ecography* 40, 913–929. https://doi.org/10.1111/ecog.02881
- Lundberg, S.M. et al. (2020). From local explanations to global understanding with explainable AI for trees. *Nature Machine Intelligence* 2, 56–67. https://doi.org/10.1038/s42256-019-0138-9

The Beale estimator is described in several load-estimation texts; cite the specific
source the user's lab or agency uses, and check it before citing.
