import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DICTIONARY_PATH = ROOT / "data_pipeline" / "config" / "slang_dictionary.json"


def load_dictionary() -> dict:
    return json.loads(DICTIONARY_PATH.read_text(encoding="utf-8"))


def detect_terms(text: str, dictionary: dict) -> list[str]:
    lowered = text.lower()
    detected = []
    for term in sorted(dictionary, key=len, reverse=True):
        if re.search(rf"(?<!\w){re.escape(term)}(?!\w)", lowered):
            detected.append(term)
    return detected


def translate_with_dictionary(text: str, dictionary: dict | None = None) -> dict:
    dictionary = dictionary or load_dictionary()
    detected = detect_terms(text, dictionary)
    translated = text.lower()
    for term in detected:
        translated = re.sub(
            rf"(?<!\w){re.escape(term)}(?!\w)",
            dictionary[term]["meaning"],
            translated,
        )
    translated = re.sub(r"\s+", " ", translated).strip()
    if translated:
        translated = translated[0].upper() + translated[1:]
    if translated and translated[-1] not in ".!?":
        translated += "."
    return {
        "formal_translation": translated,
        "confidence": 0.75 if detected else 0.25,
        "detected_slang_terms": detected,
        "unknown_terms": [],
        "model_version": "dictionary-baseline-v1",
    }
