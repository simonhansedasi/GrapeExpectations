# GrapeExpectations

A machine learning appraoch to inferring grape chemistry using topographic and weather data.

---

## Project Goal

- Use machine learning to predict various seasonal vegetation indices for vineyard plots  
- Translate late season vegetation indices to grape chemistry via transfer functions
- Derive viticultural insights for growers and wine makers

<!-- ### NDVI and NDVI Integral

The Normalized Difference Vegetation Index (NDVI) is a measure of vegetation health derived from satellite or aerial imagery. It captures how much light plants absorb versus reflect, giving a proxy for vigor and canopy density.

The NDVI integral sums NDVI over the growing season, effectively measuring total vegetation activity. In viticulture, this is crucial because:

- It reflects overall vine growth and leaf area development  
- It correlates with canopy size, photosynthetic activity, and potential yield  
- Early-season NDVI integrals can guide management decisions, like irrigation, pruning, and harvest timing  

By predicting NDVI integrals from weather and plot features, we can provide early insights into vine health and vineyard productivity, enabling more informed and timely interventions.
 -->
---

## Getting Started

This project was created using Jupyter Lab. Installation assumes conda and jupyter lab are already installed. The tech stack is quite sensitive to versions and conflicts, so it is very important to install the conda environment to reproduce results.

### Installation:

- Install conda environment via terminal by running the following command. These commands can be found in a .txt file in the repository root folder.

```console
conda create -n GrapeExpectations python=3.7.6 -y

conda activate GrapeExpectations

pip install --upgrade pip

pip install \
lxml==4.5.0 \
shapely==2.0.7 \
geopandas==0.10.2 \
requests==2.31.0 \
tqdm \
rasterio==1.2.10 \
matplotlib==3.1.3 \
pandas==1.0.1 \
numpy==1.21.6 \
rasterstats==0.20.0 \
earthengine-api==0.1.407 \
geemap==0.20.4 \
scipy==1.4.1 \
scikit-learn==1.0.2

pip install ipykernel
python -m ipykernel install --user --name=GrapeExpectations --display-name "Python 3.7.6 (GrapeExpectations)"

```
---

## Data
### Files for a single vineyard in the Columbia Valley are included. More can be downloaded to duplicate workflow.
- **Polygons:** Area geometries of vineyard facility and individual plots.
  - **Source:** Google Earth & Rasterio  
- **Digital Elevation Model:**  
  - **Source:** [National Map Downloader](https://apps.nationalmap.gov/downloader/#/)
- **Weather data:** Vineyard-wide temperature, rainfall, GDD, etc.  
  - **Source:** [PRISM Climate Data](https://prism.oregonstate.edu/downloads/)  
  
---

## Notebooks

### 01_clip_dem

Use polygons to clip and extract elevation data from a DEM geotiff file. Capable of doing vineyard-wide or plot-wide elevation data gathering.

<p align="center">
  <img src="RegressionRidge/img/dem_clip.png" alt="Digital Elevation Map" width="600"/>
</p>


### 02_breakdown_dem

Use rasterstats to derive plot-wise topographic features from clipped elevation data. Features engineered include plot area, slope, aspect, and curvature. These features are further split into directional components for eventual machine learning.












  
  
<!-- - **Plot characteristics:** elevation, slope, aspect, frost risk  
  - **Source:** Derived from Digital Elevation Model  
 -->
<!-- <p align="center">
  <img src="RegressionRidge/img/dem_w_slope.png" alt="Plot Characteristics" width="600"/>
</p>

 -->
<!-- <p align="center">
  <img src="RegressionRidge/img/frost_risk.png" alt="Frost Risk" width="600"/>
</p>
 --> 
<!-- - **NDVI measurements:** Derived from remote sensing for vegetation monitoring using Copernicus satellite data.  

<p align="center">
  <img src="RegressionRidge/img/ndvi_spaghetti.png" alt="NDVI Measurements" width="600"/>
</p>

---

## Features

- Plot-level terrain features: slope, aspect (sin/cos), elevation  
- Weather features: seasonal and daily aggregates, growing degree days  

---

## Modeling

**Goal:** Predict NDVI integral per vineyard plot  

- **Model:** XGBoost regression  
- **Test R²:** 0.82 — strong predictive performance  

**Predictions vs Observations:**  

<p align="center">
  <img src="RegressionRidge/img/pred_vs_obs.png" alt="Predicted vs Observed NDVI Integral" width="600"/>
</p>

**Residuals:**  

<p align="center">
  <img src="RegressionRidge/img/residuals.png" alt="Residuals of NDVI Predictions" width="600"/>
</p>

**Feature Importance:**  
- Top drivers reflect **biological constraints** on vine growth:  
  - **VPD & minimum temperatures** → canopy development and stress tolerance  
  - **Slope & aspect** → microclimate and sunlight exposure  
  - **Frost days** → sensitivity during early growth  
  - **Elevation** → temperature gradients and site-specific conditions  

<p align="center">
  <img src="RegressionRidge/img/feature_imp.png" alt="Top Features Influencing NDVI Integral" width="600"/>
</p>

**Techniques:**  

- Train/test split with early stopping  
- Feature importance analysis  
- Residual evaluation to detect bias patterns  

---
 -->