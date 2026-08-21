"""
migrate_schema.py
-----------------
Schema migration for all 157 RSU JSON files.

Two operations:
  1. RSU-01 to RSU-66:
       - Strip unsupported values from key_flavor_bioactives, terpenes,
         organic_acids, umami_compounds.
         "Supported" = value string cites a specific paper (author + year),
         NOT USDA FDC only, NOT "literature", NOT Phenol-Explorer,
         NOT [NEEDS PRIMARY SOURCE], NOT qualitative-only.
       - Add analytical_observations array with compound_class + driver
         for surviving values.

  2. RSU-67 to RSU-157:
       - Add analytical_observations array only (existing values intact).
       - Parse numeric value out of key_flavor_bioactives strings.

Run from repo root:
    python3 src/migrate_schema.py [--dry-run]
"""

from __future__ import annotations

import json
import re
import sys
import copy
from pathlib import Path
from typing import Optional, Tuple

RSU_DIR = Path(__file__).parent.parent / "data" / "rsu"

# ---------------------------------------------------------------------------
# Compound lookup: key pattern → (compound_class, primary_environmental_driver)
# Keys are matched as substrings (lower-cased) of the compound key name.
# Order matters: first match wins.
# ---------------------------------------------------------------------------
COMPOUND_MAP = [
    # Curcuminoids
    ("curcumin",              "curcuminoid",              "temperature"),
    ("demethoxycurcumin",     "curcuminoid",              "temperature"),
    ("bisdemethoxycurcumin",  "curcuminoid",              "temperature"),
    # Phenolic monoterpenes (UV-stress)
    ("carvacrol",             "monoterpene_phenol",       "UV_B"),
    ("thymol",                "monoterpene_phenol",       "UV_B"),
    # Monoterpene ketones (aridity/oxidative stress)
    ("thujone",               "monoterpene_ketone",       "aridity"),
    ("camphor",               "monoterpene_ketone",       "aridity"),
    # Diterpenes (aridity/oxidative stress)
    ("carnosic_acid",         "diterpene",                "aridity"),
    ("carnosol",              "diterpene",                "aridity"),
    # Non-phenolic monoterpenes (temperature)
    ("linalool",              "monoterpene_non_phenol",   "temperature"),
    ("borneol",               "monoterpene_non_phenol",   "temperature"),
    ("limonene",              "monoterpene_non_phenol",   "temperature"),
    ("pinene",                "monoterpene_non_phenol",   "temperature"),
    ("myrcene",               "monoterpene_non_phenol",   "temperature"),
    ("terpinene",             "monoterpene_precursor",    "UV_B"),
    ("cymene",                "monoterpene_precursor",    "UV_B"),
    ("sabinene",              "monoterpene_non_phenol",   "temperature"),
    ("essential_oil_yield",   "monoterpene_total",        "aridity"),
    # Naphthodianthrones / phloroglucinols (Hypericum)
    ("hypericin",             "naphthodianthrone",        "UV_B"),
    ("pseudohypericin",       "naphthodianthrone",        "UV_B"),
    ("hyperforin",            "phloroglucinol",           "UV_B"),
    ("biapigenin",            "biflavonoid",              "UV_B"),
    # Carotenoid glycosides (saffron)
    ("crocin",                "carotenoid_glycoside",     "UV_B"),
    ("crocetin",              "carotenoid_glycoside",     "UV_B"),
    ("picrocrocin",           "iridoid_glycoside",        "UV_B"),
    ("safranal",              "monoterpene_aldehyde",     "UV_B"),
    # Flavonols (UV-stress)
    ("rutin",                 "flavonol",                 "UV_B"),
    ("quercetin",             "flavonol",                 "UV_B"),
    ("kaempferol",            "flavonol",                 "UV_B"),
    ("isoquercitrin",         "flavonol",                 "UV_B"),
    ("quercitrin",            "flavonol",                 "UV_B"),
    ("avicularin",            "flavonol",                 "UV_B"),
    ("hyperoside",            "flavonol",                 "UV_B"),
    ("myricetin",             "flavonol",                 "UV_B"),
    ("naringin",              "flavanone",                "UV_B"),
    ("hesperidin",            "flavanone",                "UV_B"),
    # Anthocyanins (UV-stress)
    ("anthocyanin",           "anthocyanin",              "UV_B"),
    ("acy",                   "anthocyanin",              "UV_B"),
    ("cyanidin",              "anthocyanin",              "UV_B"),
    ("delphinidin",           "anthocyanin",              "UV_B"),
    # Flavan-3-ols / catechins (UV_B + temperature seasonality)
    ("catechin",              "flavan_3_ol",              "UV_B"),
    ("epicatechin",           "flavan_3_ol",              "UV_B"),
    ("egcg",                  "flavan_3_ol",              "UV_B"),
    ("egc",                   "flavan_3_ol",              "UV_B"),
    ("ecg",                   "flavan_3_ol",              "UV_B"),
    ("polyphenol_content",    "flavan_3_ol",              "UV_B"),   # tea RSUs only — see override logic
    # Phenolic acids (UV-stress)
    ("chlorogenic_acid",      "phenolic_acid",            "UV_B"),
    ("chlorogenic",           "phenolic_acid",            "UV_B"),
    ("cga",                   "phenolic_acid",            "UV_B"),
    ("gallic_acid",           "phenolic_acid",            "UV_B"),
    ("ferulic_acid",          "phenolic_acid",            "UV_B"),
    ("caffeic_acid",          "phenolic_acid",            "UV_B"),
    ("neochlorogenic",        "phenolic_acid",            "UV_B"),
    ("syringic",              "phenolic_acid",            "UV_B"),
    ("total_phenolic_acids",  "phenolic_acid",            "UV_B"),
    # Total phenolics
    ("total_phenolic",        "total_phenolic",           "UV_B"),
    ("tpc",                   "total_phenolic",           "UV_B"),
    ("tannin_content",        "total_phenolic",           "UV_B"),
    # Glucosinolates (UV-stress Brassica)
    ("sulforaphane",          "glucosinolate",            "UV_B"),
    ("indole_3_carbinol",     "glucosinolate",            "UV_B"),
    ("isothiocyanate",        "glucosinolate",            "UV_B"),
    # Carotenoids
    ("lycopene",              "carotenoid",               "UV_B"),
    ("tocopherol",            "tocopherol",               "UV_B"),
    ("carotene",              "carotenoid",               "UV_B"),
    # Olive / hydroxytyrosol
    ("hydroxytyrosol",        "phenolic",                 "UV_B"),
    # Capsaicinoids (temperature — heat stress defense)
    ("capsaicinoid",          "capsaicinoid",             "temperature"),
    # Sesquiterpenes / other terpenes
    ("cineole",               "monoterpene_oxide",        "temperature"),
    ("viridiflorol",          "sesquiterpene",            "temperature"),
    ("caryophyllene",         "sesquiterpene",            "temperature"),
    ("camphene",              "monoterpene_non_phenol",   "temperature"),
    ("carvone",               "monoterpene_ketone",       "aridity"),
    ("alpha_thujene",         "monoterpene_non_phenol",   "temperature"),
    ("oil_yield",             "monoterpene_total",        "aridity"),
    # Alkaloids / nitrogen compounds
    ("trigonelline",          "alkaloid",                 "temperature"),
    ("guanylate",             "nucleotide",               "fermentation"),
    ("lysine",                "amino_acid",               "fermentation"),
    # Aggregate phenolic measures
    ("total_polyphenols",     "total_phenolic",           "UV_B"),
    ("total_flavonoids",      "total_phenolic",           "UV_B"),
    ("antioxidant_capacity",  "total_phenolic",           "UV_B"),
    ("altitude_effect",       "total_phenolic",           "UV_B"),   # summary field — exclude below
    # Conjugated fatty acids (pasture quality)
    ("conjugated_linoleic",   "conjugated_fatty_acid",    "pasture_quality"),
    ("cla",                   "conjugated_fatty_acid",    "pasture_quality"),
    # Organic acids
    ("malic_acid",            "organic_acid",             "temperature"),
    ("citric_acid",           "organic_acid",             "temperature"),
    ("lactic_acid",           "organic_acid",             "fermentation"),
    ("acetic_acid",           "organic_acid",             "fermentation"),
    ("propionic_acid",        "organic_acid",             "fermentation"),
    ("tartaric_acid",         "organic_acid",             "temperature"),
    # Alkaloids (temperature)
    ("caffeine",              "alkaloid",                 "temperature"),
    ("theobromine",           "alkaloid",                 "temperature"),
    # Umami
    ("glutamate",             "amino_acid",               "fermentation"),
    ("inosinate",             "nucleotide",               "fermentation"),
]


