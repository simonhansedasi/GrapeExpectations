# TerraMetabolica — Citation Audit
**Date:** 2026-04-13  
**Scope:** All RSUs in the five main regressions (butter CLA n=7, coffee CGA n=6, coffee malic n=6, tea catechins n=9, apple malic n=5). Web search verification of every primary citation.

---

## VERDICT SUMMARY

| Regression | n | Status | Blocker? |
|---|---|---|---|
| Butter CLA | 7 | **CRITICAL** — 2 RSUs likely fabricated, 4 others have wrong journal/page | YES |
| Coffee CGA | 6 | **HIGH RISK** — primary source (5/6 RSUs) not confirmable | YES |
| Coffee malic | 6 | **HIGH RISK** — same Campa 2012 citation issue | YES |
| Apple malic | 5 | **MODERATE** — 2/5 sources unconfirmed | Review needed |
| Tea catechins | 9 | **MODERATE** — 5/9 confirmed, 3 issues | Review needed |

---

## 1. BUTTER CLA — CRITICAL

Paper table values (g/100g fat):

| RSU | Alt (m) | Value | Primary Citation | Status |
|---|---|---|---|---|
| RSU-46 NZ Waikato | 50 | 3.00 | MacGibbon & Taylor 2006, *Advanced Dairy Chemistry* Vol 2 Ch 1; Parodi 1997 *Aust J Dairy Tech* 52:92 | Plausible — book chapter, not verifiable online but credible |
| RSU-37 Irish Atlantic | 100 | 2.75 | Collomb et al. 2002 *J Dairy Sci* 85:1239; Leiber 2005 JDS 88:1316 | **Collomb JDS 85:1239 — NOT FOUND in any search.** Leiber JDS 88:1316 — GHOST (wrong page, wrong title, paper unlocatable) |
| RSU-51 Scottish Highlands | 350 | 3.50 | Lock & Bauman 2004 *J Dairy Sci* 87:2283; Collomb 2002 *J Dairy Res* 69:598 | **Lock & Bauman WRONG JOURNAL** — paper is in *Lipids* 39:1197, not JDS. Collomb JDR 69:598 — paper with matching title found at Cambridge Core but page number unverified |
| RSU-52 French Pyrenees | 700 | 4.00 | Ferlay et al. 2006 *J Dairy Sci* 89:2429; Chilliard et al. 2007 *J Dairy Sci* 90:4079 | **Ferlay 2006 WRONG PAGES** — found in JDS 89 but at pages 4026–4041. Chilliard 2007 — not confirmed at JDS 90:4079; a related Chilliard paper found in *Eur J Lipid Sci Tech* (2007), not JDS |
| RSU-53 Swiss Jura Pre-Alps | 900 | 3.90 | Leiber 2005 *J Dairy Sci* 88:**1316** | **GHOST CITATION.** Page should be 1816. Bib entry `leiber2005b` has different title from JSON citation. Paper unlocatable in any database. Value 3.90 is not derivable from the Leiber Lipids 40:191 paper (which shows CLA *decreasing* at alpine, c9t11 only = ~1.3–1.7 g/100g FAME). Renna 2010 (verified) shows Swiss pasture at ~643m = 1.5 g/100g total CLA — RSU-53 at 900m claiming 3.90 is 2.6× higher, physically implausible given the Renna baseline. |
| RSU-36 Alpine | 1200 | 4.25 | Leiber 2005 *J Dairy Sci* 88:**1316**; Collomb 2002 *J Dairy Sci* 85:1239 | **GHOST CITATION** — same issues as RSU-53. Collomb JDS 85:1239 also unlocatable. Value 4.25 likely fabricated. |
| RSU-42 Himalayan/yak | 3800 | 5.00 | Jia et al. 2014 *J Dairy Sci* 97:3402 | **NOT CONFIRMED.** No paper found at JDS 97:3402 specifically for Jia 2014 yak butter CLA. A 2011 Liu et al. JDS paper on yak fatty acids exists. Yak CLA being high is biologically plausible but specific citation unverifiable. |

