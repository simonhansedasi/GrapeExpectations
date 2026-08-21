#!/usr/bin/env python3
"""
Out-of-sample test of the topographic feasibility screen on Kaua'i.

The screen's centroids and distance threshold are fitted entirely on Big Island
farm cells. Kaua'i is never seen during fitting, yet it carries a large
commercial coffee estate (10 polygons, ~3,806 acres in the same 2020 Statewide
Agricultural Land Use Baseline used for the Big Island). Applying the fitted
screen to Kaua'i therefore tests whether "Kona-like / Ka'u-like terrain" picks
out coffee ground on an island the model has no knowledge of.

Deliberately symmetric with the Big Island pipeline: the Kaua'i DEM is mosaicked
from the same USGS 3DEP 1/3 arc-second product, reprojected to UTM, resampled to
the same 500 m grid, and the same eight topographic features are computed the
same way, so no feature is defined differently between fit and test.

Usage:
    python 12_kauai_validation.py
"""
import glob
import json
import os

import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
from rasterio.merge import merge
from rasterio.warp import Resampling, calculate_default_transform, reproject
from scipy.ndimage import distance_transform_edt, maximum_filter, minimum_filter
from sklearn.preprocessing import StandardScaler

DATA = os.path.join(os.path.dirname(__file__), "..", "data")
KDIR = os.path.join(DATA, "DEM", "kauai")
UTM = "EPSG:32604"          # same zone used for the Big Island grid
RES = 500.0
FEATS = ["elev_mean", "elev_dev_mean", "slope_max", "aspect_sin", "aspect_cos",
         "total_relief", "local_relief", "dist_coast_m"]


def build_grid(paths, out_tif):
    """Mosaic -> UTM -> 500 m, matching the Big Island preparation."""
    if os.path.exists(out_tif):
        return out_tif
    srcs = [rasterio.open(p) for p in paths]
    mosaic, mt = merge(srcs)
    meta = srcs[0].meta.copy()
    meta.update(height=mosaic.shape[1], width=mosaic.shape[2], transform=mt)
    tmp = out_tif.replace(".tif", "_ll.tif")
    with rasterio.open(tmp, "w", **meta) as d:
        d.write(mosaic)
    for s in srcs:
        s.close()
    with rasterio.open(tmp) as src:
        tr, w, h = calculate_default_transform(src.crs, UTM, src.width, src.height,
                                               *src.bounds, resolution=RES)
        kw = src.meta.copy()
        kw.update(crs=UTM, transform=tr, width=w, height=h, dtype="float32", nodata=-9999.0)
        with rasterio.open(out_tif, "w", **kw) as dst:
            reproject(source=rasterio.band(src, 1), destination=rasterio.band(dst, 1),
                      src_transform=src.transform, src_crs=src.crs,
                      dst_transform=tr, dst_crs=UTM,
                      resampling=Resampling.average, dst_nodata=-9999.0)
    os.remove(tmp)
    return out_tif


def features(tif):
    """The same eight features, computed the same way as on the Big Island."""
    with rasterio.open(tif) as s:
        dem = s.read(1).astype(np.float32)
        nd, tr, crs = s.nodata, s.transform, s.crs
    dem[dem == nd] = np.nan
    dem[dem <= 0] = np.nan
    land = ~np.isnan(dem)
    scene_mean = np.nanmean(dem[land])
    dev = dem - scene_mean
    filled = np.where(land, dem, scene_mean)
    dy, dx = np.gradient(filled, RES, RES)
    slope = np.degrees(np.arctan(np.sqrt(dx ** 2 + dy ** 2)))
    arad = np.arctan2(-dx, dy)
    smax = maximum_filter(slope, size=3, mode="nearest")
    emax = maximum_filter(filled, size=3, mode="nearest")
    emin = minimum_filter(filled, size=3, mode="nearest")
    arr = {
        "elev_mean": dem, "elev_dev_mean": dev, "slope_max": smax,
        "aspect_sin": np.sin(arad), "aspect_cos": np.cos(arad),
        "total_relief": emax - emin, "local_relief": dem - emin,
        "dist_coast_m": distance_transform_edt(land) * RES,
    }
    for k in arr:
        arr[k] = np.where(land, arr[k], np.nan)
    return dem, land, arr, tr, crs


