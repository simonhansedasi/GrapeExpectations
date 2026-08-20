# GrapeExpectations

Precision viticulture pipeline for predicting vineyard canopy health and frost risk at meter resolution across a Washington State wine production area.

---

## Overview

GrapeExpectations models per-cell NDVI — a proxy for vine canopy density and vigor — using 9 years of satellite imagery stacked with topographic, climate, and soil features. The target is a spatially explicit, annually updated picture of vineyard performance that can inform block-level management decisions.

A companion analysis identifies frost risk zones using topographic position, elevation deviation, and NDVI history.

**Key result:** Stacked ensemble (RF + ExtraTrees + GBM + XGBoost + KNN → ElasticNetCV) achieves random-split test R² = 0.9323, RMSE = 0.0229 NDVI units, across 8 harvest-window weeks (ISO 36–43). LOYO validation mean R² = 0.353 ± 0.114 across 10 vintages. Terrain accounts for 75.5% of SHAP attribution.

**Paper:** `RegressionRidge/paper.tex` — full draft with 14 figures, submitted target: *Precision Agriculture* (Springer).

---

## Study Area

- **Location:** Washington State wine country, USA
- **Scale:** 3,598 equal-area hexagonal cells, ~1,000 m² each
- **Temporal coverage:** 2016–2025 (9 growing seasons)

---

## Data Sources

| Source | Variables |
|--------|-----------|
| USGS 1m DEM | Elevation, slope, aspect, curvature, relief |
| Sentinel-2 via Google Earth Engine | NDVI, EVI, NDWI, SAVI, RENDVI, MCARI2 — daily composites |
| PRISM daily weather | Tmin, Tmax, precipitation, VPD |
| USGS gSSURGO | Sand/silt/clay %, AWC, CEC, organic matter, pH, EC |

---

## Pipeline

### Data Wrangling (`RegressionRidge/data_wrangling/`)

| Notebook | Purpose |
|----------|---------|
| `00_subsample_polygons.ipynb` | Convert vineyard block KML polygons into flat-top hexagonal cells; remove slivers |
| `01_clip_dem.ipynb` | Clip USGS 1m DEM to vineyard extent; reproject to UTM Zone 10 |
| `02_breakdown_dem.ipynb` | Extract topographic features: elevation, slope, aspect (cos/sin), curvature (profile/plan/total), relief, local relief |
| `03_get_temp_data.ipynb` | Ingest PRISM daily weather for 9 years; zip extraction, clipping, file cleanup |
| `04-2_ndvi_smol.ipynb` | Pull Sentinel-2 spectral indices via GEE; 9 years of daily imagery aggregated to phenological windows |
| `05_soil.ipynb` | Integrate gSSURGO soil properties per hexagonal cell |
| `06_assemble_data.ipynb` | Join all feature layers; output: 100+ features × 32,382 rows (cells × years), pickled |

### Machine Learning (`RegressionRidge/ML/`)

| Notebook | Purpose |
|----------|---------|
| `forest_ensemble.ipynb` | Stacked ensemble: RF + ExtraTrees + GBM + XGBoost + KNN → ElasticNetCV meta-learner; multi-output NDVI regression across weeks 36–43 |
| `clustering.ipynb` | GBM leaf embeddings → PCA → k-means (3 management zones) |
| `time_series.ipynb` | Per-plot OLS on NDVI trajectory; anomaly detection |
| `linear_regression.ipynb` | Ridge/Lasso baseline models |
| `decision_trees.ipynb` | Decision tree exploration |
| `neural_net.ipynb` | MLP regression variants |
| `LSTM.ipynb` | Sequence model on temporal NDVI |
| `regression.ipynb` | Additional regression experiments |

### Frost Risk

| Notebook | Purpose |
|----------|---------|
| `assess_frost_risk.ipynb` | Composite frost risk raster combining slope, elevation deviation from local mean, NDVI, and cell area |

---

## Structure

```
GrapeExpectations/
├── README.md
├── CONTEXT.md                      — detailed architecture and data specification
├── RegressionRidge/
│   ├── paper.tex                   — manuscript (full draft, 14 figures, target: Precision Agriculture)
│   ├── references.bib              — bibliography
│   ├── img/                        — all figure files (~30 PNGs)
│   ├── data_wrangling/             — numbered ingestion pipeline (00–06)
│   ├── ML/                         — model notebooks (forest_ensemble, clustering, SHAP, etc.)
│   └── data/                       — pickled DataFrames and raw raster subdirs (~5.5 GB)
├── assess_frost_risk.ipynb
├── sensing/                        — fiber-optic sensor deployment notebooks
├── experiments/                    — experimental analysis
└── docs/                           — grant materials, DTS fiber-optic proposal (TeX)
```

