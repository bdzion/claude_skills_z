# Configuration keys (imWEBs-Python, commit 386a544)

Key names are those the code reads (`imWEBs/config/model_config.py`, `scenario_config.py`).
Where the user guide differs, the code name is used here and the guide name noted.
"Req." = the build fails or produces an incomplete model without it.

## Model configuration file

| Section | Key | Req. | Meaning |
|---|---|---|---|
| default | input_folder | yes | Folder holding every input file; all other file values are relative to it |
| watershed | dem_raster | yes | DEM GeoTIFF |
| watershed | soil_raster | yes | Soil GeoTIFF (ids mapped by soil_lookup) |
| watershed | landuse_raster | yes | Land-use GeoTIFF (ids mapped by landuse_lookup) |
| watershed | stream_shapefile | yes | Streams to burn into the DEM |
| watershed | boundary_shapefile | | Limits the watershed boundary |
| watershed | farm_shapefile | | Farms |
| watershed | field_shapefile | yes | Fields (the field is the management unit) |
| watershed | outlet_shapefile | | Read but not used by the current code |
| lookup | soil_lookup, landuse_lookup | yes | CSV: header row; column 1 project id, column 2 IMWEBs id |
| parameter | SoilLookup | | Custom soil parameter lookup (not in the user guide) |
| database | hydroclimate | yes | Hydroclimate SQLite database (STATIONS table + one table per data type) |
| reach_bmp | point_source_shapefile, flow_diversion_shapefile, reservoir_shapefile, wetland_boundary_shapefile, wetland_outlet_shapefile, manure_catch_basin_shapefile, grass_waterway_shapefile, access_management_shapefile, water_use_shapefile | | Reach BMP locations (see bmp-inputs.md) |
| structure_bmp | dugout_boundary_shapefile, riparian_buffer_shapefile, filter_strip_shapefile, tile_drain_boundary_shapefile, tile_drain_outlet_shapefile, wascob_shapefile | | Structural BMPs (guide also shows `tile_drain_shapefile`, `wascob_boundary_shapefile`, `wascob_outlet_shapefile`: not read) |
| non_structure_bmp | manure_feedlot_boundary_shapefile, manure_feedlot_outlet_shapefile, manure_storage_boundary_shapefile, offsite_watering_shapefile | | Non-structural BMPs |
| manure_adjustment_bmp | manure_adjustment_incorporation_within_48h_shapefile, _application_setback_, _no_application_on_snow_, _spring_rather_than_fall_, _based_on_n_limit_, _based_on_p_limit_shapefile | | Polygons; cell engine only |
| reservoir | reservoir_flow_routing | if reservoirs | RAT_RES, MDO_RES, MMO_RES, AAR_RES or TRR_RES |
| reservoir | reservoir_flow_data_folder | for RAT/MDO/MMO | Folder of external CSVs |
| delineation | stream_threshold_area_ha | yes (float) | Stream initiation area |
| delineation | use_all_pour_points_from_stream_threshold | | If false, a 200 ha threshold is used for pour points |
| delineation | wetland_min_area_ha | yes (float) | Wetlands smaller than this are ignored |
| marginal_crop_land | marginal_crop_land_simulation, _shapefile, _non_agriculture_landuse_ids, _buffer_size_m, _slope_threshold_percentage, _grass_type | | Guide shows `marginal_crop_shapefile` and unprefixed names: not read |
| pasture_crop_land | pasture_crop_land_simulation, _shapefile, _landuse_ids, _grass_type | | Guide shows `[pasture_land]` and `pasture_crop_shapefile`: not read |
| crop_rotation | method | | `crop_inventory` only |
| crop_rotation | AAFC_crop_inventory_folder, first_year, last_year | | `<year>.tif` files, clipped, project CRS |
| crop_rotation | include_grazing | | Default false |
| model | model_folder | yes | Output project folder (must match the scenario file) |

## Scenario configuration file

| Section | Key | Req. | Meaning |
|---|---|---|---|
| model | model_folder | yes | Same as in the model file |
| scenario | name | yes | Sub-folder created in model_folder |
| scenario | model_type | yes | `cell` or `subarea` |
| scenario | interval | yes | `daily` or `hourly` |
| scenario | start_date, end_date | | yyyy-mm-dd; empty = hydroclimate database range |
| climate_station | P, T, RM, SR, WS, WD | | Comma-separated STATIONS ids; empty = all stations (recommended); T covers TMIN and TMAX |
| climate_interpolation | method | yes | average_uniform, grid_interpolation, inverse_distance, linear_triangle, thiessen_polygon |
| climate_interpolation | radius | | Search radius for interpolation methods that use one (not in the user guide) |
