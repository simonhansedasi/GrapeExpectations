#!/usr/bin/env python3
"""
export_powerbi.py — reshape GrapeExpectations pipeline output into a
Power-BI-ready star schema.

TRAINING MISSION CONTEXT
-------------------------
Power BI (like Tableau, Looker, etc.) wants a *star schema*: a couple of
small "dimension" tables (things you filter, slice, and color by) related
to a "fact" table (the actual measurements, at their natural grain) through
shared ID columns. Building those relationships in Power BI's model view is
itself a core chunk of what "Power BI skills" means on a resume -- so this
script deliberately writes out THREE tables instead of one flat CSV, to
give you that step to practice instead of skipping it.

Grain of each output table:
    dim_cells.csv         one row per hex cell            (33,028 rows)
    dim_years.csv          one row per growing season       (10 rows, 2016-2025)
    fact_ndvi_yearly.csv    one row per (hex cell, year)      (~330,280 rows)

Relationships to draw in Power BI's Model view (drag column to column):
    dim_cells[tile_id]  --1:*-->  fact_ndvi_yearly[tile_id]
    dim_years[year]     --1:*-->  fact_ndvi_yearly[year]

Everything here only reads and reshapes existing pipeline output under
RegressionRidge/data/ and RegressionRidge/ML/ (see ../README.md for how
that data was produced). It does not touch the ML pipeline.

NOT INCLUDED: cluster / mean_vigor / mean_stability / health from
ML/clusters.csv. That file (and its companion df_clustered.pkl) was last
written 2026-04-01 against an old ~3,598-cell grid; terrain_100m2.csv and
the centroid file were regenerated 2026-06-02 at ~32,978 cells -- a
resolution change, not just added area. clusters.csv's "plot_id" numbering
almost certainly doesn't line up with the current tile_id scheme, so
joining it back in would silently mislabel cells rather than just leave
some blank. Add it back once RegressionRidge/ML/clustering.ipynb has been
rerun against the current higher-res feature set and produces a
clusters.csv keyed to today's tile_id.

Usage:
    python3 export_powerbi.py
    (writes the three CSVs into this same directory)
"""

from datetime import datetime
from pathlib import Path
from typing import Tuple

import numpy as np
import pandas as pd

from _mapping import drop_contaminated_dates

# This file lives in GrapeExpectations/powerbi_dashboard/, so the project
# root -- and the RegressionRidge data it reads from -- is one level up.
ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "RegressionRidge" / "data"
ML = ROOT / "RegressionRidge" / "ML"
OUT = Path(__file__).resolve().parent

NDVI_YEARS = range(2016, 2026)  # inclusive of both ends: 2016 .. 2025

# Earliest month-day eligible to be picked as that year's pre-green-up
# trough. Without this floor, the search (correctly, by design) picks
# whatever pre-peak date has the lowest vineyard-wide mean NDVI -- but in
# 2 of the 10 years (2022, 2025) that landed in raw January, i.e. winter
# dormancy/holiday-season noise, not the spring trough canopy_trend_map.py
# was designed around. Checked against all 10 years before picking this:
# Feb 1 excludes both January outliers while leaving every already-sensible
# spring trough untouched, including the earliest legitimate one (2016,
# Feb 8) -- Feb 15 or Mar 1 would also fix the outliers but needlessly
# push 2016's trough later. Peak and harvest dates stay fully data-driven,
# no equivalent floor needed -- neither ever landed outside the growing
# season across any of the 10 years.
TROUGH_FLOOR_MD = "02-01"


def _iso_week_date(year: int, week: int, weekday: int) -> str:
    """ISO year/week/weekday -> 'YYYY-MM-DD'. (date.fromisocalendar() needs
    Python 3.8+; this env is 3.7, so strptime with %G/%V/%u does the same
    conversion.)"""
    return datetime.strptime(f"{year}-W{week}-{weekday}", "%G-W%V-%u").date().isoformat()


def load_cell_geometry() -> pd.DataFrame:
    """One row per hex cell: tile_id plus its centroid lon/lat, for mapping."""
    return pd.read_csv(DATA / "polygons" / "tiles_100m2_centroids.csv")


