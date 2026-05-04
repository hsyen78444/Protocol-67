"""Generate Markdown and JSON reports for dataset quality review."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
INTERIM = ROOT / "data" / "interim" / "merged_raw_dataset.csv"
DATASET = PROCESSED / "brainrot_clean_dataset.csv"
REPORT_DIR = ROOT / "data" / "reports"


def split_counts() -> dict:
    counts = {}
    for name in ["train", "validation", "test"]:
        path = PROCESSED / f"{name}.csv"
        if path.exists():
            counts[name] = len(pd.read_csv(path))
    return counts


def pipe_counter(series: pd.Series) -> Counter:
    counter: Counter = Counter()
    for value in series.fillna(""):
        for item in str(value).split("|"):
            if item:
                counter[item] += 1
    return counter


def main() -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(DATASET).fillna("")
    merged = pd.read_csv(INTERIM).fillna("") if INTERIM.exists() else pd.DataFrame()
    slang_counts = pipe_counter(df["detected_slang_terms"])
    unknown_counts = pipe_counter(df["unknown_terms"])
    flag_counts = pipe_counter(df["quality_flags"])
    duplicates_removed = max(len(merged) - len(df), 0) if not merged.empty else 0

    stats = {
        "total_rows": int(len(df)),
        "rows_per_source": df["source"].value_counts().to_dict(),
        "rows_per_platform": df["platform"].value_counts().to_dict(),
        "sentiment_distribution": df["sentiment"].value_counts().to_dict(),
        "confidence_distribution": df["confidence_label"].value_counts().to_dict(),
        "top_20_slang_terms": dict(slang_counts.most_common(20)),
        "total_unknown_terms": int(sum(unknown_counts.values())),
        "top_unknown_terms": dict(unknown_counts.most_common(20)),
        "rows_with_quality_flags": int((df["quality_flags"] != "clean").sum()),
        "quality_flag_counts": dict(flag_counts),
        "duplicate_rows_removed": int(duplicates_removed),
        "split_sizes": split_counts(),
    }

    (REPORT_DIR / "dataset_statistics.json").write_text(json.dumps(stats, indent=2), encoding="utf-8")

    report = f"""# Data Quality Report

## Overview

This report summarizes the curated dataset for **Brainrot to English: Agent-Driven Diachronic Linguistic Analysis**. The dataset is designed for Member 1 responsibilities: source ingestion, slang detection, preprocessing, translation-pair generation, split creation, and quality checking.

## Dataset Size

- Total processed rows: {stats["total_rows"]}
- Duplicate or unusable rows removed during curation: {stats["duplicate_rows_removed"]}

## Source Coverage

Rows per source:

{json.dumps(stats["rows_per_source"], indent=2)}

Rows per platform:

{json.dumps(stats["rows_per_platform"], indent=2)}

## Label Distributions

Sentiment distribution:

{json.dumps(stats["sentiment_distribution"], indent=2)}

Confidence distribution:

{json.dumps(stats["confidence_distribution"], indent=2)}

## Slang Coverage

Top 20 detected slang terms:

{json.dumps(stats["top_20_slang_terms"], indent=2)}

Unknown term count: {stats["total_unknown_terms"]}

Top unknown terms:

{json.dumps(stats["top_unknown_terms"], indent=2)}

## Quality Flags

Rows with at least one quality flag: {stats["rows_with_quality_flags"]}

Quality flag counts:

{json.dumps(stats["quality_flag_counts"], indent=2)}

## Train / Validation / Test Sizes

{json.dumps(stats["split_sizes"], indent=2)}

## Limitations

- Urban Dictionary-style definitions are user-generated and may contain subjective, noisy, or inconsistent explanations.
- Synthetic fallback social data is useful for pipeline testing but cannot fully represent real platform diversity.
- Dictionary-based slang detection provides transparency but may miss emerging spellings, sarcasm, and context-dependent meanings.
- Rule-based formal translations are suitable for bootstrapping but should be reviewed before final model fine-tuning.

## Recommendations

- Add human-reviewed manual annotations for ambiguous and high-frequency slang.
- Replace fallback corpora with approved public datasets or exported data that complies with platform terms.
- Expand the slang dictionary iteratively using active learning feedback from low-confidence examples.
- Add demographic and temporal metadata when ethically and legally available to support diachronic analysis.
"""
    (REPORT_DIR / "data_quality_report.md").write_text(report, encoding="utf-8")
    print(f"Wrote reports to {REPORT_DIR}")


if __name__ == "__main__":
    main()
