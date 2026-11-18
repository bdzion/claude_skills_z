#!/usr/bin/env python3
"""Terrain and flow-path layers for field-scale precision conservation targeting.

Pipeline (WhiteboxTools, Lindsay 2016), written against the `whitebox` Python package v2:
  0. check the DEM: projected CRS in metres, cell size, nodata, extent (rasterio)
  1. optional: burn streams at road crossings (culverts) so embankments do not dam flow
  2. breach depressions with the least-cost method (Lindsay 2016 hybrid breach-fill)
  3. D8 pointer and D8 flow accumulation (specific contributing area, m2/m)
  4. slope (degrees)
  5. topographic wetness index (Beven & Kirkby 1979), stream power index and sediment
     transport index (Moore et al. 1991)
  6. stream / concentrated-flow-path extraction at a contributing-area threshold

What this does not capture: subsurface tile drainage. Surface flow paths on a DEM show
where overland flow and ephemeral gullies concentrate; in tile-drained fields much water
leaves through drains and surface inlets, so pair these layers with drainage maps and
field observation before calling an area "critical".

Status: step 0 is tested; the WhiteboxTools calls match the package's function
signatures but were not executed when this skill was built (the WhiteboxTools binary
could not be downloaded there). Run once on a small DEM and inspect the outputs before
relying on it.

Usage:
  python terrain_targeting.py check dem.tif
  python terrain_targeting.py run dem.tif --out outdir [--breach-dist 50]
         [--stream-threshold-ha 2] [--streams streams.shp --roads roads.shp --road-width 20]
  python terrain_targeting.py --selftest
Requires: rasterio (check), whitebox (run; first use downloads the WhiteboxTools binary).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def check_dem(path: str) -> dict:
    import rasterio
    with rasterio.open(path) as r:
        crs = r.crs
        info = dict(path=path, crs=crs.to_string() if crs else None, epsg=crs.to_epsg() if crs else None,
                    projected=bool(crs and crs.is_projected),
                    linear_units=(crs.linear_units if crs and crs.is_projected else None),
                    cell_size=r.res, width=r.width, height=r.height, nodata=r.nodata, dtype=r.dtypes[0],
                    bounds=tuple(round(b, 3) for b in r.bounds))
    problems = []
    if not info["projected"]:
        problems.append("CRS is geographic or missing: slope, area and flow accumulation need a projected CRS in metres (e.g. EPSG:2958 or 26917 in SW Ontario)")
    elif str(info["linear_units"]).lower() not in ("metre", "meter", "m"):
        problems.append(f"horizontal units are {info['linear_units']!r}, not metres")
    if abs(info["cell_size"][0] - info["cell_size"][1]) > 1e-6:
        problems.append("non-square cells")
    if info["nodata"] is None:
        problems.append("no nodata value set; edges may be treated as elevations")
    info["problems"] = problems
    info["vertical_units_note"] = "vertical units are not recorded in most GeoTIFFs; confirm metres from the data source"
    return info


def run(dem: str, out: str, breach_dist: int, threshold_ha: float, streams=None, roads=None, road_width=20.0):
    from whitebox import WhiteboxTools
    info = check_dem(dem)
    if info["problems"]:
        raise SystemExit("fix the DEM first:\n  - " + "\n  - ".join(info["problems"]))
    o = Path(out).resolve(); o.mkdir(parents=True, exist_ok=True)
    wbt = WhiteboxTools(); wbt.set_verbose_mode(False)
    p = lambda name: str(o / name)
    src = str(Path(dem).resolve())
    if streams and roads:
        wbt.burn_streams_at_roads(src, str(Path(streams).resolve()), str(Path(roads).resolve()), p("dem_burned.tif"), width=road_width)
        src = p("dem_burned.tif")
    wbt.breach_depressions_least_cost(src, p("dem_breached.tif"), dist=breach_dist, fill=True)
    wbt.d8_pointer(p("dem_breached.tif"), p("d8_pointer.tif"))
    wbt.d8_flow_accumulation(p("dem_breached.tif"), p("sca.tif"), out_type="specific contributing area")
    wbt.d8_flow_accumulation(p("dem_breached.tif"), p("contrib_area_m2.tif"), out_type="catchment area")
    wbt.slope(p("dem_breached.tif"), p("slope_deg.tif"), units="degrees")
    wbt.wetness_index(p("sca.tif"), p("slope_deg.tif"), p("twi.tif"))
    wbt.stream_power_index(p("sca.tif"), p("slope_deg.tif"), p("spi.tif"))
    wbt.sediment_transport_index(p("sca.tif"), p("slope_deg.tif"), p("sti.tif"))
    wbt.extract_streams(p("contrib_area_m2.tif"), p("flowpaths.tif"), threshold=threshold_ha * 10_000, zero_background=True)
    meta = dict(dem=info, breach_dist_cells=breach_dist, flowpath_threshold_ha=threshold_ha,
                culverts_burned=bool(streams and roads), units=dict(sca="m2/m", contrib_area="m2", slope="degrees"))
    (o / "run_metadata.json").write_text(json.dumps(meta, indent=2, default=str))
    print(f"outputs in {o}; parameters recorded in run_metadata.json")


def selftest() -> int:
    import tempfile

    import numpy as np
    import rasterio
    from rasterio.transform import from_origin
    d = tempfile.mkdtemp()
    z = (np.add.outer(np.arange(50), np.arange(50)) * 0.1).astype("float32")
    ok, bad = Path(d, "ok.tif"), Path(d, "geo.tif")
    with rasterio.open(ok, "w", driver="GTiff", width=50, height=50, count=1, dtype="float32",
                       crs="EPSG:2958", transform=from_origin(450000, 4800000, 2, 2), nodata=-9999) as w:
        w.write(z, 1)
    with rasterio.open(bad, "w", driver="GTiff", width=50, height=50, count=1, dtype="float32",
                       crs="EPSG:4617", transform=from_origin(-81.5, 43.3, 1e-5, 1e-5)) as w:
        w.write(z, 1)
    a, b = check_dem(str(ok)), check_dem(str(bad))
    assert a["projected"] and not a["problems"] and a["cell_size"] == (2.0, 2.0), a
    assert not b["projected"] and any("geographic" in x for x in b["problems"]) and any("nodata" in x for x in b["problems"]), b
    print("terrain_targeting selftest passed (DEM checks; WhiteboxTools steps not executed)")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--selftest", action="store_true")
    sub = ap.add_subparsers(dest="cmd")
    c = sub.add_parser("check"); c.add_argument("dem")
    r = sub.add_parser("run"); r.add_argument("dem"); r.add_argument("--out", required=True)
    r.add_argument("--breach-dist", type=int, default=50, help="maximum breach length in cells")
    r.add_argument("--stream-threshold-ha", type=float, default=2.0, help="contributing area (ha) at which a flow path starts")
    r.add_argument("--streams"); r.add_argument("--roads"); r.add_argument("--road-width", type=float, default=20.0)
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if a.cmd == "check":
        print(json.dumps(check_dem(a.dem), indent=2, default=str)); return 0
    if a.cmd == "run":
        run(a.dem, a.out, a.breach_dist, a.stream_threshold_ha, a.streams, a.roads, a.road_width); return 0
    ap.print_help(); return 2


if __name__ == "__main__":
    sys.exit(main())
