# JavaScript_v2

# Adaptation Space Peaks at Present Climate — working copy

> **`JavaScript.tex` IS DEAD — 2026-08-02.** The live document is **`DRAFT_2026-07-30.md`**, written against `notebooks/`. Do not compile, cite, submit, or edit the `.tex` for prose: it predates the rainfall correction, the matched statistic and the inversion condition, and its framing (per-district, "moves closer to optimum", 61x overestimate factors) has been retired. `check_numbers.py` reads only the `.tex` and does not pass (13 claims unresolvable) — that is expected and no longer worth fixing. The `.tex` stays readable for exactly one purpose: **provenance of constants**, e.g. line 310 documents where the +1.00/+1.35 C reference increments and the 2001-2014 GCM baseline came from. When the analysis closes, rebuild the `.tex` from the draft rather than patching it. Analysis remains gated on `ANALYSIS_TODO.md`; see memory `feedback_analysis_before_prose`.

Fork of `../JavaScript/` (the as-submitted-to-Scientific-Reports version — do not edit that copy). `data/` is symlinked back; everything else is a real copy.

## Round 25 (2026-08-05) — AGU abstract rebuilt; the inversion condition failed a bootstrap; reframed as live science

Deadline-day session, driven by Simon rather than new pipeline work. Only one notebook changed.

**The submitted AGU abstract was doubly stale.** Built 2026-07-29, it still carried pre-Round-21 contraction figures (-15.5%/-12.4%) and the retired "peak/approaching optimum" framing — it had gone stale before ever being submitted. Rebuilt from `DRAFT_2026-07-30.md` and `notebooks/data/matched.json` to match Round 24's actual state (matched statistic, `|C|` flat, `|F|` -22.1%, the `dz/h` inversion condition).

**Bootstrapped `ANALYSIS_TODO.md` item 3b (headroom `h` and `dz/h`) — and the inversion condition did not hold up.** Added a 4th section to `notebooks/05_robustness.ipynb`, reusing the existing block-bootstrap machinery (same `blocks`/`boot_idx`/`ci` as §§1-3, refits the screen AND the belt lapse-rate fit per replicate, 400 reps). Result: the 95% CI on `dz/h` includes 1 for **both** districts — Kona 1.19 (0.83, 2.47), Ka'u 1.05 (0.67, 2.08) — not just Ka'u, which is all the item anticipated when it was opened. Cause: `h` is measured at the screen's upper fringe, which §6 Limitations already names as the worst-cross-validating edge; the bootstrap shows that's enough noise to swallow even Kona's apparent margin. Written to `notebooks/data/headroom_bootstrap.json`.

**Consequence, not yet applied to the manuscript body.** `DRAFT_2026-07-30.md` §4.4 still states `dz/h > 1` as an established, transferable condition. That needs the same demotion the abstract got (below) — not done this round, lower priority than the deadline. Do not assert `dz/h > 1` as fact anywhere until this closes, ideally with a tighter estimator for `zmax` (currently a 97.5th-percentile cutoff, sensitive to which farm cells a given bootstrap replicate resamples).

**Simon's framing call: present this to AGU as live science, not a closed result.** Rather than cut the headroom mechanism or bury it as a hedge, the abstract leads with the proven half (the matched statistic) and explicitly frames the headroom/`dz/h` mechanism as the open question the poster is built around, naming the concrete next step (tighten the upper-boundary estimator). AGU Fall Meeting is Dec 2026 — months of runway to either firm the number up before the talk or present it exactly as it stands.

**Also corrected: the abstract's opening claim overstated the field's novelty gap.** "Climate suitability projections typically map a climatic envelope onto a landscape" ignored that GAEZ and the broader crop-suitability literature have screened by land availability for decades — a point the paper's own retired `JavaScript.tex` already made explicitly (line 87), which also names the real, narrower novelty: (1) a screen anchored to a *specific* designation-of-origin configuration rather than a generic arability mask, and (2) evaluating the intersection as a function of the warming amount rather than once at a fixed horizon. `DRAFT_2026-07-30.md` §1 carries the same flattened claim and needs the identical fix — not done this round.

**Final abstract state:** `agu2026_abstract.md`, 1,889 characters excluding spaces (2,000 limit), title 79 characters (300 limit). Submitted to GC002 on the 2026-08-05 deadline.

**Open for next session:** Simon has three GIF ideas for the poster/talk, not yet described in any file — ask him what they are before building anything; nothing about their content is captured here.

---

## Round 26 (2026-08-05) — the three poster GIFs, built and debugged

The three ideas: temperature change across the island, the coffee thermal envelope's leading/trailing edge migrating upslope, and the same envelope with the terrain screen applied. Built as `notebooks/make_gifs.py`, reusing `pipeline.py`'s existing functions end to end — no new statistics, no new dependencies. Outputs in `notebooks/figures/{temperature,envelope_upslope,envelope_screened}.gif`. Code now also lives as `notebooks/06_gifs.ipynb`, matching the numbered-notebook convention (`make_gifs.py` kept alongside for quick regeneration without Jupyter).

