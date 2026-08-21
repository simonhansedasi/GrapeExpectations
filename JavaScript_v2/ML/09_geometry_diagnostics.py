#!/usr/bin/env python3
"""
Geometry diagnostics for the F = C ∩ S claim. Four tests, in review priority order:

  A. |F_r|(ΔT) swept from -1.5 to +1.35 °C.  THE BLOCKER.
     If |F| peaks at ΔT=0 and is symmetric, the contraction is guaranteed by
     construction (C and S are both anchored to the same 471 farm cells) and the
     paper's central claim is an artefact. If it peaks left of zero, the belt was
     already past optimal alignment at baseline and the contraction is earned.

  B. Contraction (ΔT 1.00 -> 1.35) across the full parameter grid: sigma inflation,
     terrain threshold, tau, distance metric. The abstract claims the contraction
     survives "every parameter setting tested"; only two were ever swept.

  C. Elevation-band cross-validation. The latitude-band folds test whether the
     screen is uniform ALONG the belt; the upper boundary is the entire contraction
     mechanism, so what matters is whether it is uniform ACROSS it.

  D. Terrain features vs elevation on the west flank, 300-1500 m. Tests the
     load-bearing assertion that terrain "departs from the observed farm envelope"
     above ~950 m, rather than the boundary being the tail of the farm sample.

Run from repo root:  python ML/09_geometry_diagnostics.py
Writes img/09_*.png and merges results into paper_numbers.json.

ponytail: loader block duplicated from 08_table_s1.py rather than factored into a
shared module. Extract if a 10th script needs it; two copies is not yet a library.
"""
import json, os
import numpy as np
import pandas as pd
import geopandas as gpd
import rasterio
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from scipy.ndimage import maximum_filter, minimum_filter, distance_transform_edt
from scipy.linalg import inv

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, '..', 'data')
IMG = os.path.join(HERE, '..', 'img')

# ── load: DEM, terrain features, climatology, lava, farm cells ────────────────
with rasterio.open(f'{DATA}/DEM/hawaii_DEM_500m_utm.tif') as s:
    nd = s.nodata; dem = s.read(1).astype(np.float32); tr = s.transform
    H, W = s.height, s.width; crs = s.crs
dem[dem == nd] = np.nan; dem[dem <= 0] = np.nan; land = ~np.isnan(dem)
sm = np.nanmean(dem[land]); dev = dem - sm; ef = np.where(land, dem, sm)
dy, dx = np.gradient(ef, 500., 500.)
slope = np.degrees(np.arctan(np.sqrt(dx**2 + dy**2))); asp = np.arctan2(-dx, dy)
asin, acos = np.sin(asp), np.cos(asp)
smax = maximum_filter(slope, size=3, mode='nearest')
emax = maximum_filter(ef, size=3, mode='nearest'); emin = minimum_filter(ef, size=3, mode='nearest')
relief = emax - emin; local = dem - emin
for a in [dev, smax, asin, acos, relief, local]:
    a[~land] = np.nan
dcoast = distance_transform_edt(land) * 500.; dcoast[~land] = np.nan
flat = land.ravel()
FEATNAMES = ['elevation', 'elev. deviation', 'max slope', 'aspect sin',
             'aspect cos', 'total relief', 'local relief', 'coast distance']
X = np.column_stack([a.ravel()[flat] for a in [dem, dev, smax, asin, acos, relief, local, dcoast]])

with rasterio.open(f'{DATA}/DEM/hawaii_temp_climatology_500m_utm.tif') as s:
    tc = s.read(1).astype(np.float32); tnd = s.nodata
tc[tc == tnd] = np.nan; tc[~land] = np.nan
Tflat = tc.ravel()[flat]
with rasterio.open(f'{DATA}/DEM/hawaii_historic_lava_500m_utm.tif') as s:
    lava = (s.read(1) == 1)
farm = (smax.ravel()[flat] <= 25.) & (~np.isnan(smax.ravel()[flat])) & (~lava.ravel()[flat])

