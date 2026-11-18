# Figure guide

## Choosing the form
| Message | Form | Notes |
|---|---|---|
| Time behaviour of flow and response to rain | Hydrograph with inverted precipitation bars (`hydrograph_with_rain`) | Daily data over a year or event windows; zoom panels for events |
| Flow regime, model fit across flows | Flow-duration curve (`flow_duration`), log y | Compare observed and simulated; mark segments (high, mid, low) when discussing FDC biases |
| When a water-quality target is exceeded | Load-duration curve (`load_duration`) with flow regimes (US EPA 2007 zones: high 0–10 %, moist 10–40 %, mid-range 40–60 %, dry 60–90 %, low 90–100 %) | Shows whether exceedances occur at high flows (nonpoint, runoff) or low flows (point sources, legacy) |
| Model fit | Observed vs simulated scatter with 1:1 line (`obs_vs_sim`) plus time series | Report the metrics in the caption or a table, not crowded into the panel |
| Scenario outcomes | Bars or points with ranges (`scenario_bars`) | Order scenarios by effect or by a logical sequence; same y-axis across panels |
| Trends | Time series with Sen slope line and annotation of slope and period | Show raw data behind the trend line |
| Spatial pattern | Map (choropleth by field or subbasin, raster for continuous surfaces) | Classify with stated breaks (quantiles, natural breaks or meaningful thresholds) |
| Food-system propagation | Network or Sankey-style flow diagram; small multiples of delivery ratio over time by node | Mark illustrative values on the figure |

## Sizes
Common Elsevier artwork sizes: single column 90 mm, 1.5 column 140 mm, double column
190 mm. AGU, Wiley, Springer and MDPI differ; check the target journal's current guide and
record the width used at the top of each figure script.

## Map checklist
- CRS and datum stated (caption or map note); projected CRS for regional maps of southern
  Ontario (e.g. EPSG:2958 or 3161).
- Scale bar in km or m; north arrow if north is not up or the map is rotated.
- Inset locator (watershed in Ontario / Great Lakes basin).
- Legend with units and class breaks; same classes across comparable panels.
- Labels for key features only (outlet, gauges, sampling stations with IDs used in the text).
- Data credits and licences in the caption (e.g. Ontario Geospatial Data, AAFC, Water
  Survey of Canada), with the version or year.

## Verified sources (checked against Crossref, 18 Nov 2026)
- Crameri, F., Shephard, G.E., Heron, P.J. (2020). The misuse of colour in science communication. *Nature Communications* 11, 5444. https://doi.org/10.1038/s41467-020-19160-7
- Wong, B. (2011). Points of view: Color blindness. *Nature Methods* 8, 441. https://doi.org/10.1038/nmeth.1618
- Rougier, N.P., Droettboom, M., Bourne, P.E. (2014). Ten simple rules for better figures. *PLoS Computational Biology* 10, e1003833. https://doi.org/10.1371/journal.pcbi.1003833
- Vogel, R.M., Fennessey, N.M. (1994). Flow-duration curves. I: New interpretation and confidence intervals. *J. Water Resour. Plann. Manage.* 120(4), 485–504. https://doi.org/10.1061/(ASCE)0733-9496(1994)120:4(485)
- US EPA (2007). An approach for using load duration curves in the development of TMDLs. EPA 841-B-07-006 (report; no DOI).
