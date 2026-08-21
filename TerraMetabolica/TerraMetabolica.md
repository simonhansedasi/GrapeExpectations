# TerraMetabolica — Project Context (v0.3)

## 1. What This Is

**TerraMetabolica** is a geographic metabolite atlas: a dataset of 157 Region Sample Units (RSUs) across 6+ continents, each recording HPLC/GC-measured secondary metabolite concentrations for a specific food crop at a specific location. The analytical question is whether environmental variables — particularly UV-B radiation — predict secondary metabolite concentrations across unrelated food crops globally.

This is the **controlled continuous empirical case** in the CIPT research program. See `/home/simonhans/coding/PROGRAM_STRATEGY.md` for the theoretical framework.

---

## 2. The Core Question (v0.3, reframed 2026-04-14)

> Do UV-stress compound classes (flavonols, anthocyanins, phenolic monoterpenes) show consistent positive relationships with UV-B exposure across unrelated food crops globally?

This replaces the v0.2 approach (within-crop altitude regression per food system). The new approach:
- Pools all RSUs regardless of crop species
- Tags each compound observation with a compound class and primary environmental driver
- Uses a UV-B proxy (`cos(|lat| × π/180) × (1 + altitude_m/2500)`) as the predictor
- Tests for cross-species signal within compound classes

**Key finding (2026-04-14):** Pooled UV-B signal is null (R²=0.0001). Anthocyanins are the exception: R²=0.721, p=0.032, n=6. Chalcone synthase is the most universally UV-induced enzyme across plant taxa — the anthocyanin pathway crosses species lines in a way that terpenoid biosynthesis does not. Phenolic monoterpenes (carvacrol, thymol) show strong within-species UV signal but null cross-species signal because inter-species variance swamps the environmental gradient in a pooled regression.

**Current paper direction:** UV-B predicts fruit pigmentation intensity across unrelated crops — anthocyanins are the convergent biochemical fingerprint of high-UV food environments. Not "UV-B drives metabolites universally" but "UV-B drives a specific universal pathway (chalcone synthase) whose product is the key UV-screen pigment across all plant taxa."

---

## 3. Causal Chain

```
UV-B radiation + temperature + aridity
    ↓ (plant stress response)
Compound-class-specific biosynthetic induction
    ↓
Measured secondary metabolite concentrations
    ↓ (RSU observations)
Cross-crop pattern analysis
```

The v0.2 chain (Climate + Geology → Biodiversity → Flavor) was too abstract. v0.3 works at the biochemical mechanism level: UV-B activates chalcone synthase → anthocyanins accumulate as UV screen. This is species-agnostic and testable with the RSU dataset.

---

## 4. Unit of Analysis: Region Sample Unit (RSU)

Each RSU = one geographic site + one food crop + one set of HPLC/GC compound measurements from a specific peer-reviewed paper.

**Inclusion criteria (v0.3):**
- Any food crop (herb, fruit, vegetable, grain, root)
- Any geography (single-site papers acceptable)
- Primary peer-reviewed paper required — no USDA FDC, Phenol-Explorer, "literature" composites
- Quantitative HPLC or GC measurements in absolute units (mg/g DW, g/100g DW, % EO)
- Geographically identifiable site (named region at minimum; GPS preferred)
- Cultivar and cultivation status (wild/cultivated) recorded as metadata

**Natural experiment pairs** (same crop, same paper, two+ altitudes from one study) are the highest value RSUs because they isolate environment from variety and methodology.

---

## 5. RSU Schema (v0.3)

```json
{
  "region_id": "RSU-XXX",
  "name": "descriptive name with altitude and crop",
  "coordinates": { "lat": float, "lon": float, "altitude_m": integer },

  "climate": {
    "temperature_mean": float,
    "temperature_seasonality": float,
    "precipitation_mean": integer,
    "precipitation_seasonality": float
  },

  "geology": { "parent_material": "string", "soil_pH": null },

  "biodiversity": { ... },

  "staple_foods": [
    {
      "name": "string",
      "metabolite_profile": {
        "key_flavor_bioactives": { "compound": "value [citation]" },
        "terpenes": {},
        "organic_acids": {},
        "umami_compounds": {}
      },
      "natural_experiment": ["RSU-YYY", "..."],
      "data_sources": ["Author Year Journal DOI"]
    }
  ],

  "analytical_observations": [
    {
      "compound": "string",
      "compound_class": "see taxonomy below",
      "primary_environmental_driver": "UV_B | temperature | aridity | fermentation | pasture_quality",
      "crop": "species name",
      "value": float,
      "units": "mg_per_g_DW | g_per_100g_DW | percent_EO | mg_per_100g_FW | ...",
      "analytical_method": "HPLC | GC-MS | GC-FID | spectrophotometry",
      "cultivation_status": "wild | cultivated | unknown",
      "source": "Author Year citation string"
    }
  ]
}
```

The `analytical_observations` array is the analysis-ready flat structure for notebook consumption. The `staple_foods[*].metabolite_profile` structure retains the raw annotated string values with full citation context.