# island-cell coordinates, for the west-flank slice in (D)
rows_i, cols_i = np.divmod(np.arange(H * W)[flat], W)
Ex = tr.c + (cols_i + 0.5) * tr.a
Ny = tr.f + (rows_i + 0.5) * tr.e
Zisl = X[:, 0]

allf = pd.read_pickle(f'{DATA}/plot_all_features.pkl')
fp = gpd.GeoDataFrame(allf[allf.label == 1].copy(), geometry='geometry', crs='EPSG:4326').to_crs(crs)
cen = fp.geometry.centroid
ci = ((cen.x - tr.c) / tr.a).astype(int).values; ri = ((cen.y - tr.f) / tr.e).astype(int).values
ok = (ri >= 0) & (ri < H) & (ci >= 0) & (ci < W)
FT = np.column_stack([a[ri[ok], ci[ok]] for a in [dem, dev, smax, asin, acos, relief, local, dcoast]])
with rasterio.open(f'{DATA}/DEM/hawaii_temp_climatology_500m_utm.tif') as s:
    FTemp = np.array([v[0] for v in s.sample(zip(cen.x[ok], cen.y[ok]))])
reg = fp['region'].values[ok]
good = ~np.isnan(FT).any(axis=1)
FT, FTemp, reg = FT[good], FTemp[good], reg[good]
FX, FY = cen.x[ok][good].values, cen.y[ok][good].values

OUT = {}
print(f"loaded: {land.sum():,} land cells, {farm.sum():,} farmable, {len(FT)} farm cells "
      f"({(reg=='kona').sum()} Kona, {(reg=='kau').sum()} Ka'u)\n")


# ── screen machinery ─────────────────────────────────────────────────────────
def build_screen(FTsub, regsub, pct=95, metric='euclid', cols=None, wz=1.0):
    """Fit standardiser, centroids and threshold on a farm-cell subset.
    Returns (like_kona, like_kau) boolean masks over island land cells, plus a
    callable that scores arbitrary standardised rows (used by the CV in C).
    `cols` restricts the feature set -- used to rebuild the screen without
    elevation, which is the test of whether C and S share a coordinate.
    `wz` scales the standardised elevation coordinate: 0 removes elevation,
    1 is the corrected screen, 2 reproduces the collinear-duplicate weighting."""
    c = slice(None) if cols is None else list(cols)
    FTsub = FTsub[:, c]
    sc = StandardScaler().fit(FTsub)
    Fs = sc.transform(FTsub); Is = sc.transform(X[:, c])
    if wz != 1.0:
        # elevation is source column 0; find where it landed after the cols subset
        active = list(range(8)) if cols is None else list(cols)
        zi = active.index(0) if 0 in active else None
        if zi is not None:
            Fs = Fs.copy(); Is = Is.copy()
            Fs[:, zi] *= wz; Is[:, zi] *= wz
    ck = Fs[regsub == 'kona'].mean(0); cq = Fs[regsub == 'kau'].mean(0)
    if metric == 'maha':
        _d = np.vstack([Fs[regsub == 'kona'] - ck, Fs[regsub == 'kau'] - cq])
        VI = inv(np.cov(_d.T))
        d = lambda A, c: np.sqrt(np.einsum('ij,jk,ik->i', A - c, VI, A - c))
    else:
        d = lambda A, c: np.linalg.norm(A - c, axis=1)
    th = np.percentile(np.concatenate([d(Fs[regsub == 'kona'], ck), d(Fs[regsub == 'kau'], cq)]), pct)
    Dk, Dq = d(Is, ck), d(Is, cq)
    ident = 1 / (1 + Dq) - 1 / (1 + Dk)
    inr = (Dk <= th) | (Dq <= th)
    like = {'kona': inr & (ident <= 0), 'kau': inr & (ident > 0)}
    return like, (sc, ck, cq, d, th)


def envelope(r, sigma_mult=1.5, FTempsub=None, regsub=None):
    T = (FTemp if FTempsub is None else FTempsub)[(reg if regsub is None else regsub) == r]
    return T.mean(), T.std(ddof=1) * sigma_mult