def lookup_compound(key: str) -> Optional[Tuple[str, str]]:
    """Return (compound_class, driver) for a compound key, or None."""
    k = key.lower()
    for pattern, cls, driver in COMPOUND_MAP:
        if pattern in k:
            return cls, driver
    return None


# ---------------------------------------------------------------------------
# Citation / support detection
# ---------------------------------------------------------------------------
REJECT_PATTERNS = [
    r"\[USDA FDC",
    r"\[NEEDS PRIMARY SOURCE",
    r"CONFIRMED NONEXISTENT",
    r"UNVERIFIED",
    r"\bPhenol-Explorer\b",
    r"\bliterature\b(?!\s+\w)",          # "literature" as the citation itself
    r"\bsome chemotypes\b",
    r"\banalog:\b",
    r"estimated from\s+Kim et al",   # ghost citation Kim 2011
    r"\[sourdough rye fermentation literature",
    r"\[Nordic wild berry literature",
    r"\[Nordic berry literature",
    r"\[general apple chemistry literature",
    r"\[wild blueberry composition literature",
    r"\[buckwheat rutin literature",
    r"\[chili heat literature",
    r"\[fermented brassica",
    r"\[spice oil literature",
    r"\[fish muscle IMP",
    r"\[freshwater fish",
    r"\[fermented reindeer dairy",
    r"\[kefir fermentation",
    r"\[sourdough wheat literature",
    r"\[buckwheat saponin literature",
    r"\[regional pepper literature",
    r"\[thyme essential oil — 20-60",
    r"\[soft-ripened cheese fermentation",
    r"\[quinoa saponin literature",
    r"\[Alpine wild berry",
    r"^\s*(present|trace|detectable|absent|minimal|minor|measurable|elevated|yes)\s*[—–-]",
]