### Butter: verified papers in hand
- **Renna et al. 2010** (*J Sci Food Agric* 90:1256): Swiss lowland summer pasture (~643m) with concentrate supplement. Total CLA = **1.515 g/100g fat**. This verified measurement is inconsistent with RSU-53 (3.90) and RSU-36 (4.25) claims for only 257–557m higher.
- **Leiber et al. 2005** (*Lipids* 40:191): Experimental transition study. C9t11 CLA: lowland pasture 1.705, alpine pasture 1.340 g/100g FAME — CLA *decreases* at alpine due to energy deficit. Not a steady-state altitude transect. Not usable for regression.

### Butter: what's needed
- Verified steady-state altitude comparison of total CLA g/100g fat across the actual RSU altitudes (50–3800m)
- The Collomb *Int Dairy J* 12:649 (Swiss altitude) was ruled out earlier: c9t11 only + year-round barn system
- Collomb *J Dairy Res* 69:598 (lowlands/highlands): paper title confirmed at Cambridge Core, appears real — Simon needs full text to verify CLA values and page numbers
- If RSU-53 and RSU-36 values cannot be sourced to a verified primary, they must be removed → butter regression becomes n=5 (RSU-46, RSU-37, RSU-51, RSU-52, RSU-42)

---

## 2. COFFEE CGA — HIGH RISK

Paper table: RSU-47 (1100m), RSU-48 (1500m), RSU-18 (1600m), RSU-27 (1800m), RSU-17 (2200m), RSU-54 (1980m)

| Citation | RSUs using it | Status |
|---|---|---|
| Campa et al. 2012 *J Agric Food Chem* 60:3252 | RSU-17, 18, 27, 47, 48 (5/6) | **NOT CONFIRMED.** Extensive searching failed to find a Campa 2012 JAFC paper at vol 60 p 3252. Only confirmed Campa 2012 paper: PAL genes in *Coffea canephora* (*Planta* 236:313). Known Campa coffee CGA papers are from 2005 (*Food Chemistry*) and 2008 (*Academia.edu*). **Possible ghost citation.** |
| Gallardo-Ignacio et al. 2023 *Molecules* 28(12):4685 | RSU-54 | ✅ CONFIRMED at MDPI. CGA ~55 mg/g green beans, Bourbon/Oro Azteca, Guerrero highlands. |
| Lingle 2011 *SCAA Coffee Brewing Handbook* | multiple | Plausible reference work but not a primary analytical source for CGA values |

### Coffee: what's needed
- Find the actual primary source for CGA values in RSU-17/18/27/47/48. If Campa 2012 JAFC is a ghost, the correct citation may be Campa et al. (2005) *Food Chemistry* 93:329 (chlorogenic acids in wild Coffea) or a different year/volume/page. Actual measured CGA values for Ethiopian, Colombian, Kenyan, Jamaican, Torajan coffees need a verifiable primary source.
- Check paper bib file entry for `campa2012` to see what's there.

---

## 3. COFFEE MALIC ACID — HIGH RISK

Same n=6 RSUs, same Campa 2012 citation problem. Additionally, the paper reports n=6 at one point (table) and n=5 at another (LOOCV table, supplement). This inconsistency should be resolved.

---

## 4. APPLE MALIC ACID — MODERATE (n=5, ex RSU-04)

RSUs in regression: RSU-13, RSU-14, RSU-49, RSU-50, RSU-55

| RSU | Alt | Value (g/100g) | Citation | Status |
|---|---|---|---|---|
| RSU-13 Shanxi Yuncheng | 600m | 0.22–0.28 | Zhao/Li et al. 2021 *Foods* 10(12):2950 | ✅ CONFIRMED (PMC8701241) |
| RSU-14 Shanxi Linfen | 1050m | 0.48–0.53 | Same | ✅ CONFIRMED |
| RSU-55 Shanxi Jinzhong | 850m | 0.43–0.47 | Same | ✅ CONFIRMED |
| RSU-49 Chilean Maule | 800m | 0.38–0.50 | Vial et al. 2019 *Chilean J Agric Res* 79(2) | **NOT CONFIRMED.** No paper found in any search. |
| RSU-50 Turkish Isparta | 1100m | 0.55–0.70 | Özturk et al. 2015 *Turkish J Agric For* 39(4):549 | **NOT CONFIRMED.** No paper found. Journal exists but specific paper not located. |