---

## 6. Compound Class Taxonomy

| Class | Examples | UV-B induced? |
|-------|----------|---------------|
| `anthocyanin` | cyanidin-3-glucoside, delphinidin | YES — chalcone synthase universal |
| `flavonol` | quercetin, kaempferol, rutin | YES — same CHS pathway |
| `flavan_3_ol` | catechins, epicatechin | PARTIAL — temperature also important |
| `monoterpene_phenol` | carvacrol, thymol | WITHIN-SPECIES only — inter-sp variance swamps UV |
| `monoterpene_non_phenol` | linalool, borneol | TEMPERATURE driven — decreases with altitude |
| `monoterpene_oxide` | 1,8-cineole | mixed |
| `monoterpene_total` | essential oil yield | aridity driven |
| `sesquiterpene` | viridiflorol, caryophyllene | mixed |
| `diterpene` | carnosic acid, carnosol | aridity + UV |
| `curcuminoid` | curcumin, demethoxycurcumin | TEMPERATURE driven — decreases with altitude |
| `glucosinolate` | sulforaphane, indole-3-carbinol | UV_B — Brassica altitude |
| `hydroxycinnamic_acid` | chlorogenic acid, caffeic acid | UV_B — altitude increases |
| `alkaloid` | trigonelline | complex |
| `total_phenolic` | TPC (GAE) | heterogeneous — avoid pooling |

**Driver assignment logic:** the `primary_environmental_driver` field reflects the biochemical mechanism, not just the observed correlation. Linalool is tagged `temperature` (not UV_B) even though it decreases with altitude because the mechanism is temperature-mediated suppression of the linalool branch in favor of the phenolic branch under UV stress.

---

## 7. Observation Count (2026-04-14)

157 RSUs, 657 total analytical observations:

| Driver | n observations |
|--------|---------------|
| UV_B | 261 |
| temperature | 225 |
| fermentation | 117 |
| aridity | 48 |
| pasture_quality | 6 |

UV_B observations are the primary analysis target. Fermentation observations are excluded from the environmental driver analysis.

---

## 8. Hypothesis Space (v0.3)

| ID | Statement | Current status |
|----|-----------|---------------|
| H1 | UV-B predicts UV-stress compound concentrations across unrelated crops | **PARTIAL: anthocyanins yes (R²=0.72), monoterpene_phenols no (inter-sp variance)** |
| H2 | Temperature predicts curcuminoid concentrations across turmeric growing regions | **SUPPORTED: R²=0.724, p<0.0001, n=21** |
| H3 | Chalcone synthase UV-induction is the most conserved cross-taxa metabolite pathway | **SUPPORTED by anthocyanin finding; to be tested with more RSUs** |
| H4 | Wild plants show stronger altitude/UV gradients than cultivated plants | **SUPPORTED: Kashmir oregano — wild 76-85% carvacrol vs cultivated 52-61%** |
| H5 | Within-species UV signal is real but does not generalize cross-species in pooled regression | **CONFIRMED: marjoram within-crop R²=0.808; pooled monoterpene_phenol R²=0.001** |

---

## 9. RSU Geography (157 RSUs, 6+ continents)

**Altitude series (natural experiments — highest analytical value):**
- Turkey marjoram 766–1387m — 7 sites (RSU-90 to RSU-96)
- Kashmir oregano 1363–2896m — 10 sites (RSU-134 to RSU-143)
- Nepal turmeric 80–2150m — 18 sites (RSU-67 to RSU-70, RSU-117 to RSU-131)
- Uttarakhand thyme 412–2744m — 3 sites (RSU-155 to RSU-157)
- Dalmatia sage 8–183m — 7 sites (RSU-148 to RSU-154)

**Cross-geography comparisons:**
- Korean turmeric (RSU-132/133) — same crop, different continent from Nepal
- Ethiopian coffee 5 regions (RSU-71 to RSU-75)
- Yerba mate 3 countries (RSU-85 to RSU-87)
- Ecuador wild blueberry 2 altitudes (RSU-88/89)

**Anthocyanin RSUs (current expansion target):**
- Ecuador Vaccinium floribundum 2836m/3641m (RSU-88/89)
- Peru purple corn 2025m/2828m (RSU-97/98)
- India Brassica Ladakh/Chandigarh (RSU-99/100)
- Seeking: grape skin (Malbec altitude), bilberry (Alps), elderberry, red onion

---

## 10. Key Analytical Findings

### Notebook 12 — Multi-environment analysis
- Curcumin is temperature-driven (R²=0.72), not altitude-driven (R²=0.08)
- Korea turmeric lies ~30 mg/g below the Nepal log curve — variety or photoperiod confound unresolved
- Kashmir oregano: precipitation seasonality proxies wild/cultivated status (R²=0.742), not aridity
- Dalmatia sage: no altitude gradient at coastal scale; Hvar (most UV-sunny island) highest thujone

### Notebook 13 — Cross-crop UV-B analysis

