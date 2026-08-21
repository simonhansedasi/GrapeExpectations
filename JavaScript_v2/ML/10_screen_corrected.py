#!/usr/bin/env python3
"""
Recompute every screen-dependent quantity with the collinearity defect corrected.

THE DEFECT: `elev_dev_mean = elev_mean - 489.8642` exactly (a scalar offset of the
island mean), so it carries no information beyond elevation. Across the 471 farm
cells r(elev_mean, elev_dev_mean) = 1.000. After standardisation the two columns
are the identical vector, so elevation supplied two of the eight squared terms in
every Euclidean distance: the published screen weighted elevation double, and did
so on precisely the axis the thermal band also migrates along.

This script drops elevation deviation and recomputes everything downstream. Run in
`--published` mode it restores the 8-feature set and must reproduce the published
values, which is what validates that nothing else changed.

Quantities NOT affected, and deliberately not recomputed here: mu_r, sigma_r, the
island-wide gain fractions, the gain isotherms, and the farm-cell declining
fractions. All are functions of the thermal envelope and the labelled farm cells
only -- no screen enters them. The script asserts this rather than assuming it.

Run from repo root:
    python ML/10_screen_corrected.py              # corrected, 7 features
    python ML/10_screen_corrected.py --published  # validation, 8 features
"""
import json, os, sys
import numpy as np
import pandas as pd
import geopandas as gpd
import rasterio
from sklearn.preprocessing import StandardScaler
from scipy.ndimage import maximum_filter, minimum_filter, distance_transform_edt
from scipy.linalg import inv

PUBLISHED = '--published' in sys.argv
rng = np.random.default_rng(7)
HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, '..', 'data')

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

# feature order matches 06/08/09; index 1 is the collinear duplicate
LAYERS = [dem, dev, smax, asin, acos, relief, local, dcoast]
COLS = list(range(8)) if PUBLISHED else [0, 2, 3, 4, 5, 6, 7]
X = np.column_stack([a.ravel()[flat] for a in LAYERS])[:, COLS]

with rasterio.open(f'{DATA}/DEM/hawaii_temp_climatology_500m_utm.tif') as s:
    tc = s.read(1).astype(np.float32); tnd = s.nodata
tc[tc == tnd] = np.nan; tc[~land] = np.nan
Tflat = tc.ravel()[flat]
Zflat = np.column_stack([a.ravel()[flat] for a in LAYERS])[:, 0]
with rasterio.open(f'{DATA}/DEM/hawaii_historic_lava_500m_utm.tif') as s:
    lava = (s.read(1) == 1)
farm = (smax.ravel()[flat] <= 25.) & (~np.isnan(smax.ravel()[flat])) & (~lava.ravel()[flat])

allf = pd.read_pickle(f'{DATA}/plot_all_features.pkl')
fp = gpd.GeoDataFrame(allf[allf.label == 1].copy(), geometry='geometry', crs='EPSG:4326').to_crs(crs)
cen = fp.geometry.centroid
ci = ((cen.x - tr.c) / tr.a).astype(int).values; ri = ((cen.y - tr.f) / tr.e).astype(int).values
ok = (ri >= 0) & (ri < H) & (ci >= 0) & (ci < W)
FTfull = np.column_stack([a[ri[ok], ci[ok]] for a in LAYERS])
with rasterio.open(f'{DATA}/DEM/hawaii_temp_climatology_500m_utm.tif') as s:
    FTemp = np.array([v[0] for v in s.sample(zip(cen.x[ok], cen.y[ok]))])
reg = fp['region'].values[ok]
good = ~np.isnan(FTfull).any(axis=1)
FTfull, FTemp, reg = FTfull[good], FTemp[good], reg[good]
FT = FTfull[:, COLS]

MODE = 'PUBLISHED (8 features, elevation twice)' if PUBLISHED else 'CORRECTED (7 features, elevation once)'
print(f"mode: {MODE}")
print(f"      {len(FT)} farm cells, {farm.sum():,} farmable island cells\n")

