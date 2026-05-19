"""Create reproducible train, validation, and test splits."""

from __future__ import annotations

import os
import json
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import pandas as pd
from sklearn.model_selection import train_test_split


ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
IN_FILE = PROCESSED / "brainrot_clean_dataset.csv"
RANDOM_SEED = 42
INSTRUCTION = "Translate the following internet slang or brainrot text into clear formal English."


def stratify_or_none(df: pd.DataFrame):
    counts = df["sentiment"].value_counts()
    return df["sentiment"] if len(counts) > 1 and counts.min() >= 2 else None


def main() -> None:
    df = pd.read_csv(IN_FILE).fillna("")
    if len(df) < 3:
        raise ValueError("Need at least 3 train-ready rows before creating train/validation/test splits.")

    before = len(df)
    df = df.drop_duplicates(subset=["clean_text"]).reset_index(drop=True)
    df["id"] = range(1, len(df) + 1)
    duplicates_removed = before - len(df)

    train, temp = train_test_split(
        df,
        test_size=0.20,
        random_state=RANDOM_SEED,
        stratify=stratify_or_none(df),
    )
    val, test = train_test_split(
        temp,
        test_size=0.50,
        random_state=RANDOM_SEED,
        stratify=stratify_or_none(temp),
    )

    for name, split in [("train.csv", train), ("validation.csv", val), ("test.csv", test)]:
        split.sort_values("id").to_csv(PROCESSED / name, index=False)
    for name, split in [("train.jsonl", train), ("validation.jsonl", val), ("test.jsonl", test)]:
        write_jsonl(split.sort_values("id"), PROCESSED / name)

    print(f"Duplicate clean_text rows removed before split: {duplicates_removed}")
    print(f"Train rows: {len(train)}")
    print(f"Validation rows: {len(val)}")
    print(f"Test rows: {len(test)}")
    print("Wrote model-ready JSONL files.")


def write_jsonl(df: pd.DataFrame, path: Path) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for _, row in df.iterrows():
            record = {
                "instruction": INSTRUCTION,
                "input": row["clean_text"],
                "output": row["formal_translation"],
                "metadata": {
                    "source": row.get("source", ""),
                    "platform": row.get("platform", ""),
                    "sentiment": row.get("sentiment", ""),
                    "confidence_label": row.get("confidence_label", ""),
                    "detected_slang_terms": str(row.get("detected_slang_terms", "")).split("|")
                    if row.get("detected_slang_terms", "")
                    else [],
                },
            }
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
