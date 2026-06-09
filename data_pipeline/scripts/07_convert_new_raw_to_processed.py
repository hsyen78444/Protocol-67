"""Convert inverted new_raw JSONL files into Protocol 67 finetuning splits.

The files in data/new_raw use:
    source = formal English
    target = brainrot/slang

The model expects:
    input = brainrot/slang
    output = formal English
"""

from __future__ import annotations

import csv
import json
import random
import re
import shutil
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
NEW_RAW_DIR = ROOT / "data" / "new_raw"
PROCESSED_DIR = ROOT / "data" / "processed"
DICT_FILE = ROOT / "config" / "slang_dictionary.json"
REVIEW_FILE = PROCESSED_DIR / "new_raw_review.csv"
STATS_FILE = PROCESSED_DIR / "new_raw_conversion_stats.json"
RANDOM_SEED = 42
INSTRUCTION = "Translate the following internet slang or brainrot text into clear formal English."

CSV_COLUMNS = [
    "id",
    "raw_text",
    "clean_text",
    "detected_slang_terms",
    "formal_translation",
    "sentiment",
    "confidence_label",
    "source",
    "platform",
    "unknown_terms",
    "quality_flags",
    "training_ready",
]

REVIEW_COLUMNS = [
    "source_file",
    "line_number",
    "raw_text",
    "clean_text",
    "formal_translation",
    "detected_slang_terms",
    "quality_flags",
    "review_reason",
]

SPLIT_FILES = [
    "brainrot_clean_dataset.csv",
    "train.csv",
    "validation.csv",
    "test.csv",
    "train.jsonl",
    "validation.jsonl",
    "test.jsonl",
]

URL_RE = re.compile(r"https?://\S+|www\.\S+")
MENTION_RE = re.compile(r"@\w+")
HASHTAG_RE = re.compile(r"#(\w+)")
PUNCT_RE = re.compile(r"[!?.,;:]{2,}")
TOKEN_RE = re.compile(r"\b[a-z][a-z0-9']*\b")


def load_dictionary() -> dict[str, dict[str, str]]:
    return json.loads(DICT_FILE.read_text(encoding="utf-8"))


def normalize_text(text: str) -> str:
    text = str(text).lower()
    text = URL_RE.sub(" ", text)
    text = MENTION_RE.sub(" ", text)
    text = HASHTAG_RE.sub(r"\1", text)
    text = re.sub(r"(.)\1{2,}", r"\1\1", text)
    text = PUNCT_RE.sub(".", text)
    text = re.sub(r"[^a-z0-9\s'.,!?-]", " ", text)
    return re.sub(r"\s+", " ", text).strip(" .,!?-")


def normalize_formal_translation(text: str) -> str:
    text = re.sub(r"\s+", " ", str(text)).strip()
    if not text:
        return ""
    text = text[0].upper() + text[1:]
    if text[-1] not in ".!?":
        text += "."
    return text


def split_terms(dictionary: dict[str, dict[str, str]]) -> tuple[list[str], list[str]]:
    phrase_terms = sorted(
        [term for term in dictionary if " " in term],
        key=len,
        reverse=True,
    )
    single_terms = sorted(
        [term for term in dictionary if " " not in term],
        key=len,
        reverse=True,
    )
    return phrase_terms, single_terms


def detect_terms(
    text: str,
    phrase_terms: list[str],
    single_terms: list[str],
) -> list[str]:
    detected: list[str] = []
    protected = text

    for term in phrase_terms:
        pattern = re.compile(rf"(?<!\w){re.escape(term)}(?!\w)")
        if pattern.search(protected):
            detected.append(term)
            protected = pattern.sub(" ", protected)

    tokens = set(TOKEN_RE.findall(protected))
    for term in single_terms:
        if term in tokens:
            detected.append(term)

    return detected


def sentiment_label(
    detected: list[str],
    dictionary: dict[str, dict[str, str]],
) -> str:
    labels = [dictionary[term]["sentiment"] for term in detected if term in dictionary]
    non_neutral = {label for label in labels if label != "neutral"}
    if len(non_neutral) > 1:
        return "mixed"
    if non_neutral:
        return next(iter(non_neutral))
    return "neutral"


def backup_existing_processed_files() -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = PROCESSED_DIR / f"backup_before_new_raw_{timestamp}"
    backup_dir.mkdir(parents=True, exist_ok=False)

    for name in SPLIT_FILES:
        src = PROCESSED_DIR / name
        if src.exists():
            shutil.copy2(src, backup_dir / name)

    return backup_dir


