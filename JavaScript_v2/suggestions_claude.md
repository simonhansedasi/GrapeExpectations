# Working Review — *Adaptation Space Peaks at Present Climate* (Edasi 2026, v3)

**Manuscript:** `javascript_v2.pdf` (v3 text; supplement not supplied this round)
**Verdict:** Minor-to-moderate revision. Up from *major revision* at v2.

**Change since v2:** Substantial and, in one case, self-correcting in a way I missed. All four v2 diagnostics were run. The `elevation deviation` feature turned out to be an exact scalar offset of mean elevation (r = 1.000), so elevation contributed **two of eight squared terms** to every distance — a double weighting on precisely the axis the thermal band migrates along. That inflated the v2 headline. Finding it yourself and reporting the before/after in §7.2 is the right move and is the single most important thing that happened between drafts.

**How to use this document:** §1 and §2 interact and can both move headline numbers — do them together, first. §3–§5 are substantive but bounded. §6–§7 are cleanup. §8 is the checklist.

---

## Settled from the v2 review

No further action needed on any of these.

| v2 item | Status |
|---|---|
| **§1 ΔT sweep** | Done (§7.6, Fig. 4). Produced a better paper than either branch I predicted. The peak is real, the offsets differ in sign, and §2's second consequence *owns* the construction issue rather than defending against it. "The peak sits near ΔT = 0 by construction; the interesting measurement is the offset" is exactly the right sentence. |
| **§3 terrain break** | Done (§7.3, Fig. 3). Five of six descriptors breaking above 950 m, with aspect cosine reversing sign, is a genuine geomorphological result and converts the load-bearing assertion into evidence. |
| **§2 sensitivity** | Done (§4.5). 313/320 with medians, range, and named degenerate corners is what the claim needed. |
| **CBB arithmetic** | Rebuilt on degree-days (332 DD, 14.9 °C threshold) and now verifiable. I checked 600 m and 800 m at both increments and reproduce 18/23/25/31%. The field-rate validation against Hamilton's observed 0.33–0.78 range is the right way to do it, and avoiding extrapolation past 778 m is the right call. |
| **Scenario policy** | Fixed. +1.00/+1.35 now explicitly labelled as carrying no ensemble interpretation, and "bracket" is gone. |
| **Vestigial sources** | ERA5-Land demoted to a development acknowledgement; SSURGO and Sentinel-2 removed. |
| **v2 §5 numbers** | Mislabelled "suitability rate" gone with the multiplier rewrite; Table S1 Mahalanobis presumably filled (supplement not supplied — verify). |
| **New disclosure** | The 32% acreage-capture gap with the elevation-bias test (446 vs 452 m, p = 0.52) is a good unprompted addition. |

---

## §1 — "Present climate" is not present, and the baseline epoch is never stated

**This is the new blocker.** It moves every headline number and can invert one of them.

### The problem

- The climatology is the mean of 384 monthly rasters, **1990–2021** (§7.1.3). Midpoint ≈ **2005.5**.
- The NEX-GDDP deltas are for windows centred on 2035 and 2045, relative to a reference period **the paper never names**.
- So ΔT = 0 in Figure 4 is not today. It is roughly two decades ago, with something on the order of **+0.3 °C** of observed warming sitting between the two.

### Consequences

| Claim | As stated | If re-centred on ~2020 |
|---|---|---|
| Kona offset | 0.65 °C past peak | ≈ **0.95 °C** past peak |
| Ka'u offset | +0.15 °C — "reaches its peak within the decade" | ≈ **already past it** |
| 2035/2045 increments | measured from 1990–2021 mean | measured from a displaced origin — horizon labels may be optimistic |

**Ka'u's headline claim inverts.** The one district with margin left may not have any. That margin is load-bearing in the abstract (line 19–20), in §4.2 (line 156), in the Discussion (line 261) and in the Conclusions (line 334).

### Required

1. State the reference period for the NEX-GDDP deltas in §7.1.3.
2. State the climatology midpoint explicitly.
3. Either re-centre the sweep on ~2020, or relabel Figure 4's x-axis honestly as anomaly from the 1990–2021 mean. The dotted line currently says "present climate" and does not mark present climate.
4. Propagate wherever the offsets appear.

---

## §2 — The peak has no confidence interval, and it is now the paper's headline

Block-bootstrap machinery exists (§7.7) and is used for the multiplier and the decline fractions. **The peak location gets no interval at all**, and it is the claim in the title.

### What the current numbers imply about precision

| District | F(peak) | F(0) | separation | offset |
|---|---|---|---|---|
| Kona | ≈1,738 | 1,651 | 5.3% | −0.65 °C |
| Ka'u | ≈1,857 | 1,836 | **1.1%** | +0.15 °C |

Ka'u's peak sits **1.1% above** its present-climate value, on 62 cells supporting roughly eight independent spatial blocks. +0.15 °C is 26 m of elevation at your lapse. I would be surprised if that offset were distinguishable from zero.

