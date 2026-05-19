from model_service.src.baseline_translator import translate_with_dictionary


def translate_text(text: str) -> dict:
    """Stable contract consumed by the backend.

    Replace the implementation with a fine-tuned model loader when ready, but
    keep this function signature and response shape stable.
    """
    return translate_with_dictionary(text)
