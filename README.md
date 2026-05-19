# Protocol 67

## Project Title

**Protocol 67: An Agent-Driven Brainrot-to-English Translation and Sentiment Analysis System**

## Background

Internet vernacular evolves quickly. Slang, memes, abbreviations, emotes, and non-standard expressions from platforms such as Twitch, TikTok, Reddit, WhatsApp, Telegram, and Urban Dictionary can be difficult for non-native speakers, educators, researchers, older users, and NLP systems to interpret.

Protocol 67 translates highly contextual internet slang, commonly called "brainrot language", into formal English and returns sentiment, confidence, detected slang terms, and unknown terminology.

## System Goal

Build an end-to-end web application with:

- A fine-tuned or baseline slang-to-English translation model.
- A FastAPI backend.
- A database-backed active learning loop.
- A React JS frontend.
- Bonus-only optional integrations such as a Chrome extension or messaging helper.

## Current Data Pipeline

The `data_pipeline/` folder prepares the dataset for training and active learning.

Important outputs:

- `data_pipeline/data/processed/train.csv`
- `data_pipeline/data/processed/validation.csv`
- `data_pipeline/data/processed/test.csv`
- `data_pipeline/data/processed/train.jsonl`
- `data_pipeline/data/processed/validation.jsonl`
- `data_pipeline/data/processed/test.jsonl`
- `data_pipeline/data/interim/active_learning_candidates.csv`
- `data_pipeline/data/interim/unknown_term_summary.csv`

The recommended model input column is `clean_text`. The recommended target column is `formal_translation`.

## Architecture

```text
React Frontend
    |
    v
FastAPI Backend
    |
    |-- Translation API
    |     `-- model_service translator
    |
    |-- Sentiment + Confidence API
    |
    |-- Active Learning API
    |     `-- feedback + unknown terms
    |
    `-- SQLite Database
          |-- translations
          |-- feedback
          |-- unknown_terms
          `-- model_runs
```

SQLite is recommended for coursework speed. PostgreSQL is a good upgrade only if the project is deployed with multiple users.

## Team Task Distribution

### Member 2: Model Fine-Tuning and Translation Service

Main responsibility: make the translator work.

Folder ownership:

```text
model_service/
```

Tasks:

- Use `data_pipeline/data/processed/*.jsonl` for model training.
- Build a baseline translator first using `config/slang_dictionary.json`.
- Evaluate baseline output on `test.jsonl`.
- Fine-tune or adapt a small model with LoRA if compute allows.
- Keep one stable function for the backend:

```python
def translate_text(text: str) -> dict:
    return {
        "formal_translation": "...",
        "confidence": 0.85,
        "detected_slang_terms": ["..."],
        "unknown_terms": ["..."],
        "model_version": "baseline-v1"
    }
```

Fine-tuning steps:

1. Run the data pipeline and confirm `train.jsonl`, `validation.jsonl`, and `test.jsonl` exist.
2. Run `model_service/scripts/prepare_dataset.py` to inspect the training records.
3. Run the dictionary baseline in `model_service/src/baseline_translator.py`.
4. Evaluate baseline with `model_service/scripts/evaluate.py`.
5. Choose a small base model that fits available hardware.
6. Convert JSONL records into instruction prompts:

```text
Instruction: Translate the following internet slang or brainrot text into clear formal English.
Input: bro is cooked fr
Output: He is in serious trouble, for real.
```

7. Fine-tune with LoRA/QLoRA and save adapters under `model_service/outputs/` or `model_service/models/`.
8. Update `model_service/src/translator.py` so the backend can call the final translator.
9. Record base model, dataset version, hyperparameters, and example outputs in `model_service/README.md`.

Deliverables:

- Baseline translator.
- Fine-tuning script or documented attempt.
- Evaluation result.
- Stable `translate_text()` function.

### Member 3: Backend A, API and Model Integration

Main responsibility: expose the translator through FastAPI.

Folder ownership:

```text
backend/app/main.py
backend/app/schemas.py
backend/app/services/
```

Tasks:

- Build FastAPI routes.
- Define Pydantic request/response schemas.
- Connect `/translate` to `model_service`.
- Add CORS for React.
- Add validation and clean error responses.
- Coordinate API contract with frontend.