**Settled on a plain one-way sweep after two rejected attempts.** First version ping-ponged 0↔1.6°C in a loop with pauses held at the 2035/2045 reference increments — Simon called the reverse pass "jittery and confusing" ("looks like it's breathing"). Final: a straight sweep from 0 to the 2045 increment (1.35 C), hard-cut restart, no pause, no reverse. Titles show only the set notation and the ΔT value — an earlier version also named which scenario the sweep was passing through; Simon asked for that dropped too.

**Two real bugs, both caught by Simon's review, both fixed:**
1. The envelope GIF originally painted Kona and Ka'u as two separate overwrite-ordered colors. Their thermal envelopes are "effectively the same niche" (Round 22), so the bands nearly coincide, and the later-drawn district ate the earlier one except at the edges — which showed up as Kona-red slivers on *both* sides of the Ka'u-blue ring, unrelated to actual Kona geography. Fixed by pooling into a single band, matching the "districts indistinguishable, pooled union is the unit" convention `pooled_union()` already uses everywhere else.
2. The screened GIF's gray "farmable, not feasible" swatch silently included land that isn't farmable at all (steep slope / historic lava) — the base array was `isl['X']` (all land), not `isl['farmable']`. Fixed with a 4th color for the true not-farmable category. **This exact bug is also present in `04_feasible_set.ipynb`'s `figures/04_inversion.png`** (same plotting pattern, copied from there) — not fixed in the notebook itself, flagged in `notebooks/README.md`.

---

## Round 24 (2026-07-31 to 2026-08-02) — the headline was an unmatched comparison; fixed, and it got stronger

Simon's review of `DRAFT_2026-07-30.md` found the central result was **comparing two different statistics**. The draft paired "69.8% of farmable island land moves closer to the thermal optimum" — a directional gradient measure over all land — against "the feasible set contracts 26.4%", a set-cardinality change over the footprint. A cell can move closer to the optimum and still sit outside `C`, so that pairing could not establish that the terrain screen caused the sign flip. `|C|` might have been contracting on its own.

**It is not.** Notebook 04 now computes the matched form — the same statistic with the screen off and on — and the thermal set is flat:

```
unit      dT       |C|     dC%       |F|     dF%
kona    +1.35     9,365    -0.3     1,215   -26.4
kau     +1.35     7,174    +2.2     1,502   -18.2
pooled  +1.35     9,365    -0.3     2,717   -22.1
```

Across a displacement that removes a fifth of the feasible set, `|C|` moves -0.3% pooled and **+2.2% for Ka'u**. The entire contraction is attributable to `S`. This is narrower and much more defensible than the old pairing, and it isolates the screen as the cause rather than asserting it.

**The 61x / 38x "overestimate factors" are retired as mostly mechanical.** `S` covers 15.2% of farmable land, so 69.8/1.1 is close to the reciprocal of that share and would have come out near 50-60x regardless of whether the analysis was right about anything.

**The inversion condition is now stated, which is the transferable contribution.** `|C|` and `|F|` change by the same accounting — recruits at the window's cool leading edge minus losses at the warm trailing edge — and disagree in sign once the window's displacement along the migration axis exceeds `S`'s headroom above that leading edge. With `Gamma` = 5.73 C/km, +1.35 C displaces the window **236 m** upslope against **197 m** (Kona) and **224 m** (Ka'u) of headroom: `dz/h` = **1.19** and **1.05**. The share of `S` above the leading edge collapses 17.6% -> 1.0% (Kona) and 23.4% -> 2.1% (Ka'u), while farmable land keeps supplying cells there (260 enter vs 303 leave for Kona at +1.35, against 16 vs 56 inside `S`). A reader in another system can evaluate `dz/h` from a lapse rate, a displacement and their own footprint's upper bound. Written to `notebooks/data/matched.json`.

**The peak claim was a tautology and is reframed around boundedness.** `C` is fit on 471 farm-cell temperatures and `S` is a shell around the same 471 cells' feature centroids, so an intersection peaking near `dT = 0` follows from the construction — "you defined the optimum as where the crop is, then found the crop is at its optimum" is a fatal one-line referee comment. The draft now concedes this explicitly and reports what is empirical instead: `S` is **bounded, closely, in the direction the window migrates**. The same construction with an `S` extending further upslope gives a plateau; it is the 197-224 m ceiling against a 236 m displacement that produces a descending limb. Corroborating and unexpected: **`|C|` alone peaks at -1.15 C (Kona) and -1.75 C (Ka'u)**, nowhere near zero, so the intersection's peak position is demonstrably not inherited from the climatic set.

