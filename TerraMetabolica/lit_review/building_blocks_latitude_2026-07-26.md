# Are metabolite "building blocks" geographically constrained by latitude? — external lit review

Date: 2026-07-26. Scope: independent literature search, not a re-analysis of the 176-RSU dataset already built in this repo. Purpose: test the specific claim Simon raised on resurrecting TerraMetabolica — not that individual metabolites (curcumin, catechins, CGA) track altitude/latitude crop-by-crop (already tested here, mostly null when pooled — see CLAUDE.md), but that the biosynthetic *building blocks* — the pathway classes metabolites are made from (shikimate/phenylpropanoid, mevalonate/MEP-terpenoid, alkaloid) — cluster geographically, independent of which specific compound or crop is measured.

## Bottom line

Not stupid, but narrower than stated. The broad version of this claim ("secondary metabolite chemistry generally scales with latitude") has been directly tested at scale and rejected. A specific, scoped version of it — that shikimate/phenylpropanoid-derived compound classes (phenolics, flavonoids, anthocyanins) respond to UV/light gradients fairly consistently across unrelated taxa, while terpenoid and alkaloid classes do not — has real, independent support from multiple lines of evidence, and lines up with the one finding that already held up in this project's own shelved analysis (chalcone synthase / anthocyanin UV-induction, see CLAUDE.md). If TerraMetabolica gets resurrected, it should resurrect as this narrower, mechanism-first question, not as "all metaboloids everywhere."

---

## 1. The naive version is rejected: chemical defenses do not scale cleanly with latitude

The classical latitudinal herbivore-defense hypothesis (LHDH) predicts more chemical defense compounds toward the equator, driven by higher herbivory pressure in the tropics. Moles et al. (2011, Functional Ecology, "Assessing the evidence for latitudinal gradients in plant defence and herbivory") is the landmark quantitative test: a meta-analysis across dozens of latitudinal comparisons.

Findings, broken out by compound class (this is the important part — they did not treat "chemical defense" as one bucket):
- Tannins/phenolics: 36 comparisons. 4 showed higher concentration at low latitude, 25 showed no significant relationship, 7 showed higher concentration at HIGH latitude. Net: no clean gradient, and where a significant signal exists, it more often runs opposite the classic prediction.
- Across all chemical defenses pooled: significantly HIGHER at higher latitudes overall, the reverse of LHDH.
- Herbivory itself: only 37 percent of studies show the expected higher-herbivory-at-low-latitude pattern; the meta-analytic effect size is not distinguishable from zero.

Later work (macroevolutionary/phylogenetic tests, ~2018) reached similarly inconsistent conclusions. There is also a documented citation-bias problem: papers confirming the classic gradient get cited several times more than papers that do not, which is worth remembering before trusting any single positive result in this space.

Implication for TerraMetabolica: this is independent, external confirmation of what the RSU altitude-regression work already found the hard way (null when pooling z-scored compound classes across crops). The "flavor building blocks generally track latitude" framing, stated broadly, does not hold up in the wider literature either. This is not a project-specific failure — it is a real, replicated null in plant chemical ecology.

## 2. The scoped version has real support: phenolics specifically, not metabolites in general

A phylogenetically-controlled metabolomics study (tropical vs temperate tree species, full foliar metabolome plus four major compound-class families) found a real and specific signal: tropical species had significantly higher phenolic diversity, and polyphenolics specifically showed moderate support for the same pattern — but there was no difference for the whole metabolome, and no difference for the other major compound families tested (which includes terpenoids and alkaloids).

This is the key structural finding for Simon's reframed hypothesis. It is direct evidence that:
- Latitude does NOT predict overall metabolite chemistry.
- Latitude DOES appear to predict one specific pathway class: phenolics/polyphenolics.
- The effect is not visible if you pool all compound classes together — it only shows up once you split by pathway of origin.

That last point is exactly the distinction Simon drew ("not individual metabolites, but the building blocks"): the signal is at the pathway-class level, and gets washed out if you average across pathway classes or across unrelated crops without separating them.

## 3. A plausible mechanism exists, and it is the same one this project already found

The shikimate pathway is a major carbon sink in plants (up to ~30 percent of fixed carbon in some estimates) and feeds phenolics, flavonoids, tannins, and lignin. Its output is consistently described in the literature as induced by UV radiation, light quality, and other abiotic stress — i.e., its activity is systematically tied to variables that co-vary with latitude and altitude (UV-B dose, light intensity, temperature).

