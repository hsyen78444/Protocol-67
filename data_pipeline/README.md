# Protocol 67: Agent-Driven Diachronic Linguistic Analysis

## Scope

This folder contains the **Data Engineering & Preprocessing** deliverable. It covers data collection, dataset curation, preprocessing, slang detection, train-ready dataset generation, data quality reporting, and documentation.

It does not implement model fine-tuning, LoRA, FastAPI, PostgreSQL, or the full agent.

## Pipeline Flow

1. Collect Urban Dictionary-style definitions and examples from a compatible local API at `http://localhost:8080/api/search`, then fall back to curated local dictionary rows if the API is unavailable or too small. The local API can be cloned from `https://github.com/kashyap010/unofficial-urban-dictionary-api`.
2. Import a Twitch chat corpus from the local `train-00000-of-00001.parquet` file.
3. Merge all raw sources while preserving source metadata.
4. Clean text, detect slang, generate formal translations, and separate train-ready rows from active-learning candidates.
5. Create reproducible train, validation, and test splits in CSV and model-ready JSONL format.
6. Generate Markdown and JSON data quality reports.

## Folder Structure

```text
data_pipeline/
|-- config/
|-- data/
|   |-- raw/
|   |-- interim/
|   |-- processed/
|   `-- reports/
|-- documentation/
|-- scripts/
|-- README.md
|-- requirements.txt
`-- train-00000-of-00001.parquet  # local datasource, ignored by Git
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

The Urban Dictionary collector expects a compatible local API by default. To run one locally, clone and start this API project:

```bash
git clone https://github.com/kashyap010/unofficial-urban-dictionary-api
```

After the API is running at `http://localhost:8080`, run the first pipeline script. To use a different compatible Urban Dictionary-style API, set `URBAN_DICTIONARY_API_BASE_URL` before running the first script.

## Twitch Datasource

Place the downloaded Twitch dataset at:

```text
data_pipeline/train-00000-of-00001.parquet
```

The downloaded Parquet file has a `Message` column. The importer reads that column, normalizes it to `text`, and writes `data/raw/twitch_corpus_raw.csv`.

By default, the importer reads 5,000 rows so local runs stay manageable:

```powershell
python scripts/02_import_social_corpus.py
```

To use a different local file:

```powershell
python scripts/02_import_social_corpus.py --twitch-input path\to\twitch.parquet
```

To change the row limit:

```powershell
python scripts/02_import_social_corpus.py --twitch-limit 10000
```

Use `--twitch-limit 0` to import all rows. The full downloaded dataset has millions of rows, so importing all rows may take a long time and create large output files.

Dataset citation:

```bibtex
@misc{twitchchat2025,
  title = {Twitch Chat},
  author = {parkourer10},
  year = {2025},
  publisher = {Hugging Face Datasets},
  url = {https://huggingface.co/datasets/lparkourer10/twitch_chat}
}
```

## Expected Outputs

- `data/raw/urban_dictionary_raw.csv`
- `data/raw/twitch_corpus_raw.csv`
- `data/interim/merged_raw_dataset.csv`
- `data/interim/all_processed_rows.csv`
- `data/interim/candidate_slang_pairs.csv`
- `data/interim/active_learning_candidates.csv`
- `data/interim/unknown_term_summary.csv`
- `data/processed/brainrot_clean_dataset.csv`
- `data/processed/train.csv`
- `data/processed/validation.csv`
- `data/processed/test.csv`
- `data/processed/train.jsonl`
- `data/processed/validation.jsonl`
- `data/processed/test.jsonl`
- `data/reports/data_quality_report.md`
- `data/reports/dataset_statistics.json`

## Training vs Active Learning

The pipeline does not push every raw Twitch message into model fine-tuning. Twitch chat is noisy and often contains short messages, emotes, usernames, or terms that do not have a formal translation target yet.

Instead, preprocessing creates two tracks:

- `data/processed/brainrot_clean_dataset.csv`: train-ready supervised translation pairs.
- `data/interim/active_learning_candidates.csv`: rows that need review, dictionary expansion, or manual translation.

High-frequency unknown terms are summarized in `data/interim/unknown_term_summary.csv`. Review this file to decide which Twitch emotes, memes, and slang terms should be added to `config/slang_dictionary.json` or manually annotated.

## Git Hygiene

Do not commit virtual environments, caches, local secrets, temporary files, or downloaded datasets. The root `.gitignore` ignores:

- `.venv/`, `venv/`, `env/`, and `ENV/`
- Python cache files such as `__pycache__/` and `*.pyc`
- local environment files such as `.env`
- test/tool caches such as `.pytest_cache/`, `.mypy_cache/`, and `.ruff_cache/`
- OS/editor noise such as `.DS_Store`, `Thumbs.db`, and `*.log`
- local Parquet datasources such as `data_pipeline/*.parquet`

The current CSV and report files under `data/` are tracked in this repository. Keep them tracked if they are coursework deliverables; otherwise, remove them from Git tracking and add broader `data_pipeline/data/` ignore rules.

## Troubleshooting

- If the local Urban Dictionary-style API fails, the collector writes curated fallback rows so the pipeline can continue.
- If `scikit-learn`, `pandas`, `pyarrow`, or `requests` is missing, reactivate the virtual environment and run `python -m pip install -r requirements.txt`.
- If Twitch import fails, confirm `train-00000-of-00001.parquet` exists in `data_pipeline/` and contains a `Message`, `message`, or `text` column.
- If many rows have `contains_unknown_terms`, expand `config/slang_dictionary.json` and rerun preprocessing.

## Dataset Use

Modeling members can use `data/processed/train.csv`, `validation.csv`, and `test.csv` for fine-tuning and evaluation. The recommended input column is `clean_text`, and the target column is `formal_translation`.
