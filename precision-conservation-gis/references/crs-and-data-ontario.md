# CRS and data conventions for southern Ontario

## Coordinate reference systems
| Use | EPSG | Name |
|---|---|---|
| Field to watershed analysis, Lake Huron and Lake Erie basins (about 84°W–78°W) | 2958 | NAD83(CSRS) / UTM zone 17N |
| Same, for data delivered in plain NAD83 | 26917 | NAD83 / UTM zone 17N |
| Province-wide maps and areas | 3161 | NAD83 / Ontario MNR Lambert |
| National products (Statistics Canada, some AAFC layers) | 3347 | NAD83 / Statistics Canada Lambert |
| Geographic storage only | 4617 / 4269 | NAD83(CSRS) / NAD83 |

Rules: check each input's CRS on load; reproject vectors to the raster's CRS (not the
reverse) to avoid resampling elevation; use bilinear resampling for continuous rasters
and nearest-neighbour for categorical ones; record the datum transformation used between
NAD83 and NAD83(CSRS).

## Data sources to confirm before use
Availability, licences and URLs change, so confirm the current source and record the
version and access date:
- Provincial LiDAR-derived DTMs (Ontario Elevation Mapping Program, distributed through
  Land Information Ontario / Ontario GeoHub).
- Ontario Hydro Network watercourses and waterbodies; Ontario Road Network.
- Soils: Ontario soil survey data (OMAFA / Canadian Soil Information Service).
- Crops: AAFC Annual Crop Inventory (30 m, annual; also in Earth Engine as `AAFC/ACI`).
- Tile drainage: OMAFA Agricultural Information Atlas tile drainage areas (coverage is
  incomplete; unmapped does not mean undrained).
- Flow and water quality: Water Survey of Canada (HYDAT), Provincial (Stream) Water
  Quality Monitoring Network, conservation-authority networks.