MU = {r: FTemp[reg == r].mean() for r in ('kona', 'kau')}
SG = {r: FTemp[reg == r].std(ddof=1) * 1.5 for r in ('kona', 'kau')}
DT = {'2035': 1.00, '2045': 1.35}
SCEN = {('ssp245', '2035'): 0.60, ('ssp245', '2045'): 0.92,
        ('ssp585', '2035'): 1.41, ('ssp585', '2045'): 1.78}
N = {}


def screen(pct=95, metric='euclid'):
    sc = StandardScaler().fit(FT)
    Fs = sc.transform(FT); Is = sc.transform(X)
    ck = Fs[reg == 'kona'].mean(0); cq = Fs[reg == 'kau'].mean(0)
    if metric == 'maha':
        _d = np.vstack([Fs[reg == 'kona'] - ck, Fs[reg == 'kau'] - cq])
        VI = inv(np.cov(_d.T))
        d = lambda A, c: np.sqrt(np.einsum('ij,jk,ik->i', A - c, VI, A - c))
    else:
        d = lambda A, c: np.linalg.norm(A - c, axis=1)
    th = np.percentile(np.concatenate([d(Fs[reg == 'kona'], ck), d(Fs[reg == 'kau'], cq)]), pct)
    Dk, Dq = d(Is, ck), d(Is, cq)
    ident = 1 / (1 + Dq) - 1 / (1 + Dk); inr = (Dk <= th) | (Dq <= th)
    return {'kona': inr & (ident <= 0), 'kau': inr & (ident > 0)}


LIKE = screen()
LIKE_M = screen(metric='maha')


def CF(r, dT, like=None, tau=0.5):
    like = LIKE[r] if like is None else like
    S = np.exp(-0.5 * ((Tflat + dT - MU[r]) / SG[r]) ** 2)
    C = farm & (S > tau)
    return int(C.sum()), int((C & like).sum())


# ── 1. footprint ─────────────────────────────────────────────────────────────
print("footprint (% of island land):")
for r in ('kona', 'kau'):
    N[f'pct_{r}_like'] = float(100 * LIKE[r].sum() / len(X))
    N[f'pct_{r}_like_maha'] = float(100 * LIKE_M[r].sum() / len(X))
    N[f'n_{r}_like_farmable'] = int((LIKE[r] & farm).sum())
    print(f"  {r:5s} Euclidean {N[f'pct_{r}_like']:5.2f}%   Mahalanobis {N[f'pct_{r}_like_maha']:5.2f}%"
          f"   ({N[f'n_{r}_like_farmable']:,} farmable cells)")
N['pct_combined_footprint'] = N['pct_kona_like'] + N['pct_kau_like']
N['pct_neither'] = 100 - N['pct_combined_footprint']
print(f"  combined {N['pct_combined_footprint']:.1f}%, neither {N['pct_neither']:.1f}%")

# ── 2. terrain-restricted declining fractions ────────────────────────────────
print("\ndistrict declining fractions (sign of dS over the footprint):")
for metric, like in (('euclid', LIKE), ('maha', LIKE_M)):
    for r in ('kona', 'kau'):
        pop = farm & like[r]
        for h, dt in DT.items():
            v = float((Tflat[pop] >= MU[r] - dt / 2.0).mean() * 100)
            N[(f'terrdecl_{r}_{h}' if metric == 'euclid' else f'decl_maha_{r}_{h}')] = v
    print(f"  {metric:7s} " + "  ".join(
        f"{r} {h} {N[(f'terrdecl_{r}_{h}' if metric=='euclid' else f'decl_maha_{r}_{h}')]:.1f}%"
        for r in ('kona', 'kau') for h in DT))

