NEGATIVE_HINTS = {"cooked", "sadge", "madge", "cringe", "l", "monkas", "pepega"}
POSITIVE_HINTS = {"pog", "poggers", "w", "feelsgoodman", "clutch", "fire", "goated"}


def analyze_sentiment(text: str, detected_terms: list[str]) -> str:
    lowered = text.lower()
    terms = {term.lower() for term in detected_terms}
    if terms & NEGATIVE_HINTS or any(word in lowered for word in NEGATIVE_HINTS):
        return "negative"
    if terms & POSITIVE_HINTS or any(word in lowered for word in POSITIVE_HINTS):
        return "positive"
    return "neutral"
