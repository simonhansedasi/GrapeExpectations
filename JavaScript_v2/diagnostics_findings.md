# Geometry diagnostics — what the four blocking tests returned (2026-07-30)

Script: `ML/09_geometry_diagnostics.py`. Outputs: `img/09_F_vs_dT.png`, `img/09_F_vs_dT_noelev.png`, `img/09_features_vs_elevation.png`, `ML/09_sensitivity_grid.csv`. All 56 new quantities merged into `paper_numbers.json`. Self-check reproduces the published |F| and contraction for both districts, so the harness is the same one the paper's numbers come from.

## Headline: two results got much stronger, one central claim does not survive as stated

---

## A. The |F|(ΔT) sweep — the blocker. Partly bad news.

| ΔT | \|F\| Kona | \|F\| Ka'u |
|---|---|---|
| −1.50 | 1,502 | 1,208 |
| −1.00 | 1,738 | 1,641 |
| −0.50 | 1,860 | 1,920 |
| 0.00 | 1,780 | 2,035 |
| +0.50 | 1,599 | 2,038 |
| +1.00 | 1,371 | 1,840 |
| +1.35 | 1,158 | 1,612 |

Kona's intersection peaks at **ΔT = −0.55 °C**, Ka'u's at **+0.15 °C**. Both curves are near-symmetric bumps about their peak (asymmetry over ±1.35 °C: Kona 1.15x, Ka'u 1.00x).

The review's structural prediction is essentially confirmed. The intersection is maximised at approximately present-day climate and declines under displacement in *either* direction — cooling by 1.35 °C costs Kona about as much as warming by 1.35 °C. **"The intersection contracts under warming" is therefore not a finding about warming.** It is what happens when a window centred on a sample is translated off a footprint centred on that same sample, in whichever direction it goes.

Kona's −0.55 °C offset is the one genuinely directional signal: Kona is already about half a degree past its own best alignment, so warming costs it more than cooling would. Ka'u's +0.15 °C sits on the other side — Ka'u's feasible set is still marginally *improving* out to +0.15 °C before it turns over.

## B. Parameter sensitivity — direction robust, magnitude is not.

160 settings per district (metric x threshold x sigma inflation x tau).

- Kona: **155/160 contract**, range −19.7% to 0.0%, **median −7.0%**
- Ka'u: **159/160 contract**, range −30.4% to 0.0%, **median −7.6%**

The five non-contracting Kona settings and the one Ka'u setting are degenerate corners (sigma x2.0 with tau 0.1, where the level set saturates the footprint), not counterexamples.

So the abstract's "surviving every parameter setting tested" is directionally defensible — the intersection never expands. But the headline −15.5% / −12.4% sits at the extreme end of the grid; the median setting gives half that. Distance metric matters most (Euclidean −11.7%, Mahalanobis −4.8%).

## C. Elevation-band cross-validation — the upper fringe is the weakest part of the screen.

| held-out elevation band | n | recall |
|---|---|---|
| 98–375 m | 94 | 95.7% |
| 375–454 m | 93 | 88.2% |
| 454–533 m | 95 | 95.8% |
| 533–628 m | 94 | 96.8% |
| **628–944 m** | 95 | **64.2%** |
| in-sample reference | 471 | 94.9% |

Fitting on the lower 60% of the belt recovers only **63%** of the upper 40%.

The screen reconstructs the belt well everywhere except its top, and the top is where the entire adaptation argument lives. This has to be disclosed, and it means specific upper-fringe cells cannot be nominated with uniform confidence — a limitation the paper currently states qualitatively for latitude folds and should now state quantitatively for elevation.

## D. Terrain break above 950 m — the best news in the session. The frame is earned.

Slope of each feature per 100 m (farm-cell SD units), west flank, below vs above 950 m:

| feature | below 950 m | above 950 m | ratio |
|---|---|---|---|
| max slope | −0.050 | −0.137 | 2.7 |
| aspect sin | +0.009 | +0.048 | 5.2 |
| aspect cos | −0.022 | +0.087 | 4.0 (sign flip) |
| total relief | −0.065 | −0.198 | 3.1 |
| local relief | −0.039 | −0.215 | 5.5 |
| coast distance | +0.360 | +0.583 | 1.6 |