def load_terrain() -> pd.DataFrame:
    """
    Static terrain features per cell (elevation, slope, aspect, curvature).

    The source CSV has more rows than unique tile_ids even though terrain
    doesn't change year to year -- collapse with a groupby mean so each
    cell ends up with exactly one row. If the duplicate rows genuinely
    agree (as they should for a static DEM feature) the mean changes
    nothing; this just makes the join safe either way.
    """
    terrain = pd.read_csv(DATA / "terrain_100m2.csv")
    dupes = terrain["tile_id"].duplicated().sum()
    if dupes:
        print(f"  note: terrain_100m2.csv has {dupes} duplicate tile_id rows; "
              f"averaging them down to one row per cell")
    keep = ["tile_id", "elev_mean", "slope_mean", "aspect_mean", "curvature_mean",
            "aspect_cos", "aspect_sin", "slope_x", "slope_y",
            "profile_curv_mean", "plan_curv_mean"]
    return terrain[keep].groupby("tile_id", as_index=False).mean()


def load_ndvi_yearly() -> pd.DataFrame:
    """
    Long-format fact table: one row per (tile_id, year) holding that cell's
    mean NDVI across every satellite pass in that growing season.
    """
    yearly = []
    for year in NDVI_YEARS:
        path = DATA / "ndvi" / "tiles_100m2" / f"ndvi_100m2_{year}.csv"
        if not path.exists():
            print(f"  note: no NDVI file for {year}, skipping")
            continue
        daily = pd.read_csv(path)
        cell_year = daily.groupby("tile_id", as_index=False)["ndvi"].mean()
        cell_year["year"] = year
        yearly.append(cell_year.rename(columns={"ndvi": "ndvi_mean"}))
    return pd.concat(yearly, ignore_index=True)


def ndvi_trend_per_cell(fact_ndvi: pd.DataFrame) -> pd.DataFrame:
    """
    Slope of a straight-line fit through each cell's yearly NDVI: positive
    means canopy vigor improved over 2016-2025, negative means it declined.
    One number per cell -- lets the map be colored by trajectory instead of
    just a single year's snapshot.

    Kept for the map's diverging color and as a long-run summary, but NOT
    the right metric for "which cells build up / decline the most" --
    averaging a whole season into one number per year washes out the
    within-season up-then-down cycle entirely. See phenology_slopes()
    below for that.
    """
    trend = (
        fact_ndvi.groupby("tile_id")[["year", "ndvi_mean"]]
        .apply(lambda g: np.polyfit(g["year"], g["ndvi_mean"], 1)[0])
        .rename("ndvi_trend_per_year")
        .reset_index()
    )
    return trend


