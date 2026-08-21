#!/usr/bin/env python3
"""
Bulk-download monthly 250 m climate GeoTIFFs (Big Island) from the Hawai'i Climate
Data Portal / Hawai'i Mesonet API -- the Kodama et al. (2024) gridded temperature
product (references.bib: Kodama2024) and the matching gridded rainfall.

Requires an API key: sign up at
https://www.hawaii.edu/climate-data-portal/hcdp-hawaii-mesonet-api/
then:  export HCDP_API_KEY="your-key-here"

Usage:
    # temperature (as originally run -- produced data/kodama_temperature/)
    python 09_kodama_temperature_download.py --start 1990-01 --end 2021-12

    # rainfall, for re-deriving precip_dry / precip_wet / precip_dry_frac,
    # which are still on the superseded 4 km product (see 14_swap_rainfall.py)
    python 09_kodama_temperature_download.py --datatype rainfall \
        --start 1990-01 --end 2021-12

Resumable: skips any month whose GeoTIFF is already on disk. Safe to re-run.
API docs: https://raw.githubusercontent.com/HCDP/hcdp_api_docs/master/hcdp_api.yaml
"""
import argparse
import os
import sys
import time
from datetime import date

import requests

API_BASE = "https://api.hcdp.ikewai.org"
OUT_DIRS = {
    "temperature": os.path.join(os.path.dirname(__file__), "..", "data", "kodama_temperature"),
    "rainfall": os.path.join(os.path.dirname(__file__), "..", "data", "rainfall_monthly"),
}
DELAY_S = 2.0
MAX_RETRIES = 5

# Parameters per the HCDP OpenAPI spec (hcdp_api.yaml, read 2026-07-30):
#   datatype=temperature -> takes `aggregation` (min|max|mean), NOT `production`
#   datatype=rainfall    -> takes `production` (new|legacy), NOT `aggregation`
#       new    = contemporary methods, 1990-present  <- matches the 1990-2021 baseline
#       legacy = older techniques, monthly only, 1920-2012
# Spec-verified but not yet exercised: api.hcdp.ikewai.org returned 502 on every
# endpoint including root on 2026-07-30, so the rainfall path has never run.


def month_range(start: str, end: str):
    y, m = map(int, start.split("-"))
    ey, em = map(int, end.split("-"))
    while (y, m) <= (ey, em):
        yield f"{y:04d}-{m:02d}"
        m += 1
        if m > 12:
            m = 1
            y += 1


def fetch_month(session, api_key, ym, aggregation, out_dir, datatype="temperature",
                production="new"):
    is_temp = datatype == "temperature"
    stem, tag = ("temp", aggregation) if is_temp else ("rain", production)
    out_path = os.path.join(out_dir, f"{stem}_{tag}_{ym}.tif")
    if os.path.exists(out_path) and os.path.getsize(out_path) > 0:
        return "skipped"

    params = {
        "date": ym,
        "extent": "bi",
        "datatype": datatype,
        "period": "month",
    }
    # the two datatypes take mutually exclusive qualifiers; sending the wrong one is
    # what a guessed call would get wrong
    params["aggregation" if is_temp else "production"] = aggregation if is_temp else production
    headers = {"Authorization": f"Bearer {api_key}"}

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = session.get(f"{API_BASE}/raster", params=params, headers=headers, timeout=30)
        except requests.RequestException as e:
            print(f"  [{ym}] request error (attempt {attempt}/{MAX_RETRIES}): {e}", flush=True)
            time.sleep(5 * attempt)
            continue

        if resp.status_code == 200:
            with open(out_path, "wb") as f:
                f.write(resp.content)
            return "ok"
        elif resp.status_code == 404:
            print(f"  [{ym}] 404 not found -- no data for this month, skipping", flush=True)
            return "missing"
        elif resp.status_code == 401:
            print(f"  [{ym}] 401 unauthorized -- check HCDP_API_KEY", flush=True)
            sys.exit(1)
        elif resp.status_code == 429:
            wait = int(resp.headers.get("Retry-After", 60 * attempt))
            print(f"  [{ym}] 429 rate limited, waiting {wait}s", flush=True)
            time.sleep(wait)
        else:
            print(f"  [{ym}] HTTP {resp.status_code} (attempt {attempt}/{MAX_RETRIES}): {resp.text[:200]}", flush=True)
            time.sleep(5 * attempt)

    print(f"  [{ym}] FAILED after {MAX_RETRIES} attempts", flush=True)
    return "failed"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", default="2017-01", help="YYYY-MM, inclusive")
    ap.add_argument("--end", default="2021-12", help="YYYY-MM, inclusive (Kodama et al. 2024 covers through 2021)")
    ap.add_argument("--aggregation", default="mean", choices=["mean", "min", "max"],
                    help="temperature only; ignored for rainfall")
    ap.add_argument("--datatype", default="temperature", choices=["temperature", "rainfall"])
    ap.add_argument("--production", default="new", choices=["new", "legacy"],
                    help="rainfall only; new=1990-present, legacy=1920-2012")
    args = ap.parse_args()

    api_key = os.environ.get("HCDP_API_KEY")
    if not api_key:
        print("ERROR: set HCDP_API_KEY (see docstring for sign-up link)", file=sys.stderr)
        sys.exit(1)

    out_dir = os.path.abspath(OUT_DIRS[args.datatype])
    os.makedirs(out_dir, exist_ok=True)

    months = list(month_range(args.start, args.end))
    qual = (f"aggregation={args.aggregation}" if args.datatype == "temperature"
            else f"production={args.production}")
    print(f"Fetching {len(months)} months ({args.start} to {args.end}), "
          f"datatype={args.datatype}, {qual}, extent=bi -> {out_dir}", flush=True)

    counts = {"ok": 0, "skipped": 0, "missing": 0, "failed": 0}
    with requests.Session() as session:
        for i, ym in enumerate(months, 1):
            result = fetch_month(session, api_key, ym, args.aggregation, out_dir,
                                 args.datatype, args.production)
            counts[result] += 1
            if result == "ok":
                time.sleep(DELAY_S)
            if i % 12 == 0 or i == len(months):
                print(f"  progress: {i}/{len(months)} months processed", flush=True)

    print(f"\nDone. ok={counts['ok']} skipped={counts['skipped']} "
          f"missing={counts['missing']} failed={counts['failed']}", flush=True)
    if counts["failed"] > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