# The corrected feature set: elevation deviation dropped, being an exact scalar
# offset of mean elevation (r = 1.000). See ML/10_screen_corrected.py.
CORR = [0, 2, 3, 4, 5, 6, 7]
LIKE95, _ = build_screen(FT, reg, 95, 'euclid', cols=CORR)
LIKE_PUB8, _ = build_screen(FT, reg, 95, 'euclid')
MU = {r: envelope(r)[0] for r in ('kona', 'kau')}
SG = {r: envelope(r)[1] for r in ('kona', 'kau')}


def setsizes(r, dT, like=None, mu=None, sg=None, tau=0.5):
    """(|C_r|, |F_r|) at warming dT. C is farmable island cells above tau;
    F is C intersected with the district's terrain footprint."""
    mu = MU[r] if mu is None else mu; sg = SG[r] if sg is None else sg
    like = LIKE95[r] if like is None else like
    S = np.exp(-0.5 * ((Tflat + dT - mu) / sg) ** 2)
    C = farm & (S > tau)
    return int(C.sum()), int((C & like).sum())


# ── A. the blocker: |F_r|(ΔT) ────────────────────────────────────────────────
print("=" * 78)
print("A. |F_r| swept over ΔT  --  does the intersection peak at ΔT = 0?")
print("=" * 78)
sweep = np.round(np.arange(-3.0, 3.001, 0.01), 2)
A = {r: np.array([setsizes(r, t) for t in sweep]) for r in ('kona', 'kau')}
print(f"{'ΔT':>7} | {'|C| kona':>9} {'|F| kona':>9} | {'|C| kau':>9} {'|F| kau':>9}")
for t in [-1.5, -1.0, -0.5, -0.25, 0.0, 0.25, 0.5, 1.0, 1.35]:
    i = int(np.argmin(np.abs(sweep - t)))
    print(f"{sweep[i]:+7.2f} | {A['kona'][i,0]:9,d} {A['kona'][i,1]:9,d} | "
          f"{A['kau'][i,0]:9,d} {A['kau'][i,1]:9,d}")

for r in ('kona', 'kau'):
    F = A[r][:, 1]
    pk = sweep[int(np.argmax(F))]
    # symmetry about the peak, over ±1.35 °C
    lo = np.interp(pk - 1.35, sweep, F); hi = np.interp(pk + 1.35, sweep, F)
    OUT[f'Fpeak_{r}'] = float(pk)
    OUT[f'Fpeak_{r}_val'] = int(F.max())
    OUT[f'Fasym_{r}'] = float(hi / lo) if lo > 0 else np.nan
    print(f"\n  {r}: |F| peaks at ΔT = {pk:+.2f} °C ({F.max():,} cells); "
          f"|F| at peak-1.35 = {lo:,.0f}, at peak+1.35 = {hi:,.0f} "
          f"(asymmetry {hi/lo:.2f}x)")
    print(f"       |F| at ΔT=0: {F[np.argmin(np.abs(sweep))]:,d}   "
          f"at +1.00: {np.interp(1.0,sweep,F):,.0f}   at +1.35: {np.interp(1.35,sweep,F):,.0f}")

fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
for ax, r, nm in zip(axes, ('kona', 'kau'), ('Kona', "Ka'u")):
    ax.plot(sweep, A[r][:, 0], color='#888888', lw=1.5, label=r'$|\mathcal{C}|$ (island-wide)')
    ax.plot(sweep, A[r][:, 1], color='#c1440e', lw=2.2, label=r'$|\mathcal{F}| = |\mathcal{C}\cap\mathcal{S}|$')
    ax.axvline(0, color='k', ls=':', lw=1)
    ax.axvspan(1.00, 1.35, color='#c1440e', alpha=0.10)
    ax.axvline(sweep[int(np.argmax(A[r][:, 1]))], color='#c1440e', ls='--', lw=1)
    ax.set_xlabel(r'$\Delta T$ (°C)'); ax.set_title(nm)
    ax.set_ylabel('farmable cells' if r == 'kona' else '')
    ax.legend(frameon=False, fontsize=9)
