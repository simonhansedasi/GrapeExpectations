# 🍇 GrapeExpectations

Predicting **vineyard NDVI integrals** using weather and plot data.  
Data-driven insights for vineyard monitoring and optimization.

---

## Project Goal

- Use **machine learning** to predict seasonal NDVI integrals for vineyard plots  
- Understand which **weather variables and plot features** drive vegetation growth  
- Provide **early insights into vine vigor and productivity**

---

## Data
- **Polygons:** Area geometries of vineyard facility and individual plots
    - **Source:** Google Earth & Rasterio
- **Digital Elevation Model:** 
    - **Source:** https://apps.nationalmap.gov/downloader/#/
    
![DEM Map](RegressionRidge/img/dem_clip.png "Digital Elevation Map of Regression Ridge")

- **Weather data**:Vineyard wide temperature, rainfall, GDD, etc:
    - **Source:** https://prism.oregonstate.edu/downloads/
- **Plot characteristics**: elevation, slope, aspect, soil proxies
    - **Source:** Derived from Digintal Elevation Model
    
![Plot_chars](RegressionRidge/img/dem_w_slope.png "Digital Elevation Map of Regression Ridge")
- **NDVI measurements**: derived from remote sensing for vegetation monitoring using Copernicus satellite data. 

![Plot_chars](RegressionRidge/img/ndvi_spaghetti.png "Digital Elevation Map of Regression Ridge")
---

## Features

- Plot-level terrain features: slope, aspect (sin/cos), elevation  
- Weather features: seasonal and daily aggregates, growing degree days  
<!-- - NDVI metrics for model training: integral, peak, greenup, senescence   -->

---

## Modeling

- **Target**: NDVI integral per plot  
- **Model**: XGBoost regression  
 - **R2:** 0.82
 
 ![Plot_chars](RegressionRidge/img/pred_vs_obs.png "Digital Elevation Map of Regression Ridge")
 
 ![Plot_chars](RegressionRidge/img/residuals.png "Digital Elevation Map of Regression Ridge")
- **Techniques**:  
  - Train/test split with early stopping  
  - Feature importance analysis  
  - Residual evaluation to detect bias patterns  

![Plot_chars](RegressionRidge/img/feature_imp.png "Digital Elevation Map of Regression Ridge")

---
