#!/usr/bin/env python3
"""
Verify the manuscript's numbers against the pipeline.
`paper_numbers.json` is emitted by ML/05_forward_projection.ipynb (cell E8) and is
the single source of truth. This script checks each registered claim against it.
Motivation: across successive revisions the .tex was updated by hand while the
pipeline moved underneath it, and derived statistics (t, p, CI, contraction
percentages, sensitivity ranges) drifted out of agreement with the mu/sigma they
are computed from -- in several places by a full sample-size revision. Every
number quoted in the paper should be checkable here.
Usage:
    python check_numbers.py            # report
    python check_numbers.py --strict   # exit 1 on any mismatch (for pre-submission)
"""
import json
import os
import re
import sys
HERE = os.path.dirname(os.path.abspath(__file__))
NUM = json.load(open(os.path.join(HERE, "paper_numbers.json")))
TEX = open(os.path.join(HERE, "JavaScript.tex")).read()
SUPP = open(os.path.join(HERE, "JavaScript_supp.tex")).read()
# Each claim: (label, regex with one capture group, canonical key, tolerance, source)
# Tolerance is absolute, in the units the paper prints.
CLAIMS = [
    # ── study area / thermal envelope (unaffected by the screen correction) ──
    ("mu Kona",              r"\\mu_\{\\text\{Kona\}\}\s*=\s*([0-9.]+)",        "mu_kona",       0.005, "tex"),
    ("mu Ka'u",              r"\\mu_\{\\text\{Ka'u\}\}\s*=\s*([0-9.]+)",        "mu_kau",        0.005, "tex"),
    ("sigma Kona",           r"\\sigma_\{\\text\{Kona\}\}\s*=\s*([0-9.]+)",     "sigma_kona",    0.005, "tex"),
    ("sigma Ka'u",           r"\\sigma_\{\\text\{Ka'u\}\}\s*=\s*([0-9.]+)",     "sigma_kau",     0.005, "tex"),
    ("n farm cells",         r"([0-9]+) labelled farm cells",                   "n_farm_cells",  0.5,   "tex"),
    ("Welch t",              r"Welch \$t = ([\-0-9.]+)\$",                      "mu_diff_t",     0.02,  "tex"),
    ("Welch p",              r"\$p = ([0-9.]+)\$",                              "mu_diff_p",     0.005, "tex"),
    ("R2 temp~elev belt",    r"the fit is \$R\^2 = ([0-9.]+)\$",                 "R2_belt",       0.001, "tex"),
    ("resid SD belt",        r"residual SD \$([0-9.]+)\$\\,\\textdegree C\.",        "resid_sd_belt", 0.002, "tex"),
    ("lapse belt",           r"slope \$-([0-9.]+)\$\\,\\textdegree C\\,km",        "lapse_belt",    0.01,  "tex"),
    ("R2 island-wide",       r"climatology gives \$R\^2 = ([0-9.]+)\$",          "R2_island",     0.005, "tex"),
    ("farmable pct",         r"Of island land, ([0-9.]+)\\% satisfies both",    "pct_farmable",  0.06,  "tex"),
    # ── footprint, corrected 7-feature screen ──
    ("pct Kona-like",        r"Kona ([0-9.]+)\\%, Ka\\okina u",                  "pct_kona_like", 0.06,  "tex"),
    ("pct Ka'u-like",        r"Ka\\okina u ([0-9.]+)\\%\); the remaining",       "pct_kau_like",  0.06,  "tex"),
    ("pct neither",          r"the remaining ([0-9.]+)\\% carries",             "pct_neither",   0.06,  "tex"),
    ("combined footprint",   r"covers ([0-9.]+)\\% of island land",             "pct_combined_footprint", 0.06, "tex"),
    ("maha footprint Ka'u",  r"Ka\\okina u footprint \(([0-9.]+) vs",            "pct_kau_like_maha", 0.06, "tex"),
    # ── THE PEAK: the paper's central claim, stated in abstract, S3.2 and Conclusions ──
    ("peak Kona (abstract)", r"peaks at \$-([0-9.]+)\$\\,\\textdegree C for Kona", "Fpeak_kona", 0.02, "tex"),
    ("peak Ka'u (abstract)", r"and \$\+([0-9.]+)\$\\,\\textdegree C for Ka\\okina u \(", "Fpeak_kau", 0.02, "tex"),
    ("peak Ka'u (results)",  r"and Ka\\okina u's at \$\+([0-9.]+)\$",           "Fpeak_kau",     0.03,  "tex"),
    ("peak Kona (concl)",    r"peaked \$([0-9.]+)\$\\,\\textdegree C ago",         "Fpeak_kona_recentred", 0.02, "tex"),
    ("asymmetry Kona",       r"is ([0-9.]+) for Kona, meaning",                  "Fasym_kona",    0.02,  "tex"),
    ("asymmetry Ka'u",       r"Ka\\okina u's ratio is ([0-9.]+)",                "Fasym_kau",     0.02,  "tex"),
    ("peak no-elev Kona",    r"Kona \$-([0-9.]+)\$\\,\\textdegree C, Ka",           "Fpeak_noelev_kona", 0.03, "tex"),
    ("peak no-elev Ka'u",    r"Ka\\okina u \$\+([0-9.]+)\$\\,\\textdegree C\)",     "Fpeak_noelev_kau",  0.03, "tex"),
    # ── decline from present: headline, duplicated in abstract and Conclusions ──
    ("F today Kona",         r"from (1\{,\}[0-9]+) to 1\{,\}215",                "Fr_kona_present", 2.0, "tex"),
    ("F 2045 Kona",          r"from 1\{,\}651 to (1\{,\}[0-9]+)",                "Fr_kona_2045",    2.0, "tex"),
    ("F today Ka'u",         r"falls from (1\{,\}[0-9]+) to 1\{,\}502",          "Fr_kau_present",  2.0, "tex"),
    ("F 2045 Ka'u",          r"from 1\{,\}836 to (1\{,\}[0-9]+)",                "Fr_kau_2045",     2.0, "tex"),
    ("drop 2045 Kona",       r"a decline of \\textbf\{([0-9.]+)\\%\}",          "Fdrop_present_kona_2045", 0.06, "tex"),
    ("drop 2045 Ka'u",       r"or \\textbf\{([0-9.]+)\\%\}",                    "Fdrop_present_kau_2045",  0.06, "tex"),
    ("drop 2035 Kona",       r"the declines are ([0-9.]+)\\% and",              "Fdrop_present_kona_2035", 0.06, "tex"),
    ("drop 2035 Ka'u",       r"the declines are [0-9.]+\\% and ([0-9.]+)\\%",   "Fdrop_present_kau_2035",  0.06, "tex"),
    ("off-peak 2045 Kona",   r"the 2045 losses are ([0-9.]+)\\% and",           "Fdrop_peak_to_2045_kona", 0.06, "tex"),
    ("off-peak 2045 Ka'u",   r"the 2045 losses are [0-9.]+\\% and ([0-9.]+)\\%", "Fdrop_peak_to_2045_kau", 0.06, "tex"),
    ("ABS drop Kona",        r"falls ([0-9.]+)\\% \(Kona\) and",                 "Fdrop_present_kona_2045", 0.06, "tex"),
    ("ABS drop Ka'u",        r"falls [0-9.]+\\% \(Kona\) and ([0-9.]+)\\%",     "Fdrop_present_kau_2045",  0.06, "tex"),
    ("CONCL drop Kona",      r"down ([0-9.]+)\\% and [0-9.]+\\% from the climatological", "Fdrop_present_kona_2045", 0.06, "tex"),
    ("CONCL drop Ka'u",      r"down [0-9.]+\\% and ([0-9.]+)\\% from the climatological", "Fdrop_present_kau_2045", 0.06, "tex"),
    # ── inter-horizon contraction, against static inputs ──
    ("Cr change Kona",       r"thermal set moves \$-([0-9.]+)\\%\$ and",        "Crchange_kona", 0.06, "tex"),
    ("Cr change Ka'u",       r"thermal set moves \$-[0-9.]+\\%\$ and \$\+([0-9.]+)\\%\$", "Crchange_kau", 0.06, "tex"),
    ("Fr contraction Kona",  r"the intersections contract ([0-9.]+)\\% and",     "Frchange_kona", 0.06, "tex"),
    ("Fr contraction Ka'u",  r"the intersections contract [0-9.]+\\% and ([0-9.]+)\\%", "Frchange_kau", 0.06, "tex"),
    ("SSP245 Fr Kona",       r"intersection contracts \(\$-([0-9.]+)\\%\$",      "ssp245_kona_Frchange", 0.06, "tex"),
    ("SSP585 Fr Ka'u",       r"\(\$-13\.4\\%\$, \$-([0-9.]+)\\%\$",              "ssp585_kau_Frchange",  0.06, "tex"),
    # ── incidence ──
    ("terr decline Kona 2035", r"([0-9.]+)\\% is on a declining thermal trajectory by 2035", "terrdecl_kona_2035", 0.06, "tex"),
    ("terr decline Ka'u 2035", r"for Ka\\okina u-like terrain, ([0-9.]+)\\%",  "terrdecl_kau_2035",  0.06, "tex"),
    ("farm decline Kona 2035", r"\\textbf\{([0-9.]+)\\%\} are on a declining trajectory by 2035", "farmdecl_kona_2035", 0.06, "tex"),
    ("island gain Kona 2035",  r"([0-9.]+)\\% of farmable island cells gain",  "islandgain_kona_2035", 0.06, "tex"),
    ("island gain Ka'u 2035",  r"and ([0-9.]+)\\% under Ka\\okina u's",        "islandgain_kau_2035",  0.06, "tex"),
    ("gain isotherm Kona",     r"z \\gtrsim ([0-9]+)\$",                       "gainZ_kona_2035",      3.0,  "tex"),
    ("decl CI Kona 2035 lo",   r"\(95\\% CI ([0-9.]+)--78\.0\)",              "decl_ci_kona_2035_lo", 0.05, "tex"),
    ("decl CI Kona 2035 hi",   r"\(95\\% CI 65\.8--([0-9.]+)\)",              "decl_ci_kona_2035_hi", 0.05, "tex"),
    ("decl CI Ka'u 2045 hi",   r"\(65\.0--([0-9.]+)\)",                       "decl_ci_kau_2045_hi",  0.05, "tex"),
    # ── the terrain break: new evidence, stated in abstract, S3.1 and Conclusions ──
    ("slope break below",      r"from \$-([0-9.]+)\$ to \$-0\.137\$",            "featslope_below_2", 0.006, "tex"),
    ("slope break above",      r"to \$-([0-9.]+)\$ standard deviations",         "featslope_above_2", 0.006, "tex"),
    # ── robustness ──
    ("factor Kona",          r"is \$([0-9.]+)\\times\$ for Kona",               "factor_kona_2035", 0.06, "tex"),
    ("factor Ka'u",          r"and \$([0-9.]+)\\times\$ for Ka\\okina u \(3",   "factor_kau_2035",  0.06, "tex"),
    ("factor CI Kona lo",    r"95\\% CI ([0-9.]+)--8\.7\)",                    "factor_ci_kona_lo", 0.06, "tex"),
    ("factor CI Kona hi",    r"95\\% CI 6\.1--([0-9.]+)\)",                    "factor_ci_kona_hi", 0.06, "tex"),
    ("elev null Kona",       r"median ratios of \$([0-9.]+)\\times\$",          "elevnull_kona_median", 0.02, "tex"),
    ("elev null Ka'u",       r"and \$([0-9.]+)\\times\$ against observed",       "elevnull_kau_median",  0.02, "tex"),
    ("no-elev peak Kona",      r"sign unchanged \(Kona \$-([0-9.]+)\$",           "Fpeak_noelev_kona", 0.03, "tex"),
    ("no-elev peak Ka'u",      r"Ka\\okina u \$\+([0-9.]+)\$\\,\\textdegree C\)\.",  "Fpeak_noelev_kau", 0.03, "tex"),
    ("CV in-sample",         r"a ([0-9.]+)\\% in-sample reference",             "elevcv_insample",  0.06, "tex"),
    ("CV upper from lower",  r"recovers ([0-9]+)\\% of the upper 40",           "elevcv_upper_from_lower", 1.0, "tex"),
    ("collinearity r",       r"\$r = ([0-9.]+)\$ across the 471",                "r_elev_dev",       0.001, "tex"),
    # ── supplement ──
    ("SUPP factor Kona",     r"factor is \$([0-9.]+)\\times\$ for Kona",        "factor_kona_2035", 0.02, "supp"),
    ("SUPP factor CI lo",    r"95\\% CI ([0-9.]+)--8\.73\)",                   "factor_ci_kona_lo", 0.02, "supp"),
    ("SUPP factor Ka'u",     r"\$([0-9.]+)\\times\$ for Ka\\okina u \(3\.10",  "factor_kau_2035",  0.02, "supp"),
    ("SUPP CV upper",        r"recovering ([0-9]+)\\% of 189",                  "elevcv_upper_from_lower", 1.0, "supp"),
    ("SUPP CV in-sample",    r"the same ([0-9.]+)\\% in-sample reference",       "elevcv_insample",  0.06, "supp"),
    ("SUPP maha footprint",  r"\(([0-9.]+)\\% to 3\.56\\% of",                 "pct_kau_like",     0.06, "supp"),
    # ── R22: baseline epoch, peak intervals, elevation-weight sweep ──
    ("belt trend/decade",    r"warms \$([0-9.]+) \\pm",                        "trend_belt_per_decade", 0.002, "tex"),
    ("belt trend SE",        r"\\pm ([0-9.]+)\$\\,\\textdegree C per decade",  "trend_belt_se_per_decade", 0.002, "tex"),
    ("island trend",         r"\$\+([0-9.]+) \\pm [0-9.]+\$\\,\\textdegree C per decade island-wide", "trend_island_per_decade", 0.002, "tex"),
    ("offset to end record", r"record \$([0-9.]+)\$\\,\\textdegree C above the climatological mean", "offset_belt_to_endrec", 0.002, "tex"),
    ("peak Kona pt",         r"maximised at \$([\-0-9.]+)\$\\,\\textdegree C \(95",  "Fpeak_kona", 0.02, "tex"),
    ("peak Kona CI lo",      r"\(95\\% CI \$([\-0-9.]+)\$, \$\+0\.03\$\)",     "Fpeak_kona_ci_lo", 0.02, "tex"),
    ("peak Kona CI hi",      r"\(95\\% CI \$-0\.95\$, \$\+([0-9.]+)\$\)",     "Fpeak_kona_ci_hi", 0.02, "tex"),
    ("peak Kau pt",          r"Ka\\okina u's at \$\+([0-9.]+)\$\\,\\textdegree C", "Fpeak_kau", 0.02, "tex"),
    ("peak Kona recentred",  r"Kona's peak lies at \$-([0-9.]+)\$",           "Fpeak_kona_recentred", 0.02, "tex"),
    ("peak Kau recentred",   r"Ka\\okina u's lies at \$-([0-9.]+)\$",          "Fpeak_kau_recentred",  0.02, "tex"),
    ("peak diff",            r"difference \$-([0-9.]+)\$\\,\\textdegree C, CI",  "Fpeak_diff",     0.02, "tex"),
    ("asymmetry Kona dir",   r"peak \$-1\.35\$\\,\\textdegree C is ([0-9.]+) for Kona", "Fasym_kona", 0.02, "tex"),
    ("Cr change present Kona", r"moves by \$-([0-9.]+)\\%\$ under the Kona envelope", "Crchange_present_kona_2045", 0.06, "tex"),
    ("Cr change present Kau",  r"\\textit\{grows\} ([0-9.]+)\\% under Ka\\okina u's", "Crchange_present_kau_2045", 0.06, "tex"),
    ("acreage outside",      r"so ([0-9.]+)\\% of mapped acreage falls outside", "acreage_outside_pct", 0.06, "tex"),
    ("big island acres",     r"the (6\{,\}[0-9]+) acres of coffee mapped",       "bigisland_coffee_acres", 3.0, "tex"),
    ("wz contr max Kona",    r"runs monotonically from \$-([0-9.]+)\\%\$",    "wz_contr_max_kona", 0.06, "tex"),
    ("wz contr min Kona",    r"to \$-([0-9.]+)\\%\$ for Kona",                "wz_contr_min_kona", 0.06, "tex"),
    ("sz mode Kona",         r"with a mode at ([0-9]+)\\,m",                   "sz_mode_kona",     1.0,  "tex"),
    ("bp median",            r"median of ([0-9]+)\\,m",                        "bp_median_features", 1.0, "tex"),
    ("bp joint",             r"places \$b\$ at ([0-9]+)\\,m",                  "bp_joint",         1.0,  "tex"),
]
def norm(s):
    return float(s.replace("{,}", "").replace(",", ""))
def main():
    strict = "--strict" in sys.argv
    src = {"tex": TEX, "supp": SUPP}
    bad, missing, ok = [], [], 0
    for label, rx, key, tol, where in CLAIMS:
        m = re.search(rx, src[where])
        if not m:
            missing.append(label)
            continue
        if key is None:
            ok += 1
            continue
        got, want = norm(m.group(1)), NUM[key]
        # contraction values are printed unsigned
        if abs(got - abs(want)) <= tol or abs(got - want) <= tol:
            ok += 1
        else:
            bad.append((label, got, want))
    print(f"checked {len(CLAIMS)} claims against paper_numbers.json")
    print(f"  agree   : {ok}")
    print(f"  MISMATCH: {len(bad)}")
    print(f"  not found in tex (regex may need updating): {len(missing)}")
    for label, got, want in bad:
        print(f"    MISMATCH  {label:26s} paper={got:<12g} pipeline={want:.4f}")
    for label in missing:
        print(f"    NOT FOUND {label}")
    if strict and (bad or missing):
        sys.exit(1)
if __name__ == "__main__":
    main()
