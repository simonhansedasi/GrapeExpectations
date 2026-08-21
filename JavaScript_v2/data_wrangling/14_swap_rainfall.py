#!/usr/bin/env python3
"""
Swap the coarse ~4 km precip_annual for the 250 m Rainfall Atlas values sampled by
`13_rainfall_atlas.py`, and recompute the four projected precipitation pickles so
they keep their original scenario ratios.

The old column was not merely coarse, it was inverted: it put Kona at a 6,471 mm/yr
mean and Ka'u at 741, when the atlas has Kona at 1,321 and Ka'u at 1,783. Every
"Kona wet / Ka'u dry" statement in the repo descends from it.

Backs up each pickle to *.bak_precip4km before writing. Re-runnable: restores from
the backup first, so running twice does not compound.

Also replaces the seasonal columns. precip_dry / precip_wet / precip_dry_frac used
DRY_MONTHS = [6,7,8,9] ("Kona leeward dry season") for BOTH districts; measured
against the monthly climatology those are Kona's four WETTEST months (125 vs 77
mm/mo) and Ka'u's driest are Apr-Jul. The districts' monthly cycles are
anti-correlated (r = -0.58), so no single window can serve both. The three are
blanked and replaced with window-free descriptors computed per cell:

    precip_driest_q / precip_wettest_q   mm in that cell's driest/wettest 3
                                         consecutive months (BIO17/BIO16-style)
    precip_seasonality                   CV of monthly means (BIO15-style)
    precip_peak_sin / _cos / _month      PHASE -- the circular mean of the cycle.
                                         This is the one that matters: amplitude is
                                         near-identical between districts, and the
                                         entire difference is timing (Kona peaks
                                         month 7.4, Ka'u 12.2).

Requires `15_rainfall_seasonality.py` to have built the monthly climatology; without
it the seasonal step is skipped with a warning and only precip_annual is swapped.

Usage:  python data_wrangling/14_swap_rainfall.py
"""
import argparse
import os
import shutil

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.abspath(os.path.join(HERE, '..', 'data'))
RAIN = os.path.join(DATA, 'rainfall_atlas_250m.csv')
BASE = ['df.pkl', 'plot_climate_features.pkl']
PROJ = ['plot_climate_features_ssp245_2035.pkl', 'plot_climate_features_ssp245_2045.pkl',
        'plot_climate_features_ssp585_2035.pkl', 'plot_climate_features_ssp585_2045.pkl']
SEASONAL = ['precip_dry', 'precip_wet', 'precip_dry_frac']
SUFFIX = '.bak_precip4km'