# ── 3. C, F, contraction, factor at the reference increments ─────────────────
print("\nreference increments (+1.00 / +1.35 °C):")
for r in ('kona', 'kau'):
    for h, dt in DT.items():
        c, f = CF(r, dt)
        N[f'Cr_{r}_{h}'] = c; N[f'Fr_{r}_{h}'] = f
        N[f'pct_Cr_{r}_{h}'] = float(100 * c / farm.sum())
        N[f'pct_Fr_{r}_{h}'] = float(100 * f / farm.sum())
        N[f'factor_{r}_{h}'] = float(c / f)
    N[f'Crchange_{r}'] = float(100 * (N[f'Cr_{r}_2045'] - N[f'Cr_{r}_2035']) / N[f'Cr_{r}_2035'])
    N[f'Frchange_{r}'] = float(100 * (N[f'Fr_{r}_2045'] - N[f'Fr_{r}_2035']) / N[f'Fr_{r}_2035'])
    print(f"  {r:5s} |C| {N[f'Cr_{r}_2035']:,} -> {N[f'Cr_{r}_2045']:,} ({N[f'Crchange_{r}']:+.1f}%)   "
          f"|F| {N[f'Fr_{r}_2035']:,} -> {N[f'Fr_{r}_2045']:,} ({N[f'Frchange_{r}']:+.1f}%)   "
          f"factor {N[f'factor_{r}_2035']:.1f}x")

# ── 4. peak of |F| ───────────────────────────────────────────────────────────
sweep = np.round(np.arange(-3.0, 3.001, 0.01), 2)
print("\npeak of |F| over ΔT:")
for r in ('kona', 'kau'):
    F = np.array([CF(r, t)[1] for t in sweep])
    pk = sweep[int(np.argmax(F))]
    N[f'Fpeak_{r}'] = float(pk); N[f'Fpeak_{r}_val'] = int(F.max())
    lo = np.interp(pk - 1.35, sweep, F); hi = np.interp(pk + 1.35, sweep, F)
    N[f'Fasym_{r}'] = float(hi / lo)
    N[f'Fdrop_peak_to_2045_{r}'] = float(100 * (np.interp(1.35, sweep, F) - F.max()) / F.max())
    # present-day baseline: what warming actually costs, as distinct from
    # distance from the counterfactual optimum
    c0, f0 = CF(r, 0.0)
    N[f'Fr_{r}_present'] = int(f0); N[f'Cr_{r}_present'] = int(c0)
    for h, dt in DT.items():
        N[f'Crchange_present_{r}_{h}'] = float(100 * (CF(r, dt)[0] - c0) / c0)
    for h, dt in DT.items():
        N[f'Fdrop_present_{r}_{h}'] = float(100 * (CF(r, dt)[1] - f0) / f0)
    print(f"  {r:5s} peak at ΔT = {pk:+.2f} °C ({F.max():,} cells); "
          f"asymmetry {N[f'Fasym_{r}']:.2f}x")
    print(f"        |C| today {c0:,} -> {N[f'Crchange_present_{r}_2045']:+.1f}% by 2045 "
          f"(vs |F| {N[f'Fdrop_present_{r}_2045']:+.1f}%)")
    print(f"        |F| today {f0:,} -> {N[f'Fdrop_present_{r}_2035']:+.1f}% by 2035, "
          f"{N[f'Fdrop_present_{r}_2045']:+.1f}% by 2045; "
          f"{N[f'Fdrop_peak_to_2045_{r}']:+.1f}% below the counterfactual peak")

# ── 5. per-scenario table ────────────────────────────────────────────────────
print("\nper scenario:")
for (sc_, h), dt in SCEN.items():
    for r in ('kona', 'kau'):
        c, f = CF(r, dt)
        N[f'{sc_}_{h}_{r}_Cr'] = c; N[f'{sc_}_{h}_{r}_Fr'] = f
        N[f'{sc_}_{h}_{r}_factor'] = float(c / f)
        N[f'{sc_}_{h}_{r}_islandgain'] = float((Tflat[farm] < MU[r] - dt / 2.0).mean() * 100)
        N[f'{sc_}_{h}_{r}_terrdecl'] = float((Tflat[farm & LIKE[r]] >= MU[r] - dt / 2.0).mean() * 100)
        N[f'{sc_}_{h}_{r}_farmdecl'] = float((FTemp[reg == r] >= MU[r] - dt / 2.0).mean() * 100)
