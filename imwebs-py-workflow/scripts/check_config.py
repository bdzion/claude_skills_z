#!/usr/bin/env python3
"""Check imWEBs-Python model and scenario configuration files before a run.

Why: the package reads its two INI files with ConfigParser and, for any key it does not
find, logs a warning and carries on, so a misspelt or outdated key silently drops that
input or BMP. Several key names in the user guide and in the repository's own example
INI differ from the names the code reads. This checker compares the files with the keys
the code accepts (hawklorry/imWEBs-Python, commit 386a544, package version 0.0.40) and
checks what it can without running the package:

  * unknown keys and sections (usually typos or names from older docs),
  * required keys that are missing or empty,
  * input files that do not exist under input_folder,
  * BMP shapefile attribute fields (read from the .dbf header, no GIS libraries needed),
    including case mismatches and duplicate ids,
  * raster CRS, resolution and extent agreement (only when rasterio is installed),
  * crop inventory files named <year>.tif for every year in first_year..last_year.

Usage:
  python check_config.py model.ini [scenario.ini]
  python check_config.py --template model > model_template.ini     (or: scenario)
  python check_config.py --selftest
Exit status 1 when an error is found; warnings alone exit 0.
"""
from __future__ import annotations

import argparse
import configparser
import os
import struct
import sys

# Keys read by imWEBs/config/model_config.py and scenario_config.py (commit 386a544).
MODEL_KEYS = {
    "default": ["input_folder"],
    "watershed": ["dem_raster", "soil_raster", "landuse_raster", "stream_shapefile", "boundary_shapefile",
                  "farm_shapefile", "field_shapefile", "outlet_shapefile"],
    "lookup": ["soil_lookup", "landuse_lookup"],
    "parameter": ["SoilLookup"],
    "database": ["hydroclimate"],
    "reach_bmp": ["point_source_shapefile", "flow_diversion_shapefile", "reservoir_shapefile",
                  "wetland_boundary_shapefile", "wetland_outlet_shapefile", "manure_catch_basin_shapefile",
                  "grass_waterway_shapefile", "access_management_shapefile", "water_use_shapefile"],
    "structure_bmp": ["dugout_boundary_shapefile", "riparian_buffer_shapefile", "filter_strip_shapefile",
                      "tile_drain_boundary_shapefile", "tile_drain_outlet_shapefile", "wascob_shapefile"],
    "non_structure_bmp": ["manure_feedlot_boundary_shapefile", "manure_feedlot_outlet_shapefile",
                          "manure_storage_boundary_shapefile", "offsite_watering_shapefile"],
    "reservoir": ["reservoir_flow_routing", "reservoir_flow_data_folder"],
    "delineation": ["stream_threshold_area_ha", "use_all_pour_points_from_stream_threshold", "wetland_min_area_ha"],
    "marginal_crop_land": ["marginal_crop_land_simulation", "marginal_crop_land_shapefile",
                           "marginal_crop_land_non_agriculture_landuse_ids", "marginal_crop_land_buffer_size_m",
                           "marginal_crop_land_slope_threshold_percentage", "marginal_crop_land_grass_type"],
    "pasture_crop_land": ["pasture_crop_land_simulation", "pasture_crop_land_shapefile",
                          "pasture_crop_land_landuse_ids", "pasture_crop_land_grass_type"],
    "manure_adjustment_bmp": ["manure_adjustment_incorporation_within_48h_shapefile",
                              "manure_adjustment_application_setback_shapefile",
                              "manure_adjustment_no_application_on_snow_shapefile",
                              "manure_adjustment_spring_rather_than_fall_shapefile",
                              "manure_adjustment_based_on_n_limit_shapefile",
                              "manure_adjustment_based_on_p_limit_shapefile"],
    "crop_rotation": ["method", "AAFC_crop_inventory_folder", "first_year", "last_year", "include_grazing"],
    "model": ["model_folder"],
}
SCENARIO_KEYS = {
    "model": ["model_folder"],
    "scenario": ["name", "model_type", "interval", "start_date", "end_date"],
    "climate_station": ["P", "T", "RM", "SR", "WS", "WD"],
    "climate_interpolation": ["method", "radius"],
}
# Required non-empty values. Delineation floats are read with getfloat and raise if absent.
MODEL_REQUIRED = [("default", "input_folder"), ("watershed", "dem_raster"), ("watershed", "soil_raster"),
                  ("watershed", "landuse_raster"), ("watershed", "stream_shapefile"), ("watershed", "field_shapefile"),
                  ("lookup", "soil_lookup"), ("lookup", "landuse_lookup"), ("database", "hydroclimate"),
                  ("delineation", "stream_threshold_area_ha"), ("delineation", "wetland_min_area_ha"),
                  ("model", "model_folder")]
