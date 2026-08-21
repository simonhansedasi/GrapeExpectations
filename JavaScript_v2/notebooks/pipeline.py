import os
import warnings

warnings.filterwarnings('ignore')
import numpy as np
import pandas as pd
import geopandas as gpd
import rasterio
from scipy.ndimage import maximum_filter, minimum_filter, distance_transform_edt
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
HW = np.sqrt(2 * np.log(2.0))        # half-width of the tau=0.5 level set, in sigmas
DT_HORIZON = {'2035': 1.00, '2045': 1.35}


def load_island():
    """Terrain stack + temperature climatology for every land cell on the island."""
    with rasterio.open(f'{DATA}/DEM/hawaii_DEM_500m_utm.tif') as s:
        nd, dem, tr = s.nodata, s.read(1).astype(np.float32), s.transform
        H, W, crs = s.height, s.width, s.crs
    dem[dem == nd] = np.nan
    dem[dem <= 0] = np.nan
    land = ~np.isnan(dem)
    ef = np.where(land, dem, np.nanmean(dem[land]))
    dy, dx = np.gradient(ef, 500., 500.)
    slope = np.degrees(np.arctan(np.sqrt(dx ** 2 + dy ** 2)))
    asp = np.arctan2(-dx, dy)
    asin_, acos_ = np.sin(asp), np.cos(asp)
    smax = maximum_filter(slope, size=3, mode='nearest')
    emax = maximum_filter(ef, size=3, mode='nearest')
    emin = minimum_filter(ef, size=3, mode='nearest')
    relief, local = emax - emin, dem - emin
    for a in (smax, asin_, acos_, relief, local):
        a[~land] = np.nan
    dcoast = distance_transform_edt(land) * 500.
    dcoast[~land] = np.nan
    flat = land.ravel()
    X = np.column_stack([a.ravel()[flat] for a in
                         (dem, smax, asin_, acos_, relief, local, dcoast)])
    with rasterio.open(f'{DATA}/DEM/hawaii_temp_climatology_500m_utm.tif') as s:
        tc = s.read(1).astype(np.float32)
        tc[tc == s.nodata] = np.nan
    tc[~land] = np.nan
    with rasterio.open(f'{DATA}/DEM/hawaii_historic_lava_500m_utm.tif') as s:
        lava = (s.read(1) == 1)
    # "farmable": workable slope, not on historic lava
    farmable = (smax.ravel()[flat] <= 25.) & ~np.isnan(smax.ravel()[flat]) & ~lava.ravel()[flat]
    return dict(X=X, T=tc.ravel()[flat], farmable=farmable,
                tr=tr, H=H, W=W, crs=crs, dem=dem, land=land)


def load_farms(isl):
    """The 471 labelled coffee cells, in the same feature space as the island."""
    allf = pd.read_pickle(f'{DATA}/plot_all_features.pkl')
    fp = gpd.GeoDataFrame(allf[allf.label == 1].copy(), geometry='geometry',
                          crs='EPSG:4326').to_crs(isl['crs'])
    cen = fp.geometry.centroid
    tr, H, W = isl['tr'], isl['H'], isl['W']
    ci = ((cen.x - tr.c) / tr.a).astype(int).values
    ri = ((cen.y - tr.f) / tr.e).astype(int).values
    ok = (ri >= 0) & (ri < H) & (ci >= 0) & (ci < W)
    with rasterio.open(f'{DATA}/DEM/hawaii_DEM_500m_utm.tif') as s:
        pass
    # rebuild the per-cell stack by sampling the same rasters at farm centroids
    idx = np.ravel_multi_index((ri[ok], ci[ok]), (H, W))
    lin = np.full(H * W, -1)
    lin[np.where(isl['land'].ravel())[0]] = np.arange(isl['X'].shape[0])
    pos = lin[idx]
    good = pos >= 0
    FT = isl['X'][pos[good]]
    FTemp = isl['T'][pos[good]]
    reg = fp['region'].values[ok][good]
    xy = np.column_stack([cen.x[ok][good], cen.y[ok][good]])
    keep = ~np.isnan(FT).any(axis=1) & ~np.isnan(FTemp)
    return FT[keep], FTemp[keep], reg[keep], xy[keep]


def spatial_blocks(reg, xy, cells_per_block=8, seed=0):
    """KMeans spatial blocks per district, for the block bootstrap."""
    out = {}
    for r in ('kona', 'kau'):
        m = reg == r
        n = int(m.sum())
        nb = max(4, int(round(n / cells_per_block)))
        lab = KMeans(n_clusters=nb, random_state=seed, n_init=10).fit_predict(xy[m])
        out[r] = (np.where(m)[0], lab, nb)
    return out


def screen(FT, reg, X, idx=None, wz=1.0, pct=95.0):
    """The stationary feasibility set S: cells within the farm envelope.

    Refits the standardiser, both district centroids and the percentile cutoff on
    whatever subset is passed, so a bootstrap replicate inherits none of the
    point estimate's parameters.
    """
    idx = np.arange(len(FT)) if idx is None else idx
    sc = StandardScaler().fit(FT[idx])
    Fs, Is = sc.transform(FT[idx]), sc.transform(X)
    if wz != 1.0:
        Fs, Is = Fs.copy(), Is.copy()
        Fs[:, 0] *= wz
        Is[:, 0] *= wz
    rr = reg[idx]
    ck, cq = Fs[rr == 'kona'].mean(0), Fs[rr == 'kau'].mean(0)
    dk = np.linalg.norm(Fs[rr == 'kona'] - ck, axis=1)
    dq = np.linalg.norm(Fs[rr == 'kau'] - cq, axis=1)
    th = np.percentile(np.concatenate([dk, dq]), pct)
    Dk, Dq = np.linalg.norm(Is - ck, axis=1), np.linalg.norm(Is - cq, axis=1)
    ident = 1 / (1 + Dq) - 1 / (1 + Dk)          # <=0 -> Kona-like
    inside = (Dk <= th) | (Dq <= th)
    return dict(inside=inside, kona_like=inside & (ident <= 0),
                kau_like=inside & (ident > 0), threshold=th)


def envelope(FTemp, reg, idx, region, sigma_infl=1.5):
    """Thermal envelope (mu, sigma) for one district, fit on the lapse surface."""
    T = FTemp[idx][reg[idx] == region]
    return T.mean(), T.std(ddof=1) * sigma_infl


def feasible_size(Tflat, mask, mu, sg, dt):
    """|F| at a given warming offset: farmable, screen-passing, inside the band."""
    lo, hi = mu - HW * sg - dt, mu + HW * sg - dt
    pool = np.sort(Tflat[mask])
    return int(np.searchsorted(pool, hi, 'right') - np.searchsorted(pool, lo, 'left'))


def pooled_union(isl, FT, FTemp, reg, idx=None, wz=1.0, dt=0.0):
    """Cells feasible for EITHER district -- total coffee ground on the island.

    The pooled union is the analysis unit because no district contrast in this
    project is resolvable (see notebook 02); reporting two separate declines
    invites a comparison the data cannot support.
    """
    idx = np.arange(len(FT)) if idx is None else idx
    s = screen(FT, reg, isl['X'], idx, wz)
    u = np.zeros(len(isl['X']), bool)
    for r, like in (('kona', s['kona_like']), ('kau', s['kau_like'])):
        mu, sg = envelope(FTemp, reg, idx, r)
        band = np.exp(-0.5 * ((isl['T'] + dt - mu) / sg) ** 2) > 0.5
        u |= isl['farmable'] & like & band
    return int(u.sum()), u
