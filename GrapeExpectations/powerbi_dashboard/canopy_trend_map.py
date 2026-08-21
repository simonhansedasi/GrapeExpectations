#!/usr/bin/env python3
"""
canopy_trend_map.py — one static, postable map of 2024 canopy build-up
across the GrapeExpectations vineyard: per-cell NDVI delta from start of
the growing season to peak NDVI before harvest.

Two definitional calls, stated explicitly since they change what the map
means: "start of grow" = the pre-green-up trough -- the lowest-mean-NDVI
date among everything before the peak, found from the data rather than
hardcoded. (An earlier version of this script used the literal first date
of the year, 2024-01-07, instead; that overlaps winter cover-crop/soil-
moisture greenness with actual vine dormancy, which undersells how much
the vines themselves built up. The trough usually lands in April/May, once
the plateau season begins.) "Peak before harvest" = the single pre-harvest
date with the highest vineyard-wide mean NDVI, using the harvest-window
convention already used elsewhere in this pipeline's ML notebooks (ISO
week 36, ~Sept 2). Delta = peak − start, so a more positive cell built up
more canopy over the season; this replaced an earlier version of this
script that computed a 9-year (2016-2025) linear trend instead of a single
season's build-up.

This is the counterpart to the Looker Studio exercise, not a replacement
for it: the BI dashboard demonstrates the tool, this demonstrates the
finding. 30k+ points as a bubble map turns to visual mud in a browser
tool -- here, matplotlib draws it as a continuous filled surface
(tricontourf) instead of one marker per cell, so all 32,978 cells render
as one clean gradient with no crash and no overlap smear.

Color: diverging red (declined) <-> gray (flat) <-> blue (built up),
centered at zero. The delta genuinely spans negative to positive -- plenty
of cells show LESS NDVI at the June peak than on the January start date,
not just noise -- so this is a polarity around a baseline, not a pure
magnitude, and needs the studio's diverging pair rather than the
sequential green ramp ndvi_season_gif.py uses for absolute NDVI level.
(An earlier version of this script reused that sequential ramp here; it
made "declined" cells look tan/bare, which collides with what tan means
in the companion GIF.)

Usage:
    python3 canopy_trend_map.py
    (reads dim_cells.csv and ../RegressionRidge/data/ndvi/tiles_100m2/ndvi_100m2_2024.csv,
    writes canopy_trend_map.png)
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.colors import Normalize

from _mapping import DELTA_CMAP, drop_contaminated_dates, masked_triangulation, to_local_meters

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "RegressionRidge" / "data"

HARVEST_WINDOW_START = "2024-09-02"  # ISO week 36 -- the harvest-window convention already used in RegressionRidge/ML


def main() -> None:
    daily = pd.read_csv(DATA / "ndvi" / "tiles_100m2" / "ndvi_100m2_2024.csv")
    daily = daily.groupby(["tile_id", "date"], as_index=False)["ndvi"].mean()
    daily, _ = drop_contaminated_dates(daily)

    # "Peak NDVI" as a single shared date -- whichever pre-harvest date the
    # vineyard as a whole was greenest -- rather than each cell's own
    # independent max. A per-cell argmax over ~40 noisy dates lets
    # neighboring cells land on different dates purely from measurement
    # noise, which inflates cell-to-cell variance with noise, not signal
    # (confirmed visually: an argmax version of this map was badly
    # speckled). One shared peak date is also the more literal reading of
    # "peak NDVI before harvest" as a point in the season.
    pre_harvest = daily[daily["date"] < HARVEST_WINDOW_START]
    peak_date = pre_harvest.groupby("date")["ndvi"].mean().idxmax()
    peak = pre_harvest[pre_harvest["date"] == peak_date].set_index("tile_id")["ndvi"]

    # "Start of grow" as the pre-green-up trough, not the literal first date
    # of the year -- January NDVI is inflated by winter cover crop / soil
    # moisture between rows, not vine signal, so it undersells how much the
    # vines themselves built up. The trough is just the lowest-mean date
    # among everything before the peak -- no hardcoded date, so this still
    # finds the right point if run against a different year or a vineyard
    # with a different calendar.
    pre_peak = daily[daily["date"] < peak_date]
    start_date = pre_peak.groupby("date")["ndvi"].mean().idxmin()
    start = pre_peak[pre_peak["date"] == start_date].set_index("tile_id")["ndvi"]

    buildup = (peak - start).rename("ndvi_buildup")
    print(f"start (pre-green-up trough): {start_date} | peak: {peak_date} "
          f"(highest mean NDVI before {HARVEST_WINDOW_START})")
    print(f"buildup -- mean {buildup.mean():.3f}, min {buildup.min():.3f}, max {buildup.max():.3f}")

    cells = pd.read_csv(HERE / "dim_cells.csv")[["tile_id", "lon", "lat"]]
    df = cells.merge(buildup, on="tile_id", how="left")
    x, y = to_local_meters(df["lon"].to_numpy(), df["lat"].to_numpy())

    fig, ax = plt.subplots(figsize=(10, 8), dpi=200)

    # Symmetric around zero so "flat" always lands on the neutral gray
    # midpoint, regardless of how skewed the actual min/max are.
    span = max(abs(df["ndvi_buildup"].quantile(0.01)), abs(df["ndvi_buildup"].quantile(0.99)))
    norm = Normalize(vmin=-span, vmax=span)
    triang = masked_triangulation(x, y)
    contour = ax.tricontourf(triang, df["ndvi_buildup"], levels=20, cmap=DELTA_CMAP, norm=norm)

    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)

    cbar = fig.colorbar(contour, ax=ax, shrink=0.7, pad=0.02)
    cbar.set_label("NDVI Δ (peak − start): red declined, blue built up", fontsize=10)

    ax.set_title(
        "2024 canopy build-up: bud break to pre-harvest peak",
        fontsize=15, weight="bold", pad=14,
    )
    ax.text(
        0.5, -0.04,
        f"{len(df):,} hex cells, ~100 m² each — Washington State wine country — "
        f"{start_date} to peak on {peak_date} — mean ΔNDVI {buildup.mean():.2f}",
        transform=ax.transAxes, ha="center", fontsize=9, color="#52514e",
    )

    # Simple scale bar -- 200 m, drawn directly rather than pulling in a
    # cartography dependency for one line and a tick.
    bar_len = 200
    x0 = x.min() + (x.max() - x.min()) * 0.05
    y0 = y.min() + (y.max() - y.min()) * 0.05
    ax.plot([x0, x0 + bar_len], [y0, y0], color="#0b0b0b", linewidth=2)
    ax.text(x0 + bar_len / 2, y0 + (y.max() - y.min()) * 0.015, "200 m",
             ha="center", fontsize=8, color="#0b0b0b")

    fig.tight_layout()
    out = HERE / "canopy_trend_map.png"
    fig.savefig(out, bbox_inches="tight", facecolor="white")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
