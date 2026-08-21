"""
qgis_elevation_ndvi_lawn.py -- run this INSIDE the QGIS Python Console
(Plugins > Python Console > Show Editor > open this file > Run script, the
green triangle) after build_ndvi_temporal_gpkg.py has produced
grapeexpectations_ndvi_temporal_<YEAR>.gpkg.

What it builds:
  - the vineyard DEM as a soft grayscale elevation basemap (stretched
    singleband gray, not hillshade -- hillshade's shadow model reads as
    stark black/white "binary" blocks on this terrain's real ~200m relief)
  - the long-format per-date NDVI point layer on top: one thin vertical
    LINE marker per tile centroid -- length (NOT width) scales with that
    date's NDVI, color rides tan->dark-green. Narrow and long reads as an
    actual blade instead of a wide shape that washes out into a solid
    mass at even moderate density. Zoomed into a patch, 33,028 of these
    read as a patchy lawn; the season's Temporal Controller playback
    grows and shrinks them.
  - the layer's 'date' field wired into QGIS's native Temporal Controller.

Three rounds of fixes behind this version, in case any of this recurs:
  1. First version used QGIS's stock landuse_grass.svg (a 4-blade tuft)
     with per-feature data-defined size AND color. Continuous data-defined
     size means almost every feature gets a distinct (size, color) key,
     so QGIS's SVG raster cache almost never hits -- it rasterizes the SVG
     fresh per feature. Switched to a vector-drawn QgsSimpleMarkerSymbolLayer
     (no rasterization needed at all).
  2. That first vector marker used shape=Triangle, which is wide relative
     to its height -- at any real density the triangles overlap edge to
     edge and the "grass" reads as one solid green mass (washout), not
     texture. shape=Line fixes this: size controls LENGTH, strokeWidth
     controls thickness, set independently -- long and thin stays
     distinguishable at densities a filled shape can't.
  3. The source data was hex POLYGON geometry duplicated one row per
     (tile, date) -- 1.78M polygon features total, each needing its
     symbol placed via a QgsCentroidFillSymbolLayer indirection (fill
     symbol wrapping a marker sub-symbol) since a marker can't be a
     polygon layer's direct renderer. Rebuilt the source as CENTROID
     POINT geometry instead: smaller WKB per feature, no centroid
     computed at render time, and the marker can be the layer's direct
     renderer with no wrapper layer. Re-run build_ndvi_temporal_gpkg.py
     to regenerate the gpkg in this shape before running this script.
  4. The script's own default view was the real bug behind "still slow"
     after fixes 1-3: it zoomed to the FULL DEM extent on load, which is
     the one view that's actually slow (~2.7s/frame measured, vs
     ~0.12s/frame at single-block zoom) -- 33k+ simultaneously visible
     markers is a real cost, not a bug, so the fix is defaulting to a fast
     view rather than eliminating that cost. Now opens zoomed to one block.

After running: View > Panels > Temporal Controller, set the step to a
couple of days, hit Play. Blade length range, thickness, and the
tan->green color stops are all one-line tweaks below.
"""
from pathlib import Path

from qgis.core import (
    QgsProject, QgsRasterLayer, QgsVectorLayer, QgsRectangle,
    QgsSimpleMarkerSymbolLayer, QgsMarkerSymbol, QgsSingleSymbolRenderer,
    QgsProperty, QgsVectorLayerTemporalProperties, QgsDateTimeRange,
    QgsSingleBandGrayRenderer, QgsContrastEnhancement,
)
from qgis.PyQt.QtCore import QDateTime, QDate
from qgis.PyQt.QtGui import QColor

YEAR = 2024
BASE = Path("/home/simonhans/coding/GeoGastronomy/GrapeExpectations")

# --- elevation basemap: soft gradient, not hillshade ---
dem = QgsRasterLayer(
    str(BASE / "RegressionRidge/data/DEM/RegressionRidge_DEM_latlon.tif"), "elevation"
)
QgsProject.instance().addMapLayer(dem)

enhancement = QgsContrastEnhancement(dem.dataProvider().dataType(1))
enhancement.setContrastEnhancementAlgorithm(QgsContrastEnhancement.StretchToMinimumMaximum)
enhancement.setMinimumValue(dem.dataProvider().bandStatistics(1).minimumValue)
enhancement.setMaximumValue(dem.dataProvider().bandStatistics(1).maximumValue)
gray_renderer = QgsSingleBandGrayRenderer(dem.dataProvider(), 1)
gray_renderer.setContrastEnhancement(enhancement)
dem.setRenderer(gray_renderer)
dem.triggerRepaint()

# --- NDVI-through-season "lawn" layer (point geometry) ---
gpkg = BASE / "powerbi_dashboard" / f"grapeexpectations_ndvi_temporal_{YEAR}.gpkg"
ndvi = QgsVectorLayer(f"{gpkg}|layername=ndvi_by_date", f"NDVI {YEAR} (blade)", "ogr")
QgsProject.instance().addMapLayer(ndvi)

blade = QgsSimpleMarkerSymbolLayer()
blade.setShape(QgsSimpleMarkerSymbolLayer.Line)
blade.setStrokeWidth(0.35)  # thin -- this is what keeps it a "blade" not a "bar"
blade.setDataDefinedProperty(
    QgsSimpleMarkerSymbolLayer.PropertySize,
    QgsProperty.fromExpression('scale_linear("ndvi", 0.05, 0.55, 1.5, 9)'),
)
blade.setDataDefinedProperty(
    QgsSimpleMarkerSymbolLayer.PropertyStrokeColor,
    QgsProperty.fromExpression(
        "color_mix_rgb('#d9c38a', '#0a4d0a', scale_linear(\"ndvi\", 0.05, 0.55, 0, 100))"
    ),
)
blade.setStrokeColor(QColor("#4a7d2e"))  # fallback if data-defined color fails to evaluate

marker = QgsMarkerSymbol()
marker.deleteSymbolLayer(0)
marker.appendSymbolLayer(blade)

ndvi.setRenderer(QgsSingleSymbolRenderer(marker))
ndvi.setOpacity(0.95)

temporal = ndvi.temporalProperties()
temporal.setMode(QgsVectorLayerTemporalProperties.ModeFeatureDateTimeInstantFromField)
temporal.setStartField("date")
temporal.setIsActive(True)

# NOTE: don't call aggregate('layer','min/max','date') on this layer from
# the console/expression bar -- it's a full-table scan and will hang the
# session for minutes on a layer this size. Season range hardcoded below.
QgsProject.instance().timeSettings().setTemporalRange(
    QgsDateTimeRange(QDateTime(QDate(YEAR, 1, 7)), QDateTime(QDate(YEAR, 12, 9)))
)

# Default view is ONE vineyard block, not the full DEM extent. Measured
# directly (QgsMapRendererParallelJob, 8 frames each): a single-block frame
# averages ~0.12s (playback feels live); the full-vineyard-block view
# averages ~2.7s/frame (playback feels like a slideshow). This is the
# actual fix for "the animation is slow" -- the renderer was already fast
# enough, the script was just opening on the slow view by default. Pan out
# yourself if you want the wider view; just know playback there is ~20x
# slower per frame, that's a real cost of 33k+ visible markers, not a bug.
iface.mapCanvas().setExtent(QgsRectangle(-119.762, 45.878, -119.756, 45.882))
iface.mapCanvas().refresh()

print(
    "Loaded, zoomed to a single vineyard block (fast: ~0.12s/frame measured). "
    "Open View > Panels > Temporal Controller, set a ~2-3 day step, hit Play."
)
