# Analysis completion checklist — JavaScript_v2

**Status as of 2026-07-31: `JavaScript.tex` is DEAD, not merely frozen.** The live document is `DRAFT_2026-07-30.md`, written against `notebooks/`. Do not edit, compile, cite, or read the `.tex` for prose — it predates the rainfall correction, the matched statistic and the inversion condition, and its framing (per-district, "moves closer to optimum", 61x overestimate factors) has been retired. It remains readable for one purpose only: provenance of constants, e.g. line 310 documents where the +1.00/+1.35 C reference increments and the 2001-2014 GCM baseline came from. When the analysis closes, the `.tex` is rebuilt from the draft, not patched.

Simon's direction, 2026-07-30: the paper is not to be written until the analysis is complete and final. Four consecutive rounds rewrote the manuscript around a claim the next diagnostic then undercut. See memory `feedback_analysis_before_prose`.

## Current manuscript state — inconsistent, do not compile or submit

The `.tex` was left mid-edit when the freeze was called. It is not a coherent document right now:

- The Abstract, §4.3, §4.5, Discussion and Conclusions were rewritten around the **pooled union** framing.
- `check_numbers.py` still carries the **per-district** claim anchors. 13 claims no longer resolve; the pooled numbers are unregistered. **The checker does not pass** (81/94 agree, 13 not found, 0 mismatches).
- The Methods uncertainty subsection was *not* updated to describe the pooled/contrast bootstrap or the unpropagated trend uncertainty.
- Backups of the last coherent state: `JavaScript.tex.bak_prerebuild`, `JavaScript_supp.tex.bak_prerebuild`.

Nothing here is lost — every number is in `paper_numbers.json` and reproducible from `ML/09`--`ML/14`. The prose is the only thing in a broken state, and it is the thing that should not have been written yet.

## Open analysis items

Ordered by whether they can still move a headline.

### Can move a headline

1. ~~**Does the pooled decline survive the elevation-weight sweep?**~~ **CLOSED 2026-07-30.** `pooled()` in `ML/14` accepted a `wz` argument it never applied; fixed, and the sweep appended to the same script. The pooled 2045 decline runs -12.0% (`w_z`=0) to -37.5% (`w_z`=2) and its CI **excludes zero at every weight**, including `w_z = 0` where elevation is dropped from the screen entirely — so the shared-coordinate objection cannot account for the decline. The headline is safe in sign and significance; the **magnitude is not a measurement**. Quote it as a range across screen weightings, not as -22.1%. Registered as `pooled_decline_2045_wz*` in `paper_numbers.json`.
2. ~~**Propagate the trend uncertainty into the re-centred peak.**~~ **CLOSED 2026-07-30.** `ML/12` now draws the re-centring shift per replicate from N(+0.470, 0.097) — the SE is the belt trend's ±0.065 °C/decade over the 1.50 decades of extrapolation — instead of subtracting a constant. Kona's re-centred interval widens from (-1.42, -0.44) to **(-1.47, -0.38)**, still excluding zero; Ka'u moves (-0.65, +0.31) → (-0.71, +0.34), still including it. **No conclusion changes**, which is the point: the "past peak" claim was not resting on the omission. The unpropagated interval is still printed for comparison but the registered `Fpeak_*_recentred_ci_*` keys are now the propagated ones.
2b. **Test the mechanism behind the peak offset.** Kona's feasible mode sits 170 m *below* its farms (CI excludes zero) and its peak is at negative ΔT; Ka'u's mode is 150 m *above* (CI includes zero) and its peak is positive. Warming translates the thermal window upslope, so `sign(mode(s_r) - mean(farms_r))` should predict which side of its peak a region is on. Two districts cannot support a regression, but `ML/12` and `ML/13`/`ML/14` already produce paired bootstrap replicates of both quantities — the correlation across replicates is a real test. This is the item that would make the paper predictive rather than descriptive; everything else on this list only protects claims already made.

