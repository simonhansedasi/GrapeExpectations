#!/usr/bin/env python3
"""
How much does temperature swing seasonally, and does each district get its rain at
a different point in that swing?

Rainfall seasonality is anti-phase between the districts (r = -0.58, Kona peaking
Sep, Ka'u Mar). Temperature on a tropical island is close to in-phase everywhere,
so if that holds, the two districts sit in structurally different agroclimatic
regimes: rain arriving in the warm half of the year versus the cool half. That is a
different thing from "one is wetter", and it is testable directly.

Three quantities per district:
  1. monthly temperature climatology -> annual range and phase
  2. correlation between the monthly temperature and rainfall cycles
  3. RAIN-WEIGHTED mean temperature minus plain mean temperature -- the temperature
     at which the water actually arrives. This is the direct answer: two districts
     can share an annual mean temperature and an annual rainfall total and still
     deliver that water at very different temperatures.

Output: data/temp_monthly_climatology.csv (plot_id x month_01..12, degC).

Usage:  python data_wrangling/16_temp_rain_joint.py
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
OUT = os.path.join(DATA, 'temp_monthly_climatology.csv')
NAMES = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
         'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

d = pd.read_pickle(f'{DATA}/plot_all_features.pkl')
d = d[d.label == 1].copy()
g = gpd.GeoDataFrame(d, geometry='geometry', crs='EPSG:4326')
cen = g.geometry.centroid
pts = list(zip(cen.x.values, cen.y.values))
pid, reg = g.plot_id.values, g.region.values

# only the dated monthly files -- the directory also holds a derived climatology
files = sorted(f for f in glob.glob(os.path.join(DATA, 'kodama_temperature', '*.tif'))
               if re.search(r'_\d{4}-\d{2}\.tif$', f))
print(f"{len(files)} monthly temperature rasters, {len(pts)} farm cells")

if os.path.exists(OUT):
    tc = pd.read_csv(OUT).set_index('plot_id')
    print(f"reusing {OUT}")
else:
    acc = np.zeros((len(pts), 12)); cnt = np.zeros(12, dtype=int)
    for f in files:
        mo = int(re.search(r'_(\d{4})-(\d{2})\.tif$', f).group(2))
        with rasterio.open(f) as s:
            nd = s.nodata
            v = np.array([x[0] for x in s.sample(pts)], dtype=float)
        v[v == nd] = np.nan
        acc[:, mo - 1] += np.nan_to_num(v); cnt[mo - 1] += 1
    tc = pd.DataFrame(acc / cnt, columns=[f'month_{i:02d}' for i in range(1, 13)])
    tc.insert(0, 'plot_id', pid)
    tc.to_csv(OUT, index=False)
    tc = tc.set_index('plot_id')
    print(f"wrote {OUT}  ({cnt.min()}-{cnt.max()} years/month)")

cols = [f'month_{i:02d}' for i in range(1, 13)]
T = tc.loc[pid, cols].values
R = pd.read_csv(os.path.join(DATA, 'rainfall_monthly_climatology.csv')) \
      .drop_duplicates('plot_id').set_index('plot_id').loc[pid, cols].values

print(f"\n{'':>8} " + " ".join(f"{n:>6}" for n in NAMES))
for r in ('kona', 'kau'):
    print(f"{r:>8} " + " ".join(f"{v:6.1f}" for v in T[reg == r].mean(axis=0)))

print(f"\n{'district':>8} {'annual range':>13} {'warmest':>9} {'coolest':>9} "
      f"{'corr(T,R)':>10} {'mean T':>8} {'rain-wtd T':>11} {'shift':>7}")
res = {}
for r in ('kona', 'kau'):
    t, rn = T[reg == r].mean(axis=0), R[reg == r].mean(axis=0)
    rng = t.max() - t.min()
    corr = np.corrcoef(t, rn)[0, 1]
    mt = t.mean()
    wt = float((t * rn).sum() / rn.sum())      # temperature at which the rain falls
    res[r] = (rng, corr, mt, wt)
    print(f"{r:>8} {rng:12.2f}C {NAMES[t.argmax()]:>9} {NAMES[t.argmin()]:>9} "
          f"{corr:10.2f} {mt:7.2f}C {wt:10.2f}C {wt-mt:+6.2f}C")

print(f"\nseasonal temperature range is {res['kona'][0]:.2f}C (Kona) and "
      f"{res['kau'][0]:.2f}C (Ka'u) -- for scale, the projected warming to 2045 is "
      f"+1.35C, i.e. {1.35/res['kona'][0]:.1f}x the entire annual cycle.")

dk, dq = res['kona'][3] - res['kona'][2], res['kau'][3] - res['kau'][2]
print(f"\nrain-weighted minus plain mean temperature: Kona {dk:+.2f}C, Ka'u {dq:+.2f}C "
      f"-> gap {dk-dq:+.2f}C")
if dk > 0 and dq < 0:
    print("  Kona's rain arrives in its WARM season, Ka'u's in its COOL season.")
    print("  Same plant, same annual means, opposite warm/wet coupling.")
elif dk * dq > 0:
    print("  Both districts receive rain on the same side of their temperature cycle.")

# per-cell version, so the contrast is not resting on two district averages
wcell = (T * R).sum(axis=1) / R.sum(axis=1) - T.mean(axis=1)
for r in ('kona', 'kau'):
    s = wcell[reg == r]
    print(f"  per-cell {r:5s}: {s.mean():+.2f}C  (sd {s.std():.2f}, n={len(s)}, "
          f"{100*(s > 0).mean():.0f}% positive)")