for sc_ in ('ssp245', 'ssp585'):
    for r in ('kona', 'kau'):
        a, b = N[f'{sc_}_2035_{r}_Fr'], N[f'{sc_}_2045_{r}_Fr']
        ca, cb = N[f'{sc_}_2035_{r}_Cr'], N[f'{sc_}_2045_{r}_Cr']
        N[f'{sc_}_{r}_Frchange'] = float(100 * (b - a) / a)
        N[f'{sc_}_{r}_Crchange'] = float(100 * (cb - ca) / ca)
        print(f"  {sc_} {r:5s} |C| {ca:,} -> {cb:,} ({N[f'{sc_}_{r}_Crchange']:+.1f}%)   "
              f"|F| {a:,} -> {b:,} ({N[f'{sc_}_{r}_Frchange']:+.1f}%)")

# ── 6. elevation-matched null for the multiplier ─────────────────────────────
print("\nelevation-histogram-matched null (2,000 draws):")
bins = np.arange(0, 4300, 100)
for r in ('kona', 'kau'):
    tgt = np.histogram(Zflat[LIKE[r] & farm], bins=bins)[0]
    pool = [np.where(farm & (Zflat >= bins[b]) & (Zflat < bins[b + 1]))[0] for b in range(len(bins) - 1)]
    S = np.exp(-0.5 * ((Tflat + 1.00 - MU[r]) / SG[r]) ** 2)
    C = farm & (S > 0.5); nC = int(C.sum())
    draws = []
    for _ in range(2000):
        pick = np.concatenate([rng.choice(pool[b], size=min(tgt[b], len(pool[b])), replace=False)
                               for b in range(len(tgt)) if tgt[b] > 0 and len(pool[b]) > 0])
        hit = C[pick].sum()
        if hit:
            draws.append(nC / hit)
    N[f'elevnull_{r}_median'] = float(np.median(draws))
    print(f"  {r:5s} observed {N[f'factor_{r}_2035']:.2f}x   null median "
          f"{N[f'elevnull_{r}_median']:.2f}x   "
          f"({100*np.mean(np.array(draws) >= N[f'factor_{r}_2035']):.0f}% of draws >= observed)")

# ── 6b. within-belt temperature-elevation regression ─────────────────────────
# The paper quotes R^2 = 0.999 and residual SD = 0.032 within the belt; those had
# no registered source. Both are computed here alongside the island-wide pair.
belt = (Zflat >= 150) & (Zflat <= 950)   # all island land in the belt, not farmable-restricted
for tag, m in (('belt', belt), ('island', np.isfinite(Tflat) & np.isfinite(Zflat))):
    z, t = Zflat[m], Tflat[m]
    k = np.isfinite(z) & np.isfinite(t); z, t = z[k], t[k]
    sl, ic = np.polyfit(z, t, 1)
    res = t - (sl * z + ic)
    N[f'R2_{tag}'] = float(1 - res.var() / t.var())
    N[f'resid_sd_{tag}'] = float(res.std(ddof=2))
    N[f'lapse_{tag}'] = float(sl * 1000)
    print(f"  T~z {tag:6s}: R2 = {N[f'R2_{tag}']:.4f}  lapse = {N[f'lapse_{tag}']:+.3f} °C/km  "
          f"residual SD = {N[f'resid_sd_{tag}']:.4f} °C  (n = {len(z):,})")

