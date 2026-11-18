# Terrain methods and their effects

| Choice | Options | Effect |
|---|---|---|
| Depression handling | Least-cost breaching (preferred), filling, hybrid | Filling flattens large areas and creates parallel artefact flow paths; breaching cuts through barriers and keeps relief |
| Culverts | Burn streams at roads before breaching | Without it, roads dam flow and create false ponds and diverted paths |
| Flow routing | D8 (single direction), D-infinity, FD8 (dispersive) | D8 for channels and flow-path lines; dispersive methods for hillslope indices such as TWI |
| Contributing area | Cells, catchment area (m²), specific contributing area (m²/m) | TWI, SPI and STI use specific contributing area |
| Flow-path threshold | e.g. 1–5 ha for field-scale concentrated flow | Lower values give more, shorter paths; report it and test sensitivity |
| DEM resolution | 0.5–5 m LiDAR | Finer captures field features (furrows, berms) and noise; smoothing or resampling to 2–5 m is common for field targeting |

## Indices
- TWI = ln(a / tan β), with a the specific contributing area (m²/m) and β the slope
  (Beven & Kirkby 1979). High values mark likely saturation and runoff generation.
- SPI = a · tan β: erosive power of concentrated flow (Moore et al. 1991).
- STI = (a/22.13)^0.6 · (sin β/0.0896)^1.3 in its usual form (the WhiteboxTools default
  exponents are 0.4 and 1.3; state the exponents used): sediment transport capacity,
  related to the LS factor.
Indices rank locations within a landscape; they are not loads.

## Verified sources (checked against Crossref, 18 Nov 2026)
- Lindsay, J.B. (2016). Whitebox GAT: a case study in geomorphometric analysis. *Computers & Geosciences* 95, 75–84. https://doi.org/10.1016/j.cageo.2016.07.003
- Lindsay, J.B. (2016). Efficient hybrid breaching-filling sink removal methods for flow path enforcement in digital elevation models. *Hydrological Processes* 30, 846–857. https://doi.org/10.1002/hyp.10648
- Beven, K.J., Kirkby, M.J. (1979). A physically based, variable contributing area model of basin hydrology. *Hydrological Sciences Bulletin* 24, 43–69. https://doi.org/10.1080/02626667909491834
- Moore, I.D., Grayson, R.B., Ladson, A.R. (1991). Digital terrain modelling: a review of hydrological, geomorphological, and biological applications. *Hydrological Processes* 5, 3–30. https://doi.org/10.1002/hyp.3360050103
- Tomer, M.D. et al. (2013). Combining precision conservation technologies into a flexible framework to facilitate agricultural watershed planning. *J. Soil Water Conserv.* 68(5), 113A–120A. https://doi.org/10.2489/jswc.68.5.113A
- Gorelick, N. et al. (2017). Google Earth Engine: planetary-scale geospatial analysis for everyone. *Remote Sensing of Environment* 202, 18–27. https://doi.org/10.1016/j.rse.2017.06.031
