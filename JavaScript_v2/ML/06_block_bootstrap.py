#!/usr/bin/env python3
"""
Spatial block bootstrap for the two interval-bearing quantities in the paper.

Farm cells are spatially contiguous, so resampling cells independently
understates uncertainty. Blocks are k-means clusters of farm-cell centroids
at ~8 cells per block; each replicate resamples blocks with replacement and
REFITS the whole screen -- standardiser, both centroids, and the
95th-percentile distance threshold -- so the intervals carry threshold
uncertainty rather than inheriting the point-estimate cutoff.

Produces, and merges into ../paper_numbers.json:
  factor_ci_{kona,kau}_{lo,hi}   overestimation multiplier at 2035
  decl_ci_{kona,kau}_{2035,2045}_{lo,hi}   declining farm-cell fraction

Run from the repo root:  python ML/06_block_bootstrap.py
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
X=np.column_stack([a.ravel()[flat] for a in [dem,smax,asin,acos,relief,local,dcoast]])  # elev_dev dropped: r=1.000 with dem
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
FT=np.column_stack([a[ri[ok],ci[ok]] for a in [dem,smax,asin,acos,relief,local,dcoast]])
with rasterio.open(f'{DATA}/DEM/hawaii_temp_climatology_500m_utm.tif') as s:
    FTemp=np.array([v[0] for v in s.sample(zip(cen.x[ok],cen.y[ok]))])
reg=fp['region'].values[ok]
good=~np.isnan(FT).any(axis=1)
FT,FTemp,reg=FT[good],FTemp[good],reg[good]
xy=np.column_stack([cen.x[ok][good],cen.y[ok][good]])
blocks={}
for r in ['kona','kau']:
    m=reg==r; n=m.sum(); nb=max(4,int(round(n/8)))
    blocks[r]=(np.where(m)[0],KMeans(n_clusters=nb,random_state=0,n_init=10).fit_predict(xy[m]),nb)

def factor(idx,dt):
    sc=StandardScaler().fit(FT[idx]); Fs=sc.transform(FT[idx]); Is=sc.transform(X)
    rr=reg[idx]; out={}
    ck=Fs[rr=='kona'].mean(0); cq=Fs[rr=='kau'].mean(0)
    dk=np.linalg.norm(Fs[rr=='kona']-ck,axis=1); dq=np.linalg.norm(Fs[rr=='kau']-cq,axis=1)
    th=np.percentile(np.concatenate([dk,dq]),95)
    Dk=np.linalg.norm(Is-ck,axis=1); Dq=np.linalg.norm(Is-cq,axis=1)
    ident=1/(1+Dq)-1/(1+Dk); inr=(Dk<=th)|(Dq<=th)
    for r,mu_s,like in [('kona',rr=='kona',(inr)&(ident<=0)),('kau',rr=='kau',(inr)&(ident>0))]:
        T=FTemp[idx][mu_s]; mu=T.mean(); sg=T.std(ddof=1)*1.5
        S=np.exp(-0.5*((Tflat+dt-mu)/sg)**2)
        cr=farm&(S>0.5); fr=cr&like
        out[r]=cr.sum()/fr.sum() if fr.sum()>0 else np.nan
    return out

base=factor(np.arange(len(FT)),1.00)
print(f"observed: Kona {base['kona']:.2f}x  Ka'u {base['kau']:.2f}x")
res={'kona':[],'kau':[]}
for b in range(2000):
    idx=[]
    for r in ['kona','kau']:
        gi,lb,nb=blocks[r]
        pick=rng.integers(0,nb,nb)
        idx.append(np.concatenate([gi[lb==k] for k in pick]))
    idx=np.concatenate(idx)
    if (reg[idx]=='kau').sum()<5 or (reg[idx]=='kona').sum()<5: continue
    try:
        f=factor(idx,1.00)
        for r in ['kona','kau']:
            if np.isfinite(f[r]): res[r].append(f[r])
    except Exception: pass
for r,lab in [('kona','Kona'),('kau',"Ka'u")]:
    a=np.array(res[r]); print(f"{lab}: n_boot={len(a)}  median={np.median(a):.2f}x  95% CI [{np.percentile(a,2.5):.2f}, {np.percentile(a,97.5):.2f}]")


# ---- declining farm-cell fraction, same blocks -----------------------------
# Sign only: dS_r > 0 iff T < mu_r - dT/2, so sigma (and its 1.5x inflation)
# cannot enter here. mu_r is refit within each replicate.
def decl(idx, dt):
    out = {}
    for r in ['kona', 'kau']:
        m = reg[idx] == r
        T = FTemp[idx][m]
        if m.sum() < 5:
            return None
        out[r] = float((T >= T.mean() - dt / 2.0).mean() * 100)
    return out

DT = {'2035': 1.00, '2045': 1.35}
dres = {(r, h): [] for r in ['kona', 'kau'] for h in DT}
allidx = np.arange(len(FT))
for h, dt in DT.items():
    print(f"observed decline {h}: " + "  ".join(
        f"{r} {decl(allidx, dt)[r]:.1f}%" for r in ['kona', 'kau']))
for b in range(2000):
    idx = []
    for r in ['kona', 'kau']:
        gi, lb, nb = blocks[r]
        idx.append(np.concatenate([gi[lb == k] for k in rng.integers(0, nb, nb)]))
    idx = np.concatenate(idx)
    for h, dt in DT.items():
        d = decl(idx, dt)
        if d:
            for r in ['kona', 'kau']:
                dres[(r, h)].append(d[r])

N = {}
for r in ['kona', 'kau']:
    a = np.array(res[r])
    N[f'factor_ci_{r}_lo'] = float(np.percentile(a, 2.5))
    N[f'factor_ci_{r}_hi'] = float(np.percentile(a, 97.5))
    for h in DT:
        a = np.array(dres[(r, h)])
        N[f'decl_ci_{r}_{h}_lo'] = float(np.percentile(a, 2.5))
        N[f'decl_ci_{r}_{h}_hi'] = float(np.percentile(a, 97.5))
        print(f"  decline {r} {h}: 95% CI [{N[f'decl_ci_{r}_{h}_lo']:.1f}, "
              f"{N[f'decl_ci_{r}_{h}_hi']:.1f}]  (n_boot={len(a)})")

pn = os.path.join(HERE, '..', 'paper_numbers.json')
d = json.load(open(pn)); d.update(N); json.dump(d, open(pn, 'w'), indent=1)
print(f"\nmerged {len(N)} bootstrap keys into paper_numbers.json")