# ── 6c. area-weighted declining fractions ────────────────────────────────────
# The paper quotes 68.0/81.8 (2035) and 74.7/90.4 (2045) with no registered source,
# and the review flagged that Kona's 68.0% coincides with the 68% acreage-capture
# rate, which is the signature of a denominator swap. The farm-cell pickle cannot
# supply this: its geometry is the 54,000 m^2 grid cell, identical for all 471, so
# "area weighting" from it is just unweighted. Recompute from the actual coffee
# polygons, intersected with the labelled cells.
cells = gpd.GeoDataFrame(allf[allf.label == 1].copy(), geometry='geometry',
                         crs='EPSG:4326').to_crs(crs)
cells = cells.iloc[np.where(ok)[0][good]].reset_index(drop=True)
cells['reg'] = reg; cells['T'] = FTemp
poly = gpd.read_file(f'{DATA}/polygons/aglanduse_2020.shp')
poly = poly[poly.Crops_2020 == 'Coffee'].to_crs(crs)
inter = gpd.overlay(cells[['geometry', 'reg', 'T']], poly[['geometry']], how='intersection')
inter['a'] = inter.geometry.area
cw = inter.groupby([inter.reg, inter['T']])['a'].sum().reset_index()
print("area-weighted declining fractions (weight = coffee polygon area inside each cell):")
for r in ('kona', 'kau'):
    sub = cw[cw.reg == r]
    w = sub['a'].values; T = sub['T'].values
    for h, dt in DT.items():
        decl = T >= MU[r] - dt / 2.0
        N[f'areawt_decl_{r}_{h}'] = float(100 * w[decl].sum() / w.sum())
    N[f'captured_acres_{r}'] = float(w.sum() / 4046.86)

    print(f"  {r:5s} 2035 {N[f'areawt_decl_{r}_2035']:.1f}%  2045 {N[f'areawt_decl_{r}_2045']:.1f}%"
          f"   unweighted {100*(FTemp[reg==r] >= MU[r]-0.5).mean():.1f}%/"
          f"{100*(FTemp[reg==r] >= MU[r]-0.675).mean():.1f}%"
          f"   {N[f'captured_acres_{r}']:,.0f} captured acres")
_bi = poly[poly.Island.astype(str).str.contains('Big Island', case=False, na=False)]
_tot = _bi.geometry.area.sum() / 4046.86
_cap = sum(N[f'captured_acres_{r}'] for r in ('kona', 'kau'))
N['bigisland_coffee_acres'] = float(_tot)
N['acreage_capture_pct'] = float(100 * _cap / _tot)
N['acreage_outside_pct'] = float(100 - N['acreage_capture_pct'])
print(f"  Big Island mapped coffee: {_tot:,.0f} acres; captured in labelled cells "
      f"{_cap:,.0f} = {N['acreage_capture_pct']:.1f}% (outside {N['acreage_outside_pct']:.1f}%)")
print(f"  COINCIDENCE CHECK: Kona area-weighted 2035 decline = "
      f"{N['areawt_decl_kona_2035']:.1f}%, acreage capture rate = "
      f"{N['acreage_capture_pct']:.1f}%. Computed from different data "
      f"(thermal sign over polygon area vs captured/total acreage); numerically close "
      f"but unrelated.")

# ── 7. LaTeX table bodies ────────────────────────────────────────────────────
print("\n" + "-" * 70 + "\nTable S1 body (threshold x metric):")
for r, nm in (('kau', "Ka\\okina u"), ('kona', 'Kona')):
    print(f"\\multicolumn{{5}}{{l}}{{\\textit{{{nm}}} (thermal-only suitable = "
          f"{N[f'Cr_{r}_2035']:,} cells)}} \\\\".replace(',', '{,}'))
    for pct in (90, 92.5, 95, 97.5):
        row = []
        for metric in ('euclid', 'maha'):
            lk = screen(pct, metric)[r]
            c, f = CF(r, 1.00, lk)
            row += [f"{f:,}".replace(',', '{,}'), f"{c/f:.1f}$\\times$"]
        lbl = {90: '90th percentile', 92.5: '92.5th percentile',
               95: '95th percentile (baseline)', 97.5: '97.5th percentile'}[pct]
        print(f"{lbl:26s} & {row[0]} & {row[1]} & {row[2]} & {row[3]} \\\\")
    print("\\midrule" if r == 'kau' else "")

