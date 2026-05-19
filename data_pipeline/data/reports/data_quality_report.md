# Data Quality Report

## Overview

This report summarizes the curated dataset for **Brainrot to English: Agent-Driven Diachronic Linguistic Analysis**. The dataset is designed for Member 1 responsibilities: source ingestion, slang detection, preprocessing, translation-pair generation, split creation, and quality checking.

## Dataset Size

- Train-ready supervised rows: 431
- All processed source rows: 3853
- Active-learning candidate rows: 3422
- Duplicate, unsafe, or not-train-ready rows excluded from supervised split: 3696

## Source Coverage

Rows per source:

{
  "twitch": 337,
  "local_urban_dictionary_api": 94
}

Rows per platform:

{
  "twitch": 337,
  "urban_dictionary": 94
}

## Label Distributions

Sentiment distribution:

{
  "positive": 212,
  "negative": 161,
  "neutral": 55,
  "mixed": 3
}

Confidence distribution:

{
  "high": 305,
  "medium": 126
}

## Slang Coverage

Top 20 detected slang terms in the train-ready dataset:

{
  "feelsgoodman": 129,
  "madge": 80,
  "sadge": 32,
  "omegalul": 14,
  "idk": 12,
  "bro": 10,
  "pog": 8,
  "copium": 8,
  "real": 7,
  "king": 6,
  "lul": 6,
  "l": 5,
  "bet": 4,
  "fit": 4,
  "fr": 3,
  "rn": 3,
  "giving": 3,
  "pepehands": 3,
  "feelsstrongman": 3,
  "monkas": 3
}

Unknown term count across all processed source rows: 994

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

Rows with at least one quality flag: 3548

Quality flag counts:

{
  "contains_unknown_terms": 808,
  "clean": 305,
  "short_text": 2017,
  "missing_slang": 3322,
  "low_translation_confidence": 3322
}

Review action counts:

{
  "mine_or_ignore_no_dictionary_match": 2649,
  "review_unknown_terms": 682,
  "review_short_context": 91
}

## Train / Validation / Test Sizes

{
  "train": 344,
  "validation": 43,
  "test": 44
}

## Limitations

- Urban Dictionary-style definitions are user-generated and may contain subjective, noisy, or inconsistent explanations.
- Raw Twitch chat is excellent for mining emerging slang and emotes, but it is not automatically a supervised translation dataset.
- Dictionary-based slang detection provides transparency but may miss platform-specific emotes, sarcasm, and context-dependent meanings.
- Rule-based formal translations are suitable for bootstrapping but should be reviewed before final model fine-tuning.

## Recommendations

- Review `data/interim/active_learning_candidates.csv` for high-priority Twitch examples.
- Expand `config/slang_dictionary.json` using `data/interim/unknown_term_summary.csv`.
- Add human-reviewed manual translations for high-frequency unknown slang and emotes.
- Add demographic and temporal metadata when ethically and legally available to support diachronic analysis.
