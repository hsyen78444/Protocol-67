# Data Quality Report

## Overview

This report summarizes the curated dataset for **Brainrot to English: Agent-Driven Diachronic Linguistic Analysis**. The dataset is designed for Member 1 responsibilities: source ingestion, slang detection, preprocessing, translation-pair generation, split creation, and quality checking.

## Dataset Size

- Total processed rows: 2504
- Duplicate or unusable rows removed during curation: 3

## Source Coverage

Rows per source:

{
  "twitter_x": 1200,
  "twitch": 1200,
  "local_urban_dictionary_api": 104
}

Rows per platform:

{
  "twitter_x": 1200,
  "twitch": 1200,
  "urban_dictionary": 104
}

## Label Distributions

Sentiment distribution:

{
  "positive": 1159,
  "negative": 745,
  "neutral": 559,
  "mixed": 41
}

Confidence distribution:

{
  "high": 1509,
  "medium": 948,
  "low": 47
}

## Slang Coverage

Top 20 detected slang terms:

{
  "w": 122,
  "rn": 121,
  "clean": 82,
  "fr": 81,
  "ngl": 81,
  "mid": 81,
  "cooked": 81,
  "no cap": 81,
  "tweaking": 81,
  "slaps": 81,
  "sus": 81,
  "locked in": 81,
  "yapping": 81,
  "valid": 81,
  "side quest": 81,
  "wild": 81,
  "clutch": 81,
  "nerfed": 81,
  "speedrun": 81,
  "bro": 47
}

Unknown term count: 1128

Top unknown terms:

{
  "meeting": 158,
  "testing": 120,
  "debugging": 120,
  "streaming": 120,
  "took": 41,
  "door": 41,
  "studying": 40,
  "confusing": 40,
  "noodles": 40,
  "worked": 40,
  "walking": 40,
  "timing": 40,
  "pathing": 40,
  "activated": 40,
  "passed": 40,
  "saving": 40,
  "good": 7,
  "too": 6,
  "going": 4,
  "being": 3
}

## Quality Flags

Rows with at least one quality flag: 995

Quality flag counts:

{
  "contains_unknown_terms": 957,
  "clean": 1509,
  "short_text": 3,
  "missing_slang": 47,
  "low_translation_confidence": 47
}

## Train / Validation / Test Sizes

{
  "train": 2003,
  "validation": 250,
  "test": 251
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