Chalcone synthase (CHS), the enzyme gating the flavonoid/anthocyanin branch of this pathway, is described as broadly UV-induced across plant taxa at the regulatory level — this is the exact mechanism TerraMetabolica's own shelved analysis converged on (anthocyanin natural experiments: 6 of 6 independent crop systems positive direction, sign test p = 0.016; monoterpene phenols and total phenolics pooled showed no signal). The external literature and the internal RSU dataset are pointing at the same narrow mechanism from two different directions.

No literature was found directly quantifying relative carbon allocation between the shikimate and mevalonate/MEP pathways across a climate gradient — that specific comparison (phenylpropanoid output vs terpenoid output, same sites) does not appear to have been done as a dedicated study. That is a real gap, and potentially a real opening, rather than a red flag.

## 4. A tempting shortcut to avoid: carbon-nutrient balance hypothesis

The carbon-nutrient balance hypothesis (CNBH) offers a clean a priori story for why compound CLASS (not just concentration) should shift with climate: carbon-based defenses (phenolics, terpenoids) should be favored when carbon is in excess relative to nutrients (e.g., nutrient-poor, light-rich environments), while nitrogen-based defenses (alkaloids) should be favored when nitrogen is abundant relative to carbon.

This is worth knowing about because it is the obvious mechanism someone would reach for to justify "building blocks cluster by climate" — but Hamilton et al. (2001, Ecology Letters, "The carbon-nutrient balance hypothesis: its rise and fall") is a direct, citable warning: CNBH has been invoked to explain hundreds of studies post hoc, works in some cases, and fails often enough that it is no longer considered a reliable predictive framework. A further conceptual problem: nitrogen-rich enzymes and nitrogen-containing precursors are themselves involved in producing so-called "carbon-based" defenses, so the C/N split is a leakier proxy for pathway identity than it first appears.

Recommendation: do not lean on CNBH as the theoretical backbone for a resurrected TerraMetabolica. Use it as a candidate mechanism to test, not an assumption to build the RSU schema around — the same mistake ("plausible based on mechanism" standing in for a verified source) is explicitly the failure mode TerraMetabolica's own CLAUDE.md already warns against for individual compound values.

## 5. What this means for a resurrection

If TerraMetabolica comes back, the defensible version of the question is narrower than "metaboloids in general cluster by latitude." It is closer to:

Does shikimate/phenylpropanoid-pathway output (flavonoids, anthocyanins, hydroxycinnamic acids -- the UV-screening compound classes) show a consistent, cross-taxa geographic/climatic signal, while mevalonate/MEP-pathway output (terpenoids) and alkaloids do not?

This is testable, has independent support from at least two unrelated lines of evidence (the tropical/temperate phylogenetic metabolome study, and CHS UV-conservation biochemistry), and is consistent with -- not a re-litigation of -- what the 176-RSU dataset already found before it was shelved. It would also resolve the "lit review drift" problem noted in the shelving decision, because the hypothesis is now stated at the pathway-class level from the start, rather than discovered post hoc after chasing individual compounds crop by crop.

What it is NOT: a claim that any given flavor compound, or food's flavor generally, is latitude-determined. The literature is fairly clear that this broader claim does not hold.

---

## References

- Moles AT et al. (2011). Assessing the evidence for latitudinal gradients in plant defence and herbivory. Functional Ecology. DOI 10.1111/j.1365-2435.2010.01814.x
- Tropical vs temperate foliar metabolome phylogenetic comparison (phenolic/polyphenolic diversity higher in tropical trees; no whole-metabolome or terpenoid/alkaloid difference). PMC7998528.
- Hamilton JG et al. (2001). The carbon-nutrient balance hypothesis: its rise and fall. Ecology Letters. DOI 10.1046/j.1461-0248.2001.00192.x
- Shikimate pathway carbon flux and phenylpropanoid/UV-stress responsiveness (ScienceDirect topic overview; IntechOpen chapter on shikimic acid pathway in phenolic biosynthesis).
- TerraMetabolica internal: CLAUDE.md session 7-8 notes, chalcone synthase / anthocyanin cross-crop natural experiment analysis (6/6 positive, sign test p = 0.016), notebook 13 pooled null results for monoterpene phenols and total phenolics.

## Not yet checked

- Whether a dedicated study exists comparing shikimate vs mevalonate/MEP pathway carbon allocation directly across the same sites (searched, not found -- may not exist, or search terms need refinement).
- Dictionary of Natural Products, or a direct GBIF-occurrence-plus-climate join, for a systematic geographic tally of compound-class occurrence.

## 6. KNApSAcK checked (2026-07-26) -- usable for compounds, not for geography

