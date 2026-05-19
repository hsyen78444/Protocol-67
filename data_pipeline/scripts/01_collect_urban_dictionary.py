"""
Collect Urban Dictionary-style definitions for slang seed terms.

Urban Dictionary content is user-generated, informal, inconsistent, and noisy.
This script preserves metadata for traceability and falls back to a curated
local sample so the rest of the coursework pipeline can run offline.
"""

from __future__ import annotations

import csv
import json
import os
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
LOCAL_API_BASE_URL = os.getenv("URBAN_DICTIONARY_API_BASE_URL", "http://localhost:8080").rstrip("/")
LOCAL_SEARCH_URL = f"{LOCAL_API_BASE_URL}/api/search"


def make_session() -> requests.Session:
    retry = Retry(
        total=2,
        backoff_factor=0.6,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET",),
    )
    session = requests.Session()
    session.mount("http://", HTTPAdapter(max_retries=retry))
    session.mount("https://", HTTPAdapter(max_retries=retry))
    session.headers.update({"User-Agent": "coursework-data-pipeline/1.0"})
    return session


def load_terms() -> List[str]:
    return [
        line.strip()
        for line in SEED_FILE.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    ]


def first_entry(payload: object) -> Dict[str, object] | None:
    """Accept several common API response shapes from compatible UD services."""
    if isinstance(payload, list):
        return payload[0] if payload else None
    if not isinstance(payload, dict):
        return None
    for key in ("data", "results", "definitions", "list"):
        value = payload.get(key)
        if isinstance(value, list) and value:
            return value[0]
    return payload if payload else None


def normalize_api_row(term: str, entry: Dict[str, object], source: str) -> Dict[str, object]:
    definition = entry.get("definition") or entry.get("meaning") or entry.get("def") or ""
    example = entry.get("example") or entry.get("usage") or ""
    return {
        "term": entry.get("word") or entry.get("term") or term,
        "definition": str(definition).replace("\r", " ").replace("\n", " "),
        "example": str(example).replace("\r", " ").replace("\n", " "),
        "thumbs_up": entry.get("thumbs_up") or entry.get("upvotes") or entry.get("up_votes") or 0,
        "thumbs_down": entry.get("thumbs_down") or entry.get("downvotes") or entry.get("down_votes") or 0,
        "source": source,
        "collection_date": date.today().isoformat(),
    }


def fetch_search_api(
    session: requests.Session,
    term: str,
    url: str,
    source: str,
) -> Dict[str, object] | None:
    response = session.get(
        url,
        params={"term": term, "strict": "true", "limit": 1},
        timeout=8,
    )
    response.raise_for_status()
    entry = first_entry(response.json())
    if not entry:
        return None
    return normalize_api_row(term, entry, source)


def fetch_local_search(session: requests.Session, term: str) -> Dict[str, object] | None:
    return fetch_search_api(session, term, LOCAL_SEARCH_URL, "local_urban_dictionary_api")


def fetch_term(session: requests.Session, term: str) -> Dict[str, object] | None:
    return fetch_local_search(session, term)


def curated_fallback_rows(terms: List[str]) -> List[Dict[str, object]]:
    dictionary = json.loads(DICT_FILE.read_text(encoding="utf-8"))
    rows = []
    missing_terms = []
    for term in terms:
        item = dictionary.get(term)
        if not item:
            missing_terms.append(term)
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
    if missing_terms:
        print(f"[warning] Skipped seed terms missing from slang dictionary: {', '.join(missing_terms)}")
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
