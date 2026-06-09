import contextlib
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db import get_db
from app.services.database import DatabaseService

from app.schemas import FeedbackRequest, TranslateRequest, TranslateResponse, ResolveTermRequest
from app.services.sentiment import analyze_sentiment
from app.services.translation import translate_text
from app.db import engine
from app import models

@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    """Everything before 'yield' runs BEFORE the server starts taking requests"""
    models.Base.metadata.create_all(bind=engine)
    print("Database tables created/verified")
    
    yield  # The server is running and handling requests while paused here
    
    """Everything after 'yield' runs when the server is SHUTTING DOWN"""
    print("Database session closed / cleaning up if needed")

app = FastAPI(title="Protocol 67 API", version="0.1.0", lifespan=lifespan)

frontend_origin = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")
allowed_origins = {
    frontend_origin,
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
}

app.add_middleware(
    CORSMiddleware,
    allow_origins=sorted(allowed_origins),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/translate", response_model=TranslateResponse)
def translate(
    request: TranslateRequest,
    db: Session = Depends(get_db)
) -> TranslateResponse:
    print(f"\n=== DEBUG: /translate called with: {request.text} ===")
    
    translation = translate_text(request.text)
    print(f"DEBUG: translate_text returned: confidence={translation.confidence}, model={translation.model_version}")
    
    sentiment = analyze_sentiment(request.text, translation.detected_slang_terms)
    print(f"DEBUG: sentiment = {sentiment}")
    
    db_service = DatabaseService(db)
    print(f"DEBUG: About to call store_translation...")
    
    translation_id = db_service.store_translation(
        input_text=request.text,
        output_text=translation.formal_translation,
        sentiment=sentiment,
        confidence=translation.confidence,
        detected_slang_terms=translation.detected_slang_terms,
        unknown_terms=translation.unknown_terms,
        model_version=translation.model_version
    )
    
    db_service._upsert_unknown_terms(translation.unknown_terms, request.text)
    
    print(f"DEBUG: store_translation returned ID: {translation_id}")
    print(f"=== DEBUG: /translate returning ===\n")
    
    return TranslateResponse(
        input=request.text,
        formal_translation=translation.formal_translation,
        sentiment=sentiment,
        confidence=translation.confidence,
        detected_slang_terms=translation.detected_slang_terms,
        unknown_terms=translation.unknown_terms,
        model_version=translation.model_version,
        translation_id=translation_id
    )


@app.post("/feedback")
def submit_feedback(
    request: FeedbackRequest,
    db: Session = Depends(get_db)
) -> dict:
    # Verify translation exists if translation_id provided
    if request.translation_id:
        from app.models import Translation
        translation = db.query(Translation).filter(
            Translation.id == request.translation_id
        ).first()
        if not translation:
            raise HTTPException(status_code=404, detail="Translation not found")
    
    # Store feedback using database service
    db_service = DatabaseService(db)
    feedback_id = db_service.store_feedback(
        translation_id=request.translation_id,
        input_text=request.input_text,
        original_translation=request.original_translation,
        corrected_translation=request.corrected_translation,
        notes=request.notes
    )
    
    return {"status": "stored", "feedback_id": feedback_id}


@app.get("/unknown-terms")
def list_unknown_terms(
    status: str | None = Query(None, pattern="^(open|reviewing|resolved|ignored)$"),
    page: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
) -> dict:
    db_service = DatabaseService(db)
    terms, total = db_service.get_unresolved_unknown_terms(
        status=status,
        page=page,
        limit=limit
    )
    
    return {
        "items": [
            {
                "id": getattr(t, "id"),
                "term": getattr(t, "term"),
                "frequency": getattr(t, "frequency", 1),
                "status": getattr(t, "status", "open"),
                "example_text": getattr(t, "example_text", ""),
                "proposed_meaning": getattr(t, "proposed_meaning", None)
            }
            for t in terms
        ],
        "total": total,
        "page": page,
        "limit": limit
    }


@app.post("/unknown-terms/{term_id}/resolve")
def resolve_unknown_term(term_id: int, request: ResolveTermRequest, db: Session = Depends(get_db)) -> dict:
    proposed_meaning = request.proposed_meaning
    if not proposed_meaning:
        raise HTTPException(status_code=400, detail="proposed_meaning is required")
    
    db_service = DatabaseService(db)
    success = db_service.resolve_unknown_term(term_id, proposed_meaning)
    
    if not success:
        raise HTTPException(status_code=404, detail="Term not found")
    
    return {"status": "resolved", "term_id": term_id}


@app.post("/unknown-terms/{term_id}/ignore")
def ignore_unknown_term(term_id: int, db: Session = Depends(get_db)) -> dict:
    db_service = DatabaseService(db)
    success = db_service.ignore_unknown_term(term_id)

    if not success:
        raise HTTPException(status_code=404, detail="Term not found")

    return {"status": "ignored", "term_id": term_id}


@app.get("/stats")
def stats(db: Session = Depends(get_db)) -> dict:
    db_service = DatabaseService(db)
    return db_service.get_stats()