Core endpoints:

```text
GET  /health
POST /translate
GET  /stats
```

Main response contract:

```json
{
  "input": "chat this run is cooked fr",
  "formal_translation": "This attempt is in serious trouble, for real.",
  "sentiment": "negative",
  "confidence": 0.82,
  "detected_slang_terms": ["cooked", "fr"],
  "unknown_terms": ["chat"],
  "model_version": "baseline-v1"
}
```

Deliverables:

- Working FastAPI server.
- `/translate` endpoint.
- API README or Swagger screenshots.
- Integration with Member 2 translator.

### Member 4: Backend B, Database and Active Learning

Main responsibility: make the system remember feedback and unknown slang.

Folder ownership:

```text
backend/app/db.py
backend/app/models.py
backend/docs/database_schema.md
```

Tasks:

- Set up SQLite with SQLAlchemy.
- Create database tables.
- Store translation logs.
- Store unknown terms from model/API responses.
- Store user corrections from frontend feedback.
- Add review/update endpoints for active learning.

Recommended database tables:

```text
translations
- id
- input_text
- output_text
- sentiment
- confidence
- detected_slang_terms
- unknown_terms
- model_version
- created_at

unknown_terms
- id
- term
- example_text
- frequency
- status
- proposed_meaning
- created_at
- resolved_at

feedback
- id
- translation_id
- input_text
- original_translation
- corrected_translation
- notes
- created_at

model_runs
- id
- model_version
- base_model
- dataset_version
- metrics_json
- created_at
```

Active learning endpoints:

```text
POST /feedback
GET  /unknown-terms
POST /unknown-terms/{term_id}/resolve
```

Deliverables:

- SQLite database setup.
- SQLAlchemy models.
- Feedback persistence.
- Unknown-term review flow.
- Basic stats for demo.

### Member 5: React Frontend

Main responsibility: build the user interface.

Folder ownership:

```text
frontend/
```

Tasks:

- Build a React JS app, preferably with Vite.
- Call FastAPI `/translate`.
- Display translation, sentiment, confidence, detected slang, and unknown terms.
- Add feedback form for corrected translations.
- Add loading, error, empty, and success states.
- Optionally add an admin/review page for unknown terms if backend is ready.

Suggested component structure:

```text
frontend/src/
|-- api/client.js
|-- components/TranslatorForm.jsx
|-- components/TranslationResult.jsx
|-- components/FeedbackDialog.jsx
|-- components/ConfidenceBadge.jsx
|-- pages/Home.jsx
`-- pages/ReviewQueue.jsx
```

Deliverables:

- Working React app.
- Clean translator page.
- Feedback UI.
- `.env.example` with backend URL.
- Demo screenshots or short screen recording.

## Bonus Ideas

These are optional. Do them only after the main model, backend, database, and frontend work.

Best bonus: Chrome extension.

- User selects slang text on any webpage.
- Extension sends selected text to FastAPI.
- Popup shows formal translation, sentiment, and confidence.

Other bonus options:

- Telegram bot using the Telegram Bot API.
- WhatsApp-style helper page where users paste chat messages.
- Discord bot for slang-heavy chat servers.
- Browser bookmarklet for a lightweight demo.

## Development Order

1. Member 2 creates baseline `translate_text()`.
2. Member 3 builds FastAPI around that function.
3. Member 4 creates database models and feedback storage.
4. Member 5 builds React against the API contract.
5. Member 2 improves model quality with fine-tuning.
6. Backend members connect active learning to unknown terms and feedback.
7. Team prepares final demo.
8. Bonus integrations only if the main app is stable.

## Suggested Repository Structure

```text
Protocol 67/
|-- backend/
|-- frontend/
|-- model_service/
|-- data_pipeline/
|-- tests/
|-- README.md
`-- .gitignore
```

## Git Hygiene

Do not commit:

- Virtual environments.
- `.env` files.
- Downloaded Parquet datasets.
- Model weights or adapters.
- SQLite database files.
- Large generated artifacts unless the team explicitly agrees.

Ignored examples include `venv/`, `.venv/`, `models/`, `model_service/outputs/`, `*.safetensors`, `*.bin`, `backend/*.db`, and `data_pipeline/*.parquet`.
