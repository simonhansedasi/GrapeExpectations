# What this project found, in plain language

Written 2026-07-30. This is a summary of the JavaScript_v2 analysis with no statistics jargon, meant to be read away from the code. Every number here comes from `paper_numbers.json` and is reproducible from the scripts in `ML/`.

## What the project is

There are 471 places on the Big Island of Hawaii where coffee is actually grown, mapped as cells on a 500-metre grid. 409 of them are in Kona and 62 are in Ka'u. The project asks a simple question about those places: as the climate warms, does the island keep having land where coffee can grow?

## The two things being measured

The analysis holds two pictures of the island side by side.

The first is **the ground**. Coffee farms sit on a particular kind of terrain: a certain steepness, a certain amount of local relief, a certain distance from the coast, on the flanks of the volcano between roughly 150 and 950 metres. That terrain is fixed. Warming does not move a hillside.

The second is **the temperature band**. Coffee grows well in a fairly narrow range of temperatures. On a volcano, temperature tracks elevation, so that band is a stripe running around the mountain. When the climate warms, the stripe slides uphill.

The land you can actually grow coffee on is the overlap of the two: ground of the right kind that also has the right temperature. The whole project is about what happens to that overlap as the stripe slides.

## What it found

**The overlap is about as large as it is ever going to get.** Sliding the temperature band in either direction makes the overlap smaller. Warming shrinks it. Cooling would shrink it too. There is no climate pathway, in any scenario tested, where there is more usable coffee land than there is now.

**Kona has already passed its best moment.** The island has warmed measurably over the period the data covers, about 0.31 degrees C per decade across the coffee belt, adding up to roughly 0.47 degrees C since the middle of the baseline period. Measured against the end of the actual observed record rather than the baseline average, Kona sits about 1.1 degrees C past the point where its overlap was largest. That result holds up when the uncertainty in the warming trend itself is accounted for.

**The overlap shrinks measurably from here.** Taking Kona and Ka'u together as one coffee-growing region, the usable land falls about 14 percent by 2035 and about 22 percent by 2045.

**The terrain constraint is what makes this interesting.** If you only look at temperature and ignore terrain, roughly 70 percent of the island appears to be *gaining* coffee suitability as it warms. That is the answer you would get from a climate model alone, and it is badly wrong. Once you require the land to also be the right kind of ground, about two-thirds of actual coffee country is on a declining path instead. The temperature-only picture overstates the good news by a factor of 40 to 50. That gap is the finding most worth publishing, because it is a mistake anyone doing this kind of work could make.

## How confident to be

The direction is solid. The size of the number is not.

The decline was re-tested under every setting the analysis has a choice about: how heavily elevation counts in defining the terrain, how the map is chopped up for the error bars, which of several distance measures is used, and about 320 combinations of threshold settings. The overlap shrinks in essentially all of them. It never grows.

But the *size* of the shrinkage moves a lot depending on those choices, from about 12 percent to about 38 percent by 2045. So the honest way to state it is "the usable land declines, by something in the range of 12 to 38 percent by 2045, depending on how the terrain is defined" rather than quoting a single figure. Any single figure would be a choice dressed up as a measurement.

## What the analysis cannot say

**It cannot compare Kona and Ka'u.** This is the important one, because it is what the project originally set out to do, and it is what keeps creeping back into the writing.

Kona and Ka'u are different places with different reputations, and the natural question is whether the same plant in two different settings faces two different futures. The data cannot answer that. Ka'u has 62 mapped cells. Every comparison between the districts comes back with an uncertainty range wide enough to contain both "Kona is much worse off" and "Ka'u is much worse off." That is true of their preferred temperature, their peak timing, their rate of decline, and the shape of their available ground. It stays true when the map is chopped finer, giving Ka'u twice as many independent pieces. It is a limit of the sample size, not a finding about coffee.

There is one exception worth noting honestly: the districts' point estimates all lean the same way, and two of the comparisons miss statistical significance by a hair. So it is quite possible a real difference exists. The analysis simply cannot see it, and saying "the districts are the same" would be as much of an overclaim as saying they differ.

**It cannot name a sharp elevation boundary.** The terrain does change character as you go above the farm belt, and that change is real and well demonstrated. But when the analysis is allowed to find the boundary on its own it lands anywhere between about 660 and 1330 metres. The transition is genuine but gradual. Earlier drafts quoted 950 metres as if it were a measured line; it is not.

## Why the paper kept breaking

This is worth writing down because it explains twenty-two rounds of revision better than any individual mistake does.

Each review round found something real. Each fix added another layer of machinery to account for it. The machinery is now more elaborate than 471 cells can support. The pattern was not carelessness, it was that the paper kept trying to say more than the data could carry: reviewers caught the overreach, the claim got trimmed, and the trim exposed the next overreach underneath. The district comparison is the clearest example, and it survived so long because it was the original motivation rather than a conclusion the analysis reached.

The way out is to decide the smallest true claim and stop, rather than to keep answering the next objection.

## What is actually left

Three things, only one of which is analysis.

| item | what it is | status |
|---|---|---|
| Lee et al. 2023 | Three separate numbers in the paper are credited to this source and none was checked against it. The crop value probably traces to USDA NASS instead. | Needs the actual paper read. No computation fixes it. |
| Kaua'i check | A test on a different island, run to show the method is not tuned to Kona. It was run against an older version of the terrain definition and never re-run. | Runnable, roughly an hour. |
| Supplement audit | A read-through for numbers left over from the superseded eight-feature version. | Reading, not computing. |

Everything else on the old checklist is closed. The manuscript files themselves are frozen and mid-edit; they should be rewritten from the current numbers rather than patched further.

## The decision in front of you

The analysis supports a small, clean, defensible paper: **usable coffee land on the Big Island is at its maximum today, declines under any warming, and the terrain constraint is what separates that conclusion from the much rosier one a climate model alone would give.** One region, three claims, no district comparison.

That paper can be written from what is already computed. The alternative is to keep the project shelved, which is also a legitimate choice given how much revision it has absorbed. What is not available is the paper the project originally wanted to write, about two districts diverging, because 62 cells will never support it.