SCENARIO_REQUIRED = [("model", "model_folder"), ("scenario", "name"), ("scenario", "model_type"),
                     ("scenario", "interval"), ("climate_interpolation", "method")]
# Known renames: key used in older docs or examples -> key the code reads.
RENAMES = {
    "wascob_boundary_shapefile": "wascob_shapefile", "wascob_outlet_shapefile": "wascob_shapefile",
    "tile_drain_shapefile": "tile_drain_boundary_shapefile",
    "marginal_crop_shapefile": "marginal_crop_land_shapefile",
    "pasture_crop_shapefile": "pasture_crop_land_shapefile",
    "non_agriculture_landuse_ids": "marginal_crop_land_non_agriculture_landuse_ids (or pasture_crop_land_landuse_ids)",
    "buffer_size_m": "marginal_crop_land_buffer_size_m",
    "slope_threshold_percentage": "marginal_crop_land_slope_threshold_percentage",
}
SECTION_RENAMES = {"pasture_land": "pasture_crop_land"}
# Attribute fields the BMP classes require (field names as in the code; 'id' is checked for all BMP files).
BMP_FIELDS = {
    "tile_drain_boundary_shapefile": ["Depth", "Spacing", "Radius", "Elevation", "StartYear", "StartMon", "StartDay"],
    "wascob_shapefile": ["StartYear", "StartMon", "StartDay", "BermElev", "DeadV", "DeadA", "NormV", "NormA",
                         "MaxV", "MaxA", "MaxQ", "FieldID", "TdrainID"],
    "reservoir_shapefile": ["op", "sa_em", "v_em", "sa_pr", "v_pr", "file"],
    "point_source_shapefile": ["Operation", "TableName"],
    "manure_feedlot_boundary_shapefile": ["cb", "ani_id", "adult", "nonadult", "stoid", "storatio"],
    "manure_storage_boundary_shapefile": ["feedlot"],
}
RESERVOIR_METHODS = {"RAT_RES", "MDO_RES", "MMO_RES", "AAR_RES", "TRR_RES"}
INTERPOLATION = {"average_uniform", "grid_interpolation", "inverse_distance", "linear_triangle", "thiessen_polygon"}


def dbf_fields_and_ids(path):
    """Field names from a dBASE header, plus the values of an 'id' field if present."""
    with open(path, "rb") as fh:
        head = fh.read(32)
        n_rec, head_len, rec_len = struct.unpack("<IHH", head[4:12])
        fields, offset = [], 1
        while True:
            d = fh.read(32)
            if not d or d[0] == 0x0D:
                break
            name = d[:11].split(b"\x00")[0].decode("latin-1").strip()
            fields.append((name, offset, d[16])); offset += d[16]
        ids = None
        idf = [f for f in fields if f[0].lower() == "id"]
        if idf:
            _, off, length = idf[0]
            fh.seek(head_len); ids = []
            for _ in range(n_rec):
                rec = fh.read(rec_len)
                if len(rec) < rec_len:
                    break
                if rec[:1] == b"*":
                    continue
                ids.append(rec[off:off + length].decode("latin-1").strip())
    return [f[0] for f in fields], ids