3. ~~**Decide what, if anything, can be said district-specifically.**~~ **CLOSED 2026-07-31.** The paper commits to the pooled union throughout and says plainly that Ka'u is unresolvable. `DRAFT_2026-07-30.md` §4.1 argues it structurally (62 cells, geographically disjoint, no spatial block contains both districts, so no honest cross-validation exists) rather than by appeal to interval narrowing.

3b. ~~**Bootstrap the headroom `h` and the ratio `dz/h`.**~~ **CLOSED 2026-08-05 — badly.** Block-bootstrapped in `notebooks/05_robustness.ipynb` §4 (400 replicates, same k-means block machinery as §§1-3, refits the screen AND the belt lapse-rate fit inside every replicate). Result: the 95% CI on `dz/h` **includes 1 for BOTH districts**, not only Ka'u as this item anticipated when it was opened.

```
            point   95% CI
h_kona      197.4   (95.3, 283.0)
h_kau       224.0   (113.5, 352.6)
dz/h_kona   1.19    (0.83, 2.47)
dz/h_kau    1.05    (0.67, 2.08)
```

Cause: `h` is measured from `S`'s upper elevation bound, and the §6 Limitations text already names that as the fringe where elevation-band cross-validation performs worst — the bootstrap now shows this concretely, because resampling farm cells shifts the screen's centroid/threshold enough to swing which high-elevation island cells count as inside `S` by a wide margin. Kona's point estimate (1.19) looked like it had real margin over Ka'u's (1.05); bootstrapped, it does not.

**Consequence for the manuscript.** §4.4 currently presents `dz > h` as "the transferable part... a reader in another system can evaluate `dz/h`." That claim is not supported at 95% confidence in the one system where it has been measured most carefully. It does not touch the matched-statistic result in §4.3 (`|C|` flat, `|F|` −22.1%), which is a direct measurement and does not depend on `dz/h` clearing any threshold — that result stands. But §4.4 as currently written overclaims, and so does the AGU abstract, which states "the threshold is already crossed" as fact. Both need revision: `dz/h` demoted from a confirmed condition to a candidate mechanism consistent with the point estimate, or dropped from any claim that requires statistical confidence. Written to `notebooks/data/headroom_bootstrap.json`.

3c. ~~**Reconcile the two baseline periods.**~~ **NOT AN ITEM — already closed in Round 22.** Raised 2026-07-31 and withdrawn the same round: the GCM historical window (2001-2014, midpoint 2008) and the observational climatology (1990-2021, midpoint 2006) are 2 years apart, which at +0.313 C/decade is **0.063 C** — negligible. Registered as `baseline_mismatch` = 2.0 with `clim_midpoint` / `hist_midpoint`. The draft now states the number in §2 rather than carrying it as a limitation. The gap that does matter is climatology-to-present (+0.486 C), which is a separate quantity and is handled in §4.2.

### Opened by the rainfall swap (2026-07-30, round 23)