**Warming increments were mis-described twice.** +1.00/+1.35 C are **round reference increments carrying no ensemble interpretation** (`JavaScript.tex:310`), not projections — the NEX-GDDP ensemble deltas are +0.60/+0.92 C (SSP2-4.5) and +1.41/+1.78 (SSP5-8.5). And `dT = 0` is the 1990-2021 climatological mean (midpoint 2006), not the present, so +1.35 C is about **+0.86 C of further warming from the end of record**. The GCM-vs-observational baseline periods differ but their midpoints are only 2 years apart (0.063 C, `baseline_mismatch` in the registry) — raised as a limitation during this round and **withdrawn**, since Round 22 had already quantified it as negligible.

**Weakened claims that were overstated.** The `w_z = 0` test removes elevation's *label*, not its *information* — slope, relief, distance to coast and soil all covary hard with elevation on a shield volcano — so it **constrains** the shared-coordinate objection without settling it. The 0.058 C rain-weighted-temperature gap between districts is no longer called "disjoint": two spatially disjoint regions separate on almost any smoothly varying derived field, which is the same fact that denies an honest cross-validation. And §4.1 no longer offers "pooling narrows Ka'u's interval from one that includes zero to one that excludes it" as evidence that pooling is principled — it reads as the opposite; the structural argument (62 cells, disjoint districts, no spatial block contains both) stands alone.

**Journal handling resolved.** Two obligations, executed as two acts: the published paper's rainfall-dependent claims need correcting or retracting **on their own terms**, and this analysis is a **new submission**. Routing a changed model, sample, headline and thesis through the correction mechanism presents a replacement as a fix.

Notebook 04 gained four cells (matched statistic, edge accounting, headroom) and was re-executed end to end; all pre-existing asserts against `paper_numbers.json` still pass. New values go to `notebooks/data/matched.json`, **not** the registry, because `ML/10` regenerates `paper_numbers.json` and would wipe them.

Open after this round: bootstrap `h` and `dz/h` (both point estimates; `h` is measured on the upper fringe where the screen validates worst, and Ka'u's 1.05 is close enough to unity to need an interval) — `ANALYSIS_TODO.md` item 3b.

## Round 23 (2026-07-30) — the precipitation column was inverted; 250 m rainfall swapped in

**`precip_annual` had Kona and Ka'u backwards.** The old ~4 km product put Kona at a 6,471 mm/yr mean and Ka'u at 741 -- Kona nine times wetter, with zero overlap between districts. Sampling the actual Rainfall Atlas of Hawai'i (Giambelluca et al. 2013, 250 m, 1978-2007) gives Kona 1,321 and Ka'u 1,783: **Ka'u is the wetter district**, the ranges overlap by 475 mm, and Cohen's d is +2.11 rather than a large negative. Every "Kona wet / Ka'u dry" statement in this repo descends from the broken column.

Resolution improved as much as accuracy: 246 distinct values across 258 Kona cells and 55 across 59 Ka'u, against 8 and 4 before. At the old granularity precipitation acted as a *region label* rather than a measurement, so any model separating the districts with it was circular. That defect is gone.

`data_wrangling/13_rainfall_atlas.py` samples the raster (99.5% coverage, 10,165 of 10,211 cells) and `14_swap_rainfall.py` writes it into `df.pkl` and `plot_climate_features.pkl`, recomputing the four scenario pickles from their original ratios. Both are resumable and back up to `*.bak_precip4km`.

Source note: the atlas's own host (`atlas.uhtapis.org`) returns 403 to scripted requests, so the raster comes from the State of Hawai'i GIS `Climate_Raster` service, which documents it as the Giambelluca product reprojected to EPSG:3750. Validated against three reference points -- Mauna Kea summit 212 mm (the atlas's own documented statewide minimum is 204 mm), Hilo 3,644 mm, leeward Waikoloa 618 mm.

**The seasonal columns were wrong too, and fixing them produced the day's real finding.** `05_climate.ipynb` hard-codes `DRY_MONTHS = [6,7,8,9]` ("Kona leeward dry season") and applies it to both districts. Measured against 384 months of 250 m HCDP rainfall (`09_...--datatype rainfall`, `15_rainfall_seasonality.py`), those are Kona's four **wettest** months -- 125 mm/mo against 77 for the rest -- and Ka'u's driest are Apr-Jul.

The reason no single window works: **the two districts have anti-phase rainfall seasonality**, monthly cycles correlated at **r = -0.58**. Kona peaks in September and bottoms in February (sea-breeze convection on the leeward slope); Ka'u peaks in March and bottoms in June. Amplitude is near-identical (driest/wettest quarter 181/396 mm Kona vs 214/455 Ka'u, seasonality 30 vs 29) -- **the entire district difference is timing, not amount.** Circular-mean peak month: Kona 7.4, Ka'u 12.2.