REJECT_RE = [re.compile(p, re.IGNORECASE) for p in REJECT_PATTERNS]

PAPER_YEAR_RE = re.compile(r'\b(19|20)\d{2}\b')


def is_paper_backed(value: str) -> bool:
    """Return True if value string cites a specific primary paper (strict — for RSU-01 to RSU-66)."""
    if not value or not isinstance(value, str):
        return False
    v = value.strip()
    for rx in REJECT_RE:
        if rx.search(v):
            return False
    if not PAPER_YEAR_RE.search(v):
        return False
    if not re.search(r'\d+\.?\d*', v):
        return False
    return True


def is_usable_late(value: str) -> bool:
    """Looser check for RSU-67+: reject only explicit flags, keep everything else numeric."""
    if not value or not isinstance(value, str):
        return False
    v = value.strip()
    # Hard rejects that also apply to late RSUs
    hard_rejects = [
        r'\[NEEDS PRIMARY SOURCE',
        r'CONFIRMED NONEXISTENT',
        r'UNVERIFIED',
        r'^\s*(present|trace|detectable|absent|minimal|minor|measurable|elevated|yes)\s*[—–-]',
        r'not detected',
        r'range across',       # cross-site ranges stored on individual RSU — skip
        r'altitude_effect',    # text summary fields, not measurements
        r'^\d+[-–]\d+%\s+lower',  # altitude effect summary prose
    ]
    for pat in hard_rejects:
        if re.search(pat, v, re.IGNORECASE):
            return False
    if not re.search(r'\d+\.?\d*', v):
        return False
    return True


# ---------------------------------------------------------------------------
# Value extraction
# ---------------------------------------------------------------------------
NUM_RE = re.compile(r'(\d+\.?\d*)\s*[–—-]\s*(\d+\.?\d*)')  # range
SINGLE_RE = re.compile(r'~?(\d+\.?\d*)')


def extract_value(s: str) -> Optional[float]:
    """Extract first numeric value (midpoint for ranges)."""
    if not s:
        return None
    m = NUM_RE.search(s)
    if m:
        lo, hi = float(m.group(1)), float(m.group(2))
        if hi > lo:  # genuine range (not negative sign artifact)
            return round((lo + hi) / 2, 4)
        # Looks like a negative sign artifact — return lo
        return lo
    m = SINGLE_RE.search(s)
    if m:
        return float(m.group(1))
    return None