### Apple: note
RSU-04 (Western Europe, 100m) is excluded from the regression — consistent with "maritime climate outlier" exclusion criterion. RSU-04 cites Zhao 2021 but its malic value (0.30–0.50) is described as based on "general apple chemistry literature" — the Zhao 2021 citation is misleading since that paper is for Shanxi, not Western Europe.

---

## 5. TEA CATECHINS — MODERATE (n=9)

Regression RSUs (excluding RSU-60 interpolated, RSU-59 excluded): RSU-62, RSU-27, RSU-63, RSU-56, RSU-61, RSU-20, RSU-64, RSU-65, RSU-58

| RSU | Alt | Value (g/100g DW) | Citation | Status |
|---|---|---|---|---|
| RSU-62 Hangzhou Longjing | 100m | 13.99 | Zhao et al. 2014 *Sci World J* 2014:863984 (PMC4163330) | ✅ CONFIRMED — paper exists (galloyl catechins in Chinese teas). **But: RSU-62 JSON has empty `data_sources` array**. Also: paper covers multiple tea types 4.34–24.27%; need to verify 13.99 is the specific Longjing sample, not a pan-fired green tea average. |
| RSU-63 Kangra Valley India | 1290m | 16.97 | Sourabh et al. 2013 *J Nat Prod Plant Resour* 3(1):18 | **NOT CONFIRMED.** Journal name seems non-standard. Citation incomplete in JSON (no page or DOI). |
| RSU-56 Da Lat Vietnam | 1500m | 14.25 | Nguyen et al. 2023 *Antioxidants* 12(5):1003 (PMC10142074) | ✅ CONFIRMED. Value is midpoint of 11.5–17.0 range for cultivated Da Lat teas. |
| RSU-61 Yunnan raw pu-erh | 1750m | 16.25 | Lv et al. 2013 *J Food Sci* 78(8):C1402 | **INCLUSION CRITERIA CONCERN.** Pu-erh (even raw/maocha) is explicitly excluded by inclusion criteria ("oolong, pu-erh, matcha/gyokuro excluded"). Raw maocha is unoxidised but is still classified as pu-erh material. Additionally, the Lv 2013 paper found by search appears to be about pile-fermented pu-erh metabolomics — mismatch with RSU-61's "raw maocha" description. |
| RSU-27 Kenyan Highlands | 1800m | 17.50 | Wachira et al. 2014 *AJPS* 5(2):180 | **MISMATCH.** RSU-27 JSON tea food entry cites Wachira 2002 *Euphytica* 125:69 and shows "theaflavins+thearubigins" as the polyphenol — CTC black tea, not green/catechin. Wachira 2014 catechin paper is cited for RSU-58, not RSU-27. Unclear where the 17.50 catechin value comes from for RSU-27. |
| RSU-20 Darjeeling | 2000m | 20.0 | Kim et al. 2011 *Food Chem* 129:486 | **NOT CONFIRMED** at those exact coordinates. Paper plausibly exists (Darjeeling/Assam catechin altitude gradient) but could not be verified in searches. |
| RSU-64 Timbilil Kenya | 2020m | 16.2 | Mutuku 2016 *AJPS* 7:855–869 | ✅ CONFIRMED. SCIRP paper found. Value 16.2% matches reported Timbilil mean. |
| RSU-65 Kangaita Kenya | 2180m | 18.7 | Mutuku 2016 *AJPS* 7:855–869 | ✅ CONFIRMED. Value 18.7% matches reported Kangaita mean. |
| RSU-58 Kericho Kenya | 2200m | 17.7 | Wachira et al. 2014 *AJPS* 5(2):180–191 | ✅ CONFIRMED. Paper is real at SCIRP AJPS. Value 16.0–19.4 range encompasses 17.7. |

### Tea: additional issues
- **RSU-21 Assam (100m)**: Used as the Kim 2011 low-altitude anchor (catechin 12.0–16.0). RSU-21 is cited in the paper (line 383) as "within-study altitude anchor" with RSU-20. Both use the same unconfirmed Kim 2011 paper. If Kim 2011 is wrong, the Darjeeling/Assam gradient disappears.
- **RSU-57 Suoi Giang**: Cited from same Nguyen 2023 paper as RSU-56, but RSU-57 is described as "wild/ancient-tree" category. Wild tea may be a different cultivar type — check inclusion criteria compliance.

---

## 6. ADDITIONAL STRUCTURAL ISSUES

