#!/usr/bin/env python3
"""
export_qgis.py — reshape GrapeExpectations pipeline output into a
QGIS-ready GeoPackage.

TRAINING MISSION CONTEXT
-------------------------
export_powerbi.py builds the same dim_cells table but with lat/lon
POINTS, because Looker Studio's map chart only takes a Location
dimension. That's also exactly why Looker crashed: drawing 32,978
individual point markers client-side. A real GIS tool doesn't have that
problem -- it wants actual polygon geometry and renders it as one layer,
regardless of feature count. This script reuses export_powerbi.py's
loaders (same terrain/NDVI-trend logic, same v1/v2 clusters.csv
exclusion -- see that file's docstring) but joins them onto the real hex
polygons instead of centroids, and writes a single GeoPackage instead of
CSVs.

Usage:
    python3 export_qgis.py
    (writes grapeexpectations.gpkg into this same directory)
"""

from pathlib import Path

import geopandas as gpd

from export_powerbi import DATA, load_ndvi_yearly, load_terrain, ndvi_trend_per_cell

OUT = Path(__file__).resolve().parent


def load_cell_polygons() -> gpd.GeoDataFrame:
    """Real hex polygon geometry, one row per cell, WGS84 (CRS84)."""
    return gpd.read_file(DATA / "polygons" / "tiles_100m2.geojson")[["tile_id", "geometry"]]


def main() -> None:
    print("Loading source tables...")
    polygons = load_cell_polygons()
    terrain = load_terrain()
    fact_ndvi = load_ndvi_yearly()
    trend = ndvi_trend_per_cell(fact_ndvi)

    latest_year = fact_ndvi["year"].max()
    latest_ndvi = (
        fact_ndvi[fact_ndvi["year"] == latest_year][["tile_id", "ndvi_mean"]]
        .rename(columns={"ndvi_mean": f"ndvi_mean_{latest_year}"})
    )

    print("Building GeoDataFrame...")
    cells = (
        polygons
        .merge(terrain, on="tile_id", how="left")
        .merge(trend, on="tile_id", how="left")
        .merge(latest_ndvi, on="tile_id", how="left")
    )

    # Same failure mode export_powerbi.py guards against: a bad join key
    # silently duplicating or dropping cells rather than just leaving gaps.
    assert len(cells) == len(polygons), \
        "row count changed during merge -- a join key is duplicated somewhere"
    assert cells.geometry.notna().all(), "some cells ended up with null geometry"

    out = OUT / "grapeexpectations.gpkg"
    cells.to_file(out, driver="GPKG", layer="hex_cells")

    print(f"\nWrote {len(cells):,} polygons -> {out}")
    print(f"Columns: {list(cells.columns)}")
    print(f"Bounds (lon/lat): {tuple(round(b, 4) for b in cells.total_bounds)}")
    print("\nOpen in QGIS: Layer > Add Layer > Add Vector Layer > grapeexpectations.gpkg")
    print("See HOW_TO_LOAD_QGIS.md for a first styling exercise.")


if __name__ == "__main__":
    main()