---

## BI + GIS dashboard / static & animated maps (`powerbi_dashboard/`)

Side deliverable built on the v2 100 m² grid (33,028 cells post hex-grid fix, 2026-08-19), separate from the paper pipeline — job-market tool practice (BI + GIS), not part of the manuscript.

**This is a different model from the paper's v1 result above.** The v2 grid trains its own RF + GBT ensemble in `RegressionRidge/spark_pipeline/05_spark_ml.ipynb` — GBT test R² = 0.8950, RMSE = 0.03164 (the number on the public site), vs. the v1 stacked ensemble's R² = 0.9323 quoted above for the paper. Different grid resolution, different feature set, not directly comparable.

| File | What it produces |
|------|-------------------|
| `export_powerbi.py` | Star-schema CSV export (`dim_cells`, `dim_years`, `fact_ndvi_yearly`) for Power BI / Looker Studio / Tableau. `dim_cells` includes both raw terrain scalars and their vector decomposition (`slope_x`/`slope_y`/`aspect_cos`/`aspect_sin`/`profile_curv_mean`/`plan_curv_mean`) plus 10-year-average phenology rates (`buildup_rate_mean`/`decline_rate_mean`); `fact_ndvi_yearly` carries the per-year detail behind those averages (`buildup_rate`/`decline_rate` at cell×year grain) |
| `export_qgis.py` | GeoPackage export (`grapeexpectations.gpkg`) — real hex polygon geometry + terrain + NDVI trend, for QGIS |
| `HOW_TO_LOAD.md` | Looker Studio loading walkthrough (Power BI Service needs a work email; this project uses Looker Studio instead), plus a Tableau note (parked — no Linux desktop client) |
| `HOW_TO_LOAD_QGIS.md` | QGIS loading + graduated-symbology walkthrough |
| `canopy_trend_map.py` | Static PNG: 2024 canopy build-up (bud break to pre-harvest peak) |
| `harvest_decline_map.py` | Static PNG: 2024 harvest-window decline |
| `ndvi_season_gif.py [year]` | Animated GIF: NDVI through one growing season, real satellite dates |
| `_mapping.py` | Shared geometry/color helpers used by all map scripts |

Run any script directly from `powerbi_dashboard/` — each reads straight from `RegressionRidge/data/`. See `CONTEXT.md` for the full writeup, including a data-quality note on three cloud-contaminated 2024 NDVI dates and a warning that `ML/clusters.csv` predates the v2 regrid and should not be joined to current data.

## Public report site (`site/`)

Static page at `grape-expectations.simonhansedasi.com` — a full report tying together three branches: §1 Pipeline (ingestion, feature engineering, model training/evaluation, spatial residual diagnostics — the ML side), §2 GIS (QGIS export + toggle between two graduated-symbology maps + matplotlib fallback), §3 BI (Looker Studio walkthrough + star-schema CSV downloads). Deploy with `site/deploy_hetzner.sh` (rsyncs to the Hetzner box, no DNS change needed — `*.simonhansedasi.com` is already wildcarded there, and `.ipynb_checkpoints/` is excluded from the sync). `site/nginx_grape_expectations.conf` is a reference config; the live server block's cert directives should be copied from an already-working simonhansedasi.com subdomain rather than assumed from this file.

**Live and current as of 2026-08-19** — https://grape-expectations.simonhansedasi.com, all data/images on the corrected 33,028-cell grid, §1's model-report figures (actual-vs-predicted, spatial residuals, both models' feature importances) generated fresh the same day. Re-run `site/deploy_hetzner.sh` for content updates; nginx/cert are already provisioned. §3 (BI/Looker) is still being actively written — check CONTEXT.md before assuming it's finished.

**Idea for later (not built): three-column layout.** Simon wants the three branches (§1/§2/§3) side by side instead of stacked vertically, so a visitor doesn't have to scroll past the whole pipeline report to reach GIS or BI. Not started.

---

## Environment

Python 3.10+. Key dependencies: `geopandas`, `rasterio`, `earthengine-api`, `scikit-learn`, `xgboost`, `pandas`, `numpy`.

Google Earth Engine authenticated session required for `04-2_ndvi_smol.ipynb`.
