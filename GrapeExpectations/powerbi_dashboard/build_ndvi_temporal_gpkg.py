#!/usr/bin/env python3
"""
build_ndvi_temporal_gpkg.py -- long-format (tile, date, ndvi) CENTROID POINT
geometry for QGIS's native Temporal Controller: one point feature per
(tile, satellite date). Reuses the same contaminated-date filter as
ndvi_season_gif.py so the animation doesn't include cloud/shadow artifacts.

Point, not the original hex polygon: a point marker renderer can be
assigned directly (no QgsCentroidFillSymbolLayer indirection needed) and
the smaller point WKB is cheaper to read per feature than the ~7-vertex
hex polygon, which matters at 1.7M+ rows re-read every animation frame.

Usage:
    /home/simonhans/anaconda3/envs/GrapeExpectations/bin/python build_ndvi_temporal_gpkg.py [year]
    (defaults to 2024; writes grapeexpectations_ndvi_temporal_<year>.gpkg
    into this directory)
"""
import sqlite3
import sys
from pathlib import Path

import geopandas as gpd
import pandas as pd

from _mapping import drop_contaminated_dates

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "RegressionRidge" / "data"


def main() -> None:
    year = int(sys.argv[1]) if len(sys.argv) > 1 else 2024

    daily = pd.read_csv(DATA / "ndvi" / "tiles_100m2" / f"ndvi_100m2_{year}.csv")
    daily = daily.groupby(["tile_id", "date"], as_index=False)["ndvi"].mean()
    daily, dates = drop_contaminated_dates(daily)
    daily["date"] = pd.to_datetime(daily["date"])

    hexes = gpd.read_file(DATA / "polygons" / "tiles_100m2.geojson")[["tile_id", "geometry"]]
    hexes["geometry"] = hexes["geometry"].centroid
    gdf = hexes.merge(daily, on="tile_id", how="inner")

    out = HERE / f"grapeexpectations_ndvi_temporal_{year}.gpkg"
    gdf.to_file(out, layer="ndvi_by_date", driver="GPKG")

    # GeoPackage gets a spatial rtree index for free; QGIS's Temporal
    # Controller filters on the 'date' attribute on every repaint, which
    # without its own index is a full scan of this (large) table -- add one.
    conn = sqlite3.connect(out)
    conn.execute("CREATE INDEX idx_ndvi_by_date_date ON ndvi_by_date(date)")
    conn.commit()
    conn.close()

    print(f"{len(dates)} dates x {hexes['tile_id'].nunique()} tiles = {len(gdf)} features -> {out}")


if __name__ == "__main__":
    main()
