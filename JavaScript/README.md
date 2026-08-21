# JavaScript

# Terrain-Thermal Convergence Framework (TTCF)

**This is the as-submitted-to-Scientific-Reports state — currently in peer review.** A 2026-07-26 review (`suggestions_claude.md`) found that the submitted lapse-rate model is a broken regression (R²=0.011, not the R²=0.73 claimed in Methods) that produces a physically impossible result in Figure 3b. Fixed version, with corrected headline numbers, is in `../JavaScript_v2/` — see that README for what changed. The error has been disclosed to the journal (`editor_correction_letter.md`, sent to srep@nature.com 2026-07-26); awaiting their reply on how to submit the correction before touching this copy — see memory `project_javascript_paper.md` for current status.

This repository contains code and data for:

Edasi et al. (2026) – Terrain-Constrained Suitability in Specialty Agriculture

Part of the GeoGastronomy research program.
---

## Overview

JavaScript characterizes the environmental fingerprint of two historically distinct Hawaiian coffee regions — Kona and Kaʻu — using terrain, climate, satellite vegetation, and soil at 500m resolution. The pipeline identifies what makes each region distinct, where similar conditions exist elsewhere on the island, and how projected warming reshapes thermal suitability boundaries.

---

## Study Area

- **Location:** Big Island of Hawaiʻi — Kona and Kaʻu districts
- **Scale:** 385 labeled hexagonal cells (~54,000 m² each), 500m resolution
- **Farm coverage:** 674 coffee-farm polygons from the 2020 Hawaii Agricultural Land Use dataset
- **Baseline climate:** ERA5-Land
- **Forward projections:** NEX-GDDP-CMIP6 (SSP2-4.5 and SSP5-8.5, 2035 and 2045)

---

## Data Sources

| Source | Variables |
|--------|-----------|
| USGS 1m DEM | Elevation (mean/min/max/dev), slope, aspect (sin/cos), curvature, relief, distance to coast |
| Sentinel-2 via Google Earth Engine | NDVI median composite |
| ERA5-Land | Mean temperature, temperature range, GDD, cold months, annual precip, dry-season fraction, wind speed |
| NEX-GDDP-CMIP6 | ΔT and precipitation ratio per scenario and horizon |
| USDA gSSURGO (SSURGO) | Drainage order, restriction depth, AWC, pH, organic matter, sand/silt/clay %, CEC |

---

## Pipeline

### Data Wrangling (`data_wrangling/`)

| Notebook | Purpose |
|----------|---------|
| `00_region_polygon.ipynb` | Define study region; load 2020 Hawaii Agricultural Land Use shapefile; extract 674 coffee-farm polygons; buffer union preserves U-shape around Mauna Loa |
| `01_generate_grid.ipynb` | Subdivide region into 250m equal-area hexagonal grid; label cells by coffee-farm centroid overlap; EPSG:32604 (UTM Zone 4N) |
| `02_clip_dem.ipynb` | Extract and clip USGS 1m DEM to study area |
| `03_dem_features.ipynb` | Compute topographic feature set per cell |
| `04_ndvi.ipynb` | Sentinel-2 NDVI median composite via GEE |
| `05_climate.ipynb` | ERA5-Land climate variables: temperature, precipitation, GDD, dry-season fraction, wind |
| `06_soil_features.ipynb` | SSURGO soil properties per cell |
| `07_assemble_features.ipynb` | Join all layers; output: ~25 features × 385 coffee cells, pickled |
| `08_pkl_to_delta_csvs.ipynb` | Transform local NEX-GDDP pkl files into delta CSVs (ΔT, precip ratio) |
| `08_climate_projections.ipynb` | Blend ERA5 baseline + NEX-GDDP deltas into future climate feature pickles (2035, 2045) |

### Machine Learning (`ML/`)

| Notebook | Purpose |
|----------|---------|
| `01_model.ipynb` | Random Forest classifier (coffee vs. background) + PCA on the full feature set; regional distinctiveness metric; topographic and climate importance by district |
| `02_clustering.ipynb` | Per-region k-means (Kona K=3, Kaʻu K=2) on terrain, climate, soil, and NDVI; elbow + silhouette K selection; radar plot cluster profiles |
| `03_ndvi_regression.ipynb` | Predict NDVI median separately per region; feature importance comparison — Kaʻu (dry) emphasizes moisture proxies, Kona (wet) emphasizes elevation and aspect |
| `04_similarity_search.ipynb` | Environmental analog finder: locate island cells most similar to Kona/Kaʻu in terrain-climate-soil space; expansion suitability and topographic identity maps |
| `05_forward_projection.ipynb` | Thermal suitability under NEX-GDDP warming scenarios; ensemble ΔT of +1.00°C (2035) and +1.35°C (2045); separate projections for Kona and Kaʻu |

---

## Key Findings

- **Kona thermal optimum:** 18.4°C (σ = 1.4°C)
- **Kaʻu thermal optimum:** 19.9°C (σ = 2.2°C)
- **PCA climate variance explained:** Kona 24%, Kaʻu 40%
- Under projected warming, Kona's thermal window contracts upslope; Kaʻu's expands

---

## Structure

```
JavaScript/
├── README.md
├── data_wrangling/                 — numbered ingestion pipeline (00–08)
├── ML/                             — model notebooks (01–05)
├── data/
│   ├── climate_projections/        — NEX-GDDP delta CSVs and future feature pickles
│   └── raw/                        — DEM, soil, and other source data
└── img/                            — generated figures (300 dpi for publication)
```

---

## Environment

Python 3.10+. Key dependencies: `geopandas`, `rasterio`, `earthengine-api`, `scikit-learn`, `pandas`, `numpy`, `matplotlib`.

Google Earth Engine authenticated session required for `04_ndvi.ipynb`.
