"""Merge raw definition, social corpus, and optional manual annotation sources."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "interim" / "merged_raw_dataset.csv"
COLS = ["id", "raw_text", "term", "definition", "example", "platform", "source", "source_type", "collection_date"]


def load_urban() -> pd.DataFrame:
    path = RAW / "urban_dictionary_raw.csv"
    if not path.exists():
        return pd.DataFrame(columns=COLS)
    df = pd.read_csv(path).fillna("")
    return pd.DataFrame(
        {
            "raw_text": df["example"].where(df["example"].astype(str).str.len() > 0, df["definition"]),
            "term": df.get("term", ""),
            "definition": df.get("definition", ""),
            "example": df.get("example", ""),
            "platform": "urban_dictionary",
            "source": df.get("source", "urban_dictionary"),
            "source_type": "definition_api_or_fallback",
            "collection_date": df.get("collection_date", date.today().isoformat()),
        }
    )


def load_social(filename: str, platform: str) -> pd.DataFrame:
    path = RAW / filename
    if not path.exists():
        return pd.DataFrame(columns=COLS)
    df = pd.read_csv(path).fillna("")
    return pd.DataFrame(
        {
            "raw_text": df["text"],
            "term": "",
            "definition": "",
            "example": "",
            "platform": df.get("platform", platform),
            "source": platform,
            "source_type": df.get("source_type", "local_or_fallback_corpus"),
            "collection_date": df.get("collection_date", date.today().isoformat()),
        }
    )


def load_manual() -> pd.DataFrame:
    path = RAW / "manual_annotations.csv"
    if not path.exists():
        return pd.DataFrame(columns=COLS)
    df = pd.read_csv(path).fillna("")
    text_col = "raw_text" if "raw_text" in df.columns else "text"
    return pd.DataFrame(
        {
            "raw_text": df[text_col],
            "term": df.get("term", ""),
            "definition": df.get("definition", ""),
            "example": df.get("example", ""),
            "platform": df.get("platform", "manual"),
            "source": "manual_annotation",
            "source_type": "human_annotation",
            "collection_date": df.get("collection_date", date.today().isoformat()),
        }
    )


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    merged = pd.concat(
        [
            load_urban(),
            load_social("twitch_corpus_raw.csv", "twitch"),
            load_manual(),
        ],
        ignore_index=True,
    )
    merged["raw_text"] = merged["raw_text"].astype(str).str.strip()
    merged = merged[merged["raw_text"].ne("")]
    before = len(merged)
    merged = merged.drop_duplicates(subset=["raw_text", "platform", "source"]).reset_index(drop=True)
    merged.insert(0, "id", range(1, len(merged) + 1))
    merged[COLS].to_csv(OUT, index=False)
    print(f"Saved {len(merged)} merged rows to {OUT} ({before - len(merged)} exact duplicates removed).")


if __name__ == "__main__":
    main()
