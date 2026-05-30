# Data Quality Report

## Overview

This report summarizes the curated dataset for **Brainrot to English: Agent-Driven Diachronic Linguistic Analysis**. The dataset is designed for Member 1 responsibilities: source ingestion, slang detection, preprocessing, translation-pair generation, split creation, and quality checking.

## Dataset Size

- Train-ready supervised rows: 107
- All processed source rows: 3960
- Active-learning candidate rows: 3853
- Duplicate, unsafe, or not-train-ready rows excluded from supervised split: 4127

## Source Coverage

Rows per source:

{
  "manual_annotation": 107
}

Rows per platform:

{
  "manual": 107
}

## Label Distributions

Sentiment distribution:

{
  "positive": 44,
  "neutral": 34,
  "negative": 29
}

Confidence distribution:

{
  "high": 107
}

## Slang Coverage

Top 20 detected slang terms in the train-ready dataset:

{
  "clean": 2,
  "fr": 1,
  "ngl": 1,
  "idk": 1,
  "imo": 1,
  "rn": 1,
  "mid": 1,
  "cooked": 1,
  "ate": 1,
  "slay": 1,
  "rizz": 1,
  "cap": 1,
  "no cap": 1,
  "ratioed": 1,
  "w": 1,
  "l": 1,
  "tweaking": 1,
  "slaps": 1,
  "goated": 1,
  "sus": 1
}

Unknown term count across all processed source rows: 1021

Top unknown terms:

{
  "too": 32,
  "larry": 19,
  "theultracoolcutiebobo": 15,
  "smadging": 14,
  "fucking": 12,
  "licked": 12,
  "xoosd": 10,
  "jazzy": 10,
  "lol": 9,
  "cool": 8,
  "randomping": 7,
  "wicked": 7,
  "snoopydoly": 7,
  "razzy": 7,
  "jazzykat": 7,
  "peepopissed": 7,
  "fixed": 6,
  "sorry": 6,
  "pulled": 6,
  "bapped": 6
}

## Quality Flags

Rows with at least one quality flag: 3766

Quality flag counts:

{
  "contains_unknown_terms": 808,
  "clean": 194,
  "short_text": 2017,
  "definition_like_translation": 347,
  "missing_slang": 3322,
  "low_translation_confidence": 3322
}

Review action counts:

{
  "mine_or_ignore_no_dictionary_match": 2649,
  "review_unknown_terms": 808,
  "review_translation_quality": 305,
  "review_short_context": 91
}

## Train / Validation / Test Sizes

{
  "train": 85,
  "validation": 10,
  "test": 12
}

## Limitations

- Urban Dictionary-style definitions are user-generated and may contain subjective, noisy, or inconsistent explanations.
- Raw Twitch chat is excellent for mining emerging slang and emotes, but it is not automatically a supervised translation dataset.
- Dictionary-based slang detection provides transparency but may miss platform-specific emotes, sarcasm, and context-dependent meanings.
- Machine-generated formal translations are kept out of the supervised split and should be reviewed before they are added to fine-tuning data.

## Recommendations

- Review `data/interim/active_learning_candidates.csv` for high-priority Twitch examples.
- Expand `config/slang_dictionary.json` using `data/interim/unknown_term_summary.csv`.
- Add more human-reviewed manual translations for high-frequency unknown slang and emotes.
- Add demographic and temporal metadata when ethically and legally available to support diachronic analysis.
