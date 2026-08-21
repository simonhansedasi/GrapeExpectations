#!/usr/bin/env python3
"""
Does the rainfall phase offset predict a different crop calendar in each district?

Arabica flowers on the first substantial rain following a dry period, and cherry
matures roughly 7-9 months after flowering. So a district's rainfall ONSET month
should set its flowering month, and onset + ~8 predicts harvest. Kona and Ka'u have
anti-phase rainfall (r = -0.58), so this predicts different crop calendars from
climate alone -- a prediction that can be checked against documented harvest
windows, which are not climate data and were not used to fit anything.

Onset is defined per cell without a fixed window: walk forward from that cell's own
driest month and take the first month whose rainfall crosses its annual mean. That
inherits no assumption from the old DRY_MONTHS=[6,7,8,9] definition, which was
Kona's wettest quarter.

Usage:  python data_wrangling/17_phenology_offset.py
"""
import os
import warnings

warnings.filterwarnings('ignore')
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.abspath(os.path.join(HERE, '..', 'data'))
NAMES = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
         'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
MATURATION = 8          # months, flowering -> ripe cherry (Arabica, mid-elevation)

cols = [f'month_{i:02d}' for i in range(1, 13)]
R = pd.read_csv(f'{DATA}/rainfall_monthly_climatology.csv').drop_duplicates('plot_id')
meta = pd.read_pickle(f'{DATA}/plot_all_features.pkl')
meta = meta[meta.label == 1][['plot_id', 'region']]
d = meta.merge(R, on='plot_id')
M = d[cols].values
reg = d.region.values
print(f"{len(d)} farm cells (kona {(reg=='kona').sum()}, kau {(reg=='kau').sum()})")


def onset(row):
    """First month after the driest that rises above the cell's annual mean."""
    dry = int(np.argmin(row))
    mean = row.mean()
    for k in range(1, 13):
        m = (dry + k) % 12
        if row[m] > mean:
            return m + 1                      # 1-indexed
    return np.nan


ons = np.array([onset(r) for r in M])
d['onset_month'] = ons
d['harvest_month'] = (ons - 1 + MATURATION) % 12 + 1
d[['plot_id', 'onset_month', 'harvest_month']].to_csv(
    f'{DATA}/phenology_offset.csv', index=False)

print(f"\n{'district':>8} {'driest':>8} {'onset':>8} {'+8mo -> predicted harvest':>28}")
pred = {}
for r in ('kona', 'kau'):
    sub = M[reg == r]
    dry = NAMES[int(np.argmin(sub.mean(axis=0)))]
    o = ons[reg == r]
    # circular mode is safer than a mean across the Dec/Jan wrap
    om = int(pd.Series(o).mode().iloc[0])
    hm = (om - 1 + MATURATION) % 12 + 1
    pred[r] = (om, hm)
    spread = pd.Series(o).value_counts(normalize=True).head(2)
    print(f"{r:>8} {dry:>8} {NAMES[om-1]:>8} {NAMES[hm-1]:>28}"
          f"   (onset {100*spread.iloc[0]:.0f}% of cells)")

off = (pred['kona'][0] - pred['kau'][0]) % 12
off = off if off <= 6 else off - 12
print(f"\nonset offset Kona - Ka'u: {off:+d} months")
print(f"predicted harvest: Kona {NAMES[pred['kona'][1]-1]}, Ka'u {NAMES[pred['kau'][1]-1]}")
print("\nCheck these against documented harvest windows -- they are independent of")
print("every input used here, so agreement is real validation and disagreement means")
print("the flowering-trigger model is too simple for this island.")