def check(model_ini=None, scenario_ini=None):
    errors, warnings = [], []
    for path, keys, required, label in ((model_ini, MODEL_KEYS, MODEL_REQUIRED, "model"),
                                        (scenario_ini, SCENARIO_KEYS, SCENARIO_REQUIRED, "scenario")):
        if not path:
            continue
        cf = configparser.ConfigParser(); cf.optionxform = str  # keep case for reporting
        if not cf.read(path):
            errors.append(f"{label}: cannot read {path}"); continue
        for sec in cf.sections():
            if sec not in keys:
                hint = f" (the code reads [{SECTION_RENAMES[sec]}])" if sec in SECTION_RENAMES else ""
                warnings.append(f"{label}: section [{sec}] is not read by the package{hint}")
                continue
            valid = {k.lower(): k for k in keys[sec]}
            for opt in cf.options(sec):
                if opt.lower() not in valid:
                    hint = f"; did you mean {RENAMES[opt]}?" if opt in RENAMES else ""
                    (errors if cf.get(sec, opt).strip() else warnings).append(
                        f"{label}: [{sec}] {opt} is not a key the code reads, so its value is ignored{hint}")
        for sec, opt in required:
            if not cf.has_option(sec, opt) or not cf.get(sec, opt).strip():
                errors.append(f"{label}: required [{sec}] {opt} is missing or empty")
        if label == "model":
            _check_model_files(cf, errors, warnings)
        else:
            m = cf.get("climate_interpolation", "method", fallback="").strip()
            if m and m not in INTERPOLATION:
                errors.append(f"scenario: climate_interpolation method {m!r} not in {sorted(INTERPOLATION)}")
            mt = cf.get("scenario", "model_type", fallback="").strip().lower()
            if mt and mt not in ("cell", "subarea"):
                errors.append(f"scenario: model_type must be cell or subarea, not {mt!r}")
            iv = cf.get("scenario", "interval", fallback="").strip().lower()
            if iv and iv not in ("daily", "hourly"):
                errors.append(f"scenario: interval must be daily or hourly, not {iv!r}")
    if model_ini and scenario_ini:
        a, b = configparser.ConfigParser(), configparser.ConfigParser()
        a.read(model_ini); b.read(scenario_ini)
        if a.get("model", "model_folder", fallback="") != b.get("model", "model_folder", fallback=""):
            errors.append("model_folder differs between the model and scenario files")
    return errors, warnings


def _check_model_files(cf, errors, warnings):
    folder = cf.get("default", "input_folder", fallback="").strip()
    if folder and not os.path.isdir(folder):
        errors.append(f"model: input_folder does not exist: {folder}"); return
    rasters = {}
    for sec in ("watershed", "lookup", "parameter", "database", "reach_bmp", "structure_bmp",
                "non_structure_bmp", "manure_adjustment_bmp"):
        if not cf.has_section(sec):
            continue
        for opt in cf.options(sec):
            val = cf.get(sec, opt).strip()
            if not val or opt.lower() not in {k.lower() for k in MODEL_KEYS.get(sec, [])}:
                continue
            p = os.path.join(folder, val)
            if not os.path.exists(p):
                errors.append(f"model: [{sec}] {opt} = {val} not found in input_folder"); continue
            if opt.endswith("_raster"):
                rasters[opt] = p
            if opt.endswith("_shapefile") and sec != "watershed":
                dbf = os.path.splitext(p)[0] + ".dbf"
                if not os.path.exists(dbf):
                    warnings.append(f"model: {val}: no .dbf beside the shapefile; attributes not checked"); continue
                fields, ids = dbf_fields_and_ids(dbf)
                lower = {f.lower(): f for f in fields}
                for need in ["id"] + BMP_FIELDS.get(opt.lower(), []):
                    if need.lower() not in lower:
                        errors.append(f"model: {val}: required field '{need}' missing (has: {', '.join(fields)})")
                    elif need != "id" and lower[need.lower()] != need:
                        warnings.append(f"model: {val}: field '{lower[need.lower()]}' differs in case from '{need}' expected by the code")
                if ids is not None:
                    dup = sorted({i for i in ids if ids.count(i) > 1})
                    if dup:
                        errors.append(f"model: {val}: duplicate id values {dup[:10]}")
                    if any(i == "" for i in ids):
                        errors.append(f"model: {val}: empty id values")
    if cf.has_section("reservoir"):
        m = cf.get("reservoir", "reservoir_flow_routing", fallback="").strip()
        if m and m not in RESERVOIR_METHODS:
            errors.append(f"model: reservoir_flow_routing {m!r} not in {sorted(RESERVOIR_METHODS)}")
    if cf.has_section("crop_rotation") and cf.get("crop_rotation", "AAFC_crop_inventory_folder", fallback="").strip():
        d = cf.get("crop_rotation", "AAFC_crop_inventory_folder").strip()
        try:
            y0, y1 = int(cf.get("crop_rotation", "first_year")), int(cf.get("crop_rotation", "last_year"))
            missing = [y for y in range(y0, y1 + 1) if not os.path.exists(os.path.join(d, f"{y}.tif"))]
            if missing:
                errors.append(f"model: crop inventory files missing for years {missing[:12]} in {d} (files must be named <year>.tif)")
        except (ValueError, configparser.Error):
            errors.append("model: crop_rotation first_year and last_year must be integers")
    if len(rasters) > 1:
        try:
            import rasterio
        except ImportError:
            warnings.append("model: rasterio not installed; raster CRS, resolution and extent not compared"); return
        meta = {}
        for k, p in rasters.items():
            try:
                with rasterio.open(p) as r:
                    meta[k] = (r.crs.to_string() if r.crs else None, tuple(round(x, 6) for x in r.res), tuple(round(b, 3) for b in r.bounds))
            except Exception as e:  # noqa: BLE001 - report any unreadable raster
                errors.append(f"model: {k} could not be read as a raster ({e.__class__.__name__})")
        if len(meta) < 2:
            return
        ref_k, ref = next(iter(meta.items()))
        for k, m in meta.items():
            for i, what in enumerate(("CRS", "resolution", "extent")):
                if m[i] != ref[i]:
                    errors.append(f"model: {k} {what} {m[i]} differs from {ref_k} {ref[i]} (all rasters must match)")