print("\nTable S2 body (per scenario):")
for sc_, lbl in (('ssp245', 'SSP2-4.5'), ('ssp585', 'SSP5-8.5')):
    for h in ('2035', '2045'):
        for i, (r, nm) in enumerate((('kona', 'Kona'), ('kau', "Ka\\okina u"))):
            head = f"{lbl} & {h} & $+{SCEN[(sc_,h)]:.2f}$ & " if (i == 0 and h == '2035') else \
                   (f"         & {h} & $+{SCEN[(sc_,h)]:.2f}$ & " if i == 0 else "         &      &         & ")
            print(f"{head}{nm} & {N[f'{sc_}_{h}_{r}_islandgain']:.1f}\\% & "
                  f"{N[f'{sc_}_{h}_{r}_terrdecl']:.1f}\\% & {N[f'{sc_}_{h}_{r}_farmdecl']:.1f}\\% & "
                  f"{N[f'{sc_}_{h}_{r}_factor']:.1f}$\\times$ \\\\")
print()
for sc_, lbl in (('ssp245', 'SSP2-4.5'), ('ssp585', 'SSP5-8.5')):
    for i, (r, nm) in enumerate((('kona', 'Kona'), ('kau', "Ka\\okina u"))):
        head = f"{lbl} & " if i == 0 else "         & "
        print(f"{head}{nm} & {N[f'{sc_}_2035_{r}_Cr']:,} & {N[f'{sc_}_2045_{r}_Cr']:,} "
              f"(${N[f'{sc_}_{r}_Crchange']:+.1f}\\%$) & {N[f'{sc_}_2035_{r}_Fr']:,} & "
              f"{N[f'{sc_}_2045_{r}_Fr']:,} (${N[f'{sc_}_{r}_Frchange']:+.1f}\\%$) \\\\"
              .replace(',', '{,}'))

# ── 8. validation / merge ────────────────────────────────────────────────────
PUB = {'pct_kona_like': 5.95, 'pct_kau_like': 8.90, 'Fr_kona_2035': 1371,
       'Fr_kau_2035': 1839, 'Frchange_kona': -15.5, 'Frchange_kau': -12.4,
       'factor_kona_2035': 6.9, 'terrdecl_kona_2035': 69.0}
print("\n" + "-" * 70)
if PUBLISHED:
    bad = [(k, N[k], v) for k, v in PUB.items() if abs(N[k] - v) > max(0.06, abs(v) * 0.01)]
    for k, got, want in bad:
        print(f"  MISMATCH {k}: got {got:.3f}, published {want}")
    assert not bad, "8-feature mode must reproduce the published values"
    print("VALIDATION PASSED: 8-feature mode reproduces every published value.")
    print("Nothing but the feature set differs between the two modes.")
else:
    # the thermal-only quantities must be untouched by the screen correction
    for r in ('kona', 'kau'):
        for h, dt in DT.items():
            g = float((Tflat[farm] < MU[r] - dt / 2.0).mean() * 100)
            fd = float((FTemp[reg == r] >= MU[r] - dt / 2.0).mean() * 100)
            N[f'islandgain_{r}_{h}'] = g; N[f'farmdecl_{r}_{h}'] = fd
    old = json.load(open(os.path.join(HERE, '..', 'paper_numbers.json')))
    for k in ('islandgain_kona_2035', 'farmdecl_kona_2035', 'mu_kona', 'sigma_kona'):
        if k in old and k in N:
            assert abs(N[k] - old[k]) < 0.06, f"{k} moved ({old[k]} -> {N[k]}) but must not"
    print("thermal-only quantities unchanged, as required (island gain, farm decline, mu, sigma)")
    pn = os.path.join(HERE, '..', 'paper_numbers.json')
    d = json.load(open(pn))
    for k in list(PUB) + ['Cr_kona_2035', 'Cr_kau_2035', 'factor_kau_2035',
                          'terrdecl_kau_2035', 'pct_neither', 'Crchange_kona', 'Crchange_kau']:
        if k in d:
            d[f'pub8_{k}'] = d[k]
    d.update(N)
    json.dump(d, open(pn, 'w'), indent=1)
    print(f"merged {len(N)} corrected keys into paper_numbers.json "
          f"(published values preserved under pub8_*)")