Probed directly (curl against the live site, not just documentation) rather than assumed.

**What KNApSAcK Core DB actually provides:** species-to-metabolite pairs via a plain query (`knapsack_core/result.php?sname=organism&word=<species>`), returning C_ID, CAS number, metabolite name, molecular formula, Mw, and organism. Each metabolite's own page (`information.php?word=<C_ID>`) adds SMILES/InChI and every species it has been reported in. No pathway-class field is present (no native "flavonoid" / "terpenoid" / "alkaloid" tag) -- assigning compound class would require running the SMILES through an external classifier (e.g. NPClassifier), which is straightforward but is a real added step, not something KNApSAcK gives for free.

**What KNApSAcK WorldMap DB actually provides, and why it does not answer the question:** per-species, per-country records of edible/medicinal use (`KNApSAcK_World/search.php?cn=<3-letter country code>&wd=<species>`), with no single call returning all countries for a species -- a full per-species footprint means querying all ~229 country codes individually. More importantly, this table tracks culinary/medicinal *adoption* by country, not native range, collection locality, or climate. The site's own top-ranked entries by "number of countries" are potato (170), strawberry (89), corn (78) -- globally traded crops, ranked by how widely they are eaten, not by where their chemistry is distinct. That is a trade-and-cuisine signal, not a biogeographic one, and using it to test latitude-linked compound-class clustering would conflate global food adoption with climatic constraint on biosynthesis.

**Access restriction:** the site states data reuse/redistribution is restricted without contacting the database group -- relevant to any scraping plan, not just a documentation footnote.

**Conclusion:** KNApSAcK is a usable source for species-to-compound-structure data (paired with an external classifier for pathway class), but its geographic component is the wrong kind of geography for this hypothesis. The actual next step, if this gets pursued, is pairing KNApSAcK (or a similar structure database) against GBIF occurrence records (which carry real lat/lon) and WorldClim, rather than using KNApSAcK's own WorldMap DB.

## 7. GBIF checked (2026-07-26) -- real occurrence coordinates, confirmed working

Probed directly against the live API (`api.gbif.org`), no auth required.

**Confirmed working:**
- `species/match?name=<name>` resolves a species name to a taxonKey cleanly (tested Vaccinium myrtillus: exact match, confidence 97).
- `occurrence/search?taxonKey=<key>&hasCoordinate=true` returns real `decimalLatitude`/`decimalLongitude` per record. Vaccinium myrtillus alone: 1,019,367 georeferenced records.
- `elevation` field is populated for a real fraction of records (not all): 179,688 of the bilberry records fall inside a 1-4000m filter, with sane individual values (1589m, 667m, 732m, etc).
- Coordinate coverage checked across five actual TerraMetabolica species: Origanum vulgare 423,941 coord records, Vitis vinifera 109,645, Coffea arabica 13,977, Camellia sinensis 4,608, Curcuma longa 1,426. Cultivated crop species have far fewer coordinate records than wild/weedy species -- see caveat below for why.
- API limits: max 300 records per page; offset+limit capped at 100,000 on the free search endpoint. Only Origanum vulgare and Vitis vinifera exceed that at full scale here -- both would need GBIF's registered Download API (free account, async job, returns a citable DOI'd dataset), which is the more rigorous choice for anything destined for a paper regardless of volume.
- No reuse-restriction friction of the kind KNApSAcK has -- GBIF is built for exactly this kind of programmatic access.

**Caveat that matters for how this gets used:** GBIF records where a species has been *observed* (heavily iNaturalist/citizen-science-driven for wild species), not where a specific paper's analyzed sample was grown. This is why coffee and tea have thin coordinate coverage relative to wild oregano -- nobody logs citizen observations of commercial coffee plantations, but wild oregano gets logged constantly. GBIF is therefore a strong fit for the wild-collected chemotype side of this project (bilberry, wild oregano, wild sage -- the natural-experiment RSUs that already produced the cleanest signal) and a weak substitute for a paper's own reported plantation coordinates on cultivated crops. It answers "what is this species' climate niche" well; it does not tell you "where was the exact plant this HPLC value came from."

**Net:** GBIF is the correct replacement for KNApSAcK's WorldMap DB as a geography source. Combined with KNApSAcK (or NPClassifier-classified structures) for compound-class assignment and WorldClim for climate variables, this is a workable three-source pipeline: species -> compound class (KNApSAcK/NPClassifier), species -> occurrence coordinates (GBIF), coordinates -> climate (WorldClim). Best suited to wild-species chemotype questions; cultivated-crop questions still need the original papers' own site data, as TerraMetabolica already does.