def template(kind):
    keys = MODEL_KEYS if kind == "model" else SCENARIO_KEYS
    lines = []
    for sec, opts in keys.items():
        lines.append(f"[{sec}]")
        lines += [f"{o} = " for o in opts]
        lines.append("")
    return "\n".join(lines)


def selftest():
    import tempfile
    d = tempfile.mkdtemp(); data = os.path.join(d, "data"); os.makedirs(data)
    for f in ("dem.tif", "soil.tif", "landuse.tif", "stream.shp", "field.shp", "soil.csv", "landuse.csv", "hc.db3", "td.shp"):
        open(os.path.join(data, f), "wb").close()
    # a dBASE file with fields id, Depth, Spacing (others missing) and a duplicate id
    def write_dbf(path, fields, rows):
        rec_len = 1 + sum(w for _, w in fields)
        hdr = bytearray(32); hdr[0] = 3
        hdr[4:12] = struct.pack("<IHH", len(rows), 32 + 32 * len(fields) + 1, rec_len)
        body = bytearray()
        for name, w in fields:
            fd = bytearray(32); fd[:len(name)] = name.encode(); fd[11] = ord("C"); fd[16] = w; body += fd
        body += b"\r"
        recs = b"".join(b" " + b"".join(str(v).ljust(w).encode() for v, (_, w) in zip(r, fields)) for r in rows)
        open(path, "wb").write(bytes(hdr) + bytes(body) + recs + b"\x1a")
    write_dbf(os.path.join(data, "td.dbf"), [("id", 4), ("depth", 6), ("Spacing", 6)], [(1, 900, 15000), (1, 900, 15000)])
    model = os.path.join(d, "model.ini")
    open(model, "w").write(f"""[default]
input_folder = {data}
[watershed]
dem_raster = dem.tif
soil_raster = soil.tif
landuse_raster = landuse.tif
stream_shapefile = stream.shp
field_shapefile = field.shp
[lookup]
soil_lookup = soil.csv
landuse_lookup = landuse.csv
[database]
hydroclimate = hc.db3
[structure_bmp]
tile_drain_boundary_shapefile = td.shp
wascob_boundary_shapefile = wascob.shp
[pasture_land]
non_agriculture_landuse_ids =
[delineation]
stream_threshold_area_ha = 10
[model]
model_folder = {d}/model
""")
    scen = os.path.join(d, "scen.ini")
    open(scen, "w").write(f"[model]\nmodel_folder = {d}/model\n[scenario]\nname = base\nmodel_type = subarea\ninterval = daily\n[climate_interpolation]\nmethod = idw\n")
    errs, warns = check(model, scen)
    text = "\n".join(errs + warns)
    assert "wascob_boundary_shapefile is not a key" in text and "did you mean wascob_shapefile" in text, text
    assert "[pasture_land]" in text and "wetland_min_area_ha is missing" in text, text
    assert "required field 'Elevation' missing" in text and "differs in case from 'Depth'" in text, text
    assert "duplicate id values ['1']" in text and "method 'idw'" in text, text
    assert "rasterio" in text or "differs from" not in text
    assert template("scenario").startswith("[model]\nmodel_folder = ")
    print("check_config selftest passed")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("model_ini", nargs="?"); ap.add_argument("scenario_ini", nargs="?")
    ap.add_argument("--template", choices=["model", "scenario"]); ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if a.template:
        print(template(a.template)); return 0
    if not a.model_ini:
        ap.error("give the model INI (and optionally the scenario INI)")
    errs, warns = check(a.model_ini, a.scenario_ini)
    for e in errs:
        print("ERROR  ", e)
    for w in warns:
        print("warning", w)
    print(f"\n{len(errs)} error(s), {len(warns)} warning(s)")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