| Compound class | n | R²(UV) | p | Verdict |
|---|---|---|---|---|
| anthocyanin | 6 | 0.721 | 0.032 | **SIGNIFICANT** |
| flavan_3_ol | 16 | 0.153 | 0.134 | marginal |
| flavonol | 11 | 0.092 | 0.366 | not significant |
| monoterpene_phenol | 46 | 0.001 | 0.860 | null |
| total_phenolic | 105 | 0.000 | 0.852 | null |
| Pooled z-scored | 254 | 0.000 | 0.869 | null |

**Interpretation:** The universal UV-B → metabolite framing is wrong. The biochemically correct framing is: chalcone synthase (CHS) is the only enzyme whose UV-induction is conserved across plant taxa at the regulatory level. All other secondary metabolite pathways are too species-specific. Anthocyanins are convergent UV screens; monoterpene profiles are divergent chemotype signatures.

---

## 11. Data Integrity Rules

1. **Never fabricate values.** If no primary paper exists for a value, write `[NEEDS PRIMARY SOURCE]` or omit.
2. **Primary source required** for each `analytical_observations` entry. USDA FDC, Phenol-Explorer, "literature ranges" are not acceptable for analysis-facing fields.
3. **RSU-01 to RSU-66**: strict — values stripped unless author/year is in citation.
4. **RSU-67 to RSU-157**: existing values retained unless explicitly flagged as `[NEEDS PRIMARY SOURCE]` or qualitative-only.
5. **Migration script** at `src/migrate_schema.py` regenerates `analytical_observations` from any updated RSU file.

---

## 12. Paper Direction (post session 7, 2026-04-14)

**Target journal:** Food Chemistry or JAFC  
**Working title:** "Anthocyanins as Convergent UV-Screen Pigments: Evidence from a 157-Site Cross-Crop Metabolite Atlas"

**Core narrative:**
1. We built a 157-RSU cross-crop metabolite atlas (6 continents, any food)
2. We tested whether UV-B stress drives secondary metabolite accumulation universally across crops
3. Pooled signal is null — inter-species variance swamps the UV gradient
4. Anthocyanins are the exception: R²=0.72, p=0.032, n=6
5. Mechanistic explanation: chalcone synthase UV-induction is conserved at the CHS promoter level across all plant taxa — this is why anthocyanins work as a cross-species signal while monoterpene chemotypes don't
6. Implication: high-UV food environments (high altitude, low latitude) predictably produce more intensely pigmented fruits regardless of species identity

**What's needed before submission:**
- n≥10 anthocyanin RSUs (currently n=6; priority: Malbec altitude, bilberry Alps, elderberry altitude, red onion altitude)
- Verify and cite the CHS UV-induction mechanism (UVR8 → COP1 → MYB transcription factors → CHS)
- Notebook 13 updated with new anthocyanin RSUs and rerun
- Paper draft in `writing/terrametabolica_paper.tex`

---

## 13. Modeling Operations Permitted

| Operation | Status |
|-----------|--------|
| OLS regression: UV proxy → compound concentration within class | Primary analysis |
| Log-linear regression: temperature → curcuminoid | Finding 2 (ready) |
| UV proxy: `cos(|lat| × π/180) × (1 + altitude_m/2500)` | Standard across all RSUs |
| Z-score within compound class before pooling | Required for cross-class comparison |
| Natural experiment slope comparison (same study, same crop) | High value; compare across crop systems |

---

## 14. File Structure

```
TerraMetabolica/
├── CLAUDE.md                          — working instructions (detailed, always current)
├── TerraMetabolica.md                 — this file (conceptual framework)
├── README.md                          — project overview for GitHub
├── data/
│   ├── rsu/                           — RSU-01 through RSU-157 JSON files
│   ├── raw/fdc/                       — cached USDA FDC responses
│   └── metabolites/                   — analysis outputs: PNGs, CSVs
├── notebooks/
│   ├── 11_altitude_regression_atlas.ipynb   — within-crop OLS across all RSUs
│   ├── 12_multi_environment_discoveries.ipynb — altitude vs temperature vs precip
│   └── 13_cross_crop_uvb_analysis.ipynb     — cross-crop UV-B signal test
├── src/
│   ├── migrate_schema.py              — generates analytical_observations from RSU JSONs
│   ├── rsu_schema.py
│   └── rsu_loader.py
└── writing/
    ├── terrametabolica_paper.tex
    └── terrametabolica.bib
```

---

## 15. Version History

| Version | Date | Change |
|---------|------|--------|
| v0.1 | 2026-03 | Initial concept: latent flavor fields, inferred metabolite presence |
| v0.2 | 2026-04-13 | Strict empirical correction; USDA FDC/Phenol-Explorer as valid sources; within-crop altitude regression per food system |
| v0.3 | 2026-04-14 | **Major reframe.** Schema migration to `analytical_observations`. Cross-crop UV-B analysis replaces within-crop regression. Anthocyanin finding. USDA FDC/Phenol-Explorer stripped from RSU-01–66. Universal UV signal abandoned; compound-class-specific framing adopted. |
