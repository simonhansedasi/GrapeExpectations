"""
Wild-species chemotype pilot: species -> compound pathway classes -> occurrence climate niche.

Three public databases, no API keys needed:
    KNApSAcK      species -> reported compounds (name, SMILES)      knapsackfamily.com
    NPClassifier  SMILES -> biosynthetic pathway class              npclassifier.ucsd.edu
    GBIF          species -> georeferenced occurrence records       api.gbif.org

Answers a narrower question than the original TerraMetabolica RSU regressions:
not "does this compound's concentration track altitude within one crop" but
"does this species' compound-pathway mix line up with its climate niche" --
a cross-species comparison, one data point per species, not a within-species
site regression. See lit_review/building_blocks_latitude_2026-07-26.md.

Pilot: one species end-to-end (Vaccinium myrtillus) before scaling to more.
Caches all raw responses under data/raw/{knapsack,npclassifier,gbif}/.
"""

import hashlib
import json
import math
import re
import statistics
import time
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen

KNAPSACK_BASE = "http://www.knapsackfamily.com/knapsack_core"
NPCLASSIFIER_BASE = "https://npclassifier.ucsd.edu"
GBIF_BASE = "https://api.gbif.org/v1"

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
CACHE_DIRS = {
    "knapsack": DATA_DIR / "raw" / "knapsack",
    "npclassifier": DATA_DIR / "raw" / "npclassifier",
    "gbif": DATA_DIR / "raw" / "gbif",
}
OUTPUT_DIR = DATA_DIR / "wild_chemotype"

ROW_RE = re.compile(
    r'<tr><td class="d1"><a href=information\.php\?word=(?P<cid>C\d+)[^>]*>.*?</a></td>'
    r'<td class="d1">(?P<cas>[^<]*)</td>'
    r'<td class="d1">(?P<name>[^<]*)</td>'
    r'<td class="d1">(?P<formula>[^<]*)</td>'
    r'<td class="d1">(?P<mw>[^<]*)</td>'
    r'<td class="d1">(?P<organism>.*?)</td></tr>',
    re.DOTALL,
)
SMILES_RE = re.compile(r'<th class="inf">SMILES</th>\s*<td colspan="4">([^<]*)</td>')
TAG_RE = re.compile(r"<[^>]+>")


def _slug(species: str) -> str:
    return species.strip().lower().replace(" ", "_")


def _get(url: str, cache_path: Path, is_json: bool = False, delay: float = 1.0):
    """Fetch a URL with a simple on-disk cache; sleeps `delay` seconds on a real fetch."""
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    if cache_path.exists():
        text = cache_path.read_text()
    else:
        req = Request(url, headers={"User-Agent": "TerraMetabolica-wild-chemotype/0.1"})
        with urlopen(req, timeout=20) as r:
            text = r.read().decode("utf-8", errors="replace")
        cache_path.write_text(text)
        time.sleep(delay)
    return json.loads(text) if is_json else text


def fetch_knapsack_compounds(species: str) -> list:
    """Species -> list of {c_id, cas, name, formula, mw, organism} from KNApSAcK Core DB."""
    url = f"{KNAPSACK_BASE}/result.php?sname=organism&word={quote(species)}"
    cache_path = CACHE_DIRS["knapsack"] / f"{_slug(species)}.html"
    html = _get(url, cache_path)

    compounds = []
    for m in ROW_RE.finditer(html):
        compounds.append({
            "c_id": m.group("cid"),
            "cas": m.group("cas").strip(),
            "name": m.group("name").strip(),
            "formula": m.group("formula").strip(),
            "mw": m.group("mw").strip(),
            "organism": TAG_RE.sub("", m.group("organism")).strip(),
        })
    return compounds


def fetch_smiles(c_id: str) -> str:
    """C_ID -> SMILES string, or None if not found."""
    url = f"{KNAPSACK_BASE}/information.php?word={c_id}"
    cache_path = CACHE_DIRS["knapsack"] / f"compound_{c_id}.html"
    html = _get(url, cache_path)
    m = SMILES_RE.search(html)
    return m.group(1).strip() if m else None