**Five of the six non-elevation features change slope by 2.7x to 5.5x above 950 m**, and aspect cosine reverses sign. Independently, mean distance to the Kona centroid crosses the 95th-percentile screen threshold at **937 m** — within 13 m of the footprint's stated 950 m upper bound, computed by a completely different route.

The review's test was "three of eight break sharply near 950 m and S really is geological there." Five of six did. Section 3.3's load-bearing assertion — that beyond the fringe "slope steepens, aspect and relief depart from the observed farm envelope" — is now demonstrated rather than asserted. This is the single highest-value figure to add, exactly as predicted.

## E. A defect nobody flagged: elevation is in the screen twice.

`elev_deviation = elevation − (island mean elevation)`, a scalar offset. Correlation with mean elevation across the 471 farm cells is **r = +1.000** — perfectly collinear. After standardisation the two features are the identical vector, so elevation contributes two of eight squared terms to every Euclidean distance. **The published screen weights elevation double.** That is also the mechanism behind the shared-coordinate problem the reviews raise.

Rebuilding the screen three ways:

| screen | footprint (Kona / Ka'u) | Jaccard vs published | \|F\| peak (Kona / Ka'u) | contraction +1.00→+1.35 |
|---|---|---|---|---|
| published, 8 features (elevation twice) | 5.9% / 8.9% | 100% | −0.55° / +0.15° | **−15.5% / −12.4%** |
| elevation once, 7 features | 6.0% / 8.4% | 88% | −0.65° / +0.15° | **−9.9% / −9.5%** |
| no elevation, 6 features | 8.0% / 12.2% | 66% | −0.85° / +0.30° | **−5.0% / −2.6%** |

Two things follow. First, the double-weighting inflates the headline contraction by roughly 5–6 percentage points; correcting it is not optional. Second, and more important, **the peak survives the removal of elevation entirely** (−0.85° / +0.30°), so the unimodal shape is not purely an artefact of C and S sharing a coordinate — but two-thirds of the contraction *magnitude* is. The footprint itself is fairly robust: dropping elevation entirely still retains 66% / 62% Jaccard overlap.

---

## What this means for the rebuild

**Dead as stated:** "the intersection contracts 7–16% under warming while neither set shrinks" as a discovery about warming. The sweep shows it contracts under displacement in any direction, and the magnitude depends on a double-counted feature.

**Alive and stronger:**

1. **S is real.** The footprint's upper boundary is a genuine terrain break (D), not the tail of the farm sample. The paper's central metaphor — fixed ground — is now evidence.
2. **The feasible set is at its maximum today.** Every climate pathway is downhill from present alignment; Kona is already about 0.55 °C past its own peak. This is a sharper and more defensible claim than the contraction percentage, and it is what makes the coffee berry borer compounding matter — the only gaining margin is both small and deteriorating.
3. **Direction is robust even if magnitude is not** (155/160, 159/160).

**Must be disclosed:** the 64% upper-band recall (C), the double-weighting correction (E), and the symmetry of the |F| curve (A).

---

# After the correction (same day)

The collinear feature was removed and every screen-dependent quantity recomputed by `ML/10_screen_corrected.py`, which reproduces all published values when run `--published` (8 features) and therefore differs from the old pipeline in nothing but the feature set. Diagnostics B and C were re-run on the corrected screen; A and D above are unchanged in substance.

## What moved

| quantity | published (8 feat.) | corrected (7 feat.) |
|---|---|---|
| Kona footprint | 5.95% | 5.99% |
| Ka'u footprint | 8.90% | 8.45% |
| Kona \|F\| 2035 | 1,371 | 1,349 |
| Ka'u \|F\| 2035 | 1,839 | 1,660 |
| Kona inter-horizon contraction | -15.5% | -9.9% |
| Ka'u inter-horizon contraction | -12.4% | -9.5% |
| Kona terrain declining 2035 | 69.0% | 64.7% |
| Ka'u terrain declining 2035 | 59.3% | 57.9% |
| Kona factor | 6.9x (6.3-9.1) | 7.0x (6.1-8.7) |
| Ka'u factor | 3.9x (3.2-8.6) | 4.3x (3.1-10.5) |
| \|F\| peak | -0.55 / +0.15 | -0.65 / +0.15 |
| SSP2-4.5 contraction | -7.9 / -5.6% | -5.7 / -4.8% |
| SSP5-8.5 contraction | -17.4 / -20.0% | -13.4 / -16.8% |