That is agronomically meaningful for coffee, where flowering, cherry fill and harvest key off when rain arrives rather than how much falls, and it is the one environmental axis on which these districts genuinely and measurably differ. The project never saw it because it applied one inverted window to both.

`14_swap_rainfall.py` now blanks the three windowed columns and writes window-free replacements: `precip_driest_q`, `precip_wettest_q`, `precip_seasonality` (BIO16/17/15-style) plus `precip_peak_sin/_cos/_month` carrying phase. Amplitude descriptors alone do **not** separate the districts; the phase columns are the ones that do.

**Independent cross-check of the annual correction.** HCDP monthly sums (1990-2021) give Kona 1,116 / Ka'u 1,402 mm, ratio 1.26; the Rainfall Atlas (1978-2007) gives 1,321 / 1,783, ratio 1.35. Two products over different decades agree Ka'u is wetter by ~30%. The old column's ratio was 0.11.

**Consequence.** `ML/03`'s finding -- that Ka'u's NDVI model weights moisture proxies while Kona's weights elevation and aspect, read as a dry-vs-wet contrast -- was fit on the inverted column and means nothing until re-run.

Separately, `cup_scores/` records a negative result: Hawaii Coffee Association competition scores (284 lots, 91 farms, 5 years) show **no district difference once variety and processing are controlled** (+0.02 points, CI -0.46 to +0.57), and score reliability caps any site model at 26% of variance. See `cup_scores/FINDINGS.md`.

## Round 22 (2026-07-30) — v3 review: baseline epoch, peak intervals, and a diffuse breakpoint

The v3 review moved the verdict to minor-to-moderate revision and raised a new blocker: **"present climate" is not present.** Confirmed and quantified. The temperature field is the mean of 384 monthly rasters spanning 1990-2021 (midpoint 2006), and the NEX-GDDP deltas are differenced against a CMIP6 historical window of 2001-2014 (midpoint 2008). Those two baselines are only 2 years apart -- 0.063 °C, negligible -- so the feared internal mismatch dissolves. But the gap to the present does not: regressing the product's own island-mean temperature on year gives **+0.313 ± 0.065 °C/decade over the belt**, putting the end of the observational record 0.470 °C above the climatological mean (`ML/11_baseline_epoch.py`).

**Ka'u's headline claim inverted, as the review predicted.** The peak now carries a block-bootstrap interval (`ML/12_peak_bootstrap.py`, 2,000 replicates, whole screen refitted): Kona -0.66 °C (CI -0.95, +0.03) and Ka'u +0.18 °C (-0.18, +0.78) against the climatological mean; re-centred on the end of record, Kona -1.13 °C (CI excludes zero) and Ka'u -0.29 °C (does not). The claim is now "neither district is still approaching its optimum -- one measurably past it, one sitting on it," which survives re-centring and is more defensible than the old point-estimate pair.

**Proposition 1's premise fails for Ka'u.** `s(z)` was never checked; it is now (`ML/13_density_and_breakpoint.py`). Kona's feasible density is single-peaked (mode 325 m); Ka'u's is a 300-800 m plateau with three interior turning points. Ka'u's |F| is still single-peaked empirically because its level set is wider than the spacing of those maxima, and the paper now says so instead of assuming the hypothesis. The modes also explain the offsets' signs: Kona's feasible ground sits 170 m *below* its farms, Ka'u's 200 m *above*.

**The 950 m breakpoint is not identified.** A free-breakpoint segmented regression puts the transition at 660-1,330 m depending on descriptor (median 860 m) with wide intervals. The terrain above the footprint still differs sharply in kind -- that result stands -- but the "937 m by an independent route" claim is **dropped**: it used the same features, standardisation, centroid and threshold, and a free fit on that same profile lands at 630 m.

**Elevation weight added as a fifth sensitivity factor** (Supplementary Fig. S2, Table S4). Contraction runs -5.0% to -20.0% (Kona) across `w_z` in [0, 2], wider than the entire 320-setting factorial; the peak moves only -0.85 to -0.29 °C and never changes sign. A duplicated column is worth `w_z = sqrt(2)`, and the sweep reproduces the superseded eight-feature contraction there -- the v2 defect is now a point on a curve.

**An error found by chasing a coincidence.** The review flagged Kona's 68.0% area-weighted decline against the 68% acreage-capture rate. The area-weighted figures turned out to have no pipeline source (the farm-cell pickle's geometry is the uniform 54,000 m² grid cell, so area weighting cannot come from it). Recomputing from the actual coffee polygons reproduces 68.0/81.8/74.7/90.4 exactly -- and shows the Big Island has 6,031 mapped coffee acres of which 3,795 are captured, so **37.1% falls outside a labelled cell, not 32%**. Corrected.

