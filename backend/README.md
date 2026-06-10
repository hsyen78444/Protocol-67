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

## Use Colab Model API

If the trained LoRA model is running in Colab through the inference API notebook, ngrok, or a similar remote model API, set `MODEL_API_URL` in `backend/.env` to the remote `/translate` URL:

```env
MODEL_API_URL=https://YOUR-NGROK-URL.ngrok-free.app/translate
```

Example:

```env
MODEL_API_URL=https://splashing-unfixed-ridden.ngrok-free.dev/translate
```

Then start the backend normally:

```powershell
uvicorn app.main:app --reload
```

When `MODEL_API_URL` is set, the backend sends translation requests to that remote model API. When it is empty or unset, the backend uses the local model service translator.

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

## Clear cache from old imports and database file that retains old schema:
```powershell
# Delete all __pycache__ folders recursively
Get-ChildItem -Path . -Include '__pycache__' -Recurse -Force | Remove-Item -Recurse -Force

# Delete the database file
Remove-Item -Path protocol67.db -Force -ErrorAction SilentlyContinue

# Delete any .pyc files
Get-ChildItem -Path . -Filter '*.pyc' -Recurse -Force | Remove-Item -Force

Write-Host "Cache cleared. Restart the server now." -ForegroundColor Green
```

## Test Each Endpoint After Fix
```powershell
# 1. Test health (should work)
Invoke-RestMethod -Uri http://localhost:8000/health

# 2. Test stats (should return zeros, not error)
Invoke-RestMethod -Uri http://localhost:8000/stats

# 3. Test translate with database persistence
$body = @{text = "bro is cooked fr"} | ConvertTo-Json
Invoke-RestMethod -Uri http://localhost:8000/translate `
                  -Method POST `
                  -Body $body `
                  -ContentType "application/json"

# 4. Test stats again (should show 1 translation)
Invoke-RestMethod -Uri http://localhost:8000/stats

# 5. Test unknown-terms (should return empty list, not error)
Invoke-RestMethod -Uri "http://localhost:8000/unknown-terms?page=0&limit=10"

# 6. Test feedback after you have a translation_id
$feedback = @{
    translation_id = 1
    input_text = "bro is cooked fr"
    original_translation = "bro is cooked fr"
    corrected_translation = "brother is in serious trouble for real"
    notes = "cooked means in trouble, fr means for real"
} | ConvertTo-Json

Invoke-RestMethod -Uri http://localhost:8000/feedback `
                  -Method POST `
                  -Body $feedback `
                  -ContentType "application/json"

# Resolve a term (assuming you have term_id=1)
$resolve = @{proposed_meaning = "in trouble"} | ConvertTo-Json
Invoke-RestMethod -Uri http://localhost:8000/unknown-terms/1/resolve `
                  -Method POST `
                  -Body $resolve `
                  -ContentType "application/json"
```
