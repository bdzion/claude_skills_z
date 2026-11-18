# Earth Engine recipes (Python API)

These are templates: run them in an authenticated Earth Engine session, check each
collection ID against the current Earth Engine catalogue, and print the image count and
date range before trusting a composite.

```python
import ee
ee.Initialize(project="YOUR-CLOUD-PROJECT")  # assumption: a registered EE project

aoi = ee.FeatureCollection("projects/YOUR-CLOUD-PROJECT/assets/watershed").geometry()
CRS, SCALE = "EPSG:2958", 10  # NAD83(CSRS) / UTM 17N, metres; Sentinel-2 10 m bands

def mask_s2_scl(img):
    """Keep vegetation, bare soil, water (SCL 4, 5, 6); drop cloud, shadow, snow."""
    scl = img.select("SCL")
    keep = scl.eq(4).Or(scl.eq(5)).Or(scl.eq(6))
    return img.updateMask(keep).divide(10000).copyProperties(img, ["system:time_start"])

s2 = (ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
      .filterBounds(aoi)
      .filterDate("2025-10-15", "2025-12-15")   # post-harvest window for cover/residue
      .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 60))
      .map(mask_s2_scl))
print("images:", s2.size().getInfo())

def indices(img):
    ndvi = img.normalizedDifference(["B8", "B4"]).rename("NDVI")     # green cover
    ndti = img.normalizedDifference(["B11", "B12"]).rename("NDTI")   # crop residue
    return img.addBands([ndvi, ndti])

comp = s2.map(indices).median().clip(aoi)

# Crop type context from the AAFC Annual Crop Inventory (30 m; check the year exists)
aci = (ee.ImageCollection("AAFC/ACI").filterDate("2025-01-01", "2025-12-31").first()
       .select("landcover"))

task = ee.batch.Export.image.toDrive(
    image=comp.select(["NDVI", "NDTI"]), description="cover_residue_2025",
    region=aoi, crs=CRS, scale=SCALE, maxPixels=1e10)
task.start()
```

Notes
- Always set `crs` and `scale` on exports and on `reduceRegion`; Earth Engine otherwise
  picks defaults that differ between calls.
- Cover-crop detection needs a post-harvest and an early-spring window; snow cover in
  Ontario winters removes many dates, so report how many clear observations each field had.
- Thresholds on NDVI or NDTI for "cover crop present" or "residue > 30 %" must be
  calibrated against field observations for the region and year; do not reuse thresholds
  from other studies without checking.
- Landsat 8/9 Collection 2 Level-2 (`LANDSAT/LC08/C02/T1_L2`, `LANDSAT/LC09/C02/T1_L2`)
  needs the scale factors 0.0000275 and −0.2 for surface reflectance.