Also: Ibragimov (1956) replaces an incorrect symmetry argument in Prop 1's sketch; abstract intervals matched (baseline->2045 for both sets, giving |C| **+2.2%** for Ka'u while its intersection falls 18.2%); asymmetry direction stated; rounding unified to 8.4%; the deleted feature's panel removed from the terrain figure. Figures renumbered to document order (Fig3 is now the density panel). `check_numbers.py --strict` at **94/94**. Body ~5,431 words.

Run order if regenerating: notebook, then `ML/06`, `07`, `08`, `09`, `10`, `11`, `12`, `13`.

## Round 21 (2026-07-30) — diagnostics, a screen defect, and a full rebuild

Three external reviews (`suggestions_claude.md`, `suggestions_gemini.md`, `suggestions_pete.md`) converged on one blocking question: is the reported contraction of `F = C ∩ S` guaranteed by construction, given that both sets are anchored to the same 471 farm cells? Four diagnostics were run before any prose was touched (`ML/09_geometry_diagnostics.py`, full writeup in `diagnostics_findings.md`).

**The blocker's answer was partly bad news.** Sweeping ΔT from −3 to +3 °C shows |F| is single-peaked and near-symmetric, peaking at −0.65 °C (Kona) and +0.15 °C (Ka'u). Cooling contracts the intersection about as much as warming does, so "the intersection contracts under warming" was never a claim about warming. The paper was rebuilt around what the sweep actually shows: **adaptation space has a maximum, it is at present climate, and no pathway increases it.** Kona has already passed its own peak.

**A defect nobody had flagged.** `elev_dev_mean = elev_mean − 489.8642` exactly — a scalar offset, r = 1.000 with mean elevation, identical to it after standardisation. The eight-feature screen therefore weighted elevation **double**, on precisely the axis the thermal band migrates along. `ML/10_screen_corrected.py` drops the duplicate and recomputes every screen-dependent quantity; run `--published` it restores the 8-feature set and reproduces every published value, which is what proves nothing but the feature set changed.

Correcting it moved the headline contraction from −15.5%/−12.4% to **−9.9%/−9.5%**, and *improved* the screen: elevation-band cross-validation in the top quintile went from 64.2% to 90.5%, and fitting on the lower 60% of the belt to predict the upper 40% went from 63% to 75%. Double-weighting the migration axis had made the screen brittle exactly where it must extrapolate.

**The best new evidence.** The claim that terrain "departs from the observed farm envelope" above the footprint's upper boundary was load-bearing and merely asserted. It is now shown: five of six non-elevation descriptors change slope by 2.7- to 5.5-fold above 950 m and aspect cosine reverses sign, while mean distance to the Kona centroid crosses the screen's own threshold at **937 m** by an independent route. `S` is stationary ground, demonstrated rather than assumed.

**What the rebuilt paper says.** Relative to present climate the feasible set falls 18.3% (Kona) and 9.6% (Ka'u) by 2035, and 26.4% and 18.2% by 2045, while the island-wide thermal set moves −0.6% and +0.6% and the terrain set not at all. The intersection contracts in 313 of 320 parameter settings. A new theory section states the single-peak result as a proposition with three sufficient conditions, which is what Pete's review asked for and what makes the case study an illustration rather than the whole contribution.

**Structure changed.** Body text 5,787 → ~4,476 words (−23%) *while adding* a theory section (§2) and a consolidated robustness section (§4.5). Deleted: "Why We Report the Multiplier Only as a Sign" (compressed to one paragraph), the suitability-rate decomposition (its first term was mislabelled), the C4b shape-matched null, and the scattered hedging the reviews all flagged as self-undermining. New Table S3 reports the full 320-setting factorial.

**Figures.** Fig2 (identity map) and Fig4 (feasible set) regenerated on the corrected screen; FigS1 (threshold sensitivity) likewise. Fig5 (terrain break) and Fig6 (ΔT sweep) are new. Fig1 and Fig3A/B are unchanged, being screen-independent. Previous versions preserved as `*.jpg.bak_prerebuild`.

`python check_numbers.py --strict` is at **77/77**. Run order if regenerating: notebook, then `ML/06`, `07`, `08`, `09`, `10`.

**Still open:** the journal re-disclosure decision, and one review item not closed — Lee et al. (2023) is cited for three separate quantities (crop value, $25.7 M CBB loss, 20% yield decline) and none has been verified against the paper; the crop value normally traces to NASS.

## Earlier rounds

# Terrain-Thermal Convergence Framework (TTCF) — bug-fix fork

This is a fork of `../JavaScript/` (the as-submitted-to-Scientific-Reports version — do not edit that copy further). `data/` is symlinked back to the original; everything else is a real copy.

**Why this fork exists:** a critical review (`../JavaScript/suggestions_claude.md`) found that the island-wide temperature model (`ML/05_forward_projection.ipynb`) was fitting a linear regression on 385 pooled Kona+Ka'u farm cells that has **R²=0.011 — statistical noise**, not the R²=0.73 claimed in the submitted manuscript. That noise fit produced a physically impossible result (Ka'u showing 100% of the island gaining thermal suitability, 0% losing) reported as a real finding.