Unchanged, and asserted in the script rather than assumed: mu, sigma, the island-wide gain fractions, the gain isotherms, the farm-cell declining fractions and their bootstrap intervals. All are functions of the thermal envelope and the labelled farm cells, with no screen term.

## The correction improved the screen

Elevation-band cross-validation, published vs corrected:

| held-out band | published | corrected |
|---|---|---|
| 98-375 m | 95.7% | 96.8% |
| 375-454 m | 88.2% | 88.2% |
| 454-533 m | 95.8% | 95.8% |
| 533-628 m | 96.8% | 96.8% |
| **628-944 m** | **64.2%** | **90.5%** |
| fit lower 60% -> upper 40% | 63% | 75% |

Double-weighting elevation made the screen brittle in exactly the direction the paper needs it to extrapolate. Removing the duplicate fixes that, which is independent evidence that the duplicate was doing harm rather than being merely redundant.

## Parameter factorial, corrected screen

Kona 156/160 settings contract (median -7.2%, range -15.9% to 0.0%); Ka'u 157/160 (median -7.5%, range -25.0% to +1.9%). 313 of 320 overall. The seven exceptions are degenerate corners at extreme tau where the level set either saturates the footprint or falls outside it.

## Headline numbers the rebuilt paper uses

Relative to present climate, the feasible set falls 18.3% (Kona) and 9.6% (Ka'u) by 2035, and 26.4% and 18.2% by 2045. Measured against the counterfactual peak instead, the 2045 losses are 30.1% and 19.1%. Over the same interval the island-wide thermal set moves -0.6% and +0.6%, and the terrain set not at all.

## Still open

- **Lee et al. (2023) is carrying three separate claims** (2021-22 crop value, the $25.7 M CBB loss, the 20% yield decline). Not verified; the crop value normally traces to NASS. This is the one item from the reviews not closed.
- The C4b shape-matched null (size- and elongation-matched random patches) was dropped from the manuscript rather than re-run, since the multiplier is no longer load-bearing under the new framing. If it is ever reinstated it needs regenerating on the corrected screen.

---

# Round 22 (2026-07-30, same day) — the v3 review

Four new scripts: `ML/11_baseline_epoch.py`, `ML/12_peak_bootstrap.py`, `ML/13_density_and_breakpoint.py`, plus a fifth factor added to `ML/09`.

## The blocker was real, and worse than estimated — but its internal half dissolved

The sweep's origin is not the present. The temperature field is the mean of 384 monthly rasters spanning 1990-2021 (midpoint 2006), and the NEX-GDDP deltas are differenced against a CMIP6 historical window of **2001-2014** (midpoint 2008, from `data_wrangling/08_colab_extract.ipynb`, `HIST_YEARS = range(2001, 2015)`).

**The two baselines are only 2 years apart**, worth +0.063 °C — so the internal inconsistency the review feared between the climatology and the deltas is negligible, and that can now be stated with a number rather than left unstated.

**The labelling problem is worse than the review's ~0.3 °C estimate.** Regressing the product's own island-mean annual temperature on year across 32 complete years:

| series | trend | offset from climatological mean to end of record (2021) |
|---|---|---|
| island | +0.284 ± 0.062 °C/decade | +0.426 °C |
| coffee belt (150-950 m) | +0.313 ± 0.065 °C/decade | +0.470 °C |

Re-centring on the end of the *observed record* (no extrapolation needed) shifts both offsets by -0.47 °C, and Ka'u's headline claim inverts exactly as predicted.

## The argmax now has an interval, and it lands on the review's better sentence

| district | peak (vs 1990-2021 mean) | 95% CI | re-centred on 2021 | 95% CI |
|---|---|---|---|---|
| Kona | -0.66 °C | (-0.95, +0.03) | **-1.13 °C** | (-1.42, -0.44) **excludes zero** |
| Ka'u | +0.18 °C | (-0.18, +0.78) | -0.29 °C | (-0.65, +0.31) |

Difference Kona - Ka'u: -0.84 °C (-1.60, +0.01), not distinguishable. So the defensible claim is *not* that the districts differ, but that **neither is still approaching its optimum** — one measurably past it, one sitting on it.

## Proposition 1's premise fails for Ka'u

`s(z)` checked directly for the first time. Kona's feasible density is single-peaked (mode 325 m). **Ka'u's is not** — a broad 300-800 m plateau with three interior turning points. The conclusion still holds for Ka'u empirically because its level set is ±214 m wide, broader than the spacing of those maxima, so the convolution smooths them. The paper now states the proposition as verified-for-Kona and checked-by-computation-for-Ka'u.

The modes also explain the sign of the offsets, better than expected: Kona's feasible ground sits **170 m below** its farms, Ka'u's **200 m above** them. Same volcano, same thermal optimum, opposite sides of their own feasible ground.

## The 950 m breakpoint is not identified

Free-breakpoint segmented regression (continuous two-segment, 10 m grid, 400 bootstraps):

| descriptor | breakpoint | 95% CI |
|---|---|---|
| max slope | 910 m | (810, 1390) |
| coast distance | 900 m | (820, 930) |
| total relief | 820 m | (640, 1040) |
| local relief | 800 m | (690, 950) |
| aspect sin | 660 m | (600, 1390) |
| aspect cos | 1330 m | (690, 1400) |
| distance to centroid | 630 m | (600, 680) |

Median 860 m, range 660-1330. The transition is real but **diffuse**; 950 m is inside the range but is not identified as the breakpoint. The "937 m by an independent route" claim is **dropped entirely** — the review was right that it is confirmatory rather than independent, and the free-breakpoint fit on that same profile lands at 630 m, so quoting 937 m as corroboration was not defensible.

## Elevation weight as a fifth factor

Sweeping the standardised elevation coordinate's weight `w_z` from 0 to 2: contraction runs monotonically -5.0% to -20.0% (Kona) and -2.6% to -17.6% (Ka'u) — wider than the whole 320-setting factorial. **The peak barely moves**: -0.85 to -0.29 °C (Kona), +0.18 to +0.32 °C (Ka'u), never changing sign.

Internal check: a duplicated column is worth `w_z = sqrt(2)`, since two unit columns contribute 2 to a squared distance. At w_z = 1.4 the sweep returns -15.5% / -12.2%, reproducing the superseded eight-feature values (-15.5% / -12.4%). The v2 defect is now a point on a curve rather than an anecdote.

## An error found by chasing the 68% coincidence

The review flagged that Kona's area-weighted decline (68.0%) equals the acreage capture rate (100 - 32). Chasing it found that the area-weighted figures had **no pipeline source at all** — the farm-cell pickle's geometry is the 54,000 m² grid cell, identical for all 471, so "area weighting" cannot come from it. Recomputing from the actual coffee polygons intersected with labelled cells reproduces 68.0/81.8/74.7/90.4 **exactly**, so those numbers were right but unsourced; they are now registered.

The chase also found a real error: the Big Island has **6,031 acres** of mapped coffee, of which 3,795 fall in labelled cells. So **37.1% falls outside, not 32%**. Corrected. The coincidence dissolves (68.0% vs 62.9% capture).

## Also fixed

Ibragimov (1956) replaces the incorrect symmetry argument in Prop 1's sketch (log-concavity is the actual condition); "prove" softened to "show" and the unimodal hypothesis restored to the abstract; abstract intervals matched (baseline→2045 for both |C| and |F|, giving |C| **+2.2%** for Ka'u while its intersection falls 18.2%); asymmetry direction stated (1.23 means cooling costs Kona *more*); Ka'u footprint rounding unified to 8.4%; the "elevation deviation" naming discrepancy given a clause; the counterfactual-peak and settlement-history caveats added to Limitations; the deleted feature's panel removed from the flagship terrain figure; supplement Note S2's island-independence paragraph rewritten for the seven-feature screen.

Checker **94/94**. Body ~5,431 words.

## Still open

Lee et al. (2023) still carries three unverified quantities. Unchanged from round 21.