### Coffee n=6 vs n=5 inconsistency
Paper Table S3/regression table shows coffee malic acid n=6 (line 935) but LOOCV table shows n=5 (line 972). One of these is wrong. This needs resolution before submission.

### RSU-27 dual-use problem
RSU-27 (Kenyan Highlands, 1800m) appears in both the coffee CGA regression and the tea catechin regression. Coffee and tea are different foods from different samples — this is legitimate. But the tea catechin value for RSU-27 appears to be sourced incorrectly (CTC black tea theaflavins vs catechins from green tea).

### RSU-66 Swiss valley (pending)
Still placeholder [NEEDS PRIMARY SOURCE]. Cannot be added to butter regression until CLA value extracted from a verified paper. The Leiber J Dairy Sci 88:1816 paper has not been found — if it's a ghost, RSU-66 loses its natural-experiment framing entirely.

---

## 7. PAPERS THAT NEED DOWNLOADING (Priority Order)

1. **Collomb et al. 2002** *J Dairy Res* 69:598 — "Conjugated linoleic acid and trans fatty acid composition of cows' milk fat produced in lowlands and highlands" (Cambridge Core URL confirmed, paper real, page numbers unverified). This could partially rescue RSU-51.
2. **Kim et al. 2011** *Food Chemistry* 129:486 — Darjeeling/Assam catechin gradient. Two RSUs (RSU-20, RSU-21) depend on this.
3. **Campa et al. (correct year/journal)** — need to identify what the actual primary source is for coffee CGA across origins. Check bib entry `campa2012`. If not at JAFC 60:3252, locate the correct coordinates.
4. **Jia et al. 2014** *J Dairy Sci* 97:3402 — yak butter CLA. Search found yak milk fatty acid papers but not this specific one.
5. **Vial et al. 2019** *Chilean J Agric Res* 79(2) — apple malic RSU-49.
6. **Özturk et al. 2015** *Turkish J Agric For* 39(4):549 — apple malic RSU-50.

---

## 8. PAPERS CONFIRMED REAL (can remain as-is)

| Citation | RSU(s) | Notes |
|---|---|---|
| Gallardo-Ignacio et al. 2023 *Molecules* 28:4685 | RSU-54 | ✅ MDPI confirmed |
| Zhao/Li et al. 2021 *Foods* 10:2950 | RSU-13, 14, 55 | ✅ PMC8701241 |
| Wachira et al. 2014 *AJPS* 5:180 | RSU-58 | ✅ SCIRP confirmed |
| Mutuku 2016 *AJPS* 7:855 | RSU-64, 65 | ✅ Values match exactly |
| Nguyen et al. 2023 *Antioxidants* 12:1003 | RSU-56 | ✅ PMC10142074 |
| Zhao et al. 2014 *Sci World J* 863984 | RSU-62 | ✅ Paper real; verify Longjing value specifically |
| Leiber et al. 2005 *Lipids* 40:191 | (background) | ✅ PDF in hand; not usable for regression |

---

## 9. CONFIRMED WRONG/GHOST CITATIONS

| Citation as written | Correct status |
|---|---|
| Leiber 2005 *J Dairy Sci* 88:**1316** | Page typo (should be 1816). Paper title confirmed in bib but unlocatable. RSU-53 and RSU-36 values not derivable from any real Leiber 2005 paper. |
| Lock & Bauman 2004 *J Dairy Sci* 87:2283 | Wrong journal. Real paper: *Lipids* 39:1197–1206 (2004). RSU-51 corrected. |
| Ferlay 2006 *J Dairy Sci* 89:**2429** | Wrong pages. Ferlay 2006 JDS paper confirmed at 89:4026–4041. RSU-52 corrected. |
| **Campa et al. 2012 *J Agric Food Chem* 60:3252** | **COMPOUND GHOST — multiple errors:** (1) The real paper with same authors (Doulbeau, Dussert, Hamon, Noirot) and similar title is *Food Chemistry* 93:135–139 (2005) — wrong journal, wrong year, wrong pages. (2) That 2005 paper covers WILD Coffea species, not altitude-stratified cultivated arabica. No altitude-specific CGA data for Typica/Bourbon at multiple origins exists in this paper. (3) A different paper "Chlorogenic acids: diversity in green beans of wild coffee species" (Campa et al. 2008, *Advances in Plant Physiology* 10:421–437) has Arabica CGA data but no altitude stratification. **Conclusion: no real Campa paper provides the origin × altitude CGA gradient cited in TerraMetabolica.** |
| **Collomb 2002 *J Dairy Res* 69:598** | **THREE ERRORS.** Real paper: Collomb et al. (2001) *J Dairy Res* **68**:519–523, DOI 10.1017/S0022029901004885. Wrong year (2001 not 2002), wrong volume (68 not 69), wrong pages (519–523 not 598). Paper IS confirmed real (Wikidata, Cambridge Core). A separate Collomb paper in *Int Dairy J* 12:649–659 (2002) reports the 3-zone Swiss altitude data (600–650m / 900–1210m / 1275–2120m). |
| **Kim 2011 *Food Chem* 129:486** | **NOT CONFIRMED.** The confirmed Kim et al. 2011 *Food Chemistry* 129 paper is at pages 1331–1342 ("Changes in antioxidant phytochemicals and volatile composition of Camellia sinensis by oxidation during tea fermentation") — a different topic (tea oxidation, not altitude gradient). Page 486 citation not found. RSU-20 and RSU-21 tea catechin values have no verified source. |

