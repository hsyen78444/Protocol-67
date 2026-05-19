# Data Quality Report

## Overview

This report summarizes the curated dataset for **Brainrot to English: Agent-Driven Diachronic Linguistic Analysis**. The dataset is designed for Member 1 responsibilities: source ingestion, slang detection, preprocessing, translation-pair generation, split creation, and quality checking.

## Dataset Size

- Total processed rows: 304
- Duplicate or unusable rows removed during curation: 3

## Source Coverage

Rows per source:

{
  "local_urban_dictionary_api": 104,
  "twitter_x": 100,
  "twitch": 100
}

Rows per platform:

{
  "urban_dictionary": 104,
  "twitter_x": 100,
  "twitch": 100
}

## Label Distributions

Sentiment distribution:

{
  "positive": 133,
  "negative": 88,
  "neutral": 79,
  "mixed": 4
}

Confidence distribution:

{
  "high": 178,
  "medium": 116,
  "low": 10
}

## Slang Coverage

Top 20 detected slang terms:

{
  "w": 13,
  "rn": 11,
  "bro": 10,
  "fr": 9,
  "cooked": 9,
  "no cap": 9,
  "slaps": 9,
  "clean": 9,
  "ngl": 8,
  "mid": 8,
  "sus": 8,
  "yapping": 8,
  "clutch": 8,
  "tweaking": 7,
  "locked in": 7,
  "valid": 7,
  "side quest": 7,
  "wild": 7,
  "nerfed": 7,
  "speedrun": 7
}

Unknown term count: 189

Top unknown terms:

{
  "testing": 16,
  "good": 7,
  "too": 6,
  "took": 4,
  "going": 4,
  "door": 4,
  "studying": 4,
  "confusing": 4,
  "timing": 4,
  "pathing": 4,
  "being": 3,
  "died": 3,
  "cool": 3,
  "noodles": 3,
  "worked": 3,
  "walking": 3,
  "meeting": 3,
  "activated": 3,
  "passed": 3,
  "saving": 3
}

## Quality Flags

Rows with at least one quality flag: 126

Quality flag counts:

{
  "contains_unknown_terms": 116,
  "clean": 178,
  "short_text": 6,
  "missing_slang": 10,
  "low_translation_confidence": 10
}

## Train / Validation / Test Sizes

{
  "train": 243,
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