**Fixed 2026-07-26:** replaced the fitted regression with a literature-verified fixed lapse rate (−6.5°C/km, 24.0°C sea-level reference — verified against primary sources, see `references.bib`), re-ran the notebook, and rewrote every downstream number in `JavaScript.tex` and `JavaScript_supp.tex` that depended on it. The headline overestimation factor changed from 19.4× to 86.9×–119.5× — not a refinement, a different number, because the old one was an arithmetic artifact of the bug.

**Round 20 (2026-07-29) — reframe, 30% cut, and closing the last review items.** The paper's claim is no longer about coffee. It is now the general configuration `F(dT) = C(dT) INTERSECT S` — a migrating suitability set against a stationary feasibility set — with Hawaiian coffee as the demonstration, retitled "Moving Windows on Fixed Ground". Body text cut 8,193 -> 5,787 words (-29%) by moving Uncertainty Quantification and the out-of-sample tests into Supplementary Notes S1/S2, compressing eight Methods paragraphs, merging repetitive Results subsections, and deleting the "Figure Legends" section (a verbatim duplicate of the inline captions).

Three quantities the paper quoted turned out to have no source in the pipeline — they came from scratch scripts that no longer existed. All three are now reproducible and registered in `check_numbers.py`:

- `ML/06_block_bootstrap.py` — spatial block bootstrap for the farm-decline CIs and the multiplier CIs. It refits the standardiser, both centroids and the 95th-percentile cutoff inside every replicate, which answers a reviewer question about whether the intervals inherit the point-estimate threshold. Regenerated CIs shifted slightly (Kona 2035 66.0-77.9 -> 65.8-78.0) and the paper now quotes the regenerated values.
- `ML/07_cbb_degree_days.py` — coffee berry borer under warming, rebuilt on Hamilton et al. 2019's own degree-day parameters (332 DD/generation above 14.9 C, both verified against the published paper) applied to temperature directly instead of to their generations-vs-elevation regression. This removes the extrapolation past their 778 m sampling limit and **halves the numbers**: +18%/+23% at 600/800 m by 2035, not +34%/+51%. The model first reproduces their observed field rates as a check (assert-based).
- Notebook cells **E10** (C4b shape-matched null) and **E11** (elevation-histogram-stratified null). E11 replaces a quoted-but-unsourced result and comes out tighter than what the paper claimed: the null median reproduces the observed multiplier to two parts in a thousand (6.87x vs 6.88x), not "about one percent".

**C4b result:** matching each district's area *and* elongation (Kona 3.8:1, Ka'u 1.7:1) with random placement and bearing puts the observed multiplier at the *low* edge of the null — 95% (Kona) and 100% (Ka'u) of random patches score worse. Neither size, shape, nor placement explains the multiplier; the elevation histogram does.

`ML/08_table_s1.py` now generates Supplementary Table S1 rather than it being hand-maintained. Filling in the previously-empty Kona Mahalanobis column changed dependent numbers: the Ka'u factor span is 3.2x-20.7x (was 3.2x-27.7x), and the Mahalanobis declining fractions are 57.7%/50.3% (was 62.4%/50.2%). The script reproduces the Euclidean fractions exactly, which is what validates it. Metric sensitivity is now shown to be specific to Ka'u — Kona's factor moves only 6.3x-8.9x across both metrics and all four thresholds.

**E8 now merges into `paper_numbers.json` instead of overwriting it,** because rerunning the notebook silently dropped every key added by `ML/06`, `ML/07` and `ML/08`. Run order if regenerating from scratch: notebook, then 06, 07, 08. `python check_numbers.py --strict` is at **54/54**.

Also fixed: `\approx` outside math mode (would have failed to compile), the footprint complement printed as 85.1% when 85.152 rounds to 85.2, and two supplement cross-references pointing at main-text labels that cannot resolve in a separate document.

**Still open:** the journal re-disclosure decision. The paper has changed its model, sample, headline number (twice) and now its thesis since the correction letter sent 2026-07-26, which arguably makes it a new submission rather than a correction.

**Round 2 (2026-07-27), per a fresh review pass (`suggestions_claude.md`):** the 2026-07-26 fix left μ/σ for each district's thermal envelope fit on ERA5-Land temperatures, while suitability was evaluated against the new lapse-rate surface — two different, unreconciled temperature scales for the same cells (confirmed directly in `ML/05_forward_projection.ipynb`). Fixed by refitting μ/σ on the lapse-rate surface itself (each region's farm-cell elevations run through the same lapse model used everywhere else), which also resolves the R²≈0.01 ERA5-Land-noise problem for the niche definition, not just the gradient — no need to acquire the 250m Giambelluca atlas for this. Added an `assert`-based sanity check in the notebook (envelope peaks at its own reference temperature) and reran the full pipeline.

