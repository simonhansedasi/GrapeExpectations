# KushCountry

## Environmental Stratification — Cannabis Case Study, Benchmarked Against Simpler Baselines

Part of the [GeoGastronomy](../) research program. **Target journal: undecided** (was Precision Agriculture/Springer; open per 2026-07-26 decision — see CONTEXT.md).

---

## What this is

Environmental stratification — unsupervised clustering of terrain, climate, soil, and satellite-derived canopy data into landscape archetypes, evaluated post-hoc against literature agronomic envelopes — applied to outdoor cannabis cultivation in California's Emerald Triangle. This is **not** a novel method; it's a 40+ year old technique (ecoregionalization, land classification) applied to a crop with no labeled training data, since California's Department of Cannabis Control withholds all cultivator coordinates by policy.

**The paper's honest finding, as of 2026-07-26:** the clustering-derived suitability zone does **not** clearly outperform two much simpler baselines (a univariate GDD threshold, and an expert-weighted multicriteria/MCDA score) on independent enforcement-record validation. The GDD threshold beats clustering on lift and recall; MCDA roughly ties on lift with much better recall. This is now the paper's central, foregrounded methodological finding, not a buried caveat — see `suggestions_pete.md` and `suggestions_claude.md` for the external review that triggered the full rebuild, and CONTEXT.md for the blow-by-blow.

The old framing (**"Unsupervised Terrain Fingerprinting (UTF)," a named six-step "framework"**) has been dropped entirely per an explicit decision on 2026-07-26, once the baseline comparison showed clustering wasn't earning its complexity. Do not reintroduce "UTF" branding without a new explicit decision — it isn't just a naming preference, it materially overclaimed what the pipeline does relative to `writing/paper.tex`'s current related-work framing.

---

## Study Area

Humboldt, Mendocino, and Trinity Counties, California — the Emerald Triangle. The established US outdoor cannabis appellation and the most climatically diverse three-county region in the state.

- EPSG:32610 (UTM Zone 10N) throughout
- 8,900 hexagonal cells at 2 km spacing (true area 3.4641 km²/cell — verify against actual polygon geometry, not a formula assumption, if this ever needs recomputing; an earlier draft used 3.29 km²/cell and got every area figure in the paper wrong)
- Study extent from US Census TIGER 2023 county boundaries

---

## Pipeline

### Data Wrangling

| Notebook | What it does |
|----------|-------------|
| `00_study_area.ipynb` | Downloads Census TIGER county shapefile; filters to Emerald Triangle; saves county polygons + 2 km buffered study extent |
| `01_generate_grid.ipynb` | Generates 2 km hexagonal grid (8,900 cells) clipped to study extent |
| `02_clip_dem.ipynb` | Downloads 1 arc-second USGS DEM tiles via TNM API; deduplicates by vintage; mosaics with GDAL VRT; warps to UTM 10N |
| `03_dem_features.ipynb` | Zonal stats per cell: elevation (mean/max/std), slope, aspect (cos/sin), relief |
| `04_ndvi.ipynb` | Sentinel-2 SR via Google Earth Engine; July–October composite 2022–2024; ndvi_std (spatial heterogeneity proxy) |
| `05_climate.ipynb` | GEE Daymet V4 (NASA/ORNL); derives tmean, VPD, frost-free days, GDD (base 10°C), annual precip |
| `06_soil_features.ipynb` | SoilGrids ISRIC WCS 2.0.1; 6 variables × 3 depths → depth-weighted averages; warped to UTM |
| `07_assemble_features.ipynb` | Joins all layers on cell_id; median-imputes edge NaNs; StandardScaler normalization; saves feature matrix |

### Machine Learning

