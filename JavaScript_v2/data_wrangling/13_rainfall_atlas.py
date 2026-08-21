#!/usr/bin/env python3
"""
Sample 250 m mean annual rainfall (Rainfall Atlas of Hawai'i, Giambelluca et al.
2013, 1978-2007) for every grid cell, replacing the coarse ~4 km precipitation
in df.pkl.

Why this exists: the old precip_annual has 4 distinct values across 59 Ka'u cells
and 8 across 258 Kona cells, so at that resolution precipitation acts as a region
label rather than a measurement -- any model using it to separate the districts is
circular. It also appears to be simply wrong: it puts leeward Kona at 3,695-7,858
mm/yr, which is windward-Hilo territory.

Source: the atlas's own download host (atlas.uhtapis.org) returns 403 to scripted
requests, so this pulls the same raster from the State of Hawaii GIS Program's
ArcGIS service, which documents it as the Giambelluca product reprojected to UTM
Zone 4 HARN (EPSG:3750).

Resumable: appends to the output CSV and skips cells already present. Safe to re-run.

Usage:  python data_wrangling/13_rainfall_atlas.py [--batch 200] [--delay 1.0]
"""
import argparse
import os
import sys
import time

import numpy as np
import pandas as pd
import requests

URL = ("https://geodata.hawaii.gov/arcgis/rest/services/"
       "Climate_Raster/MapServer/identify")
LAYER = 9                      # Annual Rainfall (millimeters)
HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, '..', 'data')
OUT = os.path.join(DATA, 'rainfall_atlas_250m.csv')
# whole-island extent; imageDisplay must match its aspect or identify returns []
EXTENT = (-156.15, 18.85, -154.75, 20.35)
ASPECT = (EXTENT[2] - EXTENT[0]) / (EXTENT[3] - EXTENT[1])
IMGDISP = f"{int(800 * ASPECT)},800,96"


def fetch(session, pts, tol, retries=4):
    """One identify call for a batch of (lon, lat). Returns list of (x3750, y3750, mm)."""
    payload = {
        'geometry': str({'points': [[float(a), float(b)] for a, b in pts],
                         'spatialReference': {'wkid': 4326}}).replace("'", '"'),
        'geometryType': 'esriGeometryMultipoint',
        'layers': f'all:{LAYER}',
        'tolerance': tol,
        'mapExtent': ','.join(str(v) for v in EXTENT),
        'imageDisplay': IMGDISP,
        'returnGeometry': 'true',
        'f': 'json',
    }
    for attempt in range(1, retries + 1):
        try:
            r = session.post(URL, data=payload, timeout=60)
            r.raise_for_status()
            js = r.json()
        except Exception as e:
            print(f"    retry {attempt}/{retries}: {e}", flush=True)
            time.sleep(3 * attempt)
            continue
        out = []
        for res in js.get('results', []):
            g = res.get('geometry') or {}
            v = res.get('attributes', {}).get('Stretch.Pixel Value')
            try:
                mm = float(v)
            except (TypeError, ValueError):
                continue          # 'NoData' over ocean
            if 'x' in g:
                out.append((g['x'], g['y'], mm))
        return out
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--batch', type=int, default=200)
    ap.add_argument('--delay', type=float, default=1.0)
    ap.add_argument('--labelled-only', action='store_true',
                    help='only the 471 coffee-farm cells (fast smoke test)')
    args = ap.parse_args()

    import geopandas as gpd
    from pyproj import Transformer

    d = pd.read_pickle(f'{DATA}/plot_all_features.pkl')
    if args.labelled_only:
        d = d[d.label == 1]
    g = gpd.GeoDataFrame(d.copy(), geometry='geometry', crs='EPSG:4326')
    cen = g.geometry.centroid
    df = pd.DataFrame({'plot_id': g.plot_id.values,
                       'lon': cen.x.values, 'lat': cen.y.values})
    # project once so returned geometries (EPSG:3750) can be matched back to inputs
    tf = Transformer.from_crs('EPSG:4326', 'EPSG:3750', always_xy=True)
    df['x'], df['y'] = tf.transform(df.lon.values, df.lat.values)

    done = set()
    if os.path.exists(OUT):
        done = set(pd.read_csv(OUT).plot_id)
        print(f"resuming: {len(done)} cells already sampled")
    todo = df[~df.plot_id.isin(done)].reset_index(drop=True)
    print(f"{len(todo)} cells to sample, batch={args.batch}, delay={args.delay}s "
          f"({int(np.ceil(len(todo)/args.batch))} requests)")
    if not len(todo):
        print("nothing to do")
        return

    if not os.path.exists(OUT):
        pd.DataFrame(columns=['plot_id', 'rain_mm']).to_csv(OUT, index=False)

    got = miss = 0
    with requests.Session() as s:
        for i in range(0, len(todo), args.batch):
            chunk = todo.iloc[i:i + args.batch]
            res = fetch(s, chunk[['lon', 'lat']].values, tol=2)
            if res is None:
                print(f"  batch {i//args.batch}: FAILED, leaving for a re-run", flush=True)
                continue
            # match each returned pixel back to its nearest input point rather than
            # trusting result order -- NoData cells are dropped, which shifts it
            rows = []
            if res:
                R = np.array([[a, b] for a, b, _ in res])
                V = np.array([m for _, _, m in res])
                P = chunk[['x', 'y']].values
                for j, p in enumerate(P):
                    k = int(np.argmin(((R - p) ** 2).sum(axis=1)))
                    if ((R[k] - p) ** 2).sum() <= 250.0 ** 2:
                        rows.append((chunk.plot_id.values[j], V[k]))
            got += len(rows)
            miss += len(chunk) - len(rows)
            if rows:
                pd.DataFrame(rows, columns=['plot_id', 'rain_mm']).to_csv(
                    OUT, mode='a', header=False, index=False)
            print(f"  batch {i//args.batch + 1}/{int(np.ceil(len(todo)/args.batch))}: "
                  f"+{len(rows)} ({got} total, {miss} no-data)", flush=True)
            time.sleep(args.delay)

    print(f"\nDone. sampled={got} nodata_or_missing={miss} -> {OUT}")


if __name__ == '__main__':
    main()