**This changed the paper's headline finding.** The two districts' thermal optima converge to within 0.15°C of each other (µ_Kona=20.50°C, µ_Ka'u=20.65°C), so the old "Kona is thermally constrained / Ka'u is spatially constrained" asymmetry doesn't survive — both districts now show a symmetric result: ~70% of farmable island land appears to gain thermal suitability under either envelope (climate-only, no terrain screen), but restricted to each district's own terrain footprint, roughly two-thirds of both Kona's and Ka'u's actual coffee country is on a **declining** thermal trajectory, with the residual gaining fraction reduced to 1.5–1.7% of farmable island land — a 41×–53× overestimation common to both districts (was one-sided 86.9×–119.5× for Ka'u only, "zero" for Kona). Simon confirmed via AskUserQuestion this is the right call (real finding, not an artifact) and to rewrite the manuscript around it rather than hold for further investigation. Abstract, Results, Discussion, Conclusions, Methods, and both Figure 3/4 caption copies (inline + the separate "Figure Legends" section, which had desynced before) were rewritten to match.

**Also fixed this round** (six bookkeeping items named explicitly in scope, from §6 of the review): Fig. 1 caption said farm polygons were green, verified by pixel sampling they're orange; the "674 polygons constitute the entire U.S. specialty coffee industry" claim (false — Kauai Coffee alone is ~3,100 acres not in this dataset) softened to a dataset-scope claim; the manuscript's "n=385" was traced to the wrong pipeline stage (385 = cells with successful climate extraction; the actual analysis dataset, used throughout every ML notebook, is 317 = 258 Kona + 59 Ka'u after full feature-completeness filtering) and both `.tex` files corrected; "25-feature matrix" corrected to the actual 8-feature topographic screen; Acknowledgements/Data Availability wrongly attributed the Hawaii Agricultural Land Use Baseline to USGS (it's UH Hilo SDAV Lab / Hawaii Dept. of Agriculture, added a proper citation `PerroyCollier2021` to `references.bib`) and said "1m DEM" when Methods itself says 1/3 arc-second (~10m); "terrain rarely constrains agricultural access" reworded so it no longer contradicts the paper's own thesis. Supplementary Table S2 and the Fig. S1 caption's "not a tuning artefact" overclaim updated to match new numbers (a ~1.7–3.3× factor swing across the "stable" threshold plateau, honestly reported rather than waved away).

**Still open (deferred, not fixed here, same as before):** GAEZ/terroir-zoning literature review, physiological-optimum vs. observed-conditions test, SSURGO folded into the screen itself, the 250m Giambelluca atlas swap (not needed for this round's fix, but still the long-run right answer), cross-island validation, "manifold" language pass, ROC-AUC interpretation, SSP2-4.5/SSP5-8.5 scenario-range reporting, Champagne/Colombia citation re-verification.

**Figures regenerated 2026-07-27:** `Fig3A/B.jpg`, `Fig4.jpg`, `FigS1.jpg` (+ matching `.png`/`.tiff`) re-exported directly from the corrected rerun (`img/05_kona_thermal_forward.png`→Fig3A, `img/05_kau_thermal_forward.png`→Fig3B, `img/06_topo_thermal_convergence.png`→Fig4, `img/S1_threshold_sensitivity.png`→FigS1; RGBA→RGB via Pillow, no crop needed).

**Status (2026-07-27):** numeric refit + full consistency pass + figure re-export complete in both `.tex` files. Ready to compile on Overleaf. Still holding on resubmission until Scientific Reports replies on how they want the correction submitted (`../JavaScript/editor_correction_letter.md`, sent 2026-07-26).

Edasi et al. (2026) – Terrain-Constrained Suitability in Specialty Agriculture

Part of the GeoGastronomy research program.
---

## Overview

JavaScript characterizes the environmental fingerprint of two historically distinct Hawaiian coffee regions — Kona and Kaʻu — using terrain, climate, satellite vegetation, and soil at 500m resolution. The pipeline identifies what makes each region distinct, where similar conditions exist elsewhere on the island, and how projected warming reshapes thermal suitability boundaries.

---

## Study Area

- **Location:** Big Island of Hawaiʻi — Kona and Kaʻu districts
- **Scale:** 471 labeled farm cells (409 Kona + 62 Ka'u) on a 500m grid
- **Farm coverage:** 674 coffee-farm polygons from the 2020 Hawaii Agricultural Land Use dataset
- **Baseline climate:** Kodama et al. 2024 250m gridded climatology, 1990-2021 (ERA5-Land now supplies only the island-wide dT)
- **Forward projections:** NEX-GDDP-CMIP6 (SSP2-4.5 and SSP5-8.5, 2035 and 2045)

---

## Data Sources

| Source | Variables |
|--------|-----------|
| USGS 1m DEM | Elevation (mean/min/max/dev), slope, aspect (sin/cos), curvature, relief, distance to coast |
| Sentinel-2 via Google Earth Engine | NDVI median composite |
| ERA5-Land | Mean temperature, temperature range, GDD, cold months, annual precip, dry-season fraction, wind speed |
| NEX-GDDP-CMIP6 | ΔT and precipitation ratio per scenario and horizon |
| USDA gSSURGO (SSURGO) | Drainage order, restriction depth, AWC, pH, organic matter, sand/silt/clay %, CEC |

---

## Pipeline

### Data Wrangling (`data_wrangling/`)

| Notebook | Purpose |
|----------|---------|
| `00_region_polygon.ipynb` | Define study region; load 2020 Hawaii Agricultural Land Use shapefile; extract 674 coffee-farm polygons; buffer union preserves U-shape around Mauna Loa |
| `01_generate_grid.ipynb` | Subdivide region into 250m equal-area hexagonal grid; label cells by coffee-farm centroid overlap; EPSG:32604 (UTM Zone 4N) |
| `02_clip_dem.ipynb` | Extract and clip USGS 1m DEM to study area |
| `03_dem_features.ipynb` | Compute topographic feature set per cell |
| `04_ndvi.ipynb` | Sentinel-2 NDVI median composite via GEE |
| `05_climate.ipynb` | ERA5-Land climate variables: temperature, precipitation, GDD, dry-season fraction, wind |
| `06_soil_features.ipynb` | SSURGO soil properties per cell |
| `07_assemble_features.ipynb` | Join all layers; output: ~25 features × 385 coffee cells, pickled |
| `08_pkl_to_delta_csvs.ipynb` | Transform local NEX-GDDP pkl files into delta CSVs (ΔT, precip ratio) |
| `08_climate_projections.ipynb` | Blend ERA5 baseline + NEX-GDDP deltas into future climate feature pickles (2035, 2045) |

### Machine Learning (`ML/`)

| Notebook | Purpose |
|----------|---------|
| `01_model.ipynb` | Random Forest classifier (coffee vs. background) + PCA on the full feature set; regional distinctiveness metric; topographic and climate importance by district |
| `02_clustering.ipynb` | Per-region k-means (Kona K=3, Kaʻu K=2) on terrain, climate, soil, and NDVI; elbow + silhouette K selection; radar plot cluster profiles |
| `03_ndvi_regression.ipynb` | Predict NDVI median separately per region. **NO RESULT — see below.** The former claim ("Kaʻu (dry) emphasizes moisture proxies, Kona (wet) emphasizes elevation and aspect") is withdrawn: cross-validated R² is negative for both regions and both models, on the corrected data *and* on the original. Feature importances were computed on models with no predictive skill. |
| `04_similarity_search.ipynb` | Environmental analog finder: locate island cells most similar to Kona/Kaʻu in terrain-climate-soil space; expansion suitability and topographic identity maps |
| `05_forward_projection.ipynb` | Thermal suitability under NEX-GDDP warming scenarios; ensemble ΔT of +1.00°C (2035) and +1.35°C (2045); separate projections for Kona and Kaʻu |

---

## Key Findings

- **Kona thermal optimum:** 20.50°C (σ = 1.42°C), fit on the lapse-rate surface (2026-07-27 round 2 fix)
- **Kaʻu thermal optimum:** 20.65°C (σ = 1.07°C) — only 0.15°C apart from Kona's, not the divergent niches reported pre-fix
- **PCA climate variance explained:** Kona 24%, Kaʻu 40%
- Under projected warming, both districts show the same pattern: ~70% of farmable island land appears to gain thermal suitability climate-only, but restricted to each district's own terrain, ~64–67% of actual coffee country is on a declining trajectory instead — a 41×–53× overestimation common to both, not an asymmetric Kona-contracts/Kaʻu-expands story

---

## Structure

```
JavaScript/
├── README.md
├── data_wrangling/                 — numbered ingestion pipeline (00–08)
├── ML/                             — model notebooks (01–05)
├── data/
│   ├── climate_projections/        — NEX-GDDP delta CSVs and future feature pickles
│   └── raw/                        — DEM, soil, and other source data
└── img/                            — generated figures (300 dpi for publication)
```

---

## Environment

Python 3.10+. Key dependencies: `geopandas`, `rasterio`, `earthengine-api`, `scikit-learn`, `pandas`, `numpy`, `matplotlib`.

Google Earth Engine authenticated session required for `04_ndvi.ipynb`.
