#!/usr/bin/env python3
"""
Block-bootstrap confidence intervals for the argmax of |F_r(ΔT)|.

The peak offset is now the paper's headline claim and had no interval. This uses
the same spatial block machinery as ML/06 (k-means blocks of ~8 farm cells,
resampled with replacement, the WHOLE screen refitted inside each replicate:
standardiser, both centroids, the 95th-percentile threshold, and mu_r/sigma_r).

Speed note: |F_r(ΔT)| at tau = 0.5 is just a count of footprint cells whose
temperature falls in a fixed-width window, so per replicate we sort the footprint
temperatures once and answer the whole ΔT grid by searchsorted rather than
recomputing a Gaussian over 36,055 cells at every step.

Also reports the offsets RE-CENTRED on the end of the observational record, using
the trend measured in ML/11_baseline_epoch.py. The sweep's origin is the
1990-2021 climatological mean, not the present; re-centring is what makes the
offsets statements about now.

Run from repo root:  python ML/12_peak_bootstrap.py
"""
import json, os
import numpy as np
import pandas as pd
import geopandas as gpd
import rasterio
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from scipy.ndimage import maximum_filter, minimum_filter, distance_transform_edt

rng = np.random.default_rng(7)
HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, '..', 'data')
NB = 2000
TAU = 0.5
HW = np.sqrt(2 * np.log(1 / TAU))     # |T + dT - mu| < HW * sigma  <=>  S > tau

with rasterio.open(f'{DATA}/DEM/hawaii_DEM_500m_utm.tif') as s:
    nd = s.nodata; dem = s.read(1).astype(np.float32); tr = s.transform
    H, W = s.height, s.width; crs = s.crs
dem[dem == nd] = np.nan; dem[dem <= 0] = np.nan; land = ~np.isnan(dem)
sm = np.nanmean(dem[land]); ef = np.where(land, dem, sm)
dy, dx = np.gradient(ef, 500., 500.)
slope = np.degrees(np.arctan(np.sqrt(dx**2 + dy**2))); asp = np.arctan2(-dx, dy)
asin, acos = np.sin(asp), np.cos(asp)
smax = maximum_filter(slope, size=3, mode='nearest')
emax = maximum_filter(ef, size=3, mode='nearest'); emin = minimum_filter(ef, size=3, mode='nearest')
relief = emax - emin; local = dem - emin
for a in [smax, asin, acos, relief, local]:
    a[~land] = np.nan
dcoast = distance_transform_edt(land) * 500.; dcoast[~land] = np.nan
flat = land.ravel()
# corrected seven-feature set: elevation once
LAYERS = [dem, smax, asin, acos, relief, local, dcoast]
X = np.column_stack([a.ravel()[flat] for a in LAYERS])
with rasterio.open(f'{DATA}/DEM/hawaii_temp_climatology_500m_utm.tif') as s:
    tc = s.read(1).astype(np.float32); tnd = s.nodata
tc[tc == tnd] = np.nan; tc[~land] = np.nan
Tflat = tc.ravel()[flat]
with rasterio.open(f'{DATA}/DEM/hawaii_historic_lava_500m_utm.tif') as s:
    lava = (s.read(1) == 1)
farm = (smax.ravel()[flat] <= 25.) & (~np.isnan(smax.ravel()[flat])) & (~lava.ravel()[flat])

allf = pd.read_pickle(f'{DATA}/plot_all_features.pkl')
fp = gpd.GeoDataFrame(allf[allf.label == 1].copy(), geometry='geometry', crs='EPSG:4326').to_crs(crs)
cen = fp.geometry.centroid
ci = ((cen.x - tr.c) / tr.a).astype(int).values; ri = ((cen.y - tr.f) / tr.e).astype(int).values
ok = (ri >= 0) & (ri < H) & (ci >= 0) & (ci < W)
FT = np.column_stack([a[ri[ok], ci[ok]] for a in LAYERS])
with rasterio.open(f'{DATA}/DEM/hawaii_temp_climatology_500m_utm.tif') as s:
    FTemp = np.array([v[0] for v in s.sample(zip(cen.x[ok], cen.y[ok]))])
reg = fp['region'].values[ok]
good = ~np.isnan(FT).any(axis=1)
FT, FTemp, reg = FT[good], FTemp[good], reg[good]
xy = np.column_stack([cen.x[ok][good], cen.y[ok][good]])

blocks = {}
for r in ('kona', 'kau'):
    m = reg == r; n = int(m.sum()); nb = max(4, int(round(n / 8)))
    blocks[r] = (np.where(m)[0], KMeans(n_clusters=nb, random_state=0, n_init=10).fit_predict(xy[m]), nb)

SWEEP = np.round(np.arange(-3.0, 3.001, 0.01), 2)


def peaks(idx):
    """Refit the whole screen on a farm-cell subset; return argmax of |F_r| per district."""
    sc = StandardScaler().fit(FT[idx])
    Fs = sc.transform(FT[idx]); Is = sc.transform(X)
    rr = reg[idx]
    ck = Fs[rr == 'kona'].mean(0); cq = Fs[rr == 'kau'].mean(0)
    dk = np.linalg.norm(Fs[rr == 'kona'] - ck, axis=1)
    dq = np.linalg.norm(Fs[rr == 'kau'] - cq, axis=1)
    th = np.percentile(np.concatenate([dk, dq]), 95)
    Dk = np.linalg.norm(Is - ck, axis=1); Dq = np.linalg.norm(Is - cq, axis=1)
    ident = 1 / (1 + Dq) - 1 / (1 + Dk); inr = (Dk <= th) | (Dq <= th)
    out = {}
    for r, like in (('kona', inr & (ident <= 0)), ('kau', inr & (ident > 0))):
        T = FTemp[idx][rr == r]
        mu = T.mean(); sg = T.std(ddof=1) * 1.5
        pool = np.sort(Tflat[farm & like])
        if pool.size < 10:
            return None
        # |F(dT)| = #{ mu - HW*sg - dT <= T <= mu + HW*sg - dT }
        lo = np.searchsorted(pool, mu - HW * sg - SWEEP, side='left')
        hi = np.searchsorted(pool, mu + HW * sg - SWEEP, side='right')
        out[r] = SWEEP[int(np.argmax(hi - lo))]
    return out