R1. **Sweep the repo for "Kona wet / Ka'u dry".** The old `precip_annual` had the districts inverted (Kona 6,471 mm mean vs Ka'u 741; actually 1,321 vs 1,783). Every statement descending from it is wrong in direction, including the `ML/03` header comment "In Kona (wet, 6300 mm/yr) where rain is never limiting". Check both `.tex` files, all `ML/*.py`, and the README overview.

R2. ~~**Re-run `ML/03`.**~~ **CLOSED 2026-07-30 -- the finding is withdrawn, not corrected.** Re-run on the 250 m rainfall with `elev_dev_mean` (r = 1.000 with `elev_mean`) removed. Cross-validated R² is **negative in every case**: Kona Ridge -0.131 / RF -0.088, Ka'u Ridge -0.208 / RF -0.066. Both models predict NDVI worse than the regional mean.

Checked against the pre-swap backup to be sure this was not caused by the correction: the old data gives Kona -0.134 / -0.128 and Ka'u -0.132 / -0.053. **It was never predictive.** The published claim was permutation importance computed on models with no skill -- a ranking of noise. Withdrawn from the README; it never appeared in either `.tex` (zero NDVI mentions), so nothing in the manuscript depends on it.

Open question this raises: NDVI over established coffee is probably dominated by management (pruning cycle, shade, replanting age, harvest timing) rather than site, which would explain the total absence of environmental signal. If a canopy result is ever wanted, it needs a management covariate or it will keep returning noise.

R3. ~~**Seasonal precipitation is still stale.**~~ **CLOSED 2026-07-30.** 384 months of 250 m HCDP rainfall downloaded; `15_rainfall_seasonality.py` builds the climatology and `14_swap_rainfall.py` writes window-free replacements. The old `DRY_MONTHS = [6,7,8,9]` turned out to be Kona's four **wettest** months. `precip_dry/wet/dry_frac` are blanked; use `precip_driest_q`, `precip_wettest_q`, `precip_seasonality`, `precip_peak_sin/_cos/_month`.

R3d. **Phenology link tested and FAILED (2026-07-30).** `17_phenology_offset.py` derives rainfall onset per cell (Kona May, 87% of cells; Ka'u Oct) and predicts harvest at onset + 8 months: Kona Jan, Ka'u Jun, a -5 month offset. Documented harvest windows are **Kona Aug-Jan (peak Sep-Nov) and Ka'u late-summer to midwinter (peak Sep-Dec)** -- essentially simultaneous. Prediction contradicted; robust to the onset definition (a "first substantial rise" rule gives Mar/Jul, still a 4-month gap).

Cause, visible in the data beforehand: **neither district has a real dry season.** Driest months are 52 mm (Kona) and 55 mm (Ka'u). Rain-triggered synchronised flowering needs genuine water stress, which never occurs here; Kona's documented Feb-May "Kona snow" spans multiple flowerings and looks day-length/temperature driven.

Consequence for R3c: the warm/wet coupling remains real as a measurement but is **not demonstrated to be agronomically consequential**, and the most obvious pathway is now closed. Do not claim crop-calendar effects.

Still open, and more plausible since it needs no dry season: the **disease pathway**. Borer and leaf rust key off warm-AND-wet coincidence, which is exactly what differs (r = +0.90 Kona vs -0.46 Ka'u). Testable against the existing `ML/07` degree-day model.

R3c. **The warm/wet coupling is the strongest district contrast in the project.** `16_temp_rain_joint.py`: seasonal temperature range is identical (3.23 vs 3.24 C, both peaking Aug), but corr(monthly T, monthly rain) is **+0.90 in Kona and -0.46 in Ka'u**. Rain-weighted mean temperature sits **+0.31 C above** the annual mean in Kona and **-0.15 C below** it in Ka'u -- and per cell the separation is **complete** (100% of 409 Kona cells positive, 0% of 62 Ka'u cells, sd 0.07 / 0.03). Kona is warm-wet/cool-dry, Ka'u warm-dry/cool-wet: monsoonal vs Mediterranean on one volcano.

Unlike every other district contrast tried, this one does not need a bootstrap to survive -- there is no overlap to resolve. It should feed the CBB section (`ML/07`): borer and leaf-rust pressure key off warm-and-wet coincidence, which Kona has and Ka'u does not, so warming may raise pressure unevenly *for a mechanistic reason* rather than a statistical one. Also note for scale: +1.35 C to 2045 is **42% of the entire 3.2 C annual cycle**.

Caveats to carry: the gap is 0.46 C, modest in absolute terms; and it is computed from 32-year climatological means, so it describes the typical year, not ENSO-driven interannual swings.

R3b. **Use the phase columns, not the amplitude ones, wherever district difference matters.** Kona and Ka'u have near-identical rainfall amplitude (driest/wettest quarter 181/396 vs 214/455 mm, seasonality 30 vs 29) and **anti-phase timing** (r = -0.58; peak month 7.4 vs 12.2). Any feature set built only from amplitude will conclude the districts are identical in rainfall, which is true of the amount and false of the regime. This is the strongest genuine environmental contrast found in the whole project -- it should probably lead the terroir section rather than sit in a feature list.

R4. **Re-check ML/01, ML/02, ML/04 conclusions.** All four notebooks used `precip_annual` in their feature sets. Note that district *classification* from environment is circular regardless of resolution -- the districts are geographically disjoint, so no spatially honest holdout exists -- so these should be reported as magnitudes, not accuracies.

### Must be closed before writing

4. ~~**Verify Lee et al. (2023).**~~ **CLOSED 2026-07-30** via PMC10143774 (open access). All four figures are real and correctly transcribed; the problem is **attribution**, and two need requalifying.

| claim | Lee et al. text | action |
|---|---|---|
| $113 M green / $161 M roasted | "...in 2022 [1]" | cite **USDA NASS, Coffee 2022** (Lee's ref 1), not Lee |
| ~7,100 bearing acres | "For the 2021-2022 growing season, bearing acreage totaled 7100 acres [1]" | same NASS source |
| $25.7 M | "For the **2011/12 and 2012/13 seasons**... USD 25.7 M in **lost sales**" [16] | cite **Leung, Kawabata & Nakamoto 2014** |
| 20% yield decline | 1198 lbs/acre pre-CBB vs 963 post (20% reduction) | **Lee et al.'s own result** -- keep the citation |

Two substantive fixes, not just bibliographic:

- **$25.7 M is "lost sales", not total loss.** Lee lists crop loss separately at $12.7 M. Calling it an economic loss overstates by ~2x. It also covers two crop years in **2011-13**, pre-dating the IPM programs that are the paper's actual subject -- Lee reports **$251 M in cumulative management benefits 2011-2021**. Quoting the pre-IPM loss as current cites the problem while ignoring that paper's finding that it was largely addressed.
- **The 20% needs its window**: first five years after CBB arrival vs the five years before, not a standing penalty.

Primary sources to add to `references.bib`: USDA NASS *Coffee 2022*; Leung P.S., Kawabata A.M., Nakamoto S.T. (2014) *Estimated Economywide Impact of CBB for the Crop Years 2011/12 and 2012/13*, brief report to the Hawaii congressional delegation.
5. **Re-run the Kaua'i out-of-sample test on the seven-feature screen.** `data_wrangling/12_kauai_validation.py` was written against the eight-feature version. Supplementary Note S2's wording was updated but the test itself was not re-run, so the "does not change the outcome" claim is currently unsourced.
6. **Table S1 / Fig S1 / Table S2 provenance.** Regenerated on the corrected screen by `ML/10`, but confirm nothing in the supplement still quotes an eight-feature number.

### Optional, only if the relevant claim is reinstated

7. **C4b shape-matched null** — dropped from the manuscript rather than re-run on the corrected screen. Needs regenerating only if the multiplier is ever promoted back.
8. **Free-breakpoint fit is diffuse** (660-1330 m, median 860). Either accept it as diffuse in the write-up or find a better-powered formulation; do not re-assert a sharp 950 m boundary.

## Analysis assets that ARE final

These are computed, bootstrapped, swept and registered — they should not need redoing:

- Corrected seven-feature screen and every screen-dependent quantity (`ML/10`, validated by `--published` reproducing the eight-feature values exactly).
- Baseline epoch and observed trend: +0.313 ± 0.065 °C/decade over the belt, +0.470 °C from climatological mean to end of record (`ML/11`).
- Peak argmax with block-bootstrap intervals, both raw and re-centred (`ML/12`).
- s(z) unimodality check and free-breakpoint regression (`ML/13`).
- District contrasts, pooled union, and mode-offset geometry (`ML/14`).
- 320-setting parameter factorial and the continuous elevation-weight sweep (`ML/09`).
- Area-weighted declines recomputed from the actual coffee polygons; Big Island capture rate 62.9%, so 37.1% of acreage falls outside labelled cells (not the 32% the old draft claimed).

## Run order if regenerating from scratch

notebook → `ML/06` → `07` → `08` → `09` → `10` → `11` → `12` → `13` → `14`

Then `python check_numbers.py --strict` — which will fail until the prose is rewritten to match, and that is expected while frozen.