fig.tight_layout(); fig.savefig(f'{IMG}/09_F_vs_dT.png', dpi=200); plt.close(fig)
print(f"\n  -> {IMG}/09_F_vs_dT.png")


# ── B. contraction across the full parameter grid ────────────────────────────
print("\n" + "=" * 78)
print("B. contraction of |F_r| from ΔT=+1.00 to +1.35, full parameter grid")
print("=" * 78)
grid = []
for metric in ('euclid', 'maha'):
    for pct in (90, 92.5, 95, 97.5):
        like, _ = build_screen(FT, reg, pct, metric, cols=CORR)
        for smult in (1.0, 1.25, 1.5, 1.75, 2.0):
            for tau in (0.1, 0.25, 0.5, 0.8):
                for r in ('kona', 'kau'):
                    mu, sg = envelope(r, smult)
                    _, f1 = setsizes(r, 1.00, like[r], mu, sg, tau)
                    _, f2 = setsizes(r, 1.35, like[r], mu, sg, tau)
                    grid.append(dict(metric=metric, pct=pct, sigma=smult, tau=tau, region=r,
                                     F1=f1, F2=f2,
                                     contraction=100 * (f2 - f1) / f1 if f1 else np.nan))
G = pd.DataFrame(grid)
G.to_csv(f'{IMG}/../ML/09_sensitivity_grid.csv', index=False)
for r in ('kona', 'kau'):
    g = G[G.region == r].dropna(subset=['contraction'])
    n_contract = (g.contraction < 0).sum()
    print(f"\n  {r}: {n_contract}/{len(g)} settings contract; "
          f"range {g.contraction.min():+.1f}% to {g.contraction.max():+.1f}% "
          f"(median {g.contraction.median():+.1f}%)")
    OUT[f'sens_n_{r}'] = int(n_contract); OUT[f'sens_tot_{r}'] = int(len(g))
    OUT[f'sens_min_{r}'] = float(g.contraction.min()); OUT[f'sens_max_{r}'] = float(g.contraction.max())
    OUT[f'sens_med_{r}'] = float(g.contraction.median())
    for by in ('metric', 'pct', 'sigma', 'tau'):
        s = g.groupby(by).contraction.median()
        print(f"      by {by:7s}: " + "  ".join(f"{k}={v:+.1f}%" for k, v in s.items()))
    if (g.contraction >= 0).any():
        print("      NON-CONTRACTING SETTINGS:")
        print(g[g.contraction >= 0].to_string(index=False, max_rows=12))


# ── C. elevation-band cross-validation ───────────────────────────────────────
print("\n" + "=" * 78)
print("C. elevation-band cross-validation (does the screen extend ACROSS the belt?)")
print("=" * 78)
Zf = FT[:, 0]
FTC = FT[:, CORR]   # cross-validate the corrected screen, not the published one
edges = np.percentile(Zf, [0, 20, 40, 60, 80, 100])
print(f"  farm-cell elevation quintile edges: {np.round(edges).astype(int)} m")
print(f"{'held-out band':>18} {'n':>5} {'recall':>8}   (in-sample reference below)")
recalls = []
for i in range(5):
    lo, hi = edges[i], edges[i + 1]
    heldout = (Zf >= lo) & (Zf <= hi if i == 4 else Zf < hi)
    keep = ~heldout
    if (reg[keep] == 'kau').sum() < 5 or (reg[keep] == 'kona').sum() < 5:
        print(f"  {int(lo)}-{int(hi)} m: skipped, too few remaining cells in one district")
        continue
    sc = StandardScaler().fit(FTC[keep])
    Fs = sc.transform(FTC[keep])
    ck = Fs[reg[keep] == 'kona'].mean(0); cq = Fs[reg[keep] == 'kau'].mean(0)
    d = lambda A, c: np.linalg.norm(A - c, axis=1)
    th = np.percentile(np.concatenate([d(Fs[reg[keep] == 'kona'], ck), d(Fs[reg[keep] == 'kau'], cq)]), 95)
    Ho = sc.transform(FTC[heldout])
    own = np.where(reg[heldout][:, None] == 'kona', d(Ho, ck)[:, None], d(Ho, cq)[:, None]).ravel()
    rec = 100 * (own <= th).mean()
    recalls.append(rec)
    print(f"  {int(lo):>6}-{int(hi):<6} m {heldout.sum():>5} {rec:>7.1f}%")