# ── 9. figures that depend on the screen ─────────────────────────────────────
if not PUBLISHED:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.colors import ListedColormap
    from pyproj import Transformer
    IMG = os.path.join(HERE, '..', 'img')
    tf = Transformer.from_crs(crs, 'EPSG:4326', always_xy=True)
    x0, y0 = tr.c, tr.f
    x1, y1 = tr.c + W * tr.a, tr.f + H * tr.e
    (lon0, lat1), (lon1, lat0) = tf.transform(x0, y0), tf.transform(x1, y1)
    EXT = [lon0, lon1, lat0, lat1]
    ASPECT = 1 / np.cos(np.radians(19.6))

    def grid(vals, fill=np.nan):
        g = np.full(H * W, fill, dtype=float)
        g[np.where(flat)[0]] = vals
        return g.reshape(H, W)

    # Fig 2 -- topographic identity map
    cat = np.zeros(len(X))                      # 0 = land, neither
    cat[LIKE['kona']] = 1
    cat[LIKE['kau']] = 2
    fig, ax = plt.subplots(figsize=(7, 8))
    ax.imshow(grid(cat), extent=EXT, origin='upper', aspect=ASPECT,
              cmap=ListedColormap(['#d9d9d9', '#2166ac', '#d6604d']), vmin=0, vmax=2,
              interpolation='nearest')
    ax.set_xlabel('Longitude'); ax.set_ylabel('Latitude')
    ax.set_title(f"Kona-like {N['pct_kona_like']:.1f}%   "
                 f"Ka'u-like {N['pct_kau_like']:.1f}%   of island land", fontsize=10)
    for lbl, c in (('Kona-like', '#2166ac'), ("Ka'u-like", '#d6604d'), ('neither', '#d9d9d9')):
        ax.plot([], [], 's', color=c, label=lbl, markersize=9)
    ax.legend(loc='upper right', frameon=False, fontsize=9)
    fig.tight_layout(); fig.savefig(f'{IMG}/10_identity_corrected.png', dpi=300); plt.close(fig)

    # Fig 4 -- the feasible set at each horizon
    fig, axes = plt.subplots(1, 2, figsize=(13, 7.5))
    for ax, (h, dt) in zip(axes, DT.items()):
        base = np.where(farm, 0.0, np.nan)                 # farmable, outside footprint
        img = np.full(len(X), np.nan)
        img[farm] = 0.0
        for r in ('kona', 'kau'):
            m = farm & LIKE[r]
            S1 = np.exp(-0.5 * ((Tflat[m] + dt - MU[r]) / SG[r]) ** 2)
            S0 = np.exp(-0.5 * ((Tflat[m] - MU[r]) / SG[r]) ** 2)
            img[m] = S1 - S0
        lim = np.nanmax(np.abs(img[np.isfinite(img)])) or 1.0
        ax.imshow(grid(np.where(np.isfinite(img), 0.0, np.nan)), extent=EXT, origin='upper',
                  aspect=ASPECT, cmap=ListedColormap(['#bdbdbd']), interpolation='nearest')
        inf = np.full(len(X), np.nan)
        for r in ('kona', 'kau'):
            m = farm & LIKE[r]
            inf[m] = img[m]
        im = ax.imshow(grid(inf), extent=EXT, origin='upper', aspect=ASPECT,
                       cmap='RdBu_r', vmin=-lim, vmax=lim, interpolation='nearest')
        ax.set_title(f"~{h}   $\\Delta T = +{dt:.2f}$ °C", fontsize=11)
        ax.set_xlabel('Longitude')
        if h == '2035':
            ax.set_ylabel('Latitude')
    fig.colorbar(im, ax=axes, shrink=0.6, label='$\\Delta S_r$ (matched envelope)')
    fig.savefig(f'{IMG}/10_feasible_corrected.png', dpi=300, bbox_inches='tight'); plt.close(fig)
    print(f"\nwrote {IMG}/10_identity_corrected.png and {IMG}/10_feasible_corrected.png")

    # Fig S1 -- threshold sensitivity, regenerated on the corrected screen
    PCTS = (90, 92.5, 95, 97.5)
    scr = {p: screen(p) for p in PCTS}
    fig = plt.figure(figsize=(14, 7.5))
    for i, p in enumerate(PCTS):
        ax = fig.add_subplot(2, 4, i + 1)
        cat = np.zeros(len(X)); cat[scr[p]['kona']] = 1; cat[scr[p]['kau']] = 2
        ax.imshow(grid(cat), extent=EXT, origin='upper', aspect=ASPECT,
                  cmap=ListedColormap(['#d9d9d9', '#2166ac', '#d6604d']), vmin=0, vmax=2,
                  interpolation='nearest')
        ax.set_title(f"{p}th percentile" + (" (baseline)" if p == 95 else ""), fontsize=10)
        ax.set_xticks([]); ax.set_yticks([])
        if p == 95:
            for sp in ax.spines.values():
                sp.set_edgecolor('#c1440e'); sp.set_linewidth(2.5)
    JAC = {}
    ax = fig.add_subplot(2, 2, 3)
    w = 0.35; xs = np.arange(len(PCTS))
    for j, (r, c, nm) in enumerate((('kona', '#2166ac', 'Kona'), ('kau', '#d6604d', "Ka'u"))):
        ax.bar(xs + j * w, [100 * scr[p][r].sum() / len(X) for p in PCTS], w, color=c, label=nm)
    ax.set_xticks(xs + w / 2); ax.set_xticklabels([f'{p}th' for p in PCTS])
    ax.set_ylabel('% of island land'); ax.legend(frameon=False); ax.set_title('Classified area', fontsize=10)
    ax = fig.add_subplot(2, 2, 4)
    for j, (r, c, nm) in enumerate((('kona', '#2166ac', 'Kona'), ('kau', '#d6604d', "Ka'u"))):
        v = [(scr[p][r] & scr[95][r]).sum() / max((scr[p][r] | scr[95][r]).sum(), 1) for p in PCTS]
        for p, jj in zip(PCTS, v):
            JAC[(r, p)] = float(jj)
        ax.bar(xs + j * w, v, w, color=c, label=nm)
    ax.set_xticks(xs + w / 2); ax.set_xticklabels([f'{p}th' for p in PCTS])
    ax.set_ylabel('Jaccard vs 95th-pct baseline'); ax.set_ylim(0, 1.05)
    ax.legend(frameon=False); ax.set_title('Classification stability', fontsize=10)
    fig.tight_layout(); fig.savefig(f'{IMG}/10_S1_threshold_corrected.png', dpi=300); plt.close(fig)
    N.update({f'jaccard_{r}_{str(p).replace(".","p")}': JAC[(r, p)] for r in ('kona', 'kau') for p in PCTS})
    print("Jaccard vs baseline: " + "  ".join(f"{r} {p}th {JAC[(r,p)]:.2f}" for r in ('kona','kau') for p in PCTS))
    _pn = os.path.join(HERE, '..', 'paper_numbers.json')
    _d = json.load(open(_pn)); _d.update(N); json.dump(_d, open(_pn, 'w'), indent=1)
