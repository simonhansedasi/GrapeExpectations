#!/usr/bin/env python3
"""
Generate Supplementary Table S1: overestimation factor across the terrain
threshold (90th-97.5th percentile) and both distance metrics, both districts.

Table S1 previously carried an empty Kona Mahalanobis column and a caption
quoting one district's thermal-only denominator for a two-block table. This
computes all sixteen cells and emits the LaTeX body, so the table is generated
rather than hand-maintained.

Run from the repo root:  python ML/08_table_s1.py
"""
import json, os
import numpy as np, pandas as pd, geopandas as gpd, rasterio
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from scipy.ndimage import maximum_filter, minimum_filter, distance_transform_edt
from pyproj import Transformer
rng = np.random.default_rng(7)
HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, '..', 'data')
with rasterio.open(f'{DATA}/DEM/hawaii_DEM_500m_utm.tif') as s:
    nd=s.nodata; dem=s.read(1).astype(np.float32); tr=s.transform; H,W=s.height,s.width; crs=s.crs
dem[dem==nd]=np.nan; dem[dem<=0]=np.nan; land=~np.isnan(dem)
sm=np.nanmean(dem[land]); dev=dem-sm; ef=np.where(land,dem,sm)
dy,dx=np.gradient(ef,500.,500.)
slope=np.degrees(np.arctan(np.sqrt(dx**2+dy**2))); asp=np.arctan2(-dx,dy)
asin,acos=np.sin(asp),np.cos(asp)
smax=maximum_filter(slope,size=3,mode='nearest')
emax=maximum_filter(ef,size=3,mode='nearest'); emin=minimum_filter(ef,size=3,mode='nearest')
relief=emax-emin; local=dem-emin
for a in [dev,smax,asin,acos,relief,local]: a[~land]=np.nan
dcoast=distance_transform_edt(land)*500.; dcoast[~land]=np.nan
flat=land.ravel()
X=np.column_stack([a.ravel()[flat] for a in [dem,dev,smax,asin,acos,relief,local,dcoast]])
with rasterio.open(f'{DATA}/DEM/hawaii_temp_climatology_500m_utm.tif') as s:
    tc=s.read(1).astype(np.float32); tnd=s.nodata
tc[tc==tnd]=np.nan; tc[~land]=np.nan; Tflat=tc.ravel()[flat]
with rasterio.open(f'{DATA}/DEM/hawaii_historic_lava_500m_utm.tif') as s: lava=(s.read(1)==1)
farm=(smax.ravel()[flat]<=25.)&(~np.isnan(smax.ravel()[flat]))&(~lava.ravel()[flat])
allf=pd.read_pickle(f'{DATA}/plot_all_features.pkl')
fp=gpd.GeoDataFrame(allf[allf.label==1].copy(),geometry='geometry',crs='EPSG:4326').to_crs(crs)
cen=fp.geometry.centroid
ci=((cen.x-tr.c)/tr.a).astype(int).values; ri=((cen.y-tr.f)/tr.e).astype(int).values
ok=(ri>=0)&(ri<H)&(ci>=0)&(ci<W)
FT=np.column_stack([a[ri[ok],ci[ok]] for a in [dem,dev,smax,asin,acos,relief,local,dcoast]])
with rasterio.open(f'{DATA}/DEM/hawaii_temp_climatology_500m_utm.tif') as s:
    FTemp=np.array([v[0] for v in s.sample(zip(cen.x[ok],cen.y[ok]))])
reg=fp['region'].values[ok]
good=~np.isnan(FT).any(axis=1)
FT,FTemp,reg=FT[good],FTemp[good],reg[good]
xy=np.column_stack([cen.x[ok][good],cen.y[ok][good]])

from scipy.linalg import inv

sc = StandardScaler().fit(FT)
Fs = sc.transform(FT); Is = sc.transform(X)
ck = Fs[reg == 'kona'].mean(0); cq = Fs[reg == 'kau'].mean(0)

# pooled within-class covariance, as in the main-text robustness check
_dev = np.vstack([Fs[reg == 'kona'] - ck, Fs[reg == 'kau'] - cq])
VI = inv(np.cov(_dev.T))

def dist(A, c, metric):
    D = A - c
    return np.linalg.norm(D, axis=1) if metric == 'euclid' else np.sqrt(np.einsum('ij,jk,ik->i', D, VI, D))

