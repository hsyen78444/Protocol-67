"""Clean raw slang data and produce a train-ready translation dataset."""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
IN_FILE = ROOT / "data" / "interim" / "merged_raw_dataset.csv"
DICT_FILE = ROOT / "config" / "slang_dictionary.json"
OUT_FILE = ROOT / "data" / "processed" / "brainrot_clean_dataset.csv"
CANDIDATE_FILE = ROOT / "data" / "interim" / "candidate_slang_pairs.csv"

URL_RE = re.compile(r"https?://\S+|www\.\S+")
MENTION_RE = re.compile(r"@\w+")
HASHTAG_RE = re.compile(r"#(\w+)")
PUNCT_RE = re.compile(r"[!?.,;:]{2,}")
TOKEN_RE = re.compile(r"\b[a-z][a-z0-9']*\b")
BLOCKLIST = {
    "slur",
    "hate",
    "kill yourself",
    "kys",
    "nazi",
}
INFORMAL_MARKERS = re.compile(r"^[a-z]*(?:zz|xx|oo|rr|lol|omg|btw|smh|pls|broo)[a-z]*$")


def load_dictionary() -> Dict[str, Dict[str, str]]:
    return json.loads(DICT_FILE.read_text(encoding="utf-8"))


def normalize_text(text: str) -> str:
    text = str(text).lower()
    text = URL_RE.sub(" ", text)
    text = MENTION_RE.sub(" ", text)
    text = HASHTAG_RE.sub(r"\1", text)
    text = re.sub(r"(.)\1{2,}", r"\1\1", text)
    text = PUNCT_RE.sub(".", text)
    text = re.sub(r"[^a-z0-9\s'.,!?-]", " ", text)
    text = re.sub(r"\s+", " ", text).strip(" .,!?-")
    return text


def is_unsafe(text: str) -> bool:
    return any(term in text for term in BLOCKLIST)


def split_terms(dictionary: Dict[str, Dict[str, str]]) -> Tuple[List[str], List[str]]:
    phrase_terms = sorted([term for term in dictionary if " " in term], key=len, reverse=True)
    single_terms = sorted([term for term in dictionary if " " not in term], key=len, reverse=True)
    return phrase_terms, single_terms


def detect_terms(text: str, dictionary: Dict[str, Dict[str, str]]) -> List[str]:
    phrase_terms, single_terms = split_terms(dictionary)
    detected: List[str] = []
    protected = text

    for term in phrase_terms:
        pattern = re.compile(rf"(?<!\w){re.escape(term)}(?!\w)")
        if pattern.search(protected):
            detected.append(term)
            protected = pattern.sub(" ", protected)

    tokens = set(TOKEN_RE.findall(protected))
    for term in single_terms:
        if term in tokens:
            detected.append(term)

    return detected


def detect_unknown_terms(text: str, known_terms: List[str], dictionary: Dict[str, Dict[str, str]]) -> List[str]:
    known_tokens = set()
    for term in dictionary:
        known_tokens.update(term.split())
    known_tokens.update({"the", "a", "an", "is", "are", "was", "were", "i", "he", "she", "it", "they", "we", "you",
                         "that", "this", "my", "your", "our", "to", "of", "and", "or", "but", "in", "on", "for",
                         "with", "after", "before", "while", "during", "today", "again", "one", "first"})
    tokens = TOKEN_RE.findall(text)
    unknown = []
    for token in tokens:
        if token in known_tokens or token in known_terms:
            continue
        if len(token) <= 2 and token not in {"w", "l"}:
            continue
        if INFORMAL_MARKERS.match(token) or token.endswith(("ing", "ed")) and token not in known_tokens:
            unknown.append(token)
    return sorted(set(unknown))