def load(name):
    """Read a pickle, restoring from backup first so re-runs are idempotent."""
    path = os.path.join(DATA, name)
    bak = path + SUFFIX
    if os.path.exists(bak):
        shutil.copy2(bak, path)
    else:
        shutil.copy2(path, bak)
    return path, pd.read_pickle(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--drop-seasonal', action='store_true',
                    help='blank precip_dry/wet/dry_frac rather than leave them stale')
    args = ap.parse_args()

    rain = pd.read_csv(RAIN).drop_duplicates('plot_id').set_index('plot_id').rain_mm
    print(f"atlas values: {len(rain)} cells, {rain.min():.0f}-{rain.max():.0f} mm")

    # ratios must be read BEFORE the baselines are overwritten
    _, base_old = load('plot_climate_features.pkl')
    ratios = {}
    for name in PROJ:
        path = os.path.join(DATA, name)
        bak = path + SUFFIX
        src = bak if os.path.exists(bak) else path
        d = pd.read_pickle(src)
        r = d.set_index('plot_id').precip_annual / base_old.set_index('plot_id').precip_annual
        ratios[name] = r
        print(f"  {name}: scenario precip ratio {r.min():.3f}-{r.max():.3f}")

    for name in BASE:
        path, d = load(name)
        old = d.precip_annual.copy()
        d['precip_annual'] = d.plot_id.map(rain)
        if args.drop_seasonal:
            for c in SEASONAL:
                if c in d.columns:
                    d[c] = np.nan
        miss = d.precip_annual.isna().sum()
        d.to_pickle(path)
        print(f"\n{name}: {len(d)} rows, {miss} unmatched")
        print(f"  old mean {old.mean():7.0f} mm  ({old.nunique()} distinct)")
        print(f"  new mean {d.precip_annual.mean():7.0f} mm  ({d.precip_annual.nunique()} distinct)")
        if 'region' in d.columns:
            for r in ('kona', 'kau'):
                s = d[d.region == r].precip_annual
                print(f"    {r:5s} {s.min():6.0f}-{s.max():6.0f} mm  mean {s.mean():6.0f}")

    base_new = pd.read_pickle(os.path.join(DATA, 'plot_climate_features.pkl'))
    bn = base_new.set_index('plot_id').precip_annual
    for name in PROJ:
        path, d = load(name)
        d['precip_annual'] = d.plot_id.map(bn * ratios[name])
        if args.drop_seasonal:
            for c in SEASONAL:
                if c in d.columns:
                    d[c] = np.nan
        d.to_pickle(path)
        print(f"{name}: new mean {d.precip_annual.mean():.0f} mm")

    # ── seasonality, from the monthly climatology if it exists ──────────────────
    # The old precip_dry/wet/dry_frac used DRY_MONTHS=[6,7,8,9] ("Kona leeward dry
    # season") for BOTH districts. Measured, those are Kona's four WETTEST months
    # (125 vs 77 mm/mo), and Ka'u's driest are Apr-Jul. The two districts' monthly
    # cycles are anti-correlated (r = -0.58), so no single window can serve both.
    # Replaced with window-free descriptors computed per cell from its own cycle:
    #   precip_driest_q / precip_wettest_q  -- mm in that cell's driest/wettest
    #                                          3 consecutive months (BIO17/BIO16-style)
    #   precip_seasonality                  -- CV of monthly means (BIO15-style)
    clim_path = os.path.join(DATA, 'rainfall_monthly_climatology.csv')
    if not os.path.exists(clim_path):
        print("\nNOTE: no monthly climatology yet -- run 15_rainfall_seasonality.py. "
              "precip_dry / precip_wet / precip_dry_frac left as-is and are "
              "INCONSISTENT with the new precip_annual.")
        return

    c = pd.read_csv(clim_path).drop_duplicates('plot_id').set_index('plot_id')
    mo = c[[f'month_{i:02d}' for i in range(1, 13)]].values
    wrap = np.concatenate([mo, mo[:, :2]], axis=1)          # circular quarters
    q = np.stack([wrap[:, i:i + 3].sum(axis=1) for i in range(12)], axis=1)
    # Amplitude alone does NOT separate these districts -- measured, Kona and Ka'u
    # have near-identical driest/wettest quarters and seasonality (181/396/30 vs
    # 214/455/29). The whole difference is PHASE: Kona peaks in September, Ka'u in
    # March, cycles anti-correlated at r = -0.58. So carry phase explicitly, as the
    # circular mean of the monthly cycle encoded sin/cos (a raw month number would
    # put December and January 11 apart instead of 1).
    ang = 2 * np.pi * np.arange(12) / 12.0
    wsum = mo.sum(axis=1)
    px = (mo * np.cos(ang)).sum(axis=1) / wsum
    py = (mo * np.sin(ang)).sum(axis=1) / wsum
    seas = pd.DataFrame({
        'precip_driest_q': q.min(axis=1),
        'precip_wettest_q': q.max(axis=1),
        'precip_seasonality': 100.0 * mo.std(axis=1, ddof=0) / mo.mean(axis=1),
        'precip_peak_cos': px / np.hypot(px, py),
        'precip_peak_sin': py / np.hypot(px, py),
        'precip_peak_month': (np.degrees(np.arctan2(py, px)) % 360) / 30.0 + 1.0,
    }, index=c.index)
    print(f"\nseasonality from {len(seas)} cells' own monthly cycles")

    for name in BASE + PROJ:
        path = os.path.join(DATA, name)
        d = pd.read_pickle(path)
        for col in SEASONAL:                 # old windowed columns: blank, never silent
            if col in d.columns:
                d[col] = np.nan
        for col in seas.columns:
            d[col] = d.plot_id.map(seas[col])
        d.to_pickle(path)
    print(f"  wrote precip_driest_q / precip_wettest_q / precip_seasonality to "
          f"{len(BASE + PROJ)} pickles; {'/'.join(SEASONAL)} blanked")

    base = pd.read_pickle(os.path.join(DATA, 'df.pkl'))
    if 'region' in base.columns:
        for r in ('kona', 'kau'):
            s = base[base.region == r]
            print(f"    {r:5s} driest q {s.precip_driest_q.mean():5.0f} mm  "
                  f"wettest q {s.precip_wettest_q.mean():5.0f} mm  "
                  f"seasonality {s.precip_seasonality.mean():4.0f}  "
                  f"peak month {s.precip_peak_month.mean():4.1f}")


if __name__ == '__main__':
    main()