def classify_pathway(smiles: str) -> dict:
    """SMILES -> {pathway, superclass, class_} via NPClassifier. Drops the fingerprint arrays."""
    digest = hashlib.md5(smiles.encode()).hexdigest()
    cache_path = CACHE_DIRS["npclassifier"] / f"{digest}.json"

    if cache_path.exists():
        data = json.loads(cache_path.read_text())
    else:
        url = f"{NPCLASSIFIER_BASE}/classify?smiles={quote(smiles)}"
        req = Request(url, headers={"User-Agent": "TerraMetabolica-wild-chemotype/0.1"})
        with urlopen(req, timeout=20) as r:
            raw = json.loads(r.read().decode())
        data = {
            "pathway_results": raw.get("pathway_results", []),
            "superclass_results": raw.get("superclass_results", []),
            "class_results": raw.get("class_results", []),
        }
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(json.dumps(data))
        time.sleep(1.0)

    return {
        "pathway": data["pathway_results"][0] if data["pathway_results"] else None,
        "superclass": data["superclass_results"][0] if data["superclass_results"] else None,
        "class_": data["class_results"][0] if data["class_results"] else None,
    }


def fetch_gbif_occurrences(species: str, limit: int = 300) -> list:
    """Species -> list of {lat, lon, elevation} from georeferenced GBIF occurrence records.

    Filters to elevation=-500,9000 (i.e. elevation present, any plausible terrestrial value)
    rather than plain hasCoordinate=true. A first-page unfiltered query is dominated by recent
    citizen-science observations that almost never carry elevation (confirmed empirically:
    1/300 populated) -- confirmed separately that a large elevation-tagged subset exists
    (~180k of ~1M for Vaccinium myrtillus) but sits outside the default first page. Trade-off:
    this biases the sample toward observers who report elevation, which may not be random
    across geography (more common in mountain/alpine recording) -- acceptable for a pilot,
    worth revisiting if this scales to more species.
    """
    match_cache = CACHE_DIRS["gbif"] / f"{_slug(species)}_match.json"
    match = _get(f"{GBIF_BASE}/species/match?name={quote(species)}", match_cache, is_json=True, delay=0.5)
    taxon_key = match.get("usageKey")
    if not taxon_key:
        return []

    occ_cache = CACHE_DIRS["gbif"] / f"{_slug(species)}_occurrences.json"
    url = (
        f"{GBIF_BASE}/occurrence/search?taxonKey={taxon_key}&hasCoordinate=true"
        f"&elevation=-500,9000&limit={min(limit, 300)}"
    )
    data = _get(url, occ_cache, is_json=True, delay=0.5)

    return [
        {
            "lat": r.get("decimalLatitude"),
            "lon": r.get("decimalLongitude"),
            "elevation": r.get("elevation"),
        }
        for r in data.get("results", [])
        if r.get("decimalLatitude") is not None
    ]


def climate_niche_summary(occurrences: list) -> dict:
    """Median |latitude|, median elevation (where present), and the project's UV proxy."""
    if not occurrences:
        return {}

    abs_lats = [abs(o["lat"]) for o in occurrences]
    elevations = [o["elevation"] for o in occurrences if o["elevation"] is not None]

    median_abs_lat = statistics.median(abs_lats)
    median_elevation = statistics.median(elevations) if elevations else None

    # UV proxy formula from TerraMetabolica/CLAUDE.md sec. 13: cos(|lat|*pi/180) * (1 + altitude_m/2500)
    uv_proxy = math.cos(median_abs_lat * math.pi / 180) * (1 + (median_elevation or 0) / 2500)

    return {
        "n_occurrences": len(occurrences),
        "median_abs_lat": round(median_abs_lat, 2),
        "median_elevation_m": round(median_elevation, 1) if median_elevation is not None else None,
        "n_with_elevation": len(elevations),
        "uv_proxy": round(uv_proxy, 4),
    }


