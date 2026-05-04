"""
Collect Urban Dictionary-style definitions for slang seed terms.

Urban Dictionary content is user-generated, informal, inconsistent, and noisy.
This script preserves metadata for traceability and falls back to a curated
local sample so the rest of the coursework pipeline can run offline.
"""

from __future__ import annotations

import csv
import json
import time
from datetime import date
from pathlib import Path
from typing import Dict, List

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


ROOT = Path(__file__).resolve().parents[1]
SEED_FILE = ROOT / "config" / "slang_seed_terms.txt"
DICT_FILE = ROOT / "config" / "slang_dictionary.json"
OUT_FILE = ROOT / "data" / "raw" / "urban_dictionary_raw.csv"
API_URL = "https://api.urbandictionary.com/v0/define"


def make_session() -> requests.Session:
    retry = Retry(
        total=2,
        backoff_factor=0.6,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET",),
    )
    session = requests.Session()
    session.mount("https://", HTTPAdapter(max_retries=retry))
    session.headers.update({"User-Agent": "coursework-data-pipeline/1.0"})
    return session


def load_terms() -> List[str]:
    return [
        line.strip()
        for line in SEED_FILE.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    ]


def fetch_term(session: requests.Session, term: str) -> Dict[str, object] | None:
    response = session.get(API_URL, params={"term": term}, timeout=8)
    response.raise_for_status()
    payload = response.json()
    entries = payload.get("list", [])
    if not entries:
        return None
    best = sorted(entries, key=lambda row: row.get("thumbs_up", 0), reverse=True)[0]
    return {
        "term": term,
        "definition": best.get("definition", "").replace("\r", " ").replace("\n", " "),
        "example": best.get("example", "").replace("\r", " ").replace("\n", " "),
        "thumbs_up": best.get("thumbs_up", 0),
        "thumbs_down": best.get("thumbs_down", 0),
        "source": "urban_dictionary_api",
        "collection_date": date.today().isoformat(),
    }


def curated_fallback_rows(terms: List[str]) -> List[Dict[str, object]]:
    dictionary = json.loads(DICT_FILE.read_text(encoding="utf-8"))
    rows = []
    for term in terms:
        item = dictionary.get(term)
        if not item:
            continue
        rows.append(
            {
                "term": term,
                "definition": item["meaning"],
                "example": item["example"],
                "thumbs_up": 0,
                "thumbs_down": 0,
                "source": "curated_local_fallback",
                "collection_date": date.today().isoformat(),
            }
        )
    return rows


def main() -> None:
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    terms = load_terms()
    session = make_session()
    rows: List[Dict[str, object]] = []
    consecutive_failures = 0

    for term in terms:
        try:
            row = fetch_term(session, term)
            if row and (row["definition"] or row["example"]):
                rows.append(row)
            consecutive_failures = 0
            time.sleep(0.15)
        except Exception as exc:
            print(f"[warning] API lookup failed for '{term}': {exc}")
            consecutive_failures += 1
            if consecutive_failures >= 5 and not rows:
                print("[info] API appears unavailable; switching to curated fallback without querying remaining terms.")
                rows = curated_fallback_rows(terms)
                break
            continue

    if len(rows) < 20:
        print("[info] API returned too little usable data; using curated fallback rows.")
        rows = curated_fallback_rows(terms)

    columns = ["term", "definition", "example", "thumbs_up", "thumbs_down", "source", "collection_date"]
    with OUT_FILE.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Saved {len(rows)} Urban Dictionary-style rows to {OUT_FILE}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"[warning] Collector failed without stopping the wider pipeline: {exc}")
        terms = load_terms()
        rows = curated_fallback_rows(terms)
        OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
        with OUT_FILE.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=["term", "definition", "example", "thumbs_up", "thumbs_down", "source", "collection_date"],
            )
            writer.writeheader()
            writer.writerows(rows)
        print(f"Saved {len(rows)} fallback rows to {OUT_FILE}")
