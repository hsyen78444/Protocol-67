# Protocol 67

## Project Title

**Protocol 67: An Agent-Driven Brainrot-to-English Translation and Sentiment Analysis System**

## Background

Internet vernacular evolves quickly. Slang, memes, abbreviations, and non-standard expressions from platforms such as Twitch, TikTok, Reddit, WhatsApp, Telegram, and Urban Dictionary can be difficult for non-native speakers, educators, researchers, older users, and NLP systems to interpret.

Protocol 67 translates highly contextual internet slang, commonly called "brainrot language", into formal English and returns supporting analysis such as sentiment, confidence, detected slang terms, and unknown terminology.

## Project Overview

Protocol 67 is a Natural Language Processing project focused on low-resource translation for informal online language. The system uses an agent-style workflow that combines:

- A slang-to-English translation model or rule-based baseline.
- Tool-assisted sentiment analysis.
- Dictionary lookup for known slang terms.
- Unknown-term detection for active learning.
- A FastAPI backend for structured JSON responses.
- A React frontend for user interaction.
- Optional user-facing tools such as a Chrome extension, Telegram bot, or WhatsApp-style helper.

The system accepts slang-heavy user input and returns:

```json
{
  "input": "bro is cooked fr",
  "formal_translation": "He is in serious trouble, for real.",
  "sentiment": "negative",
  "confidence": 0.87,
  "detected_slang_terms": ["bro", "cooked", "fr"],
  "unknown_terms": []
}
```

## Objectives

1. Develop an agent-driven NLP system that translates internet slang and brainrot language into formal English.
2. Fine-tune or adapt a language model for slang-to-English translation using the curated dataset.
3. Integrate sentiment analysis to identify the tone or polarity of the original input.
4. Build a RESTful FastAPI backend that returns translation, sentiment, confidence, detected terms, and unknown terms.
5. Build a React frontend that lets users translate text, inspect detected slang, and submit corrections.
6. Support an active learning loop where unknown slang terms and user corrections can be reviewed and used for future retraining.

## Current Member 1 Deliverable

Member 1 owns the data pipeline in `data_pipeline/`.

Completed scope:

- Urban Dictionary-style slang collection through a local API clone.
- Twitch chat corpus ingestion from local Parquet.
- Text cleaning and normalization.
- Dictionary-based slang detection.
- Rule-based formal translation bootstrap.
- Sentiment and confidence labels.
- Unknown-term and quality-flag generation.
- Train, validation, and test CSV generation.
- Data quality reports and documentation.

The recommended model input column is `clean_text`. The recommended target column is `formal_translation`.

## Proposed System Architecture

```text
React Frontend
    |
    v
FastAPI Backend
    |
    |-- Translation Service
    |     |-- Fine-tuned model or baseline translator
    |     `-- Slang dictionary lookup
    |
    |-- Sentiment Service
    |     `-- Sentiment model or lexicon/rule baseline
    |
    |-- Active Learning Service
    |     `-- Unknown terms, corrections, feedback
    |
    `-- Database
          |-- Translation logs
          |-- User corrections
          |-- Unknown slang terms
          `-- Model/version metadata