def main():
    tiles = sorted(glob.glob(os.path.join(KDIR, "USGS_13_*.tif")))
    assert tiles, "no Kaua'i DEM tiles found"
    tif = build_grid(tiles, os.path.join(KDIR, "kauai_DEM_500m_utm.tif"))
    dem, land, arr, tr, crs = features(tif)
    flat = land.ravel()
    Xk = np.column_stack([arr[f].ravel()[flat] for f in FEATS])
    ok = ~np.isnan(Xk).any(axis=1)
    Xk = Xk[ok]
    print(f"Kaua'i: {land.sum():,} land cells at 500 m, {ok.sum():,} with complete features")

    # ---- refit the screen exactly as the Big Island analysis does -----------
    # IMPORTANT: farm-cell features must be sampled from the island 500 m grid,
    # not read from plot_all_features.pkl. That table carries a legacy
    # dist_coast_m (Kona ~29 km, Ka'u ~71 km) which exceeds the island-wide
    # maximum and is not the quantity the screen is fitted on (Kona ~4 km).
    # Sampling from the grid reproduces the published threshold of 4.620.
    bdem, bland, ba, btr, bcrs = features(os.path.join(DATA, "DEM", "hawaii_DEM_500m_utm.tif"))
    allf = pd.read_pickle(os.path.join(DATA, "plot_all_features.pkl"))
    fpb = gpd.GeoDataFrame(allf[allf.label == 1].copy(), geometry="geometry",
                           crs="EPSG:4326").to_crs(bcrs)
    cb = fpb.geometry.centroid
    cix = ((cb.x - btr.c) / btr.a).astype(int).values
    rix = ((cb.y - btr.f) / btr.e).astype(int).values
    Hb, Wb = bdem.shape
    inb = (rix >= 0) & (rix < Hb) & (cix >= 0) & (cix < Wb)
    Xb = np.column_stack([ba[f][rix[inb], cix[inb]] for f in FEATS])
    reg = fpb["region"].values[inb]
    good = ~np.isnan(Xb).any(axis=1)
    Xb, reg = Xb[good], reg[good]
    sc = StandardScaler().fit(Xb)
    Fs = sc.transform(Xb)
    ck, cq = Fs[reg == "kona"].mean(0), Fs[reg == "kau"].mean(0)
    dk = np.linalg.norm(Fs[reg == "kona"] - ck, axis=1)
    dq = np.linalg.norm(Fs[reg == "kau"] - cq, axis=1)
    thr = np.percentile(np.concatenate([dk, dq]), 95)
    print(f"screen fitted on {len(Xb)} Big Island farm cells; 95th-pct threshold = {thr:.3f}")

    Ks = sc.transform(Xk)
    Dk = np.linalg.norm(Ks - ck, axis=1)
    Dq = np.linalg.norm(Ks - cq, axis=1)
    inr = (Dk <= thr) | (Dq <= thr)
    print(f"Kaua'i cells passing the screen: {inr.sum():,} / {len(Ks):,} ({inr.mean()*100:.1f}%)")

    # ---- ground truth: Kaua'i coffee polygons, same source ------------------
    ag = gpd.read_file(os.path.join(DATA, "polygons", "aglanduse_2020.shp"))
    kc = ag[(ag.Island == "Kauai") &
            (ag["Crops_2020"].astype(str).str.lower().str.contains("coffee"))].to_crs(crs)
    print(f"Kaua'i coffee ground truth: {len(kc)} polygons, {kc.Acreage.sum():,.0f} acres")

    rows, cols = np.mgrid[0:dem.shape[0], 0:dem.shape[1]]
    xs = tr.c + (cols + 0.5) * tr.a
    ys = tr.f + (rows + 0.5) * tr.e
    xs, ys = xs.ravel()[flat][ok], ys.ravel()[flat][ok]
    pts = gpd.GeoDataFrame(geometry=gpd.points_from_xy(xs, ys), crs=crs)
    inside = np.zeros(len(pts), bool)
    join = gpd.sjoin(pts, kc[["geometry"]], how="left", predicate="within")
    inside[join[~join.index_right.isna()].index.unique()] = True
    print(f"Kaua'i cells whose centre falls in a coffee polygon: {inside.sum():,}")

    # ---- confusion / enrichment -------------------------------------------
    tp = int((inr & inside).sum()); fp = int((inr & ~inside).sum())
    fn = int((~inr & inside).sum()); tn = int((~inr & ~inside).sum())
    base = inside.mean()
    prec = tp / (tp + fp) if tp + fp else np.nan
    rec = tp / (tp + fn) if tp + fn else np.nan
    print("\n--- out-of-sample result on Kaua'i ---")
    print(f"  coffee cells inside screen : {tp:,} / {int(inside.sum()):,}  (recall {rec*100:.1f}%)")
    print(f"  screened cells that are coffee: {tp:,} / {int(inr.sum()):,}  (precision {prec*100:.1f}%)")
    print(f"  base rate of coffee on Kaua'i : {base*100:.2f}%")
    if base > 0 and not np.isnan(prec):
        print(f"  ENRICHMENT over base rate     : {prec/base:.1f}x")
    print(f"  confusion: TP={tp:,} FP={fp:,} FN={fn:,} TN={tn:,}")

    out = dict(kauai_land_cells=int(ok.sum()), screened=int(inr.sum()),
               coffee_cells=int(inside.sum()), tp=tp, fp=fp, fn=fn, tn=tn,
               recall=float(rec), precision=float(prec), base_rate=float(base),
               enrichment=float(prec / base) if base > 0 else None,
               threshold=float(thr), n_polygons=int(len(kc)), acres=float(kc.Acreage.sum()))
    with open(os.path.join(DATA, "..", "kauai_validation.json"), "w") as f:
        json.dump(out, f, indent=1)
    print("\nwrote ../kauai_validation.json")


if __name__ == "__main__":
    main()