# in-sample reference, same construction on all cells
sc = StandardScaler().fit(FTC); Fs = sc.transform(FTC)
ck = Fs[reg == 'kona'].mean(0); cq = Fs[reg == 'kau'].mean(0)
d = lambda A, c: np.linalg.norm(A - c, axis=1)
th = np.percentile(np.concatenate([d(Fs[reg == 'kona'], ck), d(Fs[reg == 'kau'], cq)]), 95)
own = np.where(reg[:, None] == 'kona', d(Fs, ck)[:, None], d(Fs, cq)[:, None]).ravel()
insample = 100 * (own <= th).mean()
print(f"  {'in-sample':>13} {len(FT):>5} {insample:>7.1f}%")
OUT['elevcv_mean'] = float(np.mean(recalls)); OUT['elevcv_min'] = float(np.min(recalls))
OUT['elevcv_insample'] = float(insample)
print(f"\n  mean out-of-band recall {np.mean(recalls):.0f}% (worst fold {np.min(recalls):.0f}%) "
      f"against {insample:.1f}% in-sample")

# the decisive sub-test: fit on the LOWER belt only, ask for the upper fringe
lowmask = Zf < np.percentile(Zf, 60)
sc = StandardScaler().fit(FTC[lowmask]); Fs = sc.transform(FTC[lowmask])
ck = Fs[reg[lowmask] == 'kona'].mean(0); cq = Fs[reg[lowmask] == 'kau'].mean(0)
th = np.percentile(np.concatenate([d(Fs[reg[lowmask] == 'kona'], ck), d(Fs[reg[lowmask] == 'kau'], cq)]), 95)
Hi = sc.transform(FTC[~lowmask])
own = np.where(reg[~lowmask][:, None] == 'kona', d(Hi, ck)[:, None], d(Hi, cq)[:, None]).ravel()
OUT['elevcv_upper_from_lower'] = float(100 * (own <= th).mean())
print(f"  fit on lower 60% of the belt -> recovers {OUT['elevcv_upper_from_lower']:.0f}% "
      f"of the upper 40% ({(~lowmask).sum()} cells)")


# ── D. terrain features vs elevation on the west flank ───────────────────────
print("\n" + "=" * 78)
print("D. do terrain features break above the footprint's upper boundary (~950 m)?")
print("=" * 78)
kx, ky = FX[reg == 'kona'], FY[reg == 'kona']
slab = ((Ny >= ky.min() - 2000) & (Ny <= ky.max() + 2000) &
        (Ex <= kx.max() + 5000) & (Zisl >= 300) & (Zisl <= 1500))
print(f"  west-flank slab: {slab.sum():,} island cells, "
       f"{Zisl[slab].min():.0f}-{Zisl[slab].max():.0f} m")

# standardise on farm cells so "departure" is in the same units the screen uses
scf = StandardScaler().fit(FT)
Sl = scf.transform(X[slab]); Zs = Zisl[slab]
bins = np.arange(300, 1501, 50); mid = bins[:-1] + 25
idx = np.digitize(Zs, bins) - 1
prof = np.full((len(mid), 8), np.nan)
for b in range(len(mid)):
    m = idx == b
    if m.sum() >= 5:
        prof[b] = Sl[m].mean(0)
# distance from the Kona farm centroid, per elevation bin -- the screen's own metric
ckf = scf.transform(FT)[reg == 'kona'].mean(0)
dprof = np.array([np.linalg.norm(Sl[idx == b] - ckf, axis=1).mean() if (idx == b).sum() >= 5 else np.nan
                  for b in range(len(mid))])
thk = np.percentile(np.linalg.norm(scf.transform(FT)[reg == 'kona'] - ckf, axis=1), 95)