def build_species_record(species: str) -> dict:
    """Full pipeline for one species: KNApSAcK compounds -> NPClassifier pathway classes,
    GBIF occurrences -> climate niche."""
    compounds = fetch_knapsack_compounds(species)

    pathway_counts = {}
    classified = []
    for c in compounds:
        smiles = fetch_smiles(c["c_id"])
        if not smiles:
            continue
        cls = classify_pathway(smiles)
        pathway = cls["pathway"]
        if pathway:
            pathway_counts[pathway] = pathway_counts.get(pathway, 0) + 1
        classified.append({**c, **cls})

    occurrences = fetch_gbif_occurrences(species)

    return {
        "species": species,
        "n_compounds": len(compounds),
        "n_classified": len(classified),
        "pathway_class_counts": pathway_counts,
        "compounds": classified,
        "climate_niche": climate_niche_summary(occurrences),
    }


# Wild species already confirmed feasible: has both KNApSAcK compound entries and GBIF
# elevation-tagged occurrences (checked 2026-07-26). Vaccinium floribundum and Cyclocarya
# paliurus were also tried and dropped -- 0 KNApSAcK compounds under either name.
SPECIES_LIST = [
    "Vaccinium myrtillus",       # wild bilberry -- original pilot
    "Origanum vulgare",         # wild oregano
    "Origanum majorana",        # wild marjoram
    "Salvia officinalis",       # sage
    "Rosmarinus officinalis",   # rosemary -- KNApSAcK uses the pre-2017 name, not Salvia rosmarinus
    "Sambucus nigra",           # elderberry
    "Thymus serpyllum",         # wild thyme
]


def summarize_pathways(pathway_class_counts: dict) -> dict:
    """Fraction of classified compounds in the shikimate/phenylpropanoid pathway vs others --
    the specific comparison the lit review flagged as having independent support."""
    total = sum(pathway_class_counts.values())
    if not total:
        return {"phenylpropanoid_frac": None, "terpenoid_frac": None, "alkaloid_frac": None}
    return {
        "phenylpropanoid_frac": round(pathway_class_counts.get("Shikimates and Phenylpropanoids", 0) / total, 3),
        "terpenoid_frac": round(pathway_class_counts.get("Terpenoids", 0) / total, 3),
        "alkaloid_frac": round(pathway_class_counts.get("Alkaloids", 0) / total, 3),
    }


if __name__ == "__main__":
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    summary_rows = []

    for species in SPECIES_LIST:
        print(f"\n=== {species} ===")
        try:
            record = build_species_record(species)
        except Exception as e:
            print(f"  FAILED: {e}")
            continue

        print(f"  KNApSAcK compounds: {record['n_compounds']} ({record['n_classified']} classified)")
        print(f"  Pathway class counts: {record['pathway_class_counts']}")
        print(f"  Climate niche: {record['climate_niche']}")

        if record["n_compounds"] == 0:
            print("  WARNING: no KNApSAcK compounds -- skipping from summary")
            continue
        if record["climate_niche"].get("n_occurrences", 0) == 0:
            print("  WARNING: no GBIF occurrences -- skipping from summary")
            continue

        out_path = OUTPUT_DIR / f"{_slug(species)}.json"
        out_path.write_text(json.dumps(record, indent=2))

        row = {
            "species": species,
            "n_compounds": record["n_compounds"],
            **summarize_pathways(record["pathway_class_counts"]),
            **record["climate_niche"],
        }
        summary_rows.append(row)

    print("\n=== Cross-species summary ===")
    header = ["species", "n_compounds", "phenylpropanoid_frac", "terpenoid_frac", "alkaloid_frac",
              "n_occurrences", "median_abs_lat", "median_elevation_m", "uv_proxy"]
    print(",".join(header))
    for row in summary_rows:
        print(",".join(str(row.get(h, "")) for h in header))

    summary_path = OUTPUT_DIR / "cross_species_summary.csv"
    with open(summary_path, "w") as f:
        f.write(",".join(header) + "\n")
        for row in summary_rows:
            f.write(",".join(str(row.get(h, "")) for h in header) + "\n")
    print(f"\nSaved summary to {summary_path}")