Independent evidence on the scale of the uncertainty: switching to the elevation-free screen moves the peaks by 0.20 °C (Kona) and 0.15 °C (Ka'u) — the latter equal to the entire Ka'u offset.

### Required

Bootstrap the argmax of |F_r(ΔT)| using the existing block machinery.

- **If Kona's interval excludes zero and Ka'u's does not** → "one district measurably past its peak, one indistinguishable from it" is a cleaner and more defensible sentence than the current pair of point estimates, and it survives §1 re-centring.
- **If both straddle zero** → the abstract must say so, and the paper's claim becomes about the geometry plus the *sign* of the offsets rather than their magnitudes.

Do this together with §1; re-centring shifts the point estimates and the interval determines whether that shift matters.

---

## §3 — The factorial omits the choice that moves the answer most

The 160-setting grid sweeps metric, threshold, inflation and τ. It does **not** sweep how much elevation is in the screen — which your own numbers show is the dominant lever:

| elevation coordinates in S | Kona | Ka'u |
|---|---|---|
| 2 (v2, collinear duplicate) | −15.5% | −12.4% |
| 1 (current) | −9.9% | −9.5% |
| 0 (elevation-free) | −5.0% | −2.6% |

A **3× range**, wider than the entire factorial's spread. §4.5 calls it "roughly half the magnitude," but that is measured from the 1-copy baseline, which is a choice rather than a reference point — as the discovery of the 2-copy bug demonstrates.

Your defence — that an elevation-free screen is not the *more correct* screen, because elevation band is part of what a designation of origin denotes — is sound and should stay. But then the honest presentation is a **continuous sweep of the elevation weight** (0 → 2 on the standardised elevation coordinate), reported alongside the factorial, so a reader sees the whole curve and applies their own prior.

Add it as a fifth factor, or as its own panel. Also report the **peak offsets** across the factorial, not just at the two screen settings currently given.

---

## §4 — The abstract overclaims against the paper's own results

1. **"prove that on a bounded landscape it is single-peaked"** (line 14–15). Proposition 1 requires **s unimodal**. Bounded support does not imply unimodal — a landscape with two benches gives bimodal s and no single peak. Restore the hypothesis to the abstract.
2. **"no climate pathway increases it"** (line 17). Ka'u's peak is at +0.15 °C, so by Figure 4 a small warming *does* increase Ka'u's adaptation space. §4.2 handles this correctly; the abstract contradicts it.
3. **Mismatched intervals** (lines 20–23). "Between now and the 2045 horizon the intersection falls 26.4%" is present→2045. "The island-wide suitable area is static to within one percent — under the lower emissions pathway it grows" is a 2035→2045 statement (§4.3, lines 178–186). Report both quantities over the same interval, or the juxtaposition is not doing the work it appears to do.
4. **Increment provenance.** 26.4% / 18.2% are computed at +1.35 °C, which §7.1.3 now explicitly says carries no ensemble interpretation. Either pair them with the per-scenario present→2045 declines or flag the increment in the abstract.

---

## §5 — Proposition 1's proof sketch is wrong (the proposition is right)

> "the cross-correlation of a unimodal function with a symmetric kernel is unimodal" (lines 77–78)

**Symmetry is not sufficient.** The convolution of two unimodal densities is not generally unimodal; that is the standard counterexample space.

The correct statement is **Ibragimov (1956)**: g ⊛ f is unimodal for *every* unimodal f if and only if g is **log-concave** (strongly unimodal). The indicator of an interval is log-concave, so your result holds — but for that reason, not symmetry. Wintner (1938) covers symmetric-unimodal ⊛ symmetric-unimodal if you want the alternative citation.

Two lines to fix, and it removes an easy referee objection.

### Two related points

**Framing.** A referee will note that unimodal ⊛ uniform is textbook. Frame Proposition 1 as the *organising observation* and put the weight on the measured offset, which is the actual contribution. You already say this at line 100 ("which is what a formal statement alone cannot do") — say it earlier, and consider softening "prove" to "show."

**Missing premise check.** Nothing in the paper verifies that s(z) — the elevation-marginal cell count of each footprint — is actually unimodal. **Add a one-panel histogram** of Kona-like and Ka'u-like cells by elevation. It does four jobs at once: verifies Prop 1's hypothesis, shows the mode directly, shows the 950 m truncation, and makes the peak offsets legible as "the footprint's mode sits ~114 m below the mean farm elevation." Cheap, and it closes the loop between §2 and §4.2.

---

## §6 — The break test doesn't test for a break, and the "independent route" isn't independent

### §7.3 measures a break, given the break location

Fitting OLS over 400–900 m and 950–1,400 m and comparing slopes tests *how large* the change is at an assumed 950 m. It does not establish that 950 m is *where* the change is.

**Fix:** fit a segmented regression with a **free breakpoint** and report where it lands, with a CI.
- Lands at 950 ± 60 m → the claim is far stronger than it currently is, and §4.1 gets a real number instead of a comparison.
- Lands at 1,150 m → you want to know before a referee does.

### The 937 m figure is confirmatory, not independent

Described as arriving "by a route independent of that threshold" (line 147–148) and called "an independent route" in the abstract (line 26) and Conclusions (line 333). It isn't:

- The footprint's 950 m upper bound **is by definition** the highest cell whose centroid distance falls under the 95th-percentile threshold.
- 937 m is where the *binned mean* centroid distance crosses **that same threshold**, using the same features, the same standardisation, and the same centroid.

Agreement to 13 m is close to arithmetic. Downgrade to "confirmatory," or drop it — the five-of-six slope breaks are the real evidence and don't need the help. Keeping it as "independent" is the kind of thing a referee will single out precisely because the rest of the paper is careful.

---

## §7 — Smaller items

- **Figure 3 still shows an `elev. deviation` panel**, identical to the elevation panel, for a feature the paper has removed. The caption explains it, but displaying a deleted feature in the flagship terrain figure invites confusion. Move to supplement.
- **Feature-name discrepancy across versions.** v2 §6.1.2 called it "elevation standard deviation"; v3 §7.2 calls it "mean elevation minus the island-wide mean elevation." Those are different objects and only the second is collinear with mean elevation. One clause confirming which was actually computed — anyone comparing versions will notice.
- **Check the 68.0% coincidence.** Kona's area-weighted declining fraction is 68.0% (line 212) and the acreage capture rate is 100 − 32 = 68% (line 353). Almost certainly coincidence, but it is exactly the shape of an accidental denominator swap. Verify once.
- **Asymmetry statistic** (lines 158–164). A ratio of 1.23 is described as "close to symmetric." It means the right limb sits 23% *above* the left at equal displacement — cooling costs Kona more than warming, not the same. State the direction; it slightly complicates "every subsequent increment is downhill."
- **"The best alignment each district could have had"** (line 176). Kona's peak is 0.65 °C below a 1990–2021 mean — roughly a pre-industrial-era climate. It is a counterfactual, not a foregone option. One qualifying phrase.
- **Settlement history vs hypsometry.** The offset conflates them: farms were sited for land tenure, road access and water, not thermal alignment. Doesn't affect the measurement, but "Kona has passed its best alignment" implies an optimum once achieved. One sentence in Limitations.
- **Rounding inconsistency.** Text says 14.4% combined and Ka'u 8.5% (line 130); Figure 2 title says 8.4%; §7.2 says 8.45%. Pick one.
- **Supplement not supplied this round.** Table S1 cell counts, Figure S1 percentages and Note S2's Kaua'i test all need rerunning against the seven-feature screen. In particular, Note S2's "six features not defined relative to the containing island" paragraph no longer parses — one of the two features it drops has been deleted outright. Also confirm the v2 errata are cleared: three `(§??)` cross-references, the raw `PerroyCollier2021` key, and the stale supplementary title.

---

## What's working

- **The reframe.** Single-peakedness is a genuine improvement on "contraction under warming." §2's first consequence — that a contraction result is incomplete without the peak location, because cooling would contract it too — is the paper imposing a discipline on itself that the literature doesn't impose, and then following it.
- **Three independent bounds on the circularity**: elevation removed entirely, the elevation-stratified null for the multiplier, and the closed-form Φ(ΔT/2s) check on the declining fraction. Few papers quantify their own weakest point once; this does it three ways.
- **Figure 3.** The strongest new empirical content. It answers the exact question I asked and answers it against interest — reporting that coastal distance only steepens 1.6× rather than rounding it in with the others.
- **The bug disclosure in §7.2.** Reporting that removing the duplicate cut the headline from 15.5% to 9.9% and *improved* out-of-band recovery from 64% to 90% is unusually clean scientific conduct. Keep it in the main text; do not let a referee talk you into moving it to a supplement.
- **§4.4's closing note** that farm-cell statistics depend only on the envelope and the labelled cells, so they are unaffected by any terrain-screen choice. That is the right thing to say and it insulates the economically load-bearing numbers from the whole §3 debate.

---

## Priority order

1. **§1 — baseline epoch.** Can invert Ka'u's headline claim. Do first.
2. **§2 — bootstrap the argmax.** Interacts with §1; determines whether the offsets are measurements or point estimates.
3. **§5 — Ibragimov fix + s(z) histogram.** Cheap, closes the theory's open premise.
4. **§4 — abstract claims.** Three sentences, but they currently contradict the body.
5. **§6 — free-breakpoint regression; downgrade the 937 m route.**
6. **§3 — elevation-weight sweep as a fifth factor.**
7. **§7 — cleanup.**
8. **Supplement — rerun against the seven-feature screen.**

Items 1 and 2 move numbers in the abstract, §4.2, §4.3, the Discussion and the Conclusions. Don't rewrite prose until they're done.

---

## Venue

After §1–§5: *Environmental Research Letters*, *Climatic Change*, *Global Change Biology*, or *Agricultural Systems*. A step up from where v2 landed.

The framing that earns that range is the measured offset, not Proposition 1 — the proposition is the organising device, and the contribution is that two districts on one volcano, sharing a thermal optimum, sit on opposite sides of their own peaks, and that this is measurable at all because a designation of origin supplies an S you can actually draw.
