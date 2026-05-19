from pydantic import BaseModel


class TranslationResult(BaseModel):
    formal_translation: str
    confidence: float
    detected_slang_terms: list[str]
    unknown_terms: list[str]
    model_version: str


def translate_text(text: str) -> TranslationResult:
    """Temporary backend adapter.

    Replace this with an import from `model_service` once Member 2 finishes the
    baseline/fine-tuned translator contract.
    """
    return TranslationResult(
        formal_translation=text,
        confidence=0.1,
        detected_slang_terms=[],
        unknown_terms=[],
        model_version="placeholder-backend-v0",
    )
