# Brainrot to English Data Pipeline

This folder contains the Member 1 data engineering deliverable for **Brainrot to English: Agent-Driven Diachronic Linguistic Analysis**. It covers data collection, dataset curation, preprocessing, slang detection, train/validation/test split generation, data quality reporting, and documentation.

It does not implement model fine-tuning, LoRA, FastAPI, PostgreSQL, or the full agent.

## Pipeline Flow

1. Collect Urban Dictionary-style definitions and examples from a compatible local API at `http://localhost:8080/api/search`, then fall back to curated local dictionary rows if the API is unavailable or too small.
2. Import Twitter/X-style and Twitch-style corpora from local CSV, JSONL, or Parquet files, or generate safe synthetic coursework fallback rows.
3. Merge all raw sources while preserving source metadata.
4. Clean text, detect slang, generate formal translations, assign sentiment labels, and flag quality issues.
5. Create reproducible train, validation, and test splits.
6. Generate Markdown and JSON data quality reports.

## Folder Structure

```text
data_pipeline/
├── config/
├── data/
│   ├── raw/
│   ├── interim/
│   ├── processed/
│   └── reports/
├── documentation/
├── scripts/
├── README.md
└── requirements.txt
```

## Create a Virtual Environment

Run these commands from the `data_pipeline` folder.

### Windows PowerShell

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If `py` is not available, use your installed Python executable:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### macOS or Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Run the Pipeline

Run each script from the `data_pipeline` folder:

```bash
python scripts/01_collect_urban_dictionary.py
python scripts/02_import_social_corpus.py
python scripts/03_merge_sources.py
python scripts/04_preprocess_dataset.py
python scripts/05_generate_train_val_test.py
python scripts/06_generate_data_quality_report.py
```

To use a different compatible Urban Dictionary-style API, set `URBAN_DICTIONARY_API_BASE_URL` before running the first script.

Optional local corpus imports:

```bash
python scripts/02_import_social_corpus.py --twitter-input path/to/twitter.csv --twitch-input path/to/twitch.jsonl
```

Input files should contain a `text` or `message` column. CSV, JSONL, and Parquet inputs are supported. If no files are provided, the script generates safe synthetic fallback corpora with at least 100 Twitter/X-style rows and 100 Twitch-style rows.

Example Hugging Face Parquet import:

```bash
python scripts/02_import_social_corpus.py --twitch-input "hf://datasets/lparkourer10/twitch_chat/data/train-00000-of-00001.parquet" --twitch-limit 5000
```

Use a row limit for large sources.

## Expected Outputs

- `data/raw/urban_dictionary_raw.csv`
- `data/raw/twitter_corpus_raw.csv`
- `data/raw/twitch_corpus_raw.csv`
- `data/interim/merged_raw_dataset.csv`
- `data/interim/candidate_slang_pairs.csv`
- `data/processed/brainrot_clean_dataset.csv`
- `data/processed/train.csv`
- `data/processed/validation.csv`
- `data/processed/test.csv`
- `data/reports/data_quality_report.md`
- `data/reports/dataset_statistics.json`

## Git Hygiene

Do not commit virtual environments, caches, local secrets, or temporary files. The root `.gitignore` ignores:

- `.venv/`, `venv/`, `env/`, and `ENV/`
- Python cache files such as `__pycache__/` and `*.pyc`
- local environment files such as `.env`
- test/tool caches such as `.pytest_cache/`, `.mypy_cache/`, and `.ruff_cache/`
- OS/editor noise such as `.DS_Store`, `Thumbs.db`, and `*.log`

The current CSV and report files under `data/` are tracked in this repository. Keep them tracked if they are coursework deliverables; otherwise, remove them from Git tracking and add broader `data_pipeline/data/` ignore rules.

## Troubleshooting

- If the local Urban Dictionary-style API fails, the collector writes curated fallback rows so the pipeline can continue.
- If `scikit-learn`, `pandas`, or `requests` is missing, reactivate the virtual environment and run `python -m pip install -r requirements.txt`.
- If real social data is unavailable, use the fallback corpus for coursework testing.
- If many rows have `contains_unknown_terms`, expand `config/slang_dictionary.json` and rerun preprocessing.

## Dataset Use

Modeling members can use `data/processed/train.csv`, `validation.csv`, and `test.csv` for fine-tuning and evaluation. The recommended input column is `clean_text`, and the target column is `formal_translation`.
