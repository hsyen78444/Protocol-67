Protocol-67/
├── .git/
├── .gitattributes
├── .gitignore
├── README.md
├── Python Project.md
├── Python Project.docx
├── Project Structure.md
│
├── backend/
│   ├── .env.example
│   ├── README.md
│   ├── requirements.txt
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── db.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   └── services/
│   │       ├── __init__.py
│   │       ├── sentiment.py
│   │       └── translation.py
│   └── docs/
│       └── database_schema.md
│
├── data_pipeline/
│   ├── README.md
│   ├── requirements.txt
│   ├── config/
│   │   ├── slang_dictionary.json
│   │   └── slang_seed_terms.txt
│   ├── data/
│   │   ├── raw/
│   │   │   ├── urban_dictionary_raw.csv
│   │   │   ├── twitch_corpus_raw.csv
│   │   │   └── manual_annotations.csv
│   │   ├── interim/
│   │   │   ├── merged_raw_dataset.csv
│   │   │   ├── all_processed_rows.csv
│   │   │   ├── candidate_slang_pairs.csv
│   │   │   ├── unknown_term_summary.csv
│   │   │   └── active_learning_candidates.csv
│   │   ├── processed/
│   │   │   ├── brainrot_clean_dataset.csv
│   │   │   ├── train.csv
│   │   │   ├── train.jsonl
│   │   │   ├── validation.csv
│   │   │   ├── validation.jsonl
│   │   │   ├── test.csv
│   │   │   └── test.jsonl
│   │   └── reports/
│   │       ├── data_quality_report.md
│   │       └── dataset_statistics.json
│   ├── documentation/
│   │   ├── data_source_strategy.md
│   │   ├── dataset_description.md
│   │   ├── ethical_considerations.md
│   │   ├── preprocessing_method.md
│   │   └── member1_contribution_summary.md
│   └── scripts/
│       ├── 01_collect_urban_dictionary.py
│       ├── 02_import_social_corpus.py
│       ├── 03_merge_sources.py
│       ├── 04_preprocess_dataset.py
│       ├── 05_generate_train_val_test.py
│       └── 06_generate_data_quality_report.py
│
├── frontend/
│   ├── .env.example
│   ├── README.md
│
└── model_service/
    ├── README.md
    ├── requirements.txt
    ├── scripts/
    │   ├── prepare_dataset.py
    │   ├── train_lora.py
    │   └── evaluate.py
    └── src/
        ├── __init__.py
        ├── baseline_translator.py
        └── translator.py