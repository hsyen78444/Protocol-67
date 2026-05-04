# Brainrot to English: Agent-Driven Diachronic Linguistic Analysis

## Scope

This folder contains the **Data Engineering & Preprocessing** deliverable. It covers data collection, dataset curation, preprocessing, slang detection, train-ready dataset generation, data quality reporting, and documentation.

It does not implement model fine-tuning, LoRA, FastAPI, PostgreSQL, or the full agent.

## Pipeline Architecture

1. Collect Urban Dictionary-style definitions and examples.
2. Import Twitter/X-style and Twitch-style corpora from local files or generate safe fallback corpora.
3. Merge all raw sources while preserving source metadata.
4. Clean text, detect slang, generate formal translations, assign sentiment and confidence labels.
5. Split the dataset into train, validation, and test sets.
6. Generate professional data quality reports.

## Folder Structure

```text
data_pipeline/
├── config/
├── data/
│   ├── raw/
│   ├── interim/
│   ├── processed/
│   └── reports/
├── scripts/
├── documentation/
├── README.md
└── requirements.txt
```

## Setup

```bash
pip install -r requirements.txt
```

## Run Commands

Run from the `data_pipeline` folder:

```bash
python scripts/01_collect_urban_dictionary.py
python scripts/02_import_social_corpus.py
python scripts/03_merge_sources.py
python scripts/04_preprocess_dataset.py
python scripts/05_generate_train_val_test.py
python scripts/06_generate_data_quality_report.py
```

Optional local corpus imports:

```bash
python scripts/02_import_social_corpus.py --twitter-input path/to/twitter.csv --twitch-input path/to/twitch.jsonl
```

Input files should contain a `text` column. If no files are provided, the script generates safe fallback corpora with at least 100 Twitter/X-style rows and 100 Twitch-style rows.

## Expected Outputs

- `data/raw/urban_dictionary_raw.csv`
- `data/raw/twitter_corpus_raw.csv`
- `data/raw/twitch_corpus_raw.csv`
- `data/interim/merged_raw_dataset.csv`
- `data/processed/brainrot_clean_dataset.csv`
- `data/processed/train.csv`
- `data/processed/validation.csv`
- `data/processed/test.csv`
- `data/reports/data_quality_report.md`
- `data/reports/dataset_statistics.json`

## Example Processed Row

| raw_text | detected_slang_terms | formal_translation | sentiment | confidence_label |
|---|---|---|---|---|
| bro is cooked fr | bro\|cooked\|fr | He is in serious trouble, for real. | negative | high |

## Troubleshooting

- If the Urban Dictionary API fails, the collector writes curated fallback rows so the pipeline can continue.
- If `scikit-learn` is missing, run `pip install -r requirements.txt`.
- If real social data is unavailable, use the fallback corpus for coursework testing.
- If many rows have `contains_unknown_terms`, expand `config/slang_dictionary.json` and rerun preprocessing.

## How Other Members Can Use the Dataset

Modelling members can use `data/processed/train.csv`, `validation.csv`, and `test.csv` for fine-tuning and evaluation. The recommended input column is `clean_text`, and the target column is `formal_translation`. API and database members can use the same schema for request/response design, confidence display, sentiment labels, and active learning queues.