def translate(text: str, detected: List[str], dictionary: Dict[str, Dict[str, str]]) -> str:
    translated = text
    replacements = {
        "bro": "he",
        "bruh": "that is frustrating",
        "fit": "outfit",
        "fr": "for real",
        "ngl": "not going to lie",
        "idk": "I do not know",
        "rn": "right now",
        "w": "a successful outcome",
        "l": "a poor outcome",
    }
    for term in sorted(detected, key=len, reverse=True):
        meaning = replacements.get(term, dictionary[term]["meaning"])
        translated = re.sub(rf"(?<!\w){re.escape(term)}(?!\w)", meaning, translated)

    translated = re.sub(r"\bthat outfit performed very well or looked impressive\b", "that outfit looked very impressive", translated)
    translated = re.sub(r"\blooked very impressive not going to lie\b", "looked very impressive, not going to lie", translated)
    translated = re.sub(r"\bhe is in serious trouble, defeated, or exhausted for real\b", "he is in serious trouble, for real", translated)
    translated = re.sub(r"\s+", " ", translated).strip()
    if translated:
        translated = translated[0].upper() + translated[1:]
    if translated and translated[-1] not in ".!?":
        translated += "."
    return translated


def sentiment_label(detected: List[str], dictionary: Dict[str, Dict[str, str]]) -> str:
    labels = [dictionary[term]["sentiment"] for term in detected if term in dictionary]
    non_neutral = {label for label in labels if label != "neutral"}
    if len(non_neutral) > 1:
        return "mixed"
    if non_neutral:
        return next(iter(non_neutral))
    return "neutral"


def quality_flags(clean_text: str, detected: List[str], unknown: List[str], formal: str) -> List[str]:
    flags = []
    if not detected:
        flags.append("missing_slang")
    if len(clean_text.split()) < 4:
        flags.append("short_text")
    if unknown:
        flags.append("contains_unknown_terms")
    if not detected or clean_text.rstrip(".") == formal.lower().rstrip("."):
        flags.append("low_translation_confidence")
    return flags or ["clean"]


def confidence(detected: List[str], unknown: List[str], flags: List[str]) -> str:
    meaningful_flags = [flag for flag in flags if flag != "clean"]
    if detected and not unknown and not meaningful_flags:
        return "high"
    if detected and unknown:
        return "medium"
    if detected and "low_translation_confidence" not in flags:
        return "medium"
    return "low"


def main() -> None:
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    dictionary = load_dictionary()
    df = pd.read_csv(IN_FILE).fillna("")
    rows = []
    candidate_rows = []
    seen = set()
    removed_unsafe = 0

    for _, row in df.iterrows():
        clean = normalize_text(row["raw_text"])
        if not clean or clean in seen:
            continue
        if is_unsafe(clean):
            removed_unsafe += 1
            continue
        seen.add(clean)
        detected = detect_terms(clean, dictionary)
        unknown = detect_unknown_terms(clean, detected, dictionary)
        formal = translate(clean, detected, dictionary)
        flags = quality_flags(clean, detected, unknown, formal)
        for term in detected:
            candidate_rows.append(
                {
                    "term": term,
                    "raw_text": row["raw_text"],
                    "clean_text": clean,
                    "source": row.get("source", ""),
                    "platform": row.get("platform", ""),
                    "matched_in_dictionary": True,
                }
            )
        rows.append(
            {
                "id": len(rows) + 1,
                "raw_text": row["raw_text"],
                "clean_text": clean,
                "detected_slang_terms": "|".join(detected),
                "formal_translation": formal,
                "sentiment": sentiment_label(detected, dictionary),
                "confidence_label": confidence(detected, unknown, flags),
                "source": row.get("source", ""),
                "platform": row.get("platform", ""),
                "unknown_terms": "|".join(unknown),
                "quality_flags": "|".join(flags),
            }
        )

    out = pd.DataFrame(rows)
    out.to_csv(OUT_FILE, index=False)
    pd.DataFrame(candidate_rows).drop_duplicates().to_csv(CANDIDATE_FILE, index=False)
    stats = Counter(flag for value in out["quality_flags"] for flag in str(value).split("|"))
    print(f"Saved {len(out)} processed rows to {OUT_FILE}")
    print(f"Saved {len(candidate_rows)} candidate slang matches to {CANDIDATE_FILE}")
    print(f"Removed unsafe rows: {removed_unsafe}")
    print(f"Quality flags: {dict(stats)}")


if __name__ == "__main__":
    main()
