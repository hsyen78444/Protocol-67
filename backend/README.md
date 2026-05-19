# Backend

FastAPI service for Protocol 67.

## Team Ownership

- Backend Member A: API endpoints, request/response schemas, CORS, API validation, and frontend integration.
- Backend Member B: database models, active learning tables, feedback storage, statistics, and persistence.

Both backend members should keep the `/translate` contract stable so the model and frontend teams can work in parallel.

## Suggested Setup

```powershell
cd backend
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
uvicorn app.main:app --reload
```

## API Endpoints

- `GET /health`
- `POST /translate`
- `POST /feedback`
- `GET /unknown-terms`
- `POST /unknown-terms/{term_id}/resolve`
- `GET /stats`

## Database Recommendation

Use SQLite for coursework/demo speed, through SQLAlchemy. If deployment grows, PostgreSQL can replace SQLite without changing the API contract much.

Suggested tables:

- `translations`: stores every translation request and model output.
- `unknown_terms`: stores unknown slang terms mined from user input.
- `feedback`: stores user corrections for active learning.
- `model_runs`: stores model version metadata.

See `docs/database_schema.md` for field-level schema guidance.
