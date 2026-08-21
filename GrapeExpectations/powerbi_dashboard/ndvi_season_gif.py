#!/usr/bin/env python3
"""
ndvi_season_gif.py — animate the GrapeExpectations vineyard's NDVI through
one growing season, one frame per real Sentinel-2 composite date.

Pairs with canopy_trend_map.py (2024 start-of-grow -> pre-harvest-peak
delta, one number per cell): that map shows the summary, this shows the
thing it's a summary OF -- canopy greening up through spring, peaking in
summer, senescing in fall, frame by real satellite date (irregular
spacing, whatever days had a usable cloud-free pass) rather than an
evenly-spaced fake calendar.

Usage:
    python3 ndvi_season_gif.py [year]
    (defaults to 2024; reads dim_cells.csv from this directory and
    ../RegressionRidge/data/ndvi/tiles_100m2/ndvi_100m2_<year>.csv,
    writes ndvi_season_<year>.gif into this directory)
"""

import io
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.cm import ScalarMappable
from matplotlib.colors import Normalize
from PIL import Image

from _mapping import NDVI_CMAP, drop_contaminated_dates, masked_triangulation, to_local_meters

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "RegressionRidge" / "data"


def main() -> None:
    year = int(sys.argv[1]) if len(sys.argv) > 1 else 2024
    ndvi_path = DATA / "ndvi" / "tiles_100m2" / f"ndvi_100m2_{year}.csv"
    daily = pd.read_csv(ndvi_path)
    # A handful of dates carry 2 rows per tile (duplicate satellite passes)
    # -- average them down to one value per (tile, date), same defensive
    # move as the terrain load in export_powerbi.py.
    daily = daily.groupby(["tile_id", "date"], as_index=False)["ndvi"].mean()

    cells = pd.read_csv(HERE / "dim_cells.csv")[["tile_id", "lon", "lat"]]
    x, y = to_local_meters(cells["lon"].to_numpy(), cells["lat"].to_numpy())
    triang = masked_triangulation(x, y)
    tile_order = cells["tile_id"].to_numpy()

    print(f"{year}: {daily['date'].nunique()} satellite dates, {cells['tile_id'].nunique()} cells")
    daily, dates = drop_contaminated_dates(daily)
    print(f"  {len(dates)} dates remain after dropping contaminated composites")

    # Fixed color scale across every frame -- per-frame autoscaling would
    # make the animation lie, since a uniformly dim early-spring frame would
    # then look just as "green" as a peak-summer one.
    vmin, vmax = daily["ndvi"].quantile([0.01, 0.99])
    norm = Normalize(vmin=vmin, vmax=vmax)

    fig, ax = plt.subplots(figsize=(9, 7), dpi=110)
    cbar = fig.colorbar(ScalarMappable(norm=norm, cmap=NDVI_CMAP), ax=ax, shrink=0.7, pad=0.02)
    cbar.set_label("NDVI")

    def frame_values(date):
        day = daily[daily["date"] == date].set_index("tile_id")["ndvi"]
        return day.reindex(tile_order).to_numpy()

    # Render each frame to an in-memory PNG and hand the sequence to
    # Pillow's own GIF writer, rather than matplotlib's FuncAnimation +
    # PillowWriter path -- that path has a known frame-buffer-size bug in
    # this environment's older matplotlib (raises "not enough image data").
    frames = []
    for date in dates:
        ax.clear()
        ax.set_aspect("equal")
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)
        ax.tricontourf(triang, frame_values(date), levels=20, cmap=NDVI_CMAP, norm=norm)
        ax.set_title(f"Vineyard NDVI — {date}", fontsize=14, weight="bold")

        buf = io.BytesIO()
        fig.savefig(buf, format="png", facecolor="white")
        buf.seek(0)
        frames.append(Image.open(buf).convert("RGB"))

    plt.close(fig)

    out = HERE / f"ndvi_season_{year}.gif"
    frames[0].save(
        out, save_all=True, append_images=frames[1:], duration=200, loop=0
    )
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