UNITS_MAP = [
    (r'%\s*of\s*essential\s*oil',     "percent_EO"),
    (r'%\s*w/w',                       "percent_ww"),
    (r'%\s*EO',                        "percent_EO"),
    (r'µg/mg\s*DPE',                   "ug_per_mg_DPE"),
    (r'µg/g\s*DW',                     "ug_per_g_DW"),
    (r'mg\s*GAE/100g\s*DW',            "mg_GAE_per_100g_DW"),
    (r'mg/g\s*dry\s*weight',           "mg_per_g_DW"),
    (r'mg/g\s*DW',                     "mg_per_g_DW"),
    (r'mg/g',                          "mg_per_g"),
    (r'mg/100g\s*DW',                  "mg_per_100g_DW"),
    (r'mg/100g\s*FW',                  "mg_per_100g_FW"),
    (r'mg/100g',                       "mg_per_100g"),
    (r'g/100g\s*dry\s*(leaf|weight|matter|bean)', "g_per_100g_DW"),
    (r'g/100g\s*DW',                   "g_per_100g_DW"),
    (r'g/100g\s*dry',                  "g_per_100g_DW"),
    (r'g/100g\s*FW',                   "g_per_100g_FW"),
    (r'g/100g\s*fresh',                "g_per_100g_FW"),
    (r'g/100g',                        "g_per_100g"),
    (r'mg/L',                          "mg_per_L"),
    (r'mg/kg',                         "mg_per_kg"),
    (r'g/kg',                          "g_per_kg"),
    (r'g/L',                           "g_per_L"),
    (r'ppm',                           "ppm"),
    (r'%\s*by\s*hydrodistillation',    "percent_EO"),
    (r'%\s*of\s*EO',                   "percent_EO"),
    (r'\bSHU\b',                       "SHU"),
    (r'Scoville',                      "SHU"),
]


def extract_units(s: str) -> str:
    for pattern, unit in UNITS_MAP:
        if re.search(pattern, s, re.IGNORECASE):
            return unit
    return "unknown"


def extract_method(s: str) -> str:
    s_low = s.lower()
    if "gc-ms" in s_low or "gc/ms" in s_low:
        return "GC-MS"
    if "gc-fid" in s_low or "gc/fid" in s_low:
        return "GC-FID"
    if "gc" in s_low and ("mass" in s_low or "fid" in s_low):
        return "GC"
    if "uplc" in s_low:
        return "UPLC"
    if "hplc" in s_low:
        return "HPLC"
    if "spectro" in s_low or "folin" in s_low or "gae" in s_low:
        return "spectrophotometry"
    return "HPLC"  # default for phenolic compounds


def extract_source(s: str) -> str:
    """Pull the bracketed citation from a value string."""
    m = re.search(r'\[([^\]]+)\]', s)
    if m:
        return m.group(1).strip()
    return ""


# ---------------------------------------------------------------------------
# Special overrides: RSU-specific compound → class/driver
# Some key names like "polyphenol_content" are ambiguous; context resolves them.
# ---------------------------------------------------------------------------
COFFEE_RSUS  = {"RSU-54", "RSU-17", "RSU-18"}
TEA_RSUS     = {"RSU-20", "RSU-56", "RSU-57", "RSU-58", "RSU-59",
                "RSU-60", "RSU-61", "RSU-62", "RSU-64", "RSU-65"}
OLIVE_RSUS   = {"RSU-23", "RSU-28", "RSU-35"}

def get_class_driver(key: str, rsu_id: str, value_str: str) -> Tuple[str, str]:
    """Return (compound_class, driver), with RSU-context overrides."""
    k = key.lower()

    # polyphenol_content is ambiguous — resolve by RSU context
    if "polyphenol_content" in k:
        if rsu_id in COFFEE_RSUS:
            # Coffee CGA reported as polyphenol_content
            return "phenolic_acid", "UV_B"
        if rsu_id in TEA_RSUS:
            return "flavan_3_ol", "UV_B"
        # Check value string for "catechin" or "CGA"
        vl = value_str.lower()
        if "catechin" in vl or "egcg" in vl:
            return "flavan_3_ol", "UV_B"
        if "cga" in vl or "chlorogenic" in vl:
            return "phenolic_acid", "UV_B"
        return "total_phenolic", "UV_B"

    result = lookup_compound(key)
    if result:
        return result
    return "unknown", "unknown"


