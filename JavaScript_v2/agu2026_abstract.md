# AGU Fall Meeting 2026 — Abstract

**Deadline:** Wednesday, 5 August 2026, 23:59 EDT
**Session:** GC002 "Advances for Measuring and Modeling Food System Resilience"

**Status: an abstract is ALREADY SUBMITTED to GC002 (fee paid), and that submitted version is stale for three separate reasons, in sequence.** (1) It was framed around a divergent "Kona contracts / Ka'u expands" portfolio effect the paper disproved. (2) A first replacement draft (written 2026-07-29) went stale before ever being submitted — it carried pre-screen-fix contraction figures (-15.5%/-12.4%) and a "peak/approaching optimum" framing later retired as a tautology (Rounds 21-24). (3) A second replacement (2026-08-05, this file, built from `DRAFT_2026-07-30.md` and `notebooks/data/matched.json`) originally asserted the `dz/h` inversion condition ("threshold is already crossed") as fact — same day, block-bootstrapping that ratio (`notebooks/05_robustness.ipynb` §4) found its 95% CI includes 1 for both districts, not just Ka'u. The text below is the corrected version: matched-statistic result stated as fact, headroom mechanism presented as the open question the poster is built around — a deliberate live-science framing, not a hedge to minimize. See the Notes section for the bootstrap numbers and why.

**Caveat on in-review status:** the paper is in peer review at *Scientific Reports* (desk-rejected by *Nature Food* 2026-05-01). An error in the as-submitted version was disclosed to the editorial inbox 2026-07-26; the analysis has since been rebuilt and reframed around a general geometric condition rather than a coffee-specific divergence. Whether that reframe now amounts to a new submission rather than a correction is still undecided — see README.

---

## Title

Bounded Ground: When Terrain Limits Invert Climate-Only Suitability Projections

*(79 characters — well under the 300-character limit)*

## Authors

Simon-Hans Edasi *(add affiliation if required)*

## Abstract body

