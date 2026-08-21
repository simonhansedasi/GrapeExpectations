#!/usr/bin/env python3
"""KILL-TEST: after controlling for variety and processing, is there any signal
left that could be environmental?

Stage 1 (this script, no geocoding needed): do Kona and Ka'u cup scores differ at
all once variety, processing and year are held constant? District is the coarsest
possible environmental contrast -- rainfall differs 4-10x with zero overlap. If the
district term is dead here, a finer environmental signal at the farm level is very
unlikely to exist, and notebook 5 dies cheaply.

Uncertainty is bootstrapped over FARMS, not rows: the same farm enters many years
and its lots are not independent observations.

Caveat carried, not fixed: only scores >=80 are published, so this is a truncated
sample. Effects here are attenuated relative to the full entry pool.
"""
import numpy as np, pandas as pd, re

rng = np.random.default_rng(0)
df = pd.read_csv('hca_scores.csv')


def canon(s):
    s = s.lower()
    s = re.sub(r'[^a-z0-9 ]', ' ', s)
    s = re.sub(r'\b(llc|ltd|inc|co|farms?|coffee|estate|the|hawaiian|kona|company)\b', ' ', s)
    return re.sub(r'\s+', ' ', s).strip()


df['farm_id'] = df.farm.map(canon)
df = df[df.district.isin(['Kona', "Ka'u"])].copy()
df = df[df.variety.notna() & df.processing.notna()]
print(f"rows {len(df)}   distinct farms {df.farm_id.nunique()}")
print(df.groupby('district').agg(n=('score', 'size'), farms=('farm_id', 'nunique'),
                                 mean=('score', 'mean'), sd=('score', 'std')).to_string())


# Build the design matrix ONCE on the full sample; bootstrap resamples its ROWS by
# farm, so dummy columns stay aligned across replicates (a per-replicate rebuild
# would silently change the reference level and make coefficients incomparable).
parts = [np.ones((len(df), 1)), (df.district.values == "Ka'u").astype(float)[:, None]]
for col in ('variety', 'processing', 'year'):
    lv = sorted(df[col].astype(str).unique())[1:]      # drop first as reference
    parts.append(np.column_stack([(df[col].astype(str).values == v).astype(float)
                                  for v in lv]))
XFULL = np.hstack(parts)
YFULL = df.score.values


def fit(rows):
    X, y = XFULL[rows], YFULL[rows]
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    return beta[1]      # the Ka'u coefficient


raw = df[df.district == "Ka'u"].score.mean() - df[df.district == 'Kona'].score.mean()
adj = fit(np.arange(len(df)))
farms = df.farm_id.unique()
frows = {f: np.where(df.farm_id.values == f)[0] for f in farms}
boot = []
for _ in range(4000):
    pick = rng.choice(farms, len(farms), replace=True)
    rows = np.concatenate([frows[f] for f in pick])
    if df.district.values[rows].__contains__('Kona') is False:
        continue
    if len(set(df.district.values[rows])) < 2:
        continue
    try:
        boot.append(fit(rows))
    except Exception:
        pass
lo, hi = np.percentile(boot, [2.5, 97.5])

print(f"\nraw Ka'u - Kona difference        {raw:+.3f} points")
print(f"adjusted (variety+processing+year) {adj:+.3f} points   95% CI ({lo:+.3f}, {hi:+.3f})")
print(f"VERDICT: district effect {'SURVIVES' if (lo > 0 or hi < 0) else 'is DEAD'} the controls")

# How much room is there for ANY site-level signal? Compare within-farm repeat
# variation (same land, different years/lots) against between-farm variation.
# If a farm cannot reproduce its own score, no site variable can predict it.
rep = df.groupby('farm_id').score.agg(['mean', 'std', 'size'])
rep = rep[rep['size'] >= 3]
within = rep['std'].median()
between = df.groupby('farm_id').score.mean().std()
print(f"\nfarms with 3+ entries: {len(rep)}")
print(f"  median WITHIN-farm SD across years : {within:.2f} points")
print(f"  BETWEEN-farm SD of farm means      : {between:.2f} points")
print(f"  ratio between/within               : {between/within:.2f}")
print("  (ratio well under 1 means lot-to-lot noise swamps any stable site effect,")
print("   and no environmental variable can beat that ceiling)")

# variety/processing effect sizes, for scale -- how big is what we controlled for?
for col in ('variety', 'processing'):
    m = df.groupby(col).score.agg(['mean', 'size']).sort_values('mean')
    m = m[m['size'] >= 8]
    print(f"\n{col} spread (groups with n>=8): {m['mean'].max()-m['mean'].min():.2f} points")
    print(m.to_string())
