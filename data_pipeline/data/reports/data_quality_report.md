# Data Quality Report

## Overview

This report summarizes the curated dataset for **Brainrot to English: Agent-Driven Diachronic Linguistic Analysis**. The dataset is designed for Member 1 responsibilities: source ingestion, slang detection, preprocessing, translation-pair generation, split creation, and quality checking.

## Dataset Size

- Total processed rows: 303
- Duplicate or unusable rows removed during curation: 1

## Source Coverage

Rows per source:

{
  "curated_local_fallback": 104,
  "twitch": 100,
  "twitter_x": 99
}

Rows per platform:

{
  "urban_dictionary": 104,
  "twitch": 100,
  "twitter_x": 99
}

## Label Distributions

Sentiment distribution:

{
  "positive": 138,
  "negative": 92,
  "neutral": 70,
  "mixed": 3
}

Confidence distribution:

{
  "high": 219,
  "medium": 81,
  "low": 3
}

## Slang Coverage

Top 20 detected slang terms:

{
  "w": 12,
  "rn": 11,
  "slaps": 10,
  "cooked": 9,
  "fr": 9,
  "mid": 9,
  "no cap": 9,
  "clean": 9,
  "ngl": 8,
  "locked in": 8,
  "sus": 8,
  "yapping": 8,
  "clutch": 8,
  "tweaking": 7,
  "valid": 7,
  "side quest": 7,
  "wild": 7,
  "nerfed": 7,
  "speedrun": 7,
  "bro": 5
}

Unknown term count: 81

Top unknown terms:

{
  "testing": 16,
  "passed": 4,
  "meeting": 4,
  "studying": 4,
  "confusing": 4,
  "timing": 4,
  "pathing": 4,
  "noodles": 3,
  "worked": 3,
  "walking": 3,
  "activated": 3,
  "took": 3,
  "door": 3,
  "saving": 3,
  "missing": 2,
  "called": 2,
  "handled": 2,
  "looks": 1,
  "forced": 1,
  "feed": 1
}

## Quality Flags

Rows with at least one quality flag: 84

Quality flag counts:

{
  "clean": 219,
  "short_text": 7,
  "contains_unknown_terms": 76,
  "missing_slang": 3,
  "low_translation_confidence": 3
}

## Train / Validation / Test Sizes

{
  "train": 242,
  "validation": 30,
  "test": 31
}

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