Crop suitability work increasingly intersects climate with land-availability screens, but usually evaluates that intersection once, at a single horizon. We show that evaluating it as a function of warming reveals something a snapshot cannot: the climate-only and land-screened answers can disagree in sign, not just magnitude, when the crop is confined to terrain bounded in the direction its envelope migrates. Writing the feasible set as F(dT) = C(dT) INTERSECT S, a migrating climatic window intersected with a stationary feasibility set defined by terrain. We test this on Hawaiian specialty coffee (471 farm cells, Kona and Ka'u districts) using a matched statistic: the same quantity computed with the terrain screen off and with it on.

At +1.35 degC, the thermal set alone is essentially unchanged in size (-0.3% pooled), while the terrain-intersected feasible set contracts 22.1% (13.7% by 2035). Because the two numbers are the same statistic differing only in whether S is applied, the contraction is attributable to the terrain constraint rather than the climatic shift: a climate-only reading reports a stable-to-improving thermal resource, while the feasible resource is measurably shrinking.

The working mechanism is the climatic window's leading edge closing in on the terrain footprint's own upper elevation limit: +1.35 degC requires roughly 236 m of upslope migration against 197-224 m of measured headroom. That is an open question, not a settled result. Block-bootstrapped, the displacement-to-headroom ratio does not yet exclude parity for either district, and tightening the footprint's upper boundary -- the screen's weakest edge -- is next.

The two designated origins are not distinguishable on any axis teste: thermal niche (0.18 degC apart, not significant), feasible-set trajectory, or cup scores from five years of competition data.The two are treated as one unit. If the headroom mechanism holds up, the transferable payoff is a portable pre-flight check: any similarly bounded system could compute its own displacement-to-headroom ratio from a lapse rate and its footprint's upper bound, without reproducing this analysis, to check whether its climate-only projection has the wrong sign.

*(1,889 characters excluding spaces — under the 2,000-character limit, ~110 to spare)*

---

## Notes

- **The opening framing was corrected 2026-08-05 — "climate-only suitability modeling" is not the state of the field.** Simon flagged that the original opening ("climate suitability projections typically map a climatic envelope onto a landscape") sets up a strawman: GAEZ and the broader crop-suitability literature have screened by land availability for decades. This is in the paper's own older `JavaScript.tex` (line 87), which explicitly says so and cites Ovalle-Rivera et al. 2015 noting upslope Colombian terrain may not be convertible — but that nuance was lost when `DRAFT_2026-07-30.md`'s Introduction was rewritten, and the AGU abstract inherited the flattened version. The actual, defensible novelty (also already in the old `.tex`) is narrower and sharper: (1) the screen here is anchored to a *specific* designation-of-origin configuration, not a generic arability mask, and (2) the intersection is evaluated *as a function of* the warming amount rather than once at a fixed horizon — which is what makes a sign reversal or a peak visible at all. The abstract's opening two sentences now state this precisely. **`DRAFT_2026-07-30.md` §1 has the same flattened claim and needs the identical fix — not done yet, lower priority than tonight's submission.**
- **Deliberate framing choice, 2026-08-05: present this as live science, not a closed result.** `dz/h` was bootstrapped the same day and does NOT hold up as a confirmed threshold — `ANALYSIS_TODO.md` item 3b originally worried only about Ka'u's 1.05 being close to 1, but the 95% CI includes 1 for **both** districts (Kona 1.19, CI 0.83-2.47; Ka'u 1.05, CI 0.67-2.08; `notebooks/05_robustness.ipynb` §4, `notebooks/data/headroom_bootstrap.json`). Rather than cut the mechanism or bury it as a caveat, Simon chose to lead with it as the open, unresolved question — the AGU room is exactly the audience for "here's a promising but not-yet-proven diagnostic, here's what would close it." This is a considered bet for engagement, not an oversight: AGU is Dec 2026, months away, so there is runway to either firm the number up before the talk or present it honestly as in-progress. Do not "fix" this by quietly reasserting `dz/h > 1` as settled — that was the previous version's mistake.
- **What the poster/talk needs to say out loud, beyond this abstract:** the concrete next step is tightening the footprint's upper elevation boundary (`zmax`, currently a 97.5th-percentile cutoff sensitive to which farm cells the bootstrap happens to resample) — that's the piece producing the wide CI. Worth having a one-line answer ready for "so is it true or not" at the poster.
- **Session fit.** GC002 wants advances in measuring and modeling food-system resilience. The proven half (the matched-statistic diagnostic) is the safe contribution; the mechanism, if it holds, is the more general and more exciting one — a portable pre-flight check for any siting-constrained system. Framing it as open work invites exactly the kind of conversation a poster session is for.
- **The CBB/degree-day result is dropped.** It was in the abstract submitted 2026-07-29 (18-23% generation-capacity increase). It is no longer part of the current draft's Results — see `DRAFT_2026-07-30.md` §6, where it survives only as a citation-correction note, not a finding. Do not reintroduce it here without checking the draft first.
- **The "peak"/optimum framing is retired, not merely rephrased.** `C` is fit on the same 471 farm-cell temperatures that `S` is a shell around, so an intersection peaking near dT=0 follows from the construction rather than being a result. The headroom mechanism in the abstract's third paragraph is the empirical replacement for that framing.
- **Every number here traces to `notebooks/data/matched.json`** (the matched-statistic table, `S_share_farmable_pct`, `headroom_m_*`, `displacement_over_headroom_*`), `notebooks/data/headroom_bootstrap.json` (the CIs), or `paper_numbers.json` keys `Frchange_pub_*`/`F_change_pooled_*`. `check_numbers.py` does not validate this abstract — it only reads the dead `.tex` — so verify by hand against those files, not by running the checker.
- °C and Δ render fine in AGU's submission form; ASCII fallbacks `degC` and `dT` used above defensively.
- Candidate figure: `notebooks/figures/04_inversion` (the matched |C| vs |F| statistic) for the proven half. For the mechanism, a figure showing the bootstrap distribution of `dz/h` straddling 1 would visually match the "open question" framing better than a single point-estimate number.
