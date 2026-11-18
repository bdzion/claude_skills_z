# Common SWAT (2012 / ArcSWAT) calibration parameters by process

Ranges differ by model version, region and input data. Take bounds from the SWAT
input/output documentation for the version in use and from regional studies, and keep
them physically plausible. SWAT-CUP change types: `r__` relative change (multiply by
1 + value), `v__` replace, `a__` add.

| Process | Parameters (file) | What they control |
|---|---|---|
| Surface runoff | CN2 (.mgt), SURLAG (.bsn) | Runoff volume; runoff lag to the channel |
| Evapotranspiration | ESCO, EPCO (.hru/.bsn) | Soil evaporation and plant uptake compensation |
| Soil water | SOL_AWC, SOL_K (.sol) | Available water capacity; saturated hydraulic conductivity |
| Groundwater | ALPHA_BF, GW_DELAY, GWQMN, GW_REVAP, REVAPMN, RCHRG_DP (.gw) | Baseflow recession, recharge delay, return-flow threshold, revap, deep recharge |
| Tile drainage | DDRAIN, TDRAIN, GDRAIN (.mgt) | Drain depth (mm), time to drain to field capacity (h), drain lag (h) |
| Snow | SFTMP, SMTMP, SMFMX, SMFMN, TIMP (.bsn) | Snowfall and melt temperatures, melt factors, snowpack temperature lag |
| Channel routing | CH_N2, CH_K2 (.rte) | Manning's n; channel transmission losses |
| Sediment | USLE_P (.mgt), SPCON, SPEXP, PRF (.bsn), CH_COV1, CH_COV2 (.rte) | Support practice; channel sediment transport and erodibility; peak rate factor |
| Phosphorus | PPERCO, PHOSKD, PSP (.bsn), ERORGP (.hru), soil P initial pools (.chm) | P percolation, partitioning, availability, enrichment ratio |
| Nitrogen | NPERCO, CDN, SDNCO, RCN (.bsn), initial soil NO3 (.chm) | Nitrate percolation, denitrification, N in rain |

Notes for tile-drained watersheds:
- Check that tile flow is being generated (HRU output) where drains exist; otherwise the
  model routes water through surface or lateral flow and nutrient pathways are wrong.
- Soluble P can move through drains; check how the version in use represents P in tile
  flow before interpreting dissolved P scenarios.
- Frozen-soil and snowmelt runoff dominate winter and spring loads in Ontario; poor
  winter fits are common and should be reported rather than tuned away with
  non-physical values.

For IMWEBs and other models, build the equivalent table from the user's model
documentation; do not transfer SWAT names or ranges.
