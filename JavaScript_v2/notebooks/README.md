# Notebook pipeline

Built 2026-07-30 to replace the scattered `data_wrangling/*.py` and `ML/*.py` scripts, which remain in the repo as artefacts. Run in order; each writes to `notebooks/data/`.

| notebook | produces | runtime |
|---|---|---|
| `01_data_assembly` | `grid_features.pkl` (10,211 cells), `farm_features.pkl` (471) | seconds |
| `02_district_characterization` | the what-differs inventory | seconds |
| `03_thermal_envelope` | `baseline_epoch.json`, envelopes | ~2 min (384 rasters) |
| `04_feasible_set` | `feasible_set.json`, `matched.json`, the inversion, the condition, the peak | ~1 min |
| `05_robustness` | sensitivity sweeps | ~15 min (bootstraps) |
| `06_gifs` | `figures/{temperature,envelope_upslope,envelope_screened}.gif` | seconds |

`pipeline.py` holds the shared screen and feasible-set geometry so it is defined once. The old pipeline drifted between `ML/09`, `ML/10` and `ML/14` because each re-implemented it.

`06_gifs` (2026-08-05) renders three AGU poster GIFs by sweeping `dt` from 0 to the 2045 reference increment (1.35 C) through the same `pipeline.py` functions — no new statistics. The envelope GIFs pool Kona/Ka'u into one band/one screened set (per the "districts indistinguishable" finding below) rather than coloring them separately — painting them separately produces confusing overlap slivers since the two envelopes nearly coincide. `make_gifs.py` is the same code as a plain script (`python make_gifs.py`), kept for quick regeneration without launching Jupyter.

## Regression checks

Every notebook asserts against `../paper_numbers.json` where a registered value exists. Confirmed reproductions:

| quantity | notebook | registered | reproduced |
|---|---|---|---|
| belt warming trend | 03 | +0.313 ± 0.065 C/decade | +0.313 ± 0.065 |
| climate-only gain (Kona 2045) | 04 | 69.8% | 69.8% |
| gain isotherm (Kona 2045) | 04 | 20.32 C | 20.32 C |
| pooled decline 2035 / 2045 | 04 | -13.7% / -22.1% | -13.7% / -22.1% |
| district declines 2045 | 04 | -26.4% / -18.2% | -26.4% / -18.2% |

Fresh code, same numbers. That is what makes this a replacement rather than a rewrite.

## What changed from the old pipeline

**Corrected inputs.** Annual rainfall came from a ~4 km product that had the districts **inverted** (Kona 6,471 mm vs Ka'u 741; actually 1,321 vs 1,783). Seasonal columns used `DRY_MONTHS = [6,7,8,9]`, which are Kona's four *wettest* months. Both replaced — 250 m Rainfall Atlas annual, plus window-free seasonality from 384 monthly HCDP rasters.

**Elevation once.** `elev_dev_mean` = `elev_mean` minus a scalar, r = 1.000. Dropped everywhere.

**Dropped.** `ML/03` (NDVI regression) is not carried forward: cross-validated R² is negative for both districts on the corrected data *and* the original, so its feature importances were a ranking of noise. See `../cup_scores/FINDINGS.md` for the parallel negative result on cup scores.

## Two definitions worth not confusing

"Climate-only gain" means **cells whose suitability increases**, i.e. cooler than `mu - dT/2`. That is ~70% of farmable land. It is *not* "cells newly entering the level set", which is ~11%. Notebook 04 computes the former and says so.

**Neither is the paper's headline any more.** Both are directional-gradient measures over all farmable land, and pairing either against a set-cardinality change over the footprint compares two different statistics — a cell can move closer to the optimum and still sit outside `C`, so that pairing cannot establish that `S` causes the sign flip. Notebook 04 now computes the matched version and the draft leads with it. The old `overestimate x` column (61x / 38x) is also retired: `S` is 15.2% of farmable land, so 69.8/1.1 was close to the reciprocal of that share and mostly mechanical.

## The result, in one line

Under a +1.35 C displacement the thermal set `|C|` is **flat** (-0.3% pooled, +2.2% for Ka'u) while the feasible set `|F|` contracts **22.1%**. The contraction is attributable to `S`, not to the climatic window — which is what the old unmatched pairing could not show.

## The condition (notebook 04, second half)

Inversion occurs when the window's displacement along the migration axis exceeds `S`'s headroom above the window's leading edge: `dz = dT/Gamma > h`. Belt lapse is 5.73 C/km, so +1.35 C displaces the window **236 m**; headroom is **197 m** (Kona) and **224 m** (Ka'u), giving `dz/h` = **1.19** and **1.05**. The share of `S` above the leading edge falls 17.6% -> 1.0% (Kona) and 23.4% -> 2.1% (Ka'u). Written to `data/matched.json`.

Caveat carried: `h` is a point estimate measured on the upper fringe, where the screen validates worst. Ka'u's 1.05 needs an interval before the condition is asserted for that district.

## Caveats carried forward

- The pooled decline's *magnitude* is screen-weight dependent (-12% at `w_z`=0 to -38% at `w_z`=2). Quote the range. Its *sign and significance* hold at every setting, including `w_z`=0 where elevation leaves the screen entirely.
- `05` uses 400 bootstrap replicates for tractability; the archived `ML/12`/`ML/14` use 2,000. Intervals here are marginally wider.
- No district contrast is resolvable. The pooled union is the unit — see `02`.
- `04`'s `figures/04_inversion.png` cell mislabels its gray swatch "farmable, not feasible": the base array covers all land cells (`isl['X']`), not just `isl['farmable']`, so gray actually merges that category with "not farmable at all" (too steep / historic lava). Found and fixed in `make_gifs.py`'s version of the same plot (2026-08-05); not yet fixed in `04` itself.
