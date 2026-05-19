from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.schemas import FeedbackRequest, TranslateRequest, TranslateResponse
from app.services.sentiment import analyze_sentiment
from app.services.translation import translate_text


app = FastAPI(title="Protocol 67 API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/translate", response_model=TranslateResponse)
def translate(request: TranslateRequest) -> TranslateResponse:
    translation = translate_text(request.text)
    sentiment = analyze_sentiment(request.text, translation.detected_slang_terms)
    return TranslateResponse(
        input=request.text,
        formal_translation=translation.formal_translation,
        sentiment=sentiment,
        confidence=translation.confidence,
        detected_slang_terms=translation.detected_slang_terms,
        unknown_terms=translation.unknown_terms,
        model_version=translation.model_version,
    )


@app.post("/feedback")
def submit_feedback(request: FeedbackRequest) -> dict:
    # Backend Member B: persist this into the feedback table.
    return {"status": "received", "translation_id": request.translation_id}


@app.get("/unknown-terms")
def list_unknown_terms() -> dict:
    # Backend Member B: return unresolved unknown terms from the database.
    return {"items": []}


@app.post("/unknown-terms/{term_id}/resolve")
def resolve_unknown_term(term_id: int) -> dict:
    # Backend Member B: mark the unknown term as resolved after review.
    return {"status": "resolved", "term_id": term_id}


@app.get("/stats")
def stats() -> dict:
    # Backend Member B: aggregate persisted translation/feedback counts.
    return {"translations": 0, "unknown_terms": 0, "feedback_items": 0}
