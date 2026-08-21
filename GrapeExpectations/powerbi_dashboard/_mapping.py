"""
Shared geometry, color, and data-cleaning helpers for GrapeExpectations
hex-cell maps. Used by both canopy_trend_map.py and ndvi_season_gif.py --
the same fixes apply either way, only the per-cell values being colored
change.
"""

import matplotlib.tri as mtri
import numpy as np
from matplotlib.colors import LinearSegmentedColormap

# Diverging pair from the studio palette: red (declined) <-> gray (flat)
# <-> blue (built up), centered at zero. Used for any NDVI DELTA between
# two dates/periods -- a signed polarity, not a magnitude, so it needs
# this instead of NDVI_CMAP below. Red first so negative reads red and
# positive reads blue, matching every caption that uses it.
DELTA_CMAP = LinearSegmentedColormap.from_list(
    "ndvi_delta", ["#e34948", "#f0efec", "#0d366b"]
)

# Bare soil tan -> mid canopy green -> full canopy dark green. Not the
# studio's documented sequential blue ramp: NDVI is universally read as
# green-means-vegetated by anyone who's seen a vegetation index before, and
# a blue "how green is it" scale would fight that convention for no reason
# worth paying. Low end is tan, not white -- a white low end would vanish
# into the page background and read as "no data" instead of "present but
# low," the same void-trap a black floor causes on a sequential ramp, just
# triggered from the light end instead of the dark one.
NDVI_CMAP = LinearSegmentedColormap.from_list(
    "ndvi_green", ["#d9c38a", "#0ca30c", "#0a4d0a"]
)


def to_local_meters(lon, lat):
    """
    Flatten lon/lat to local x/y meters around the data's own centroid.
    The vineyard spans well under a degree in either direction, so a simple
    equirectangular approximation is accurate to a few centimeters here --
    no projection library needed for an area this small.
    """
    lon0, lat0 = lon.mean(), lat.mean()
    x = (lon - lon0) * 111_320 * np.cos(np.radians(lat0))
    y = (lat - lat0) * 110_540
    return x, y


def masked_triangulation(x, y, gap_multiplier=3):
    """
    Delaunay triangulation of (x, y) with triangles spanning real gaps
    between disconnected vineyard blocks masked out, so tricontourf doesn't
    interpolate color across land that has no cells at all. Plain
    tricontourf fills the whole convex hull of the input points -- with a
    vineyard split into separate blocks, that smears color across the empty
    gaps between them.
    """
    triang = mtri.Triangulation(x, y)
    verts = np.stack([x[triang.triangles], y[triang.triangles]], axis=-1)
    edge_a = np.linalg.norm(verts[:, 0] - verts[:, 1], axis=1)
    edge_b = np.linalg.norm(verts[:, 1] - verts[:, 2], axis=1)
    edge_c = np.linalg.norm(verts[:, 2] - verts[:, 0], axis=1)
    max_edge = np.maximum(np.maximum(edge_a, edge_b), edge_c)
    typical_spacing = np.median(np.minimum(np.minimum(edge_a, edge_b), edge_c))
    triang.set_mask(max_edge > typical_spacing * gap_multiplier)
    return triang


def drop_contaminated_dates(daily, value_col="ndvi", dip_threshold=0.1):
    """
    Drop dates where the mean of value_col dips more than dip_threshold
    below BOTH chronological neighbors -- the signature of a single
    cloud/shadow-contaminated satellite composite, not real change. A
    genuine multi-date decline (e.g. autumn senescence into dormancy) is
    protected: it never dips below both a neighbor AND recovers right
    after, so it never trips this check.

    Returns (filtered_daily, kept_dates).
    """
    date_means = daily.groupby("date")[value_col].mean()
    dates = sorted(date_means.index)
    keep = []
    for i, d in enumerate(dates):
        prev_v = date_means[dates[i - 1]] if i > 0 else date_means[d]
        next_v = date_means[dates[i + 1]] if i < len(dates) - 1 else date_means[d]
        if date_means[d] < prev_v - dip_threshold and date_means[d] < next_v - dip_threshold:
            print(f"  dropping {d}: mean {value_col} {date_means[d]:.3f} vs "
                  f"neighbors {prev_v:.3f}/{next_v:.3f} -- looks cloud-contaminated")
            continue
        keep.append(d)
    return daily[daily["date"].isin(keep)], keep
