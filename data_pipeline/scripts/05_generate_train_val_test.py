"""Create reproducible train, validation, and test splits."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split


ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
IN_FILE = PROCESSED / "brainrot_clean_dataset.csv"
RANDOM_SEED = 42


def stratify_or_none(df: pd.DataFrame):
    counts = df["sentiment"].value_counts()
    return df["sentiment"] if len(counts) > 1 and counts.min() >= 2 else None


def main() -> None:
    df = pd.read_csv(IN_FILE).fillna("")
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

    print(f"Duplicate clean_text rows removed before split: {duplicates_removed}")
    print(f"Train rows: {len(train)}")
    print(f"Validation rows: {len(val)}")
    print(f"Test rows: {len(test)}")


if __name__ == "__main__":
    main()
