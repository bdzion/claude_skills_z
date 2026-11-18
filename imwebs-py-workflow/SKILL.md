---
name: imwebs-py-workflow
description: Build IMWEBs (imWEBs) watershed model projects with the imWEBs-Python package (pip install imwebs) — writing and checking the model and scenario INI configuration files, preparing DEM, soil, land-use, stream and field inputs and lookup tables, BMP shapefiles and their required attributes (reservoirs, wetlands, tile drains, WASCoBs, buffers, filter strips, feedlots, manure storage), AAFC crop-inventory crop rotations, hydroclimate database format, climate stations and interpolation, and running delineate_watershed, generate_parameters, update_crop_rotation, generate_scenario and generate_subarea_parameter_database. Use whenever the user sets up or debugs an IMWEBs model build in Python, edits an imwebs_config INI, or asks why a BMP or input was not picked up, even if they only paste an error from the package.
---

# IMWEBs model building with imWEBs-Python

The imWEBs-Python package (University of Guelph, MIT licence; source
github.com/hawklorry/imWEBs-Python) turns GIS inputs and two INI files into a ready-to-run
IMWEBs project: delineation, parameter rasters and HDF5, BMP database, crop rotations,
scenario folder, and the subarea parameter database. This skill was written against
commit 386a544 (package version 0.0.40); check the installed version before relying on
key names.

## The one thing to know first

The package reads its INI files with `ConfigParser` and, for any key it cannot find,
**logs a warning and continues**. A misspelt or outdated key therefore silently drops an
input or a BMP. The user guide and the repository's own example INI use several names
the code does not read (e.g. `wascob_boundary_shapefile`, `tile_drain_shapefile`,
`[pasture_land]`). Always run the checker before a build:

```
python scripts/check_config.py model.ini scenario.ini
python scripts/check_config.py --template model > model.ini     # all valid keys, empty
```

It reports unknown keys (with the likely intended name), missing required keys, missing
files, missing or mis-cased BMP attribute fields and duplicate ids (read from the .dbf, no
GIS libraries needed), raster CRS/resolution/extent mismatches (when rasterio is
installed), and missing crop-inventory years. Run `--selftest` once in a new environment.

## Workflow

1. **Environment.** Windows (the package calls bundled `imWEBsH5.exe` and the .NET
   `ImwebsSubarea.Input.CLI.exe`), .NET Runtime 9, Python ≥ 3.9 in its own environment,
   `pip install imwebs` (pins whitebox_workflows 1.3.2). Set up logging at INFO before
   running so the "NOT FOUND" warnings are visible.
2. **Prepare inputs** in one `input_folder`: GeoTIFF rasters with identical CRS,
   resolution and extent; shapefiles in the same CRS with a unique `id` column; soil and
   land-use lookup CSVs (first two columns: project id, IMWEBs id); the hydroclimate
   database in the current format (one STATIONS table plus one table per data type; older
   databases need `HydroClimateDatabase.migrate`, which modifies the file in place, so copy
   it first). See [references/config-reference.md](references/config-reference.md) and
   [references/bmp-inputs.md](references/bmp-inputs.md).
3. **Write the two INI files** from the templates and run the checker until it reports no
   errors. State the CRS (e.g. EPSG:2958 for southern Ontario), cell size and the
   delineation threshold in the run notes.
4. **Build**:
   ```python
   import logging; logging.basicConfig(level=logging.INFO)
   from imWEBs.imwebs import imWEBs
   m = imWEBs("model.ini", "scenario.ini")
   m.generate_all()   # delineate_watershed -> generate_parameters -> update_crop_rotation -> generate_scenario
   m.generate_subarea_parameter_database()   # subarea engine only; not part of generate_all
   ```
   Run the steps one at a time when debugging, and read the log after each.
5. **Inspect before simulating**: subbasin and subarea counts, the stream network against
   the observed streams, BMP locations against their subbasins, crop rotation tables for a
   few fields, and the generated `file.in` (dates, station counts). Then run the engine
   (see the imwebs-engine skill if installed).

## Known traps (from the code)

- WASCoB fields are `NormV` and `NormA` in the code; the user guide says `NormalV` and
  `NormalA`. Tile-drain elevation is `Elevation` (the guide shows `Eleation`).
- `stream_threshold_area_ha` and `wetland_min_area_ha` are read with `getfloat` and are
  required; `use_all_pour_points_from_stream_threshold` is read as text.
- Manure adjustment BMPs (21–26) are not supported by the subarea-based engine.
- Crop inventory GeoTIFFs must be named `<year>.tif`, clipped to the watershed and in the
  project CRS; every year from `first_year` to `last_year` must exist.
- Offsite watering must accompany grazing management; feedlot `cb` must exist in the
  catch-basin shapefile and `storatio` values must sum to 1.
- Reservoir routing methods RAT_RES, MDO_RES and MMO_RES need external CSV files named by
  the reservoir's `file` attribute in `reservoir_flow_data_folder`.

## Conventions

Python first, commented, with paths as variables at the top; record the package version,
INI files and checker output with each model build so the build can be reproduced.
