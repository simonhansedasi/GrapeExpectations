#!/usr/bin/env python3
"""
Build a "historic lava" exclusion raster from the NPS/USGS digital geologic
map of the Island of Hawai'i (Wolfe & Morris 1996 / Trusdell et al. 2006,
NPS GRE reformatting -- havoglg.shp + havoglg1.dbf legend), resampled onto
the exact same 500m UTM grid as the island DEM.

Flags cells covered by lava flows mapped as "Historic A.D. 1790 or younger"
-- the youngest, least-weathered substrate, matching the self-review's own
examples (1859/1950 Mauna Loa flows, Kilauea's recent output) of terrain
that satisfies a slope criterion but is not actually farmable.

Source: NPS IRMA DataStore Reference 1044526, HAVOSHP.ZIP
(https://irma.nps.gov/DataStore/Reference/Profile/1044526), manually
downloaded by Simon (the DataStore page is a JS-rendered SPA that doesn't
expose a fetchable direct-download link).

Usage:
    python 11_lava_flow_age.py
"""
import os
import zipfile

import geopandas as gpd
import numpy as np
import rasterio
from rasterio.features import rasterize

DATA = os.path.join(os.path.dirname(__file__), "..", "data")
GEOL_DIR = os.path.join(DATA, "geology")
ZIP_PATH = os.path.join(GEOL_DIR, "havoshp.zip")
EXTRACT_DIR = os.path.join(GEOL_DIR, "havoshp")
DEM_UTM = os.path.join(DATA, "DEM", "hawaii_DEM_500m_utm.tif")
OUT_TIF = os.path.join(DATA, "DEM", "hawaii_historic_lava_500m_utm.tif")


def extract():
    if not os.path.isdir(EXTRACT_DIR):
        with zipfile.ZipFile(ZIP_PATH) as zf:
            zf.extractall(EXTRACT_DIR)
    return os.path.join(EXTRACT_DIR, "havoglg.shp"), os.path.join(EXTRACT_DIR, "havoglg1.dbf")


def build_historic_mask(shp_path, legend_path):
    gdf = gpd.read_file(shp_path)
    legend = gpd.read_file(legend_path)[["GLG_SYM", "NOTES"]].rename(columns={"NOTES": "AGE_NOTES"})
    merged = gdf.merge(legend, on="GLG_SYM", how="left")
    assert merged["AGE_NOTES"].notna().all(), "unmatched GLG_SYM values against the legend table"

    historic = merged[merged["AGE_NOTES"].str.contains("Historic", na=False)]
    print(f"Historic (A.D. 1790 or younger) polygons: {len(historic)} / {len(merged)}")
    print(f"  area: {historic.geometry.area.sum() / 1e6:.1f} km2 "
          f"of {merged.geometry.area.sum() / 1e6:.1f} km2 mapped")
    return historic


def rasterize_to_island_grid(historic_gdf):
    with rasterio.open(DEM_UTM) as dem:
        dst_crs, dst_transform, dst_h, dst_w = dem.crs, dem.transform, dem.height, dem.width

    historic_utm = historic_gdf.to_crs(dst_crs)
    mask = rasterize(
        [(geom, 1) for geom in historic_utm.geometry if geom is not None and not geom.is_empty],
        out_shape=(dst_h, dst_w),
        transform=dst_transform,
        fill=0,
        dtype="uint8",
    )

    profile = {
        "driver": "GTiff", "dtype": "uint8", "count": 1,
        "height": dst_h, "width": dst_w, "crs": dst_crs,
        "transform": dst_transform, "nodata": 255,
    }
    with rasterio.open(OUT_TIF, "w", **profile) as dst:
        dst.write(mask, 1)

    print(f"Rasterized to island UTM grid ({dst_h}x{dst_w}, matches {os.path.basename(DEM_UTM)}): {OUT_TIF}")
    print(f"  flagged cells: {int(mask.sum()):,} / {mask.size:,} ({mask.sum() / mask.size * 100:.1f}%)")
    return mask


def demo():
    """Self-check: the flagged fraction should be in a plausible range for a
    volcanically active island (not near-zero, not the whole island), and the
    output raster must exactly match the DEM's grid."""
    with rasterio.open(OUT_TIF) as src, rasterio.open(DEM_UTM) as dem:
        assert src.shape == dem.shape
        assert src.transform == dem.transform
        assert src.crs == dem.crs
        arr = src.read(1)
        frac = (arr == 1).sum() / arr.size
        assert 0.02 < frac < 0.4, f"implausible historic-lava fraction: {frac:.3f}"
    print("demo: OK")


if __name__ == "__main__":
    shp_path, legend_path = extract()
    historic = build_historic_mask(shp_path, legend_path)
    rasterize_to_island_grid(historic)
    demo()