# elevation deviation (index 1) is the deleted duplicate -- not plotted here; it is
# identical to the elevation panel by construction and belongs in the supplement.
PLOTK = [0, 2, 3, 4, 5, 6, 7]
fig, axes = plt.subplots(3, 3, figsize=(12, 9), sharex=True)
for j, ax in enumerate(axes.ravel()[:7]):
    k = PLOTK[j]
    ax.plot(mid, prof[:, k], color='#1f4e79', lw=1.8)
    ax.axvspan(FT[reg == 'kona', 0].min(), FT[reg == 'kona', 0].max(), color='#c1440e', alpha=0.10)
    ax.axvline(950, color='k', ls='--', lw=1)
    ax.set_title(FEATNAMES[k], fontsize=10)
    ax.set_ylabel('z-score (farm-cell scale)' if j % 3 == 0 else '', fontsize=8)
axes.ravel()[8].axis('off')
ax = axes.ravel()[7]
ax.plot(mid, dprof, color='#c1440e', lw=2)
ax.axhline(thk, color='k', ls=':', lw=1.2)
ax.axvline(950, color='k', ls='--', lw=1)
ax.set_title('distance to Kona centroid', fontsize=10)
for ax in axes[-1]:
    ax.set_xlabel('elevation (m)')
fig.tight_layout(); fig.savefig(f'{IMG}/09_features_vs_elevation.png', dpi=200); plt.close(fig)
print(f"  -> {IMG}/09_features_vs_elevation.png")

# which features actually move, and where: slope of each feature per 100 m,
# below vs above 950 m, in farm-cell SD units
below = (mid >= 400) & (mid <= 900); above = (mid >= 950) & (mid <= 1400)
print(f"\n  {'feature':>16} {'z-slope/100m below 950':>24} {'above 950':>12} {'ratio':>8}")
for k in range(8):
    yb, ya = prof[below, k], prof[above, k]
    sb = np.polyfit(mid[below][~np.isnan(yb)], yb[~np.isnan(yb)], 1)[0] * 100
    sa = np.polyfit(mid[above][~np.isnan(ya)], ya[~np.isnan(ya)], 1)[0] * 100
    OUT[f'featslope_below_{k}'] = float(sb); OUT[f'featslope_above_{k}'] = float(sa)
    print(f"  {FEATNAMES[k]:>16} {sb:>24.3f} {sa:>12.3f} {abs(sa)/max(abs(sb),1e-6):>8.1f}")
zx = mid[~np.isnan(dprof)]; dv = dprof[~np.isnan(dprof)]
cross = np.interp(thk, dv[zx > 500], zx[zx > 500]) if (dv[zx > 500] > thk).any() else np.nan
OUT['centroid_dist_crosses_threshold_m'] = float(cross)
print(f"\n  mean distance-to-Kona-centroid crosses the 95th-pct threshold at "
      f"{cross:.0f} m elevation (footprint upper bound is 950 m)")

# ── E. does the screen share a coordinate with the thermal band? ─────────────
print("\n" + "=" * 78)
print("E. rebuild S WITHOUT elevation -- is the |F| peak an artefact of the shared axis?")
print("=" * 78)
Ffs = StandardScaler().fit_transform(FT)
R = np.corrcoef(Ffs.T)
print("  correlation of each terrain feature with elevation, across the 471 farm cells:")
for k in range(1, 8):
    print(f"    {FEATNAMES[k]:>16}: r = {R[0, k]:+.3f}" +
          ("   <-- perfectly collinear: elevation enters the metric twice"
           if abs(R[0, k]) > 0.999 else ""))
OUT['r_elev_dev'] = float(R[0, 1])

# three screens: as published (elevation twice), de-duplicated (once), and none
VARIANTS = [('published (8 feat.)', None, '#c1440e', '-'),
            ('elevation once (7 feat.)', [0, 2, 3, 4, 5, 6, 7], '#7a3b8f', '-.'),
            ('no elevation (6 feat.)', [2, 3, 4, 5, 6, 7], '#1f4e79', '--')]
