# BMP inputs (imWEBs-Python, commit 386a544)

Every BMP shapefile needs a unique `id` column (case-insensitive). Attribute names below
are the names the code checks; where the user guide differs, the code wins.

| BMP (code) | INI key | Geometry | Required attributes |
|---|---|---|---|
| Point source (1 PTSR) | reach_bmp.point_source_shapefile | point | `Operation` (yyyy-mm-dd), `TableName` (hydroclimate table with DATE, FLOW, SEDIMENT, ORGANICN, ORGANICP, NO3, NH3, NO2, MINERALP) |
| Reservoir (3 RESV) | reach_bmp.reservoir_shapefile | point | `op` (yyyy-mm-dd), `sa_em`, `v_em` (emergency area, volume), `sa_pr`, `v_pr` (principal), `file` (external CSV name without extension) |
| Riparian buffer (5 RIBUF) | structure_bmp.riparian_buffer_shapefile | polygon | id |
| Grassed waterway (6 GWW) | reach_bmp.grass_waterway_shapefile | polyline | id |
| Vegetation filter strip (7 VFST) | structure_bmp.filter_strip_shapefile | polygon | id |
| Isolated wetland (9 ISWET) | reach_bmp.wetland_boundary_shapefile (+ optional wetland_outlet_shapefile) | polygon (+ point) | id; filtered by delineation.wetland_min_area_ha |
| Crop, tillage, fertilizer, grazing management (12, 14–16) | crop_rotation section | AAFC crop inventory rasters | Optional custom crop-lookup.csv and default management CSVs in the inventory folder |
| Tile drain (19 TLDMG) | structure_bmp.tile_drain_boundary_shapefile (+ tile_drain_outlet_shapefile) | polygon (+ point) | `Depth` (mm, invert), `Spacing` (mm), `Radius` (mm), `Elevation` (m), `StartYear`, `StartMon`, `StartDay` |
| Manure adjustments (21–26) | manure_adjustment_bmp.* | polygon | id; not supported by the subarea engine |
| Manure storage (27 MSCD) | non_structure_bmp.manure_storage_boundary_shapefile | polygon | `feedlot` (contributing feedlot id) |
| Manure catch basin (28 MCBI) | reach_bmp.manure_catch_basin_shapefile | point | id |
| Manure feedlot (29 FDLT) | non_structure_bmp.manure_feedlot_boundary_shapefile + manure_feedlot_outlet_shapefile | polygon + point | `cb` (catch-basin id that exists), `ani_id` (livestock parameter id), `adult`, `nonadult`, `stoid` (storage ids, comma-separated), `storatio` (ratios summing to 1); outlet id = feedlot id |
| Marginal crop land (30–32) | marginal_crop_land.* | polygon or generated | `marginal_crop_land_simulation = YES` to enable |
| Pasture crop land (34–36) | pasture_crop_land.* | polygon or generated | `pasture_crop_land_simulation = YES` to enable |
| Offsite watering (39 OFSW) | non_structure_bmp.offsite_watering_shapefile | point | id; required when grazing management is used |
| WASCoB (41 WSCB) | structure_bmp.wascob_shapefile | point | `StartYear`, `StartMon`, `StartDay`, `BermElev` (m), `DeadV`, `NormV`, `MaxV` (10^4 m³), `DeadA`, `NormA`, `MaxA` (ha), `MaxQ` (m³/day), `FieldID`, `TdrainID` (must exist in the tile-drain shapefile) |

BMP type codes: 1 reach, 2 areal structural, 3 areal non-structural, 4 manure adjustment.