---

## 9b. NEW LITERATURE FINDINGS ON COFFEE CGA × ALTITUDE

Three independent studies show CGA **decreases** with altitude in Ethiopian arabica:
- **Worku et al. 2018** (*Food Res Int* 105:278): CGA declines 1.23 g/kg per 100m; 10 sites at 1150–1820m asl
- **Girma et al. 2020** (*J Chem* 2020:3904761): r = −0.917 (green bean 5-CQA vs altitude); Ethiopian varieties 74110/7454/7440/74112 at 1100–1960m; values: Teppi 1100–1200m = 33.2 mg/g (3320 mg/100g), Jimma 1750m = 33.2 mg/g, Gera 1940–1960m = 31.5 mg/g
- **Tolessa et al. 2017** (*JSFA* doi:10.1002/jsfa.8114; already in paper's Discussion): CGA highest at mid-elevation

**Important caveat:** All three studies are within Ethiopia (single-origin gradient). TerraMetabolica claims a cross-origin altitude effect (Toraja/Jamaica/Colombia/Kenya/Mexico/Ethiopia). These within-origin studies use Ethiopian breeding lines (74xx), not Typica/Bourbon — so they are excluded by inclusion criteria. The cross-origin regression direction may be mechanistically distinct from the within-origin pattern.

**Single confirmed cross-origin data point:** RSU-54 Mexico (Bourbon, 1980m) = 5575 mg/100g DW (Gallardo-Ignacio 2023, MDPI Molecules, confirmed). Typical arabica range is 3500–7500 mg/100g.

**Action:** The coffee CGA regression needs verified primary HPLC data for Ethiopia, Colombia, Jamaica, Kenya, and Toraja at their specific altitudes. No source for these currently exists in the RSU files. This is a full literature rebuilding task, not a citation correction task.

---

*Audit conducted 2026-04-13 by Claude Sonnet 4.6 via web search verification. PDFs confirmed: Renna 2010 (Swiss pasture CLA), Leiber 2005 Lipids (n-3 fatty acids), Leiber 2004 Animal Science (nitrogen balance, no CLA data). Extended search 2026-04-13 session 2: Campa ghost confirmed; Collomb J Dairy Res correct citation found; Kim 2011 page 486 confirmed nonexistent.*

---

## 10. POST-RECONSTRUCTION STATUS (2026-04-13)

### Changes made to RSU JSON files:
- **RSU-17, 18, 47, 48**: CGA (polyphenol_content) cleared — Campa 2012 JAFC ghost removed from data_sources
- **RSU-27**: Coffee CGA cleared (Lingle handbook not valid CGA source); tea polyphenol flagged as WRONG METABOLITE CLASS (theaflavins ≠ catechins)
- **RSU-36**: CLA cleared — Leiber ghost removed; remaining Collomb JDS 85:1239 flagged as UNVERIFIED
- **RSU-37**: CLA cleared — both ghost citations removed
- **RSU-53**: CLA cleared — ghost citation removed
- **RSU-51**: Lock & Bauman citation corrected to Lipids 39:1197 (was JDS 87:2283)
- **RSU-52**: Ferlay page corrected to 4026-4041 (was 2429); Chilliard 2007 flagged as UNVERIFIED journal
- **RSU-42**: CLA value flagged as PROVISIONAL (Jia 2014 unconfirmed)
- **RSU-61**: Pu-erh catechin value flagged — inclusion criteria violation (pu-erh excluded)
- **RSU-62**: data_sources populated with Zhao et al. 2014 Sci World J 863984
- **RSU-63**: catechin value cleared — Sourabh 2013 incomplete/unverified
- **RSU-64, 65**: data_sources populated with Mutuku et al. 2016 AJPS 7:855
- **RSU-20, 21**: Kim 2011 flagged as PROVISIONAL (unconfirmed in search); **now confirmed: Kim 2011 Food Chem 129 real paper is at pages 1331–1342 (tea oxidation), not page 486. RSU-20 and RSU-21 CGA values have NO verified source.**
- **RSU-49**: Apple malic cleared (Vial 2019 not found); chicha malic cleared
- **RSU-50**: Apple malic cleared (Özturk 2015 not found)
- **RSU-66**: Leiber ghost removed from data_sources
- **RSU-13, 14, 16, 28, 39, 47**: Non-regression unsourced polyphenol values flagged

### Regression status after reconstruction:

| Regression | Before | After | Action needed |
|---|---|---|---|
| Coffee CGA | n=6, r²=0.874 | **n=1** (RSU-54 only) | Campa 2012 JAFC confirmed as compound ghost; no real paper provides altitude-stratified arabica CGA; need full literature rebuild |
| Coffee malic | n=5 (or 6), r²=0.921 | **n=5 PROVISIONAL** (Lingle 2011 handbook) | Verify Lingle 2011 as acceptable primary source OR find HPLC papers for each origin |
| Butter CLA | n=7, r²=0.887-0.986 | **n=3 confirmed** (RSU-46, 51, 52) + n=1 provisional (RSU-42) | Collomb J Dairy Res is real (68:519–523, 2001, not 69:598); Int Dairy J 12:649 (2002) has 3-zone Swiss altitude data — check if summer pasture meets inclusion criteria. Find Irish butter CLA source. |
| Tea catechins | n=9, r²=0.490 | **n=5 confirmed** + **RSU-20 now UNCONFIRMED** (Kim 2011 page 486 nonexistent) = **n=5 confirmed** | Kim 2011 confirmed wrong — need Darjeeling/Assam altitude catechin source. RSU-27 still needs Kenya green tea catechin. |
| Apple malic | n=5, r²=0.912 | **n=3 confirmed** (RSU-13, 14, 55 all Zhao 2021) | Find apple malic for Maule Chile (RSU-49) and Isparta Turkey (RSU-50) |

### Priority reconstruction targets:
1. **Coffee CGA** (regression collapsed — Campa ghost confirmed): Need HPLC CGA data for Ethiopia ≥1800m, Colombia ~1600m, Jamaica ~1500m, Kenya ~1800m, Toraja ~1100m from Typica/Bourbon cultivars. No existing RSU source is valid. Note: Campa et al. (2005) *Food Chemistry* 93:135-139 (DOI 10.1016/j.foodchem.2004.10.015) is the real paper with this author group — but it covers WILD Coffea species, not cultivated arabica altitude gradient. Does not help the regression.
2. **Tea catechins** (RSU-20/21): Kim 2011 Food Chem 129:486 confirmed nonexistent; real Kim 2011 Food Chem 129 paper is about tea oxidation (pages 1331–1342). Darjeeling first flush is lightly oxidized — may fail inclusion criteria. RSU-21 Assam CTC black tea was never valid regardless. Need a green tea catechin HPLC paper for India/Nepal altitude gradient.
3. **Butter CLA**: Collomb J Dairy Res 68:519–523 (2001) is real — get full text via library (DOI 10.1017/S0022029901004885). Also assess Collomb Int Dairy J 12:649 (2002) 3-zone Swiss altitude data for total CLA vs c9t11 and feeding system. Find Irish grass-fed butter CLA source.
4. **Apple malic — Isparta RSU-50**: **CANDIDATE PAPER FOUND:** Ergün (2021) "Determination of Biochemical Contents of Five Apple Cultivars (Amasya, Braeburn, Golden Delicious, Granny Smith, and Starking)," *J Food Quality* 2021:9916694, DOI 10.1155/2021/9916694 — from Isparta, Turkey, HPLC, includes Golden Delicious and Starking. Get full text to confirm: (1) fresh weight malic acid value for Golden Delicious, (2) Isparta altitude stated (~1050m). If confirmed, RSU-50 can be restored.
5. **Apple malic — Maule Chile RSU-49**: No candidate found. May need to search Chilean journal databases or INIA (Instituto de Investigaciones Agropecuarias) repository.
6. **Coffee malic**: Lingle 2011 SCAA *Coffee Cupper's Handbook* is NOT an HPLC primary source per inclusion criteria ("dried green bean; HPLC ~320nm; g/100g dry weight"). Coffee malic acid regression is as compromised as CGA regression — needs HPLC multi-origin primary paper.
7. **Kenya green tea catechins**: Mose et al. 2018 (*Int J Tea Science* 14(1):49-55) covers Kenya agro-ecological zones (Kisii/Murang'a/Meru) but appears to measure catechins from black tea processing (not unoxidized green tea). Not directly usable for inclusion-criteria-compliant tea catechin regression. May work if green leaf catechin values are reported separately from black tea parameters.

---

## Section 11: Crop-focused rebuild search results (2026-04-13, session 2)

Systematic web search was conducted crop-by-crop to find new verified papers. No new RSUs were built from this search — all new candidates require library access.

### Coffee CGA
After >20 searches and 10+ paper fetches, **no additional verified Typica/Bourbon green bean HPLC papers found**. The regression cannot be rebuilt from open-access literature. Root causes:
1. Multi-altitude within-origin studies (Worku 2018, Girma 2020, Urugo 2024, Hu 2024) use excluded varieties
2. Cross-origin Typica papers use roasted beans (Rusinek et al. 2025, Sci Rep, DOI 10.1038/s41598-025-16126-x): Typica at Peru 1600m / Costa Rica 1540m / Guatemala 1650m / Ethiopia 2065m → roasted CGA 9.6–13.8 mg/g; confirmed new excluded paper
3. All accessible Typica/Bourbon single-origin green bean papers are at single altitudes only

**New library priority: Joët et al. 2010** (*Food Chemistry* 118:693–701, DOI 10.1016/j.foodchem.2009.05.048): green arabica beans, altitude effects confirmed. If variety is Typica/Bourbon-lineage, could restore coffee CGA regression. PAYWALLED.

**New excluded paper: Rusinek et al. 2025** (Sci Rep, DOI 10.1038/s41598-025-16126-x): confirms Typica altitude × CGA pattern but roasted beans only. Useful Discussion context.

### Apple malic — citation error fixed
- **RSU-13 and RSU-14** incorrectly cited "Zhao et al. 2021 Foods 10(12):2950." Correct first author confirmed via PMC8701241: **Yajing Li** → corrected to "Li et al. 2021" in both RSU files and in bib (li2021foods added).
- **Ergün 2021** (DOI 10.1155/2021/9916694) confirmed as SINGLE-LOCATION study (Isparta, Turkey). Not a multi-altitude study. Can provide one altitude data point (Isparta ~1030m) for RSU-50 only if fresh-weight malic acid values are accessible — currently PAYWALLED.

### Tea catechins
No new confirmed RSUs found. Key papers assessed:
- **Shen et al. 2018** (*Food Chemistry*, DOI 10.1016/j.foodchem.2018.04.094): Yunnan elevation metabolomics — non-targeted GC-GC/MS + LC → excluded
- **Kottawa-Arachchi et al. 2022** (Food Chem Advances, DOI 10.1016/j.focha.2022.100108): HPLC catechins in 131 Sri Lanka accessions → altitude zone data not confirmed, PAYWALLED
- Mose 2018 Kenya paper confirmed as black tea parameters, NOT green leaf catechins → excluded

### Butter CLA
No new open-access papers found. Library priorities unchanged.

### Note on RSU-55
RSU-55 (Shanxi Jinzhong, 850m, Golden Delicious, 0.43-0.47 g/100g FW) was confirmed as correctly sourced from Li et al. 2021 (already had correct author). This RSU correctly fills the 600–1050m gap in the Shanxi apple gradient.
