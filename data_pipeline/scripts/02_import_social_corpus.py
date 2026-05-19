"""
Import a Twitch-style social corpus.

The pipeline uses a manually downloaded local dataset instead of scraping live
platforms or pulling from a remote URL at runtime.
"""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq


ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
DEFAULT_TWITCH_INPUT = ROOT / "train-00000-of-00001.parquet"
DEFAULT_TWITCH_LIMIT = 5000
COLUMNS = ["text", "platform", "source_type", "collection_date"]
TEXT_COLUMN_CANDIDATES = ("text", "message", "Message")


def suffix_for(path: Path) -> str:
    return path.suffix.lower()


def source_type_for(path: Path) -> str:
    suffix = suffix_for(path).lstrip(".") or "file"
    return f"local_{suffix}"


def effective_limit(limit: int | None) -> int | None:
    return None if limit is None or limit <= 0 else limit


def select_text_column(columns: list[str]) -> str:
    lower_to_original = {column.lower(): column for column in columns}
    for candidate in TEXT_COLUMN_CANDIDATES:
        match = lower_to_original.get(candidate.lower())
        if match:
            return match
    if not columns:
        raise ValueError("Input file has no columns.")
    return columns[0]


def read_parquet(path: Path, limit: int | None) -> pd.DataFrame:
    parquet_file = pq.ParquetFile(path)
    text_col = select_text_column(parquet_file.schema.names)
    limit = effective_limit(limit)
    if limit is None:
        return pd.read_parquet(path, columns=[text_col])

    batches = []
    rows_loaded = 0
    for batch in parquet_file.iter_batches(columns=[text_col], batch_size=min(limit, 100_000)):
        frame = batch.to_pandas()
        batches.append(frame)
        rows_loaded += len(frame)
        if rows_loaded >= limit:
            break
    if not batches:
        return pd.DataFrame(columns=[text_col])
    return pd.concat(batches, ignore_index=True).head(limit)


def read_input(path: Path, limit: int | None) -> pd.DataFrame:
    suffix = suffix_for(path)
    limit = effective_limit(limit)
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")

    if suffix == ".csv":
        return pd.read_csv(path, nrows=limit)
    if suffix == ".jsonl":
        rows = []
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                rows.append(json.loads(line))
            if limit is not None and len(rows) >= limit:
                break
        return pd.DataFrame(rows)
    if suffix == ".parquet":
        return read_parquet(path, limit)
    raise ValueError("Only CSV, JSONL, and Parquet inputs are supported.")


def load_twitch(path: Path, limit: int | None = None) -> pd.DataFrame:
    df = read_input(path, limit)
    text_col = select_text_column(list(df.columns))

    out = pd.DataFrame({"text": df[text_col].astype(str)})
    out["platform"] = "twitch"
    out["source_type"] = source_type_for(path)
    out["collection_date"] = date.today().isoformat()
    return out[COLUMNS]


def save(df: pd.DataFrame, filename: str) -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    df.dropna(subset=["text"]).drop_duplicates(subset=["text"]).to_csv(RAW_DIR / filename, index=False)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--twitch-input",
        type=Path,
        default=DEFAULT_TWITCH_INPUT,
        help="Local CSV, JSONL, or Parquet file with a text/message column.",
    )
    parser.add_argument(
        "--twitch-limit",
        type=int,
        default=DEFAULT_TWITCH_LIMIT,
        help="Maximum Twitch rows to import. Use 0 to import all rows.",
    )
    args = parser.parse_args()

    try:
        twitch = load_twitch(args.twitch_input, args.twitch_limit)
    except Exception as exc:
        raise SystemExit(f"[error] Failed to import Twitch corpus: {exc}") from exc

    save(twitch, "twitch_corpus_raw.csv")
    print(f"Saved {len(twitch)} Twitch-style rows.")


if __name__ == "__main__":
    main()
