#!/usr/bin/env python3
"""
Build a 1990-2021-style climatological mean temperature raster from the
monthly Kodama et al. 2024 GeoTIFFs (see 09_kodama_temperature_download.py),
then resample it onto the exact same 500m UTM grid as the island DEM
(hawaii_DEM_500m_utm.tif) so it drops straight into 05_forward_projection.ipynb
in place of the fixed lapse-rate surface.

Usage:
    python 10_kodama_climatology.py
"""
import glob
import os

import numpy as np
import rasterio
from rasterio.warp import Resampling, reproject

DATA = os.path.join(os.path.dirname(__file__), "..", "data")
MONTHLY_DIR = os.path.join(DATA, "kodama_temperature")
NATIVE_OUT = os.path.join(MONTHLY_DIR, "hawaii_temp_climatology_native.tif")
UTM_OUT = os.path.join(DATA, "DEM", "hawaii_temp_climatology_500m_utm.tif")
DEM_UTM = os.path.join(DATA, "DEM", "hawaii_DEM_500m_utm.tif")


def build_climatology():
    paths = sorted(glob.glob(os.path.join(MONTHLY_DIR, "temp_mean_*.tif")))
    if not paths:
        raise SystemExit(f"No monthly GeoTIFFs found in {MONTHLY_DIR}")

    with rasterio.open(paths[0]) as ref:
        profile = ref.profile.copy()
        nodata = ref.nodata

    stack = np.empty((len(paths), profile["height"], profile["width"]), dtype=np.float32)
    for i, p in enumerate(paths):
        with rasterio.open(p) as src:
            arr = src.read(1).astype(np.float32)
            arr[arr == src.nodata] = np.nan
            stack[i] = arr

    n_valid_months = np.sum(~np.isnan(stack), axis=0)
    climatology = np.nanmean(stack, axis=0)
    climatology[n_valid_months == 0] = nodata

    profile.update(dtype="float32", count=1, nodata=nodata)
    with rasterio.open(NATIVE_OUT, "w", **profile) as dst:
        dst.write(climatology.astype(np.float32), 1)

    print(f"Native climatology ({len(paths)} months): {NATIVE_OUT}")
    valid = climatology[climatology != nodata]
    print(f"  shape={climatology.shape}  range={valid.min():.2f}..{valid.max():.2f}C  mean={valid.mean():.2f}C")
    return NATIVE_OUT


def resample_to_island_grid(native_path):
    with rasterio.open(DEM_UTM) as dem:
        dst_crs, dst_transform, dst_h, dst_w = dem.crs, dem.transform, dem.height, dem.width

    with rasterio.open(native_path) as src:
        dst_arr = np.full((dst_h, dst_w), -9999.0, dtype=np.float32)
        reproject(
            source=rasterio.band(src, 1),
            destination=dst_arr,
            src_transform=src.transform,
            src_crs=src.crs,
            src_nodata=src.nodata,
            dst_transform=dst_transform,
            dst_crs=dst_crs,
            dst_nodata=-9999.0,
            resampling=Resampling.bilinear,
        )

    os.makedirs(os.path.dirname(UTM_OUT), exist_ok=True)
    profile = {
        "driver": "GTiff", "dtype": "float32", "count": 1,
        "height": dst_h, "width": dst_w, "crs": dst_crs,
        "transform": dst_transform, "nodata": -9999.0,
    }
    with rasterio.open(UTM_OUT, "w", **profile) as dst:
        dst.write(dst_arr, 1)

    print(f"Resampled to island UTM grid ({dst_h}x{dst_w}, matches {os.path.basename(DEM_UTM)}): {UTM_OUT}")
    valid = dst_arr[dst_arr != -9999.0]
    print(f"  range={valid.min():.2f}..{valid.max():.2f}C  mean={valid.mean():.2f}C")


def demo():
    """Self-check: climatology mean must be a plausible Big Island annual temp,
    and the UTM-resampled grid must exactly match the DEM's shape/transform."""
    with rasterio.open(NATIVE_OUT) as src:
        arr = src.read(1)
        valid = arr[arr != src.nodata]
        assert 5 < valid.mean() < 26, f"implausible island-wide mean temp: {valid.mean()}"

    with rasterio.open(UTM_OUT) as clim, rasterio.open(DEM_UTM) as dem:
        assert clim.shape == dem.shape, (clim.shape, dem.shape)
        assert clim.transform == dem.transform, (clim.transform, dem.transform)
        assert clim.crs == dem.crs
    print("demo: OK")


if __name__ == "__main__":
    native = build_climatology()
    resample_to_island_grid(native)
    demo()