rows = {}
for metric in ('euclid', 'maha'):
    dk = dist(Fs[reg == 'kona'], ck, metric); dq = dist(Fs[reg == 'kau'], cq, metric)
    Dk = dist(Is, ck, metric); Dq = dist(Is, cq, metric)
    ident = 1 / (1 + Dq) - 1 / (1 + Dk)
    for pct in (90, 92.5, 95, 97.5):
        th = np.percentile(np.concatenate([dk, dq]), pct)
        inr = (Dk <= th) | (Dq <= th)
        for r, like in (('kona', inr & (ident <= 0)), ('kau', inr & (ident > 0))):
            T = FTemp[reg == r]; mu = T.mean(); sg = T.std(ddof=1) * 1.5
            S = np.exp(-0.5 * ((Tflat + 1.00 - mu) / sg) ** 2)
            cr = farm & (S > 0.5); fr = cr & like
            rows[(r, metric, pct)] = (int(fr.sum()), int(cr.sum()) / max(fr.sum(), 1), int(cr.sum()),
                                      float(like.sum()) / len(Is) * 100)

# declining fractions under each metric, so the main text quotes ONE Mahalanobis
# definition rather than the notebook's and this script's separately
print("district declining fractions, 95th-pct baseline (sign of dS; sigma cannot enter):")
_N = {}
for metric in ('euclid', 'maha'):
    dk = dist(Fs[reg == 'kona'], ck, metric); dq = dist(Fs[reg == 'kau'], cq, metric)
    Dk = dist(Is, ck, metric); Dq = dist(Is, cq, metric)
    th = np.percentile(np.concatenate([dk, dq]), 95)
    ident = 1 / (1 + Dq) - 1 / (1 + Dk); inr = (Dk <= th) | (Dq <= th)
    for r, like in (('kona', inr & (ident <= 0)), ('kau', inr & (ident > 0))):
        mu = FTemp[reg == r].mean()
        pop = farm & like
        for h, dt in (('2035', 1.00), ('2045', 1.35)):
            d = float((Tflat[pop] >= mu - dt / 2.0).mean() * 100)
            _N[f'decl_{metric}_{r}_{h}'] = d
        print(f"  {metric:7s} {r:5s} n={int(pop.sum()):5,d}  "
              f"2035 {_N[f'decl_{metric}_{r}_2035']:.1f}%  2045 {_N[f'decl_{metric}_{r}_2045']:.1f}%")
import json as _j
_pn = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'paper_numbers.json')
_d = _j.load(open(_pn)); _d.update(_N); _j.dump(_d, open(_pn, 'w'), indent=1)
print(f"  merged {len(_N)} keys into paper_numbers.json\n")

print("footprint as % of island land (both metrics, 95th-pct baseline):")
for r in ('kona', 'kau'):
    print(f"  {r}: Euclidean {rows[(r,'euclid',95)][3]:.2f}%  Mahalanobis {rows[(r,'maha',95)][3]:.2f}%")
print("factor span across all thresholds and metrics:")
for r in ('kona', 'kau'):
    _v = [rows[(r,m,p)][1] for m in ('euclid','maha') for p in (90,92.5,95,97.5)]
    print(f"  {r}: {min(_v):.1f}x - {max(_v):.1f}x")

LBL = {90: '90th percentile', 92.5: '92.5th percentile',
       95: '95th percentile (baseline)', 97.5: '97.5th percentile'}
print()
for r, nm in (('kau', "Ka\\okina u"), ('kona', 'Kona')):
    tot = rows[(r, 'euclid', 95)][2]
    print(f"\\multicolumn{{5}}{{l}}{{\\textit{{{nm}}} (thermal-only suitable = {tot:,} cells)}} \\\\".replace(',', '{,}'))
    for pct in (90, 92.5, 95, 97.5):
        e = rows[(r, 'euclid', pct)]; m = rows[(r, 'maha', pct)]
        print(f"{LBL[pct]:26s} & {e[0]:,} & {e[1]:.1f}$\\times$ & {m[0]:,} & {m[1]:.1f}$\\times$ \\\\".replace(',', '{,}'))
    print("\\midrule" if r == 'kau' else "")