# ---------------------------------------------------------------------------
# Processing RSU files
# ---------------------------------------------------------------------------
METABOLITE_SECTIONS = [
    "key_flavor_bioactives",
    "terpenes",
    "organic_acids",
    "umami_compounds",
]


def is_early_rsu(rsu_id: str) -> bool:
    """RSU-01 through RSU-66 (original food-system RSUs)."""
    m = re.match(r'RSU-(\d+)', rsu_id)
    if m:
        return int(m.group(1)) <= 66
    return False


def build_observation(
    rsu_id: str,
    food_name: str,
    compound_key: str,
    value_str: str,
    cultivar: Optional[str] = None,
    cultivation_status: Optional[str] = None,
    species: Optional[str] = None,
) -> Optional[dict]:
    """Build a single analytical_observation record, or None if not usable."""
    val = extract_value(value_str)
    if val is None:
        return None
    units = extract_units(value_str)
    method = extract_method(value_str)
    source = extract_source(value_str)
    cls, driver = get_class_driver(compound_key, rsu_id, value_str)

    return {
        "compound":                    compound_key,
        "compound_class":              cls,
        "primary_environmental_driver": driver,
        "crop":                        food_name,
        "species":                     species or "",
        "value":                       val,
        "units":                       units,
        "analytical_method":           method,
        "cultivation_status":          cultivation_status or "",
        "source":                      source,
    }


def infer_cultivation(food_name: str, cultivar_field) -> str:
    name = (food_name or "").lower()
    if "wild" in name:
        return "wild"
    if cultivar_field:
        return "cultivated"
    return "unknown"


def process_rsu(filepath: Path, dry_run: bool = False) -> dict:
    with open(filepath) as f:
        data = json.load(f)

    rsu_id = data.get("region_id", "")
    early = is_early_rsu(rsu_id)

    observations = []

    for food in data.get("staple_foods", []):
        food_name = food.get("name", "")
        cultivar = food.get("cultivar")
        cult_status = infer_cultivation(food_name, cultivar)
        mp = food.get("metabolite_profile", {})

        for section in METABOLITE_SECTIONS:
            sec = mp.get(section, {})
            if not isinstance(sec, dict):
                continue

            keys_to_remove = []

            for key, value in list(sec.items()):
                if not isinstance(value, str) or not value.strip():
                    if early:
                        keys_to_remove.append(key)
                    continue

                if early:
                    backed = is_paper_backed(value)
                    if not backed:
                        keys_to_remove.append(key)
                        continue
                    usable = True
                else:
                    usable = is_usable_late(value)

                if usable:
                    obs = build_observation(
                        rsu_id, food_name, key, value,
                        cultivar=cultivar,
                        cultivation_status=cult_status,
                    )
                    if obs:
                        observations.append(obs)

            if early and not dry_run:
                for k in keys_to_remove:
                    del sec[k]

    data["analytical_observations"] = observations

    if not dry_run:
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write("\n")

    return {
        "rsu_id": rsu_id,
        "early": early,
        "observations": len(observations),
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    dry_run = "--dry-run" in sys.argv

    files = sorted(RSU_DIR.glob("RSU-*.json"), key=lambda p: (
        int(re.search(r'RSU-(\d+)', p.name).group(1)),
        p.name
    ))

    results = []
    for fp in files:
        r = process_rsu(fp, dry_run=dry_run)
        results.append(r)
        status = "DRY" if dry_run else "OK"
        print(f"[{status}] {r['rsu_id']:12s}  early={r['early']}  obs={r['observations']}")

    early_total = sum(r["observations"] for r in results if r["early"])
    late_total  = sum(r["observations"] for r in results if not r["early"])
    total       = early_total + late_total

    print(f"\nSummary:")
    print(f"  RSU-01 to RSU-66  : {early_total} observations across {sum(1 for r in results if r['early'])} files")
    print(f"  RSU-67 to RSU-157 : {late_total} observations across {sum(1 for r in results if not r['early'])} files")
    print(f"  Total             : {total} analytical observations")
    if dry_run:
        print("\n(Dry run — no files modified)")


if __name__ == "__main__":
    main()
