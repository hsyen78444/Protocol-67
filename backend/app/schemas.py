from pydantic import BaseModel, Field


class TranslateRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=2000)


class TranslateResponse(BaseModel):
    input: str
    formal_translation: str
    sentiment: str
    confidence: float
    detected_slang_terms: list[str]
    unknown_terms: list[str]
    model_version: str


class FeedbackRequest(BaseModel):
    translation_id: int | None = None
    input_text: str
    original_translation: str
    corrected_translation: str
    notes: str | None = None
