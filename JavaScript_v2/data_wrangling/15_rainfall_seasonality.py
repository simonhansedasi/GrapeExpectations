#!/usr/bin/env python3
"""
Build a per-cell monthly rainfall climatology from the 384 monthly 250 m rasters
downloaded by `09_kodama_temperature_download.py --datatype rainfall`, and check
the dry-season definition the old pipeline used.

`05_climate.ipynb` hard-codes DRY_MONTHS = [6, 7, 8, 9] with the comment "Kona
leeward dry season", and applies it to Ka'u as well. That is an assumption, not a
measurement, and it sits on the same axis as the annual precipitation column that
turned out to be inverted. This script measures the seasonal cycle instead of
assuming it, prints both districts' monthly means, and names the driest four months
empirically. Nothing downstream is written until that comparison has been seen.

Output: data/rainfall_monthly_climatology.csv (plot_id x month_01..month_12, mm).

Usage:  python data_wrangling/15_rainfall_seasonality.py
"""
import os
import glob
import re
import warnings

warnings.filterwarnings('ignore')
import numpy as np
import pandas as pd
import geopandas as gpd
import rasterio

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.abspath(os.path.join(HERE, '..', 'data'))
TIFS = os.path.join(DATA, 'rainfall_monthly')
OUT = os.path.join(DATA, 'rainfall_monthly_climatology.csv')
OLD_DRY = [6, 7, 8, 9]

d = pd.read_pickle(f'{DATA}/plot_all_features.pkl')
d = d[d.label == 1].copy()
g = gpd.GeoDataFrame(d, geometry='geometry', crs='EPSG:4326')
cen = g.geometry.centroid
pts = list(zip(cen.x.values, cen.y.values))
pid = g.plot_id.values
reg = g.region.values
print(f"{len(pts)} farm cells (kona {(reg=='kona').sum()}, kau {(reg=='kau').sum()})")

files = sorted(glob.glob(os.path.join(TIFS, 'rain_*_*.tif')))
print(f"{len(files)} monthly rasters")
if not files:
    raise SystemExit("no rasters -- run 09_kodama_temperature_download.py --datatype rainfall")

# accumulate sum and count per (cell, calendar month) across all years
acc = np.zeros((len(pts), 12))
cnt = np.zeros(12, dtype=int)
for f in files:
    m = re.search(r'_(\d{4})-(\d{2})\.tif$', f)
    mo = int(m.group(2))
    with rasterio.open(f) as s:
        nd = s.nodata
        v = np.array([x[0] for x in s.sample(pts)], dtype=float)
    v[v == nd] = np.nan
    acc[:, mo - 1] += np.nan_to_num(v)
    cnt[mo - 1] += 1

clim = acc / cnt                      # mean rainfall in each calendar month, mm
out = pd.DataFrame(clim, columns=[f'month_{i:02d}' for i in range(1, 13)])
out.insert(0, 'plot_id', pid)
out.to_csv(OUT, index=False)
print(f"wrote {OUT}  ({cnt.min()}-{cnt.max()} years per month)\n")

names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
         'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
print(f"{'district':>8} " + " ".join(f"{n:>6}" for n in names) + "   annual")
emp = {}
for r in ('kona', 'kau'):
    mm = clim[reg == r].mean(axis=0)
    emp[r] = sorted(np.argsort(mm)[:4] + 1)
    print(f"{r:>8} " + " ".join(f"{v:6.0f}" for v in mm) + f"  {mm.sum():7.0f}")

print()
for r in ('kona', 'kau'):
    mm = clim[reg == r].mean(axis=0)
    dry_old = mm[[i - 1 for i in OLD_DRY]].mean()
    wet_old = mm[[i - 1 for i in range(1, 13) if i not in OLD_DRY]].mean()
    tag = "INVERTED" if dry_old > wet_old else "ok"
    print(f"{r}: old DRY_MONTHS {OLD_DRY} average {dry_old:.0f} mm/mo vs "
          f"rest {wet_old:.0f} mm/mo  -> {tag}")
    print(f"       driest four months measured: {[names[i-1] for i in emp[r]]} "
          f"({[int(i) for i in emp[r]]})")