```

## Task Distribution

### Member 2: Model Training and Translation Agent

Main responsibility: build the translation intelligence.

Recommended tasks:

- Use `data_pipeline/data/processed/train.csv`, `validation.csv`, and `test.csv`.
- Start with a baseline translator using the existing dictionary/rule-based outputs.
- Fine-tune or adapt a small causal language model with LoRA if compute allows.
- Create a reusable inference module, for example `model_service/translator.py`.
- Return translation text, confidence score, detected slang terms, unknown terms, and model version.
- Compare baseline vs fine-tuned model using simple metrics and human examples.

Implementation plan:

1. Load the processed CSV files.
2. Convert rows into prompt/completion or instruction format.
3. Train a baseline model or LoRA adapter.
4. Save model artifacts under an ignored folder such as `models/`.
5. Expose a Python function:

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

Suggested deliverables:

- `model_service/translator.py`
- `model_service/evaluate.py`
- `model_service/README.md`
- Short evaluation table with sample inputs and outputs.

### Member 3: FastAPI Backend, Database, and Active Learning

Main responsibility: turn the model into a usable API.

Recommended tasks:

- Build a FastAPI app with clean request/response schemas.
- Connect the translation module from Member 2.
- Add sentiment analysis as a service.
- Store translation requests, unknown terms, and user corrections.
- Implement active learning endpoints for review and correction.
- Add CORS support for the React frontend.

Core API endpoints:

```text
GET  /health
POST /translate
POST /feedback
GET  /unknown-terms
POST /unknown-terms/{term_id}/resolve
GET  /stats
```

Sample `/translate` request:

```json
{
  "text": "chat this run is cooked fr"
}
```

Sample `/translate` response:

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

Suggested database tables:

```text
translations(id, input_text, output_text, sentiment, confidence, created_at)
unknown_terms(id, term, example_text, status, created_at)
feedback(id, translation_id, corrected_translation, notes, created_at)
```

Suggested deliverables:

- `backend/app/main.py`
- `backend/app/schemas.py`
- `backend/app/services/translation.py`
- `backend/app/services/sentiment.py`
- `backend/app/db.py`
- `backend/README.md`

### Member 4: React Frontend and User Experience

Main responsibility: build the user-facing translator.

Recommended tasks:

- Build a React JS app that calls the FastAPI backend.
- Create a clean translator interface with input, output, sentiment, confidence, and detected terms.
- Add loading, empty, error, and success states.
- Add correction/feedback UI for active learning.
- Add a history panel for recent translations if the backend supports it.

Core screens:

- Translator page: text input and translation result.
- Details panel: detected slang, sentiment, confidence, unknown terms.
- Feedback modal: user correction and notes.
- Optional admin/review page: unknown terms and submitted corrections.

Suggested frontend component structure:

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

Suggested deliverables:

- `frontend/` React app.
- `.env.example` with backend URL.
- Frontend README with setup commands.
- Screenshots or short demo video.

### Member 5: Integrations, QA, Deployment, and Bonus Tools

Main responsibility: make the system usable outside the basic web app and keep the project stable.

Recommended tasks:

- Write integration tests for the FastAPI backend.
- Add frontend smoke tests or manual test checklist.
- Prepare Docker or deployment notes.
- Build one optional tool that lets users translate slang where they already read messages.
- Coordinate final demo flow and documentation.

Best bonus option: Chrome extension.

Why this is the strongest bonus:

- It can work on many websites, including web-based chat pages.
- It can call the same FastAPI `/translate` endpoint.
- It avoids the policy and API complexity of official WhatsApp or Telegram integrations.

Chrome extension implementation idea:

```text
chrome_extension/
|-- manifest.json
|-- popup.html
|-- popup.js
|-- content.js
`-- styles.css
```

Possible extension features:

- User selects slang text on a webpage.
- Extension popup sends selected text to FastAPI.
- Popup shows formal translation, sentiment, and confidence.
- Optional content script adds a small "Translate" button beside selected text.

Alternative bonus tools:

- Telegram bot using the Bot API: easiest real messaging integration if a bot token is available.
- WhatsApp-style helper page: user pastes chat text into the React app and receives translations.
- Browser bookmarklet: lightweight option if a full extension is too much.
- Discord bot: good fit for slang and chat data if the team already uses Discord.

Suggested deliverables:

- `tests/` for backend API checks.
- `docker-compose.yml` or deployment guide.
- `chrome_extension/` or `telegram_bot/`.
- Final demo script showing data pipeline, API, frontend, and optional tool.

## Recommended Development Order

1. Member 2 creates a baseline translator function first, even before final model training.
2. Member 3 builds FastAPI around that stable function contract.
3. Member 4 builds the React UI against mocked API responses, then switches to the real backend.
4. Member 5 adds tests, deployment notes, and one bonus integration.
5. All members connect active learning: unknown terms and corrections should flow back into future dataset updates.

## Integration Contract

All components should agree on this response shape:

```json
{
  "input": "string",
  "formal_translation": "string",
  "sentiment": "positive | negative | neutral | mixed",
  "confidence": 0.0,
  "detected_slang_terms": ["string"],
  "unknown_terms": ["string"],
  "model_version": "string"
}
```

## Suggested Repository Structure

```text
Protocol 67/
|-- backend/
|-- frontend/
|-- model_service/
|-- data_pipeline/
|-- chrome_extension/       # optional bonus
|-- telegram_bot/           # optional bonus alternative
|-- tests/
|-- README.md
`-- .gitignore
```

## Notes

- Do not commit virtual environments, model weights, downloaded Parquet files, `.env` files, or large generated artifacts unless the team explicitly agrees.
- Keep API responses deterministic enough for frontend testing.
- Keep the baseline translator available even if model fine-tuning is incomplete.
- Prioritize a working end-to-end demo over a perfect model.
