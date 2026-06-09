import sys
from pathlib import Path

from pydantic import BaseModel


PROJECT_ROOT = Path(__file__).resolve().parents[3]
MODEL_SERVICE_SRC = PROJECT_ROOT / "model_service" / "src"
if str(MODEL_SERVICE_SRC) not in sys.path:
    sys.path.append(str(MODEL_SERVICE_SRC))

from baseline_translator import translate_with_dictionary


class TranslationResult(BaseModel):
    formal_translation: str
    confidence: float
    detected_slang_terms: list[str]
    unknown_terms: list[str]
    model_version: str


def translate_text(text: str) -> TranslationResult:
    result = translate_with_dictionary(text)
    return TranslationResult(**result)