| Notebook | What it does |
|----------|-------------|
| `01_model.ipynb` | PCA on scaled features; synthetic RF task (real vs shuffled) for permutation importance; PC1 = coast–interior gradient (59.2% of variance among 6 kept PCs) |
| `02_clustering.ipynb` | K-means on StandardScaler-equalized PC scores; K=7; cluster 0 = cannabis archetype (GDD 1395, VPD 1568, elev 527m, pH 5.84); dissolves to suitability zone (1,924 cells, ~6,665 km², 22.2% of study area). Also tests whitened vs. unwhitened clustering: ARI=0.456, confirming the whitening choice materially changes the partition rather than being cosmetic. |
| `03_ndvi_regression.ipynb` | RF regressor within cluster 0; target ndvi_std; random 5-fold CV R²=0.650±0.043, **spatial block CV (10km blocks) R²=0.601±0.037** (8% relative drop, real but not devastating). Slope dominant (marginal importance 0.59, **conditional importance 0.43** after accounting for its correlation with relief), pH second (0.39 marginal / 0.34 conditional). Ranking is stable under conditioning; magnitudes are not. |
| `04_subclustering.ipynb` | Sub-clusters cluster 0 (labeled **S0–S5** in the paper, not C0–C5, to avoid colliding with the main 0–6 cluster numbers) using features weighted by ML/03 importance; K=6; prime stratum S0 = 714 cells (pH 6.02, slope 19.0°, VPD 1624 Pa, ~2,473 km²) |
| `05_validation.ipynb` | **Superseded by `08_validation_rebuild.ipynb`** — the original had a parcel-join bug (point-in-polygon boundary double-matching) and an APN-extraction regex bug (only matched 4-segment APNs, missing common 3-segment formats). Kept for history; do not cite its numbers. |
| `06_robustness.ipynb` | K sensitivity (K=4–7, archetype 4/4 criteria at all K); bootstrap ARI (mean=0.974, n=50, confirmed run at K=7 despite stale "K=5" comments that have since been fixed); feature ablation **now scored against external enforcement lift/recall, not just internal ARI-vs-full-stack** (that internal comparison is tautological for the full stack); Cramér's V, now computed on the corrected 135-parcel validation set |
| `07_baselines.ipynb` | **New.** Decision-gate comparison: cluster 0 vs. a GDD-threshold zone vs. a GIS-MCDA zone, all sized identically. Uses ML/08's corrected validation data. This is the notebook behind the paper's central finding. |
| `08_validation_rebuild.ipynb` | **New, supersedes ML/05.** Fixes the parcel-join and APN-extraction bugs, documents the full 510→135 parcel loss cascade, adds a Monte Carlo chi-square (asymptotic isn't valid at these expected counts), tests the enforcement-accessibility confound via logistic regression, and tests the Moran (2017) hierarchical-filtering claim directly (not supported in its strong form). |

---

## Key Results (corrected, 2026-07-26)

- **Cannabis archetype identified without any labeled data.** Cluster 0 (K=7) matches documented cultivation conditions: mid-elevation interior (527m mean), warm-dry growing season (GDD 1395, VPD 1568 Pa), Mediterranean precip pattern (1,102 mm/yr). Covers 22.2% of study area, ~6,665 km² (not 6,325 — old area figures used a wrong km²/cell constant).
- **But clustering does not clearly beat simpler baselines on validation** (`ML/07`): GDD threshold lift=3.72 vs. cluster 0's 3.32, with triple the recall (30% vs. 10%) and a far more coherent zone (25 patches vs. 113). MCDA ties on lift (3.31) with much better recall (24%). This is the paper's headline methodological finding now, not a limitation buried in Discussion.
- **Enforcement validation, corrected:** 135 parcels (not 91 — a parcel-join bug and an APN-regex bug both undercounted this), lift=2.79 (not 3.41), χ²(4)=18.58, Monte Carlo p=0.0013 (not the old asymptotic-only p=2.1e-6 over the wrong degrees of freedom). Still real and significant, about half the effect size originally claimed.
- **The enforcement signal is confounded with accessibility.** Distance to town significantly predicts enforcement presence (p=0.005) independent of cluster; cluster 0's own effect drops to non-significance (p=0.194) once that's controlled for. Read the validation as convergent evidence, not independent confirmation.
- **The Moran (2017) hierarchical-filtering claim is not supported.** Tested directly using enforcement parcels as a stand-in: only 48.9% fall within even a generous 3-cluster suitability envelope; the largest single group (44.4%) sits outside it entirely.
- **Slope and soil pH dominate within-zone canopy heterogeneity**, robust to conditional permutation importance (ranking survives; magnitudes shrink ~25-30%) and to spatial block CV (R² drops 8% relative, real but modest). One caveat not fully resolved: slope's relationship to NDVI heterogeneity could partly reflect topographic shading rather than agronomy — a partial check (comparing slope's correlation to more direct shading proxies) is reassuring but not conclusive; full illumination correction of the Sentinel-2 imagery was not performed.
- **EO (satellite NDVI) does not clearly improve validation.** The internal ablation ARI progression looked monotonic, but that's tautological for the full stack. Scored against external enforcement lift, terrain+climate alone (Stack B) beats the full stack.

---

## Data Sources

| Layer | Source | Resolution |
|-------|--------|-----------|
| Study extent | US Census TIGER 2023 | County polygons |
| DEM | USGS National Map 1 arc-second | ~30 m |
| NDVI | Sentinel-2 SR via GEE | 30 m composite |
| Climate | Daymet V4 via GEE (NASA/ORNL) | 1 km daily |
| Soil | SoilGrids ISRIC WCS 2.0.1 | 250 m |
| Roads / populated places (new) | Census TIGER 2023 (`tl_2023_06023_roads.zip`, `tl_2023_06_place.zip`) | vector |

**Note on soil units:** SoilGrids encodes pH ×10 (60 = actual pH 6.0), SOC in dg/kg, CEC in mmol/kg. All profile comparisons must account for this.

---

## Stack

Python 3.7+. `geopandas`, `rasterio`, `shapely`, `pyproj`, `scikit-learn`, `pandas`, `numpy`, `matplotlib`, `seaborn`, `scipy`, `requests`, `earthengine-api`, `statsmodels` (new, for the enforcement-bias logistic regression), `pdfplumber` (re-extraction of NOV PDFs).

GDAL command-line tools (`gdalbuildvrt`, `gdalwarp`, `gdaldem`, `gdal_calc.py`) for raster operations.

Google Earth Engine authenticated session required for `04_ndvi.ipynb`, `05_climate.ipynb`, and the ad hoc Apr–Oct growing-season temperature query in `writing/paper.tex`'s Table 1 footnote. Run `earthengine authenticate` once before first use.

See `requirements.txt`.

---

## Structure

```
KushCountry/
├── README.md
├── CONTEXT.md
├── CLAUDE.md
├── requirements.txt
├── suggestions_pete.md          — external review, lighter pass
├── suggestions_claude.md        — external review, the one that triggered the full rebuild
├── data_wrangling/       00–07: ingestion and feature extraction
├── ML/                   01–08: PCA, clustering, regression, sub-clustering, validation
│                         (05 superseded by 08), robustness, baselines (07, new)
├── writing/              paper.tex + cover_letter.tex + references.bib
│                         (target journal: undecided as of 2026-07-26; UTF branding dropped)
├── data/
│   ├── raw/              TIGER, DEM tiles, hex grid, county polygons, NOV PDF cache, roads/places (new)
│   └── processed/        features, clusters, subclusters, zone gpkgs, validation (v2/v3 = corrected),
│                         robustness, baseline_comparison.pkl (new), conditional_importance.pkl (new),
│                         whitening_check.pkl (new), enforcement_bias_regression_data.pkl (new)
└── img/                  figures at 150 dpi (ML01–ML08)
```
