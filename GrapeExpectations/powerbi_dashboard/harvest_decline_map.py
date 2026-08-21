#!/usr/bin/env python3
"""
harvest_decline_map.py — companion to canopy_trend_map.py: per-cell NDVI
delta from the pre-harvest peak to harvest itself, 2024 season.

Where canopy_trend_map.py shows the BUILD-UP phase (pre-green-up trough to
peak), this shows the DECLINE phase (peak to harvest). For wine grapes
this is usually not just senescence -- growers often deliberately cut back
irrigation after veraison to concentrate sugar/flavor in the fruit, so a
map that comes back mostly red (declining) here is an expected,
agronomically meaningful signal, not a data problem.

"Peak" reuses the same definition as canopy_trend_map.py: the single
shared pre-harvest date with the highest vineyard-wide mean NDVI (see that
script for why a per-cell argmax was rejected -- it applies here too).
"Harvest" mirrors that logic into the harvest window itself: the single
date with the LOWEST vineyard-wide mean NDVI within the harvest window
(ISO weeks 36-43, ~Sept 2 to ~Oct 27 -- the convention already used
elsewhere in this pipeline's ML notebooks) -- the furthest point into
decline actually observed during picking.

Usage:
    python3 harvest_decline_map.py
    (reads dim_cells.csv and ../RegressionRidge/data/ndvi/tiles_100m2/ndvi_100m2_2024.csv,
    writes harvest_decline_map.png)
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.colors import Normalize

from _mapping import DELTA_CMAP, drop_contaminated_dates, masked_triangulation, to_local_meters

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "RegressionRidge" / "data"

HARVEST_WINDOW_START = "2024-09-02"  # ISO week 36
HARVEST_WINDOW_END = "2024-10-27"  # ISO week 43 end -- same harvest-window convention used in RegressionRidge/ML


def main() -> None:
    daily = pd.read_csv(DATA / "ndvi" / "tiles_100m2" / "ndvi_100m2_2024.csv")
    daily = daily.groupby(["tile_id", "date"], as_index=False)["ndvi"].mean()
    daily, _ = drop_contaminated_dates(daily)

    pre_harvest = daily[daily["date"] < HARVEST_WINDOW_START]
    peak_date = pre_harvest.groupby("date")["ndvi"].mean().idxmax()
    peak = pre_harvest[pre_harvest["date"] == peak_date].set_index("tile_id")["ndvi"]

    harvest_window = daily[(daily["date"] >= HARVEST_WINDOW_START) & (daily["date"] <= HARVEST_WINDOW_END)]
    harvest_date = harvest_window.groupby("date")["ndvi"].mean().idxmin()
    harvest = harvest_window[harvest_window["date"] == harvest_date].set_index("tile_id")["ndvi"]

    decline = (harvest - peak).rename("ndvi_decline")
    print(f"peak: {peak_date} | harvest: {harvest_date} (lowest mean NDVI within the harvest window)")
    print(f"decline -- mean {decline.mean():.3f}, min {decline.min():.3f}, max {decline.max():.3f}")

    cells = pd.read_csv(HERE / "dim_cells.csv")[["tile_id", "lon", "lat"]]
    df = cells.merge(decline, on="tile_id", how="left")
    x, y = to_local_meters(df["lon"].to_numpy(), df["lat"].to_numpy())

    fig, ax = plt.subplots(figsize=(10, 8), dpi=200)

    # Symmetric around zero so "flat" always lands on the neutral gray
    # midpoint, regardless of how skewed the actual min/max are.
    span = max(abs(df["ndvi_decline"].quantile(0.01)), abs(df["ndvi_decline"].quantile(0.99)))
    norm = Normalize(vmin=-span, vmax=span)
    triang = masked_triangulation(x, y)
    contour = ax.tricontourf(triang, df["ndvi_decline"], levels=20, cmap=DELTA_CMAP, norm=norm)

    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)

    cbar = fig.colorbar(contour, ax=ax, shrink=0.7, pad=0.02)
    cbar.set_label("NDVI Δ (harvest − peak): red declined, blue held/built", fontsize=10)

    ax.set_title(
        "2024 pre-harvest decline: peak to harvest",
        fontsize=15, weight="bold", pad=14,
    )
    ax.text(
        0.5, -0.04,
        f"{len(df):,} hex cells, ~100 m² each — Washington State wine country — "
        f"peak on {peak_date} to harvest on {harvest_date} — mean ΔNDVI {decline.mean():.2f}",
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
    out = HERE / "harvest_decline_map.png"
    fig.savefig(out, bbox_inches="tight", facecolor="white")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