def read_new_raw_records() -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for path in sorted(NEW_RAW_DIR.glob("*.jsonl")):
        with path.open("r", encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                if not line.strip():
                    continue
                obj = json.loads(line)
                records.append(
                    {
                        "source_file": path.name,
                        "line_number": line_number,
                        "source": str(obj.get("source", "")),
                        "target": str(obj.get("target", "")),
                    }
                )
    return records


def review_row(
    record: dict[str, Any],
    clean_text: str,
    formal_translation: str,
    detected: list[str],
    flags: list[str],
    reason: str,
) -> dict[str, Any]:
    return {
        "source_file": record["source_file"],
        "line_number": record["line_number"],
        "raw_text": record["target"],
        "clean_text": clean_text,
        "formal_translation": formal_translation,
        "detected_slang_terms": "|".join(detected),
        "quality_flags": "|".join(flags),
        "review_reason": reason,
    }


def build_rows() -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    dictionary = load_dictionary()
    phrase_terms, single_terms = split_terms(dictionary)
    accepted: list[dict[str, Any]] = []
    review: list[dict[str, Any]] = []
    seen_clean_text: set[str] = set()
    stats: Counter[str] = Counter()

    for record in read_new_raw_records():
        stats["raw_rows"] += 1
        raw_text = record["target"]
        clean_text = normalize_text(raw_text)
        formal_translation = normalize_formal_translation(record["source"])
        detected = detect_terms(clean_text, phrase_terms, single_terms)
        flags: list[str] = []

        if not clean_text:
            flags.append("empty_clean_text")
        if not formal_translation:
            flags.append("empty_formal_translation")
        if len(clean_text.split()) < 4:
            flags.append("short_text")
        if clean_text.rstrip(".") == formal_translation.lower().rstrip("."):
            flags.append("same_as_formal_translation")
        if not detected:
            flags.append("missing_slang")
        if clean_text in seen_clean_text:
            flags.append("duplicate_clean_text")

        if flags:
            reason = flags[0]
            stats[f"review_{reason}"] += 1
            review.append(
                review_row(
                    record,
                    clean_text,
                    formal_translation,
                    detected,
                    flags,
                    reason,
                )
            )
            continue

        seen_clean_text.add(clean_text)
        stats["accepted_rows"] += 1
        accepted.append(
            {
                "raw_text": raw_text,
                "clean_text": clean_text,
                "detected_slang_terms": "|".join(detected),
                "formal_translation": formal_translation,
                "sentiment": sentiment_label(detected, dictionary),
                "confidence_label": "high",
                "source": "new_raw_parallel",
                "platform": "synthetic",
                "unknown_terms": "",
                "quality_flags": "clean",
                "training_ready": True,
            }
        )

    accepted.sort(key=lambda row: row["clean_text"])
    for idx, row in enumerate(accepted, start=1):
        row["id"] = idx

    stats["review_rows"] = len(review)
    stats["unique_accepted_clean_text"] = len({row["clean_text"] for row in accepted})
    stats["sentiment_counts"] = dict(Counter(row["sentiment"] for row in accepted))
    return accepted, review, dict(stats)


def split_rows(rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    shuffled = rows[:]
    random.Random(RANDOM_SEED).shuffle(shuffled)

    train_end = int(len(shuffled) * 0.80)
    validation_end = train_end + int(len(shuffled) * 0.10)

    splits = {
        "train": shuffled[:train_end],
        "validation": shuffled[train_end:validation_end],
        "test": shuffled[validation_end:],
    }
    return {
        name: sorted(split, key=lambda row: row["id"])
        for name, split in splits.items()
    }


def write_csv(path: Path, rows: list[dict[str, Any]], columns: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def jsonl_record(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "instruction": INSTRUCTION,
        "input": row["clean_text"],
        "output": row["formal_translation"],
        "metadata": {
            "source": row["source"],
            "platform": row["platform"],
            "sentiment": row["sentiment"],
            "confidence_label": row["confidence_label"],
            "detected_slang_terms": row["detected_slang_terms"].split("|")
            if row["detected_slang_terms"]
            else [],
        },
    }


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(jsonl_record(row), ensure_ascii=False) + "\n")


def main() -> None:
    if not NEW_RAW_DIR.exists():
        raise FileNotFoundError(f"Missing new raw data directory: {NEW_RAW_DIR}")

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    backup_dir = backup_existing_processed_files()
    accepted, review, stats = build_rows()
    splits = split_rows(accepted)

    write_csv(PROCESSED_DIR / "brainrot_clean_dataset.csv", accepted, CSV_COLUMNS)
    write_csv(REVIEW_FILE, review, REVIEW_COLUMNS)

    for split_name, split_rows_for_name in splits.items():
        write_csv(PROCESSED_DIR / f"{split_name}.csv", split_rows_for_name, CSV_COLUMNS)
        write_jsonl(PROCESSED_DIR / f"{split_name}.jsonl", split_rows_for_name)

    stats.update(
        {
            "backup_dir": str(backup_dir),
            "train_rows": len(splits["train"]),
            "validation_rows": len(splits["validation"]),
            "test_rows": len(splits["test"]),
            "random_seed": RANDOM_SEED,
        }
    )
    STATS_FILE.write_text(json.dumps(stats, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"Backed up previous processed files to {backup_dir}")
    print(f"Accepted train-ready rows: {len(accepted)}")
    print(f"Review rows: {len(review)}")
    print(f"Train rows: {len(splits['train'])}")
    print(f"Validation rows: {len(splits['validation'])}")
    print(f"Test rows: {len(splits['test'])}")
    print(f"Wrote stats to {STATS_FILE}")


if __name__ == "__main__":
    main()
