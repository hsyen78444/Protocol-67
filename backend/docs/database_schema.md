# Database Schema Guide

Use SQLite for the first working demo. It is simple, file-based, and enough for coursework. Use PostgreSQL later if the team deploys publicly or needs concurrent writes.

## translations

Stores every call to `/translate`.

| Column | Type | Notes |
|---|---|---|
| id | integer | Primary key |
| input_text | text | Original user input |
| output_text | text | Formal translation |
| sentiment | string | positive, negative, neutral, mixed |
| confidence | float | 0.0 to 1.0 |
| detected_slang_terms | text/json | Terms detected by model or dictionary |
| unknown_terms | text/json | Terms needing review |
| model_version | string | baseline-v1, lora-v1, etc. |
| created_at | datetime | Request timestamp |

## unknown_terms

Stores terms that the translator cannot confidently explain.

| Column | Type | Notes |
|---|---|---|
| id | integer | Primary key |
| term | string | Unknown slang/emote/token |
| example_text | text | User sentence containing term |
| frequency | integer | Optional aggregate count |
| status | string | open, reviewing, resolved, ignored |
| proposed_meaning | text | Reviewer-proposed explanation |
| created_at | datetime | First seen |
| resolved_at | datetime | Optional |

## feedback

Stores user corrections.

| Column | Type | Notes |
|---|---|---|
| id | integer | Primary key |
| translation_id | integer | Optional link to translations |
| input_text | text | Original user input |
| original_translation | text | Model/API output |
| corrected_translation | text | User correction |
| notes | text | Optional reviewer notes |
| created_at | datetime | Feedback timestamp |

## model_runs

Tracks model versions used in demos and reports.

| Column | Type | Notes |
|---|---|---|
| id | integer | Primary key |
| model_version | string | Human-readable version |
| base_model | string | Base model name |
| dataset_version | string | Dataset/report date |
| metrics_json | text/json | BLEU/ROUGE/exact match/manual scores |
| created_at | datetime | Training or registration timestamp |
