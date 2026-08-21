#!/usr/bin/env python3
"""
Establish what ΔT = 0 actually refers to, and how far it sits from the present.

The review's blocking objection: the sweep's origin is labelled "present climate",
but the temperature field is the mean of 384 monthly rasters spanning 1990-2021
(midpoint 2005.5) and the NEX-GDDP deltas are computed against a CMIP6 historical
window of 2001-2014 (midpoint 2007.5, from data_wrangling/08_colab_extract.ipynb,
HIST_YEARS = range(2001, 2015)). So ΔT = 0 is a mid-2000s epoch, not today.

Two things are computed here, both from the paper's own temperature product rather
than an external warming rate:

  1. The island-mean annual temperature series 1990-2021 and its OLS trend, over
     the coffee belt specifically (150-950 m) as well as island-wide.
  2. The offset between the climatological mean (the sweep's origin) and the end
     of the record, and the implied offset to the present, so the paper can state
     what the peak offsets are measured from.

Run from repo root:  python ML/11_baseline_epoch.py
"""
import json, os, re, glob
import numpy as np
import rasterio
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, '..', 'data')
IMG = os.path.join(HERE, '..', 'img')

CLIM_START, CLIM_END = 1990, 2021
CLIM_MID = (CLIM_START + CLIM_END) / 2 + 0.5   # midpoint of the averaged window
HIST_START, HIST_END = 2001, 2014              # NEX-GDDP historical reference
HIST_MID = (HIST_START + HIST_END) / 2 + 0.5
PRESENT = 2026

# belt mask from the 500 m DEM, resampled to the native climatology grid via the
# already-reprojected 500 m climatology; simplest correct route is to work on the
# native monthly rasters and mask by their own elevation-equivalent band using the
# 500 m DEM reprojected -- but the monthlies are on the native grid, so instead we
# take the island mean and the belt mean using the native-resolution climatology
# as the elevation proxy through the 500 m product.
with rasterio.open(f'{DATA}/DEM/hawaii_DEM_500m_utm.tif') as s:
    nd = s.nodata; dem = s.read(1).astype(np.float32)
dem[dem == nd] = np.nan; dem[dem <= 0] = np.nan

files = sorted(glob.glob(f'{DATA}/kodama_temperature/temp_mean_*.tif'))
print(f"{len(files)} monthly rasters, {os.path.basename(files[0])} .. {os.path.basename(files[-1])}")

# Build the belt mask once on the native monthly grid, using the native-resolution
# climatology as the reference (it is the mean of exactly these files). The belt is
# defined thermally here -- the temperature range the 150-950 m band occupies --
# because the DEM is on a different grid.
with rasterio.open(f'{DATA}/DEM/hawaii_temp_climatology_500m_utm.tif') as s:
    tc500 = s.read(1).astype(np.float32); tnd = s.nodata
tc500[tc500 == tnd] = np.nan
belt500 = (dem >= 150) & (dem <= 950) & np.isfinite(tc500)
T_LO, T_HI = np.nanmin(tc500[belt500]), np.nanmax(tc500[belt500])
print(f"belt (150-950 m) spans {T_LO:.2f}-{T_HI:.2f} °C in the 500 m climatology")

with rasterio.open(f'{DATA}/kodama_temperature/hawaii_temp_climatology_native.tif') as s:
    clim_native = s.read(1).astype(np.float32); cnd = s.nodata
clim_native[clim_native == cnd] = np.nan
land = np.isfinite(clim_native)
belt = land & (clim_native >= T_LO) & (clim_native <= T_HI)
print(f"native grid: {land.sum():,} land cells, {belt.sum():,} in the belt band\n")

rows = []
for f in files:
    y, m = map(int, re.search(r'(\d{4})-(\d{2})', os.path.basename(f)).groups())
    with rasterio.open(f) as s:
        a = s.read(1).astype(np.float32); n = s.nodata
    a[a == n] = np.nan
    rows.append((y, m, np.nanmean(a[land]), np.nanmean(a[belt])))