curves = {}
print(f"\n  {'screen':>26} {'district':>8} {'footprint':>10} {'Jaccard':>8} {'|F| peak':>9} {'contraction':>12}")
for nm, cols, _c, _ls in VARIANTS:
    likeV, _ = build_screen(FT, reg, 95, 'euclid', cols=cols)
    key = 'pub' if cols is None else ('dedup' if len(cols) == 7 else 'noelev')
    for r in ('kona', 'kau'):
        F = np.array([setsizes(r, t, likeV[r])[1] for t in sweep])
        curves[(key, r)] = F
        pk = sweep[int(np.argmax(F))]
        f1, f2 = np.interp(1.00, sweep, F), np.interp(1.35, sweep, F)
        jac = 100 * (likeV[r] & LIKE95[r]).sum() / max((likeV[r] | LIKE95[r]).sum(), 1)
        fpt = 100 * likeV[r].sum() / len(X)
        OUT[f'Fpeak_{key}_{r}'] = float(pk)
        OUT[f'Frchange_{key}_{r}'] = float(100 * (f2 - f1) / f1)
        OUT[f'pct_{r}_like_{key}'] = float(fpt)
        print(f"  {nm:>26} {r:>8} {fpt:>9.1f}% {jac:>7.0f}% {pk:>+8.2f}° "
              f"{100*(f2-f1)/f1:>+11.1f}%")

fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
for ax, r, nm in zip(axes, ('kona', 'kau'), ('Kona', "Ka'u")):
    for lbl, cols, c, ls in VARIANTS:
        key = 'pub' if cols is None else ('dedup' if len(cols) == 7 else 'noelev')
        F = curves[(key, r)]
        ax.plot(sweep, F / F.max(), color=c, ls=ls, lw=2.0, label=lbl)
    ax.axvline(0, color='k', ls=':', lw=1); ax.axvspan(1.00, 1.35, color='#c1440e', alpha=0.10)
    ax.set_xlabel(r'$\Delta T$ (°C)'); ax.set_title(nm)
    ax.set_ylabel(r'$|\mathcal{F}|$ / max' if r == 'kona' else '')
    ax.legend(frameon=False, fontsize=8)
fig.tight_layout(); fig.savefig(f'{IMG}/09_F_vs_dT_noelev.png', dpi=200); plt.close(fig)
print(f"  -> {IMG}/09_F_vs_dT_noelev.png")

# ── F. elevation weight as a fifth factor ────────────────────────────────────
print("\n" + "=" * 78)
print("F. continuous sweep of the elevation weight in S (0 = absent, 1 = corrected,")
print("   sqrt(2) ~ 1.41 = the v2 collinear duplicate: two unit columns contribute 2 in")
print("   squared distance, so duplicating elevation is equivalent to scaling it by sqrt(2))")
print("=" * 78)
print(f"  {'w_z':>5} {'Kona footprint':>15} {'Kona peak':>10} {'Kona contr':>11} "
      f"{'Kau footprint':>14} {'Kau peak':>9} {'Kau contr':>10}")
WROWS = []
for wz in np.round(np.arange(0.0, 2.001, 0.1), 2):
    lk, _ = build_screen(FT, reg, 95, 'euclid', cols=CORR, wz=wz)
    row = {'wz': float(wz)}
    for r in ('kona', 'kau'):
        F = np.array([setsizes(r, t, lk[r])[1] for t in sweep])
        f1, f2 = np.interp(1.00, sweep, F), np.interp(1.35, sweep, F)
        row[f'{r}_fp'] = 100 * lk[r].sum() / len(X)
        row[f'{r}_peak'] = float(sweep[int(np.argmax(F))])
        row[f'{r}_contr'] = float(100 * (f2 - f1) / f1) if f1 else np.nan
    WROWS.append(row)
    print(f"  {wz:>5.1f} {row['kona_fp']:>14.1f}% {row['kona_peak']:>+9.2f}° "
          f"{row['kona_contr']:>+10.1f}% {row['kau_fp']:>13.1f}% {row['kau_peak']:>+8.2f}° "
          f"{row['kau_contr']:>+9.1f}%")
