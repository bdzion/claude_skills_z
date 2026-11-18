---
name: precision-conservation-gis
description: Geospatial workflows for precision conservation in agricultural watersheds — LiDAR DEM conditioning, flow paths and contributing areas, TWI, stream power and sediment transport indices, critical source area (CSA) identification, field-scale BMP siting (grassed waterways, WASCoBs, buffers, wetlands), ACPF-style analysis adapted to Ontario, and Earth observation in Google Earth Engine (Sentinel-2/Landsat crop cover, residue and cover-crop mapping, AAFC Annual Crop Inventory). Works across WhiteboxTools, ArcGIS Pro, QGIS and GEE in Python. Use whenever the user asks about DEM processing, flow accumulation, CSAs, targeting or siting BMPs, terrain indices, crop or cover-crop mapping from imagery, or CRS and projection problems in agricultural GIS work.
---

# Precision conservation GIS

Precision conservation puts the right practice in the right place at the right scale.
The GIS work behind it succeeds when three things hold: the terrain represents how water
actually moves (including through culverts and drains), source and transport are both
considered, and every layer carries a known CRS, unit and date.

## Workflow

1. **Fix the frame first.** Projected CRS in metres for any slope, area, distance or flow
   computation; one CRS for the whole project; vertical units confirmed. Run
   `python scripts/terrain_targeting.py check dem.tif`. Ontario conventions and data
   sources are in [references/crs-and-data-ontario.md](references/crs-and-data-ontario.md).
2. **Condition the DEM for hydrology.** Burn streams at road crossings (culverts) before
   removing depressions, otherwise road embankments become false dams in flat, tile-drained
   landscapes. Prefer least-cost breaching over filling (Lindsay 2016); keep real
   depressions (wetlands, closed basins) when they matter for the question.
3. **Derive flow and terrain layers** with `python scripts/terrain_targeting.py run`
   (WhiteboxTools): D8 pointer, specific contributing area, slope, TWI, SPI, STI and
   concentrated flow paths at a stated contributing-area threshold. Method choices and
   their effects are in [references/terrain-methods.md](references/terrain-methods.md).
4. **Identify critical source areas as source × transport.** A CSA needs a pollutant
   source (high soil-test P, manure, erodible soil, bare soil in shoulder seasons) and a
   connection to water (flow path, proximity, surface inlet, tile). Terrain indices alone
   map transport potential, not CSAs.
5. **Site practices from the layers,** then check each candidate on imagery and, where
   possible, with the landowner or conservation-authority staff. Report the threshold and
   parameter values used, because the number and location of candidate sites depend on them.
6. **Remote sensing** for crop cover, residue and cover crops: follow
   [references/gee-recipes.md](references/gee-recipes.md) (Python Earth Engine API).
   Validate classifications with ground or agency data and report accuracy with a
   confusion matrix, not only overall accuracy.

## Assumptions block (top of every script and report)

```
CRS: EPSG:#### (name); horizontal units m; vertical units m (source-confirmed?)
DEM: source, acquisition year, resolution (m), DTM vs DSM, hydro-conditioning steps
Thresholds: flow-path initiation (ha), breach distance (cells), slope classes (degrees or %)
Imagery: sensor, collection ID, date range, cloud mask, scale (m) of export
```

## Things that go wrong

- Slope computed in a geographic CRS (degrees treated as metres) gives nonsense; the
  check step catches it.
- Mixing NAD83 and NAD83(CSRS) silently shifts data by up to about a metre in Ontario,
  which matters at 1 m LiDAR resolution.
- A single fixed flow-path threshold across fields of different slope and soil produces
  too many paths in some fields and too few in others; test sensitivity.
- Tile drainage and surface inlets reroute water underground; surface-only analysis
  misses this pathway (say so in reports).
- ACPF was built for US inputs (SSURGO soils, CDL crops); in Ontario the soil and crop
  inputs must be replaced (Ontario soil survey data, AAFC Annual Crop Inventory) and
  checked, not assumed equivalent.

## Code conventions

Python first, commented, reproducible: paths as arguments, parameters recorded with the
outputs (the run step writes `run_metadata.json`), CRS and units stated in docstrings.
For ArcGIS Pro use `arcpy` with environment settings (`arcpy.env.outputCoordinateSystem`,
`snapRaster`, `cellSize`) set explicitly; for QGIS, the WhiteboxTools plugin or
processing algorithms with the same parameters.

Sources with verified DOIs are in [references/terrain-methods.md](references/terrain-methods.md).
