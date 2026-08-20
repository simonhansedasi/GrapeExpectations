# GrapeExpectations v2 — PySpark Pipeline

Rebuilds the precision viticulture pipeline at native Sentinel-2 (10m) resolution.

## Resolution change
- **v1**: 1,000 m² hex tiles (~32m diameter), 3,598 tiles, sklearn
- **v2**: 100 m² hex tiles (~10m diameter, 1 Sentinel-2 pixel), ~36k tiles, PySpark + MLlib

## Prerequisites
```bash
sudo apt install -y openjdk-17-jdk   # PySpark requires Java 11+
```

**Memory gotcha (2026-08-19):** `spark.driver.memory` in notebooks 04b/05 was written on office (the desktop, more RAM). sbook (the laptop) has only 15GB total RAM — a driver heap request above ~10-12g on sbook can't be satisfied and crashes the whole Jupyter Lab process, not just the notebook. Check `free -h` before rerunning these on a different machine and size the config to what's actually free.

## Run order

| Notebook | Env | Description |
|---|---|---|
| `00_retile_polygons.ipynb` | Python 3.7 (Anaconda) | Tile polygons at 100 m² → `tiles_100m2.pkl` |
| `01_download_ndvi_gee.ipynb` | Python 3.7 (Anaconda) | GEE export to Drive (one task/year) |
| `02_terrain_features.ipynb` | Python 3.7 (Anaconda) | DEM zonal stats → `terrain_100m2.csv` |
| `03_soil_features.ipynb` | Python 3.7 (Anaconda) | SSURGO join → `soil_100m2.csv` |
| `04_spark_assemble.ipynb` | Python 3.10 (system) | Weekly aggregation + anomaly + feature join → Parquet |
| `05_spark_ml.ipynb` | Python 3.10 (system) | RF + GBT via MLlib + feature importances |

## Data flow
```
polygons/RegressionRidge_smol.geojson
    → 00 → polygons/tiles_100m2.pkl + tiles_100m2.geojson
    → 01 → data/ndvi/tiles_100m2/ndvi_100m2_YYYY.csv  (via Google Drive)
    → 02 → data/terrain_100m2.csv
    → 03 → data/soil_100m2.csv
    → 04 → data/spark/assembled/ (Parquet)
    → 05 → data/spark/models/ + feature_importances.png
```
