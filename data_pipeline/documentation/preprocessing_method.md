# Preprocessing Method

## Text Normalization

The preprocessing script lowercases text, removes URLs, removes `@mentions`, preserves hashtag words by deleting only the `#` symbol, normalizes repeated characters, and reduces excessive punctuation.

## Noise Removal

Rows with empty text are removed. Exact duplicate clean texts are removed before split generation. A simple blocklist filters unsafe or offensive rows so that the coursework dataset remains safe and reviewable.

## Slang Phrase Matching

The slang detector uses dictionary-based matching. Multi-word phrases are matched before single-word terms so expressions such as `no cap`, `let him cook`, `hits different`, and `main character` are preserved as complete units. Short terms such as `w` and `l` are matched only as standalone tokens.

## Slang Expansion

Formal translation is rule-based. Known slang terms are replaced with formal meanings from `config/slang_dictionary.json`, with a small set of contextual replacements for common terms such as `bro`, `fit`, `fr`, and `ngl`.

## Unknown Term Detection

The script identifies informal-looking tokens that are not in the slang dictionary. This produces an `unknown_terms` field that can be used by later members for active learning, annotation queues, and dictionary expansion.

## Quality Flagging

Rows are assigned quality flags:

- `missing_slang` when no known slang was detected
- `short_text` when text is very short
- `contains_unknown_terms` when unknown informal terms appear
- `low_translation_confidence` when translation is mostly unchanged
- `clean` when no review issue is detected

## Sentiment Labelling

Sentiment is inferred from the detected terms in the slang dictionary. If positive and negative slang appear together, the row is labelled `mixed`. If all detected terms are neutral, the row is labelled `neutral`.

## Train / Validation / Test Generation

The split script removes duplicate `clean_text` rows and creates reproducible 80/10/10 train, validation, and test files with a fixed random seed. Stratified splitting is used when sentiment classes have enough examples.
