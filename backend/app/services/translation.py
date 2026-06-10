import json
import os
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel


PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / "backend" / ".env")
MODEL_SERVICE_SRC = PROJECT_ROOT / "model_service" / "src"
if str(MODEL_SERVICE_SRC) not in sys.path:
    sys.path.append(str(MODEL_SERVICE_SRC))


class TranslationResult(BaseModel):
    formal_translation: str
    confidence: float
    detected_slang_terms: list[str]
    unknown_terms: list[str]
    model_version: str


def _translate_with_remote_model(text: str, model_api_url: str) -> dict:
    payload = json.dumps({"text": text}).encode("utf-8")
    request = Request(
        model_api_url,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "ngrok-skip-browser-warning": "true",
        },
        method="POST",
    )
    try:
        with urlopen(request, timeout=120) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Remote model API returned HTTP {exc.code}: {detail}") from exc
    except URLError as exc:
        raise RuntimeError(f"Could not reach remote model API: {exc.reason}") from exc


def _translate_with_local_model(text: str) -> dict:
    from translator import translate

    return translate(text)


def translate_text(text: str) -> TranslationResult:
    model_api_url = os.getenv("MODEL_API_URL", "").strip()
    if model_api_url:
        result = _translate_with_remote_model(text, model_api_url)
    else:
        result = _translate_with_local_model(text)
    return TranslationResult(**result)