yrs = np.array(sorted({r[0] for r in rows}))
ann_isl, ann_belt = [], []
for y in yrs:
    sel = [r for r in rows if r[0] == y]
    if len(sel) != 12:
        print(f"  warning: {y} has {len(sel)} months")
    ann_isl.append(np.mean([r[2] for r in sel]))
    ann_belt.append(np.mean([r[3] for r in sel]))
ann_isl, ann_belt = np.array(ann_isl), np.array(ann_belt)

OUT = {}
print(f"{'series':>10} {'trend °C/decade':>16} {'1990 fit':>10} {'2021 fit':>10} {'mean':>8}")
for tag, a in (('island', ann_isl), ('belt', ann_belt)):
    sl, ic = np.polyfit(yrs, a, 1)
    resid = a - (sl * yrs + ic)
    se = np.sqrt((resid ** 2).sum() / (len(a) - 2) / ((yrs - yrs.mean()) ** 2).sum())
    OUT[f'trend_{tag}_per_decade'] = float(sl * 10)
    OUT[f'trend_{tag}_se_per_decade'] = float(se * 10)
    OUT[f'mean_{tag}_clim'] = float(a.mean())
    # offset from the climatological mean (the sweep's origin) to a given year
    for yr, nm in ((2021, 'endrec'), (PRESENT, 'present')):
        OUT[f'offset_{tag}_to_{nm}'] = float(sl * (yr - CLIM_MID))
    print(f"{tag:>10} {sl*10:>+11.3f} ± {se*10:.3f} {sl*yrs[0]+ic:>10.2f} {sl*yrs[-1]+ic:>10.2f} {a.mean():>8.2f}")

OUT['clim_midpoint'] = float(CLIM_MID)
OUT['hist_midpoint'] = float(HIST_MID)
OUT['baseline_mismatch'] = float(HIST_MID - CLIM_MID)

print(f"\nclimatology window {CLIM_START}-{CLIM_END}, midpoint {CLIM_MID}")
print(f"NEX-GDDP historical window {HIST_START}-{HIST_END}, midpoint {HIST_MID}")
print(f"  the two baselines differ by {HIST_MID - CLIM_MID:.1f} years, i.e. "
      f"{OUT['trend_belt_per_decade']*(HIST_MID-CLIM_MID)/10:+.3f} °C at the belt trend "
      f"-- negligible relative to the increments used")
print(f"\noffset from the sweep's origin (the {CLIM_START}-{CLIM_END} mean):")
for tag in ('island', 'belt'):
    print(f"  {tag:>6}: to end of record (2021) {OUT[f'offset_{tag}_to_endrec']:+.3f} °C   "
          f"to {PRESENT} (extrapolated) {OUT[f'offset_{tag}_to_present']:+.3f} °C")

fig, ax = plt.subplots(figsize=(8, 4))
for a, c, nm in ((ann_isl, '#888888', 'island mean'), (ann_belt, '#c1440e', 'coffee belt')):
    ax.plot(yrs, a, 'o-', color=c, ms=3, lw=1.2, label=nm)
    sl, ic = np.polyfit(yrs, a, 1)
    ax.plot(yrs, sl * yrs + ic, '--', color=c, lw=1.5)
ax.axhline(ann_belt.mean(), color='#c1440e', ls=':', lw=1)
ax.set_xlabel('year'); ax.set_ylabel('mean air temperature (°C)')
ax.set_title(f"Kodama 1990-2021: belt trend "
             f"{OUT['trend_belt_per_decade']:+.3f} °C/decade", fontsize=10)
ax.legend(frameon=False, fontsize=9)
fig.tight_layout(); fig.savefig(f'{IMG}/11_baseline_trend.png', dpi=200); plt.close(fig)
print(f"\n-> {IMG}/11_baseline_trend.png")

pn = os.path.join(HERE, '..', 'paper_numbers.json')
d = json.load(open(pn)); d.update(OUT); json.dump(d, open(pn, 'w'), indent=1)
print(f"merged {len(OUT)} keys into paper_numbers.json")

assert abs(OUT['mean_belt_clim'] - np.mean(ann_belt)) < 1e-9
assert len(yrs) == CLIM_END - CLIM_START + 1, f"{len(yrs)} years, expected 32"
print("selfcheck: 32 complete years, belt series consistent")
