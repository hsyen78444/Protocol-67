# Dataset Description

## Objective

This dataset supports the project **Brainrot to English: Agent-Driven Diachronic Linguistic Analysis** by converting informal internet slang examples into structured, train-ready translation pairs. The main learning target is a mapping from slang-heavy short text to clearer formal English while preserving source metadata, sentiment tendency, and confidence indicators.

## Data Source Types

The pipeline combines Urban Dictionary-style definitions, Twitter/X-style short posts, Twitch-style live chat messages, and optional manual annotations. These source types represent both explanatory slang definitions and natural short-form usage.

## Urban Dictionary-Style Source

Urban Dictionary-style records provide term definitions and examples. This source is useful because it captures community explanations of slang, but it is noisy, subjective, and user-generated. The collection script therefore includes retries, metadata preservation, and a curated fallback dataset.

## Twitter/X-Style Source

Twitter/X-style data represents short public posts where slang is often compressed, contextual, and rapidly changing. The project does not scrape Twitter/X directly. Instead, it supports local CSV and JSONL imports from approved exports or public datasets.

## Twitch-Style Source

Twitch-style chat messages provide fast, conversational internet language. They are useful for short messages, gaming slang, meme language, and repeated discourse markers.

## Manual Annotation Source

Manual annotations can be added through `data/raw/manual_annotations.csv`. Human review is especially important for ambiguous slang, emerging terms, and examples marked as low confidence.

## Final Dataset Schema

The final processed dataset is saved as `data/processed/brainrot_clean_dataset.csv` with these columns:

- `id`: stable processed-row identifier
- `raw_text`: original source text
- `clean_text`: normalized text after preprocessing
- `detected_slang_terms`: dictionary-matched slang terms
- `formal_translation`: rule-based formal English translation
- `sentiment`: positive, negative, neutral, or mixed
- `confidence_label`: high, medium, or low
- `source`: source metadata
- `platform`: source platform category
- `unknown_terms`: informal-looking terms not in the dictionary
- `quality_flags`: review indicators such as missing slang or unknown terms

## Downstream Support

The dataset supports model fine-tuning by providing paired informal and formal text. It supports sentiment analysis through rule-based weak labels. It supports confidence scoring through known/unknown slang coverage and quality flags. It supports an active learning loop by identifying examples that need human review, especially low-confidence rows and rows with unknown slang.
