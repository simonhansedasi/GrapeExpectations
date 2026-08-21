#!/usr/bin/env python3
"""
Are Kona's and Ka'u's TRAJECTORIES distinguishable, as distinct from their peaks?

ML/12 showed the peak offsets are not distinguishable between districts. That is a
statement about one scalar (the argmax). It does not settle whether the districts
decline at different RATES, which is the quantity the Discussion's "one problem with
two local expressions" claim actually rests on.

Three paired contrasts, all block-bootstrapped on the same replicates so the
difference is paired rather than a comparison of marginal intervals:

  1. |F_r| decline from the climatological baseline to 2035 and 2045  (screen-dependent)
  2. Farm-cell declining fraction                                      (screen-INDEPENDENT)
  3. The same two contrasts across the elevation weight w_z, since ML/09 showed
     Ka'u's decline is far more w_z-sensitive than Kona's -- so "do they differ"
     may itself depend on a discretionary parameter.

Run from repo root:  python ML/14_trajectory_contrast.py
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
HW = np.sqrt(2 * np.log(2.0))          # tau = 0.5

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
X = np.column_stack([a.ravel()[flat] for a in [dem, smax, asin, acos, relief, local, dcoast]])
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
FT = np.column_stack([a[ri[ok], ci[ok]] for a in [dem, smax, asin, acos, relief, local, dcoast]])
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

DT = {'2035': 1.00, '2045': 1.35}


def stats(idx, wz=1.0):
    """Refit everything on a farm-cell subset; return |F| declines and farm-cell declines."""
    sc = StandardScaler().fit(FT[idx])
    Fs = sc.transform(FT[idx]); Is = sc.transform(X)
    if wz != 1.0:
        Fs = Fs.copy(); Is = Is.copy(); Fs[:, 0] *= wz; Is[:, 0] *= wz
    rr = reg[idx]
    ck = Fs[rr == 'kona'].mean(0); cq = Fs[rr == 'kau'].mean(0)
    dk = np.linalg.norm(Fs[rr == 'kona'] - ck, axis=1)
    dq = np.linalg.norm(Fs[rr == 'kau'] - cq, axis=1)
    th = np.percentile(np.concatenate([dk, dq]), 95)
    Dk = np.linalg.norm(Is - ck, axis=1); Dq = np.linalg.norm(Is - cq, axis=1)
    idt = 1 / (1 + Dq) - 1 / (1 + Dk); inr = (Dk <= th) | (Dq <= th)
    out = {}
    for r, like in (('kona', inr & (idt <= 0)), ('kau', inr & (idt > 0))):
        T = FTemp[idx][rr == r]
        mu = T.mean(); sg = T.std(ddof=1) * 1.5
        pool = np.sort(Tflat[farm & like])
        if pool.size < 10:
            return None
        def sz(dt):
            return (np.searchsorted(pool, mu + HW * sg - dt, 'right')
                    - np.searchsorted(pool, mu - HW * sg - dt, 'left'))
        f0 = sz(0.0)
        if f0 < 10:
            return None
        for h, dt in DT.items():
            out[f'F_{r}_{h}'] = 100.0 * (sz(dt) - f0) / f0
            out[f'farm_{r}_{h}'] = 100.0 * float((T >= mu - dt / 2.0).mean())
    return out


def ci(a):
    a = np.asarray(a)
    return np.median(a), np.percentile(a, 2.5), np.percentile(a, 97.5)


def run(wz=1.0, nb=NB, label=''):
    base = stats(np.arange(len(FT)), wz)
    res = {k: [] for k in ('dF_2035', 'dF_2045', 'dfarm_2035', 'dfarm_2045')}
    for _ in range(nb):
        idx = np.concatenate([np.concatenate([gi[lb == k] for k in rng.integers(0, n, n)])
                              for gi, lb, n in (blocks[r] for r in ('kona', 'kau'))])
        if (reg[idx] == 'kau').sum() < 5 or (reg[idx] == 'kona').sum() < 5:
            continue
        try:
            s = stats(idx, wz)
        except Exception:
            continue
        if not s:
            continue
        for h in DT:
            res[f'dF_{h}'].append(s[f'F_kona_{h}'] - s[f'F_kau_{h}'])
            res[f'dfarm_{h}'].append(s[f'farm_kona_{h}'] - s[f'farm_kau_{h}'])
    return base, res


print("=" * 78)
print("Are the TRAJECTORIES distinguishable?  (paired block bootstrap, 2,000 reps)")
print("=" * 78)
base, res = run()
OUT = {}
print(f"\npoint estimates at w_z = 1 (the screen used in the paper):")
for h in DT:
    print(f"  {h}: |F| decline  Kona {base[f'F_kona_{h}']:+.1f}%  Ka'u {base[f'F_kau_{h}']:+.1f}%"
          f"   |  farm-cell decline  Kona {base[f'farm_kona_{h}']:.1f}%  Ka'u {base[f'farm_kau_{h}']:.1f}%")

print(f"\n{'contrast (Kona - Ka u)':>30} {'point':>8} {'95% CI':>20}  verdict")
for h in DT:
    for key, nm, pt in ((f'dF_{h}', f'|F| decline {h}',
                         base[f'F_kona_{h}'] - base[f'F_kau_{h}']),
                        (f'dfarm_{h}', f'farm-cell decline {h}',
                         base[f'farm_kona_{h}'] - base[f'farm_kau_{h}'])):
        m, lo, hi = ci(res[key])
        sig = lo > 0 or hi < 0
        OUT[f'contrast_{key}'] = float(pt)
        OUT[f'contrast_{key}_lo'] = float(lo); OUT[f'contrast_{key}_hi'] = float(hi)
        OUT[f'contrast_{key}_sig'] = bool(sig)
        print(f"{nm:>30} {pt:>+7.1f}pp {f'({lo:+.1f}, {hi:+.1f})':>20}  "
              f"{'DISTINGUISHABLE' if sig else 'not distinguishable'}")

print("\n" + "-" * 78)
print("does the answer depend on the elevation weight?  (500 reps per w_z)")
print(f"  {'w_z':>5} {'|F| 2045 contrast':>22} {'verdict':>20}")
for wz in (0.0, 0.5, 1.0, 1.5, 2.0):
    b, r = run(wz, 500)
    m, lo, hi = ci(r['dF_2045'])
    pt = b['F_kona_2045'] - b['F_kau_2045']
    OUT[f'contrast_dF_2045_wz{str(wz).replace(".","p")}_lo'] = float(lo)
    OUT[f'contrast_dF_2045_wz{str(wz).replace(".","p")}_hi'] = float(hi)
    print(f"  {wz:>5.1f} {pt:>+9.1f}pp ({lo:+.1f}, {hi:+.1f}) "
          f"{'DISTINGUISHABLE' if (lo > 0 or hi < 0) else 'not distinguishable':>26}")

pn = os.path.join(HERE, '..', 'paper_numbers.json')
d = json.load(open(pn)); d.update(OUT); json.dump(d, open(pn, 'w'), indent=1)
print(f"\nmerged {len(OUT)} keys into paper_numbers.json")

# the farm-cell contrast has a closed form: decline ~ Phi(dT / 2s), so a district
# with a NARROWER farm temperature spread declines faster. Check the sign follows.
s_kona = FTemp[reg == 'kona'].std(ddof=1)
s_kau = FTemp[reg == 'kau'].std(ddof=1)
print(f"\nfarm-cell temperature spread: Kona s = {s_kona:.3f} °C, Ka'u s = {s_kau:.3f} °C")
print(f"  narrower spread -> faster farm-cell decline, so Ka'u declining faster than Kona")
print(f"  on farm cells is expected from spread alone, independent of any terrain screen.")
assert s_kau < s_kona, "Ka'u should have the narrower farm temperature spread"
assert base['farm_kau_2035'] > base['farm_kona_2035'], "Ka'u farm decline should exceed Kona's"
print("selfcheck: sign of the farm-cell contrast follows from the spreads, as expected")


# ── pooled trajectory ────────────────────────────────────────────────────────
# If the districts are indistinguishable on every axis tested, reporting two
# separate declines invites a comparison the data cannot support. The natural
# alternative is the union F_kona ∪ F_kau -- total feasible coffee ground on the
# island -- which also pools the blocks and should buy precision.
print("\n" + "=" * 78)
print("POOLED: decline of the union F_kona ∪ F_kau, and what pooling buys")
print("=" * 78)


def pooled(idx, wz=1.0):
    sc = StandardScaler().fit(FT[idx])
    Fs = sc.transform(FT[idx]); Is = sc.transform(X)
    if wz != 1.0:
        Fs = Fs.copy(); Is = Is.copy(); Fs[:, 0] *= wz; Is[:, 0] *= wz
    rr = reg[idx]
    ck = Fs[rr == 'kona'].mean(0); cq = Fs[rr == 'kau'].mean(0)
    dk = np.linalg.norm(Fs[rr == 'kona'] - ck, axis=1)
    dq = np.linalg.norm(Fs[rr == 'kau'] - cq, axis=1)
    th = np.percentile(np.concatenate([dk, dq]), 95)
    Dk = np.linalg.norm(Is - ck, axis=1); Dq = np.linalg.norm(Is - cq, axis=1)
    idt = 1 / (1 + Dq) - 1 / (1 + Dk); inr = (Dk <= th) | (Dq <= th)
    out = {}
    tot = {}
    for h, dt in list(DT.items()) + [('base', 0.0)]:
        u = np.zeros(len(X), bool)
        for r, like in (('kona', inr & (idt <= 0)), ('kau', inr & (idt > 0))):
            T = FTemp[idx][rr == r]; mu = T.mean(); sg = T.std(ddof=1) * 1.5
            S = np.exp(-0.5 * ((Tflat + dt - mu) / sg) ** 2)
            u |= (farm & like & (S > 0.5))
        tot[h] = int(u.sum())
    if tot['base'] < 10:
        return None
    for h in DT:
        out[h] = 100.0 * (tot[h] - tot['base']) / tot['base']
    out['base_cells'] = tot['base']
    return out


pb = pooled(np.arange(len(FT)))
pres = {h: [] for h in DT}
for _ in range(NB):
    idx = np.concatenate([np.concatenate([gi[lb == k] for k in rng.integers(0, n, n)])
                          for gi, lb, n in (blocks[r] for r in ('kona', 'kau'))])
    if (reg[idx] == 'kau').sum() < 5 or (reg[idx] == 'kona').sum() < 5:
        continue
    try:
        p = pooled(idx)
    except Exception:
        continue
    if p:
        for h in DT:
            pres[h].append(p[h])

print(f"  union at baseline: {pb['base_cells']:,} cells")
for h in DT:
    m, lo, hi = ci(pres[h])
    OUT[f'pooled_decline_{h}'] = float(pb[h])
    OUT[f'pooled_decline_{h}_lo'] = float(lo); OUT[f'pooled_decline_{h}_hi'] = float(hi)
    OUT[f'pooled_decline_{h}_width'] = float(hi - lo)
    print(f"  {h}: pooled decline {pb[h]:+.1f}%  (95% CI {lo:+.1f}, {hi:+.1f})  width {hi-lo:.1f} pp")

# what the separate district intervals cost by comparison
sep = {h: [] for h in DT}
for _ in range(NB):
    idx = np.concatenate([np.concatenate([gi[lb == k] for k in rng.integers(0, n, n)])
                          for gi, lb, n in (blocks[r] for r in ('kona', 'kau'))])
    if (reg[idx] == 'kau').sum() < 5 or (reg[idx] == 'kona').sum() < 5:
        continue
    try:
        s = stats(idx)
    except Exception:
        continue
    if s:
        for h in DT:
            sep[h].append(s[f'F_kau_{h}'])
print()
for h in DT:
    m, lo, hi = ci(sep[h])
    print(f"  {h}: Ka'u alone {base[f'F_kau_{h}']:+.1f}%  (95% CI {lo:+.1f}, {hi:+.1f})  "
          f"width {hi-lo:.1f} pp  ->  pooling narrows it "
          f"{(hi-lo)/OUT[f'pooled_decline_{h}_width']:.1f}x")

_d = json.load(open(pn)); _d.update(OUT); json.dump(_d, open(pn, 'w'), indent=1)
print(f"\nmerged pooled keys into paper_numbers.json")

# ANALYSIS_TODO item 1: the per-district declines span -5% to -20% across w_z, so the
# pooled headline is not safe until it is swept on the same axis. Does it stay
# negative -- and does its CI keep excluding zero -- at every elevation weight?
print("\n" + "-" * 78)
print("pooled decline vs elevation weight  (500 reps per w_z)")
print(f"  {'w_z':>5} {'pooled 2045':>12} {'95% CI':>20}  {'excludes 0':>10}")
for wz in (0.0, 0.5, 1.0, 1.5, 2.0):
    b = pooled(np.arange(len(FT)), wz)
    rep = []
    for _ in range(500):
        idx = np.concatenate([np.concatenate([gi[lb == k] for k in rng.integers(0, n, n)])
                              for gi, lb, n in (blocks[r] for r in ('kona', 'kau'))])
        if (reg[idx] == 'kau').sum() < 5 or (reg[idx] == 'kona').sum() < 5:
            continue
        try:
            p = pooled(idx, wz)
        except Exception:
            continue
        if p:
            rep.append(p['2045'])
    m, lo, hi = ci(rep)
    tag = str(wz).replace('.', 'p')
    OUT[f'pooled_decline_2045_wz{tag}'] = float(b['2045'])
    OUT[f'pooled_decline_2045_wz{tag}_lo'] = float(lo)
    OUT[f'pooled_decline_2045_wz{tag}_hi'] = float(hi)
    print(f"  {wz:>5.1f} {b['2045']:>+11.1f}% {f'({lo:+.1f}, {hi:+.1f})':>20}  "
          f"{'yes' if hi < 0 else 'NO':>10}")

_d = json.load(open(pn)); _d.update(OUT); json.dump(_d, open(pn, 'w'), indent=1)
print(f"merged pooled w_z sweep into paper_numbers.json")

# The block count is nb = round(n / 8) -- a hard-coded ~8 cells per block, never
# checked against the actual spatial correlation range of these features. It sets
# every CI width in the paper, including the pooled interval that excludes zero and
# the district contrasts that do not. Both verdicts are hostage to it, so sweep it
# before either is written up. If nothing moves, the knob is harmless and a variogram
# is not worth estimating; if the pooled exclusion breaks, the range must be measured.
print("\n" + "-" * 78)
print("block size sensitivity  (500 reps each; cells/block sets the effective n)")
print(f"  {'cells/blk':>9} {'nb kona':>8} {'nb kau':>7} {'pooled 2045 CI':>22} {'excl 0':>7}"
      f" {'|F| contrast CI':>20} {'excl 0':>7}")
for cpb in (4, 8, 16, 24):
    bl = {}
    for r in ('kona', 'kau'):
        m = reg == r; n = int(m.sum()); nbk = max(4, int(round(n / cpb)))
        bl[r] = (np.where(m)[0], KMeans(n_clusters=nbk, random_state=0, n_init=10).fit_predict(xy[m]), nbk)
    prep, crep = [], []
    for _ in range(500):
        idx = np.concatenate([np.concatenate([gi[lb == k] for k in rng.integers(0, n, n)])
                              for gi, lb, n in (bl[r] for r in ('kona', 'kau'))])
        if (reg[idx] == 'kau').sum() < 5 or (reg[idx] == 'kona').sum() < 5:
            continue
        try:
            p = pooled(idx); s = stats(idx)
        except Exception:
            continue
        if p:
            prep.append(p['2045'])
        if s:
            crep.append(s['F_kona_2045'] - s['F_kau_2045'])
    _, plo, phi = ci(prep)
    _, clo, chi = ci(crep)
    tag = f'cpb{cpb}'
    OUT[f'pooled_decline_2045_{tag}_lo'] = float(plo)
    OUT[f'pooled_decline_2045_{tag}_hi'] = float(phi)
    OUT[f'contrast_dF_2045_{tag}_lo'] = float(clo)
    OUT[f'contrast_dF_2045_{tag}_hi'] = float(chi)
    print(f"  {cpb:>9} {bl['kona'][2]:>8} {bl['kau'][2]:>7} "
          f"{f'({plo:+.1f}, {phi:+.1f})':>22} {'yes' if phi < 0 else 'NO':>7} "
          f"{f'({clo:+.1f}, {chi:+.1f})':>20} {'YES' if (clo > 0 or chi < 0) else 'no':>7}")

_d = json.load(open(pn)); _d.update(OUT); json.dump(_d, open(pn, 'w'), indent=1)
print(f"merged block-size sensitivity into paper_numbers.json")


# ── is the GEOMETRY different, even though the decline rates are not? ────────
# The mechanism behind the opposite-signed peak offsets is that each district's
# feasible density sits on a different side of its own farms: Kona's mode below,
# Ka'u's above. Unlike the argmax (8 Ka'u blocks, wide CI) this is computed from
# thousands of footprint cells -- but it still inherits screen uncertainty, so
# bootstrap it before claiming the two districts differ structurally.
print("\n" + "=" * 78)
print("GEOMETRY: does mode(s_r) - mean(farms_r) differ between districts?")
print("=" * 78)
Zisl = X[:, 0]
BW = 50
zbins = np.arange(0, 1600 + BW, BW)
zmid = zbins[:-1] + BW / 2


def modeoffset(idx):
    sc = StandardScaler().fit(FT[idx])
    Fs = sc.transform(FT[idx]); Is = sc.transform(X)
    rr = reg[idx]
    ck = Fs[rr == 'kona'].mean(0); cq = Fs[rr == 'kau'].mean(0)
    dk = np.linalg.norm(Fs[rr == 'kona'] - ck, axis=1)
    dq = np.linalg.norm(Fs[rr == 'kau'] - cq, axis=1)
    th = np.percentile(np.concatenate([dk, dq]), 95)
    Dk = np.linalg.norm(Is - ck, axis=1); Dq = np.linalg.norm(Is - cq, axis=1)
    idt = 1 / (1 + Dq) - 1 / (1 + Dk); inr = (Dk <= th) | (Dq <= th)
    out = {}
    for r, like in (('kona', inr & (idt <= 0)), ('kau', inr & (idt > 0))):
        zz = Zisl[like & farm]
        if zz.size < 50:
            return None
        h = np.histogram(zz, bins=zbins)[0]
        # smooth before taking the mode so a single noisy bin cannot flip it
        hs = np.convolve(h, np.ones(3) / 3., mode='same')
        out[r] = float(zmid[int(np.argmax(hs))] - FT[idx][rr == r, 0].mean())
    return out


b0 = modeoffset(np.arange(len(FT)))
print(f"  point estimates: Kona {b0['kona']:+.0f} m, Ka'u {b0['kau']:+.0f} m "
      f"(mode of feasible ground relative to that district's farms)")
mo = {'kona': [], 'kau': [], 'diff': []}
for _ in range(NB):
    idx = np.concatenate([np.concatenate([gi[lb == k] for k in rng.integers(0, n, n)])
                          for gi, lb, n in (blocks[r] for r in ('kona', 'kau'))])
    if (reg[idx] == 'kau').sum() < 5 or (reg[idx] == 'kona').sum() < 5:
        continue
    try:
        m = modeoffset(idx)
    except Exception:
        continue
    if m:
        mo['kona'].append(m['kona']); mo['kau'].append(m['kau'])
        mo['diff'].append(m['kona'] - m['kau'])
for k, nm in (('kona', 'Kona'), ('kau', "Ka'u"), ('diff', 'Kona - Ka\'u')):
    m, lo, hi = ci(mo[k])
    sig = lo > 0 or hi < 0
    OUT[f'modeoffset_{k}'] = float(b0[k]) if k != 'diff' else float(b0['kona'] - b0['kau'])
    OUT[f'modeoffset_{k}_lo'] = float(lo); OUT[f'modeoffset_{k}_hi'] = float(hi)
    OUT[f'modeoffset_{k}_sig'] = bool(sig)
    pt = b0[k] if k != 'diff' else b0['kona'] - b0['kau']
    print(f"  {nm:>12}: {pt:>+6.0f} m  95% CI ({lo:+.0f}, {hi:+.0f})  "
          f"{'EXCLUDES ZERO' if sig else 'includes zero'}")

_d = json.load(open(pn)); _d.update(OUT); json.dump(_d, open(pn, 'w'), indent=1)
print(f"\nmerged geometry keys into paper_numbers.json")
