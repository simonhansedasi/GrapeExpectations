# Cup-score kill-test — negative result, 2026-07-30

**Verdict: do not build the cup-score notebook.** Testing whether Hawaiian coffee cup scores carry an environmental (terroir) signal, the district effect is exactly zero after controlling for variety and processing, and the score's reliability ceiling leaves almost no room for any site variable to work with.

## What was tested

The proposal was to tie cup scores to the terrain/climate features, show the districts differ, then predict how warming changes them. Before geocoding 60-100 farms — the expensive step — the cheapest falsifying test was run: does the *coarsest possible* environmental contrast, Kona vs Ka'u, move the score at all? Those two districts differ 4-10x in annual rainfall with zero overlap. If that produces nothing, a within-district elevation gradient produces less.

## Data

Hawaii Coffee Association Statewide Cupping Competition, published results for 2019, 2021, 2022, 2023, 2024 (`parse.py` scrapes and normalises five different PDF layouts into `hca_scores.csv`). Archives also exist for 2009-2018 and 2025, not pulled.

365 rows total, 302 from Kona and Ka'u, 284 usable with both variety and processing recorded, spanning 91 distinct farms after name normalisation. Only scores >=80 are published.

| district | lots | farms | mean | sd |
|---|---|---|---|---|
| Kona | 179 | 63 | 83.51 | 1.89 |
| Ka'u | 105 | 29 | 83.13 | 1.45 |

## Results

Model is `score ~ district + variety + processing + year`, all dummies, with the interval bootstrapped over **farms** rather than lots since a farm enters many years and its lots are not independent.

| quantity | value |
|---|---|
| raw Ka'u - Kona | -0.381 points |
| adjusted for variety + processing + year | +0.018 points |
| 95% CI (farm bootstrap, 4,000 reps) | (-0.461, +0.573) |

The entire raw district gap is explained by what the two districts plant and how they process it. Nothing environmental remains.

For scale, the things that *do* move the score are farmer choices:

| factor | spread | detail |
|---|---|---|
| variety | 2.42 points | Typica 82.65 (n=135) to Geisha 85.06 (n=28) |
| processing | 1.55 points | honey 82.90 to natural 84.45 |
| district | 0.02 points | after controls |

## The ceiling result

Independent of any model, splitting score variance into stable farm identity vs lot-to-lot variation over the 57 farms with 2+ entries (266 lots, mean 4.7 lots/farm):

- between-farm variance 0.784
- within-farm (lot-to-lot) variance 2.271
- **intraclass correlation 0.26**

Three-quarters of score variance is which lot got entered that year — harvest weather, picking, milling, roast. A perfect site model could explain at most 26%, and that 26% includes management skill, mill quality and varietal choice. Terroir is a subset of a subset. There is not enough stable signal for an environmental variable to find.

## Limits of this kill

- **Truncation.** Only scores >=80 are published, so this is the top of the distribution and range restriction attenuates every effect. The correct claim is "no detectable effect among competition-grade lots," not "no effect anywhere."
- **Aggregate score.** Terroir could move specific attributes (acidity, body) while leaving the total flat. Attribute-level scores are not published.
- **Selection.** Entering is voluntary and costs money; entrants skew toward ambitious commercial farms.
- **Five years only.** 2009-2018 and 2025 archives exist and would roughly triple n, but would not change the ICC ceiling, which is the binding constraint.

None of these rescue the design. The expensive stage was geocoding, and it would have been spent chasing a fraction of 26% of the variance in a sample where the strongest available environmental contrast already reads zero.

## What is worth keeping

**Kona and Ka'u coffees score the same once variety and processing are accounted for**, despite Kona commanding a large price premium. That is a claim about what the premium buys, it is supported by 284 lots across 91 farms, and it needs no climate model. If any paper comes out of this data, it is that one.

## Reproduce

```
cd cup_scores/
python parse.py       # needs the 5 PDFs; see URLs in parse.py header
python killtest.py
```