base = peaks(np.arange(len(FT)))
print(f"observed peak offsets (relative to the 1990-2021 climatological mean):")
print(f"  Kona {base['kona']:+.2f} °C   Ka'u {base['kau']:+.2f} °C\n")

res = {'kona': [], 'kau': [], 'diff': []}
for b in range(NB):
    idx = np.concatenate([np.concatenate([gi[lb == k] for k in rng.integers(0, nb, nb)])
                          for gi, lb, nb in (blocks[r] for r in ('kona', 'kau'))])
    if (reg[idx] == 'kau').sum() < 5 or (reg[idx] == 'kona').sum() < 5:
        continue
    try:
        p = peaks(idx)
    except Exception:
        continue
    if p:
        res['kona'].append(p['kona']); res['kau'].append(p['kau'])
        res['diff'].append(p['kona'] - p['kau'])

OUT = {}
NUM = json.load(open(os.path.join(HERE, '..', 'paper_numbers.json')))
SHIFT = NUM['offset_belt_to_endrec']       # measured warming, climatology mean -> 2021
# The shift is itself estimated -- a trend of +0.313 +/- 0.065 C/decade extrapolated
# over the record. Re-centring by the point estimate alone understates the interval,
# so draw the shift per replicate instead of subtracting a constant. The two are
# independent (one is a spatial resample of farm cells, the other a temporal
# regression on island-mean temperature), so an independent draw is the right pairing.
SPAN_DEC = SHIFT / NUM['trend_belt_per_decade']          # decades of extrapolation
SHIFT_SE = NUM['trend_belt_se_per_decade'] * SPAN_DEC
OUT['recentre_shift'] = float(SHIFT); OUT['recentre_shift_se'] = float(SHIFT_SE)
print(f"re-centring shift {SHIFT:+.3f} +/- {SHIFT_SE:.3f} °C "
      f"({SPAN_DEC:.2f} decades at {NUM['trend_belt_per_decade']:+.3f} +/- "
      f"{NUM['trend_belt_se_per_decade']:.3f} °C/decade)\n")
print(f"{'district':>9} {'peak':>7} {'95% CI':>18} {'n':>6}   re-centred on end of record (2021)")
for r in ('kona', 'kau'):
    a = np.array(res[r])
    lo, hi = np.percentile(a, [2.5, 97.5])
    rc = a - rng.normal(SHIFT, SHIFT_SE, size=a.size)
    rlo, rhi = np.percentile(rc, [2.5, 97.5])
    OUT[f'Fpeak_{r}_ci_lo'] = float(lo); OUT[f'Fpeak_{r}_ci_hi'] = float(hi)
    OUT[f'Fpeak_{r}_boot_median'] = float(np.median(a))
    OUT[f'Fpeak_{r}_recentred'] = float(base[r] - SHIFT)
    OUT[f'Fpeak_{r}_recentred_ci_lo'] = float(rlo)
    OUT[f'Fpeak_{r}_recentred_ci_hi'] = float(rhi)
    OUT[f'Fpeak_{r}_excludes_zero'] = bool(hi < 0 or lo > 0)
    OUT[f'Fpeak_{r}_recentred_excludes_zero'] = bool(rhi < 0 or rlo > 0)
    print(f"{r:>9} {base[r]:>+7.2f} {f'({lo:+.2f}, {hi:+.2f})':>18} {len(a):>6}   "
          f"{base[r]-SHIFT:+.2f} ({rlo:+.2f}, {rhi:+.2f})"
          f"{'  PAST PEAK' if rhi < 0 else ''}"
          f"   [unpropagated: ({lo-SHIFT:+.2f}, {hi-SHIFT:+.2f})]")

d = np.array(res['diff'])
dlo, dhi = np.percentile(d, [2.5, 97.5])
OUT['Fpeak_diff'] = float(base['kona'] - base['kau'])
OUT['Fpeak_diff_ci_lo'] = float(dlo); OUT['Fpeak_diff_ci_hi'] = float(dhi)
OUT['Fpeak_diff_excludes_zero'] = bool(dhi < 0 or dlo > 0)
print(f"\nKona - Ka'u offset difference: {base['kona']-base['kau']:+.2f} °C "
      f"(95% CI {dlo:+.2f}, {dhi:+.2f})"
      f"{'  -- districts differ significantly' if dhi < 0 or dlo > 0 else '  -- not distinguishable'}")

print(f"\nmeasured warming from the {int(NUM['clim_midpoint'])} climatological mean to end of "
      f"record (2021): {SHIFT:+.3f} °C (belt trend "
      f"{NUM['trend_belt_per_decade']:+.3f} °C/decade)")

pn = os.path.join(HERE, '..', 'paper_numbers.json')
_d = json.load(open(pn)); _d.update(OUT); json.dump(_d, open(pn, 'w'), indent=1)
print(f"merged {len(OUT)} keys into paper_numbers.json")

assert abs(base['kona'] - (-0.65)) < 0.06, f"Kona peak {base['kona']}, expected -0.65"
assert abs(base['kau'] - 0.15) < 0.06, f"Ka'u peak {base['kau']}, expected +0.15"
print("selfcheck: point estimates reproduce ML/09 and ML/10")