WG = pd.DataFrame(WROWS)
WG.to_csv(f'{HERE}/09_elevation_weight_sweep.csv', index=False)
for r in ('kona', 'kau'):
    OUT[f'wz_contr_min_{r}'] = float(WG[f'{r}_contr'].min())
    OUT[f'wz_contr_max_{r}'] = float(WG[f'{r}_contr'].max())
    OUT[f'wz_peak_min_{r}'] = float(WG[f'{r}_peak'].min())
    OUT[f'wz_peak_max_{r}'] = float(WG[f'{r}_peak'].max())
    print(f"  {r}: contraction spans {WG[f'{r}_contr'].min():+.1f}% to "
          f"{WG[f'{r}_contr'].max():+.1f}%; peak spans {WG[f'{r}_peak'].min():+.2f} to "
          f"{WG[f'{r}_peak'].max():+.2f} °C across w_z in [0, 2]")
# validation: w_z = sqrt(2) must reproduce the v2 collinear-duplicate screen
_v2 = WG.iloc[(WG.wz - np.sqrt(2)).abs().idxmin()]
OUT['wz_sqrt2_contr_kona'] = float(_v2.kona_contr); OUT['wz_sqrt2_contr_kau'] = float(_v2.kau_contr)
print(f"  at w_z = {_v2.wz:.1f} (~sqrt2, the duplicate): Kona {_v2.kona_contr:+.1f}%, "
      f"Ka'u {_v2.kau_contr:+.1f}%  vs v2 published -15.5% / -12.4%")
assert abs(_v2.kona_contr + 15.5) < 0.6, f"w_z=sqrt2 gives {_v2.kona_contr:.1f}%, v2 published -15.5%"
assert abs(_v2.kau_contr + 12.4) < 0.6, f"w_z=sqrt2 gives {_v2.kau_contr:.1f}%, v2 published -12.4%"

fig, axes = plt.subplots(1, 2, figsize=(11, 4))
for ax, key, ylab in ((axes[0], 'contr', 'contraction +1.00→+1.35 (%)'),
                      (axes[1], 'peak', 'peak offset (°C)')):
    for r, c, nm in (('kona', '#2166ac', 'Kona'), ('kau', '#d6604d', "Ka'u")):
        ax.plot(WG.wz, WG[f'{r}_{key}'], 'o-', color=c, ms=3, label=nm)
    ax.axvline(1.0, color='k', ls='--', lw=1)
    ax.axvline(2.0, color='#999999', ls=':', lw=1)
    ax.set_xlabel('elevation weight $w_z$ in the terrain screen'); ax.set_ylabel(ylab)
    ax.legend(frameon=False, fontsize=9)
fig.tight_layout(); fig.savefig(f'{IMG}/09_elevation_weight.png', dpi=200); plt.close(fig)
print(f"  -> {IMG}/09_elevation_weight.png")

# ── merge ────────────────────────────────────────────────────────────────────
pn = os.path.join(HERE, '..', 'paper_numbers.json')
d = json.load(open(pn)); d.update(OUT); json.dump(d, open(pn, 'w'), indent=1)
print(f"\nmerged {len(OUT)} keys into paper_numbers.json")


def _selfcheck():
    """Both screens must reproduce their own published/corrected values, so the
    only thing differing between them is the collinear feature."""
    for cols, exp, tag in ((LIKE_PUB8, {'kona': (1371, -15.5), 'kau': (1839, -12.4)}, '8-feature (published)'),
                           (LIKE95, {'kona': (1349, -9.9), 'kau': (1660, -9.5)}, '7-feature (corrected)')):
        like = cols
        for r, (n1, pc) in exp.items():
            _, f = setsizes(r, 1.00, like[r]); _, f2 = setsizes(r, 1.35, like[r])
            assert abs(f - n1) <= 5, f"{tag} |F_{r}| at +1.00 = {f}, expected {n1}"
            got = 100 * (f2 - f) / f
            assert abs(got - pc) < 0.5, f"{tag} {r} contraction {got:.1f}%, expected {pc}%"
    print("selfcheck: both feature sets reproduce their expected |F| and contraction")


_selfcheck()