def phenology_slopes() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Two per-cell-per-year rates that describe the SHAPE of a growing season
    instead of collapsing it to one yearly mean (which is what
    ndvi_trend_per_cell does, and why it can't answer "how intensely does
    this patch build up and shed canopy"): buildup_rate (NDVI/day from the
    spring trough to the pre-harvest peak) and decline_rate (NDVI/day from
    that peak down to the harvest-window low). Same "peak"/"harvest"
    definitions canopy_trend_map.py and harvest_decline_map.py already use
    for a single season (2024) -- generalized here across every year --
    with one addition: the pre-peak trough search is floored at
    TROUGH_FLOOR_MD so a winter dip can't be picked as "start" (see that
    constant's comment for why).

    A shared vineyard-wide date per phase per year, not a per-cell argmax --
    same reasoning as the single-season scripts: a per-cell argmax over
    ~50 noisy dates lets neighboring cells land on different dates from
    measurement noise alone, which would inflate cell-to-cell variance
    with noise instead of signal.

    Returns (yearly, dates):
      yearly -- one row per (tile_id, year): buildup_rate, decline_rate.
                Grain matches fact_ndvi_yearly.csv -- this is the season-
                by-season detail, not collapsed to a 10-year average. The
                10-year mean per cell (for the map/leaderboard/scatter) is
                a simple groupby of this in main(), not computed here.
      dates  -- one row per year: start_date, peak_date, harvest_date,
                days_build, days_decline. Vineyard-wide, not per-cell --
                belongs in dim_years.csv, not fact_ndvi_yearly.csv.
    """
    yearly_rows = []
    date_rows = []
    for year in NDVI_YEARS:
        path = DATA / "ndvi" / "tiles_100m2" / f"ndvi_100m2_{year}.csv"
        if not path.exists():
            print(f"  note: no NDVI file for {year}, skipping phenology for that year")
            continue
        daily = pd.read_csv(path)
        daily = daily.groupby(["tile_id", "date"], as_index=False)["ndvi"].mean()
        daily, _ = drop_contaminated_dates(daily)

        win_start = _iso_week_date(year, 36, 1)  # harvest window start, ISO week 36
        win_end = _iso_week_date(year, 43, 7)    # harvest window end, ISO week 43
        trough_floor = f"{year}-{TROUGH_FLOOR_MD}"

        pre_harvest = daily[daily["date"] < win_start]
        peak_date = pre_harvest.groupby("date")["ndvi"].mean().idxmax()
        peak = pre_harvest[pre_harvest["date"] == peak_date].set_index("tile_id")["ndvi"]

        pre_peak = daily[(daily["date"] < peak_date) & (daily["date"] >= trough_floor)]
        start_date = pre_peak.groupby("date")["ndvi"].mean().idxmin()
        start = pre_peak[pre_peak["date"] == start_date].set_index("tile_id")["ndvi"]

        harvest_window = daily[(daily["date"] >= win_start) & (daily["date"] <= win_end)]
        harvest_date = harvest_window.groupby("date")["ndvi"].mean().idxmin()
        harvest = harvest_window[harvest_window["date"] == harvest_date].set_index("tile_id")["ndvi"]

        days_build = (pd.Timestamp(peak_date) - pd.Timestamp(start_date)).days
        days_decline = (pd.Timestamp(harvest_date) - pd.Timestamp(peak_date)).days
        yearly_rows.append(pd.DataFrame({
            "tile_id": peak.index,
            "year": year,
            "buildup_rate": (peak - start) / days_build,
            "decline_rate": (harvest - peak) / days_decline,
        }).reset_index(drop=True))
        date_rows.append({
            "year": year,
            "phenology_start_date": start_date,
            "phenology_peak_date": peak_date,
            "phenology_harvest_date": harvest_date,
            "phenology_days_build": days_build,
            "phenology_days_decline": days_decline,
        })

    yearly = pd.concat(yearly_rows, ignore_index=True)
    dates = pd.DataFrame(date_rows)
    return yearly, dates


def main() -> None:
    print("Loading source tables...")
    geometry = load_cell_geometry()
    terrain = load_terrain()
    fact_ndvi = load_ndvi_yearly()
    trend = ndvi_trend_per_cell(fact_ndvi)
    print("Computing phenology slopes (reads all 10 years of raw daily NDVI, ~45s)...")
    phenology_yearly, phenology_dates = phenology_slopes()
    phenology_agg = phenology_yearly.groupby("tile_id", as_index=False).agg(
        buildup_rate_mean=("buildup_rate", "mean"),
        decline_rate_mean=("decline_rate", "mean"),
    )
    dim_years = pd.read_csv(DATA / "weather_annual_100m2.csv").merge(phenology_dates, on="year", how="left")

    print("Building dim_cells...")
    dim_cells = (
        geometry
        .merge(terrain, on="tile_id", how="left")
        .merge(trend, on="tile_id", how="left")
        .merge(phenology_agg, on="tile_id", how="left")
    )

    # Looker Studio's map charts want ONE "Location" dimension, not separate
    # lat/lon fields -- pre-combine here so the only manual step left in the
    # UI is setting this column's Type to Geo > Latitude, Longitude.
    dim_cells["lat_lon"] = dim_cells["lat"].astype(str) + "," + dim_cells["lon"].astype(str)

    # Season-by-season detail, not collapsed to the 10-year average above --
    # same (tile_id, year) grain fact_ndvi_yearly already has, so this is a
    # plain column-add, not a new table to blend.
    fact_ndvi = fact_ndvi.merge(phenology_yearly, on=["tile_id", "year"], how="left")

    # One check per join step would be overkill; this one catches the failure
    # mode that actually matters -- a bad key silently dropping or duplicating
    # cells -- without hand-verifying every intermediate table.
    assert len(dim_cells) == len(geometry), \
        "dim_cells row count changed during merge -- a join key is duplicated somewhere"
    assert set(fact_ndvi["tile_id"]) <= set(dim_cells["tile_id"]), \
        "fact_ndvi_yearly references tile_ids that don't exist in dim_cells"
    assert fact_ndvi["buildup_rate"].notna().mean() > 0.99, \
        "phenology_yearly join dropped most cell-year rows -- check the (tile_id, year) key"

    OUT.mkdir(exist_ok=True)
    dim_cells.to_csv(OUT / "dim_cells.csv", index=False)
    dim_years.to_csv(OUT / "dim_years.csv", index=False)
    fact_ndvi.to_csv(OUT / "fact_ndvi_yearly.csv", index=False)

    print(f"\nWrote {len(dim_cells)} rows -> dim_cells.csv")
    print(f"Wrote {len(dim_years)} rows -> dim_years.csv")
    print(f"Wrote {len(fact_ndvi)} rows -> fact_ndvi_yearly.csv")
    print(f"\nAll three files are in {OUT}/  -- see HOW_TO_LOAD.md for the Power BI steps.")


if __name__ == "__main__":
    main()
