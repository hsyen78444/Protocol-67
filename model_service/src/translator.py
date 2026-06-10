import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
import os
import re

BASE_MODEL  = "meta-llama/Llama-3.2-3B-Instruct"
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ADAPTER_DIR = os.path.join(CURRENT_DIR, "..", "outputs", "llama3b-slang-lora")

# Known slang terms from your training data
SLANG_TERMS = {
    "fr", "imo", "rn", "mid", "cooked", "ate", "slay", "rizz", "cap", "no cap",
    "ratioed", "ratio", "w", "tweaking", "slaps", "goated", "sus", "vibe", "vibes",
    "npc", "lowkey", "highkey", "bet", "based", "cringe", "locked in", "brainrot",
    "skibidi", "gyatt", "fanum tax", "aura", "aura farming", "yapping", "touch grass",
    "let him cook", "fell off", "valid", "bussin", "drip", "fit", "opp", "glazing",
    "pookie", "real", "canon event", "mood", "fire", "lit", "clean", "peak", "wild",
    "bruh", "fam", "queen", "king", "stan", "ship", "soft launch", "hard launch",
    "rent free", "living rent free", "it is giving", "giving", "big yikes", "yikes",
    "vibe check", "skill issue", "clutch", "sweat", "tryhard", "carried", "nerfed",
    "buffed", "speedrun", "irl", "jomo", "vibe coded", "girlboss", "devoured",
    "salty", "chill", "unserious", "valid take", "hot take", "safe take",
}

# Simple sentiment heuristic — expand as needed
_POSITIVE = {"slay", "ate", "goated", "bussin", "fire", "lit", "clutch", "buffed", "slaps", "w", "clean", "peak"}
_NEGATIVE = {"mid", "cooked", "cap", "ratioed", "sus", "npc", "cringe", "fell off", "nerfed", "salty", "yikes"}

_model = None
_tokenizer = None


def _load():
    global _model, _tokenizer
    if _model is None:
        _tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL, trust_remote_code=True)
        _tokenizer.pad_token = _tokenizer.eos_token
        base = AutoModelForCausalLM.from_pretrained(
            BASE_MODEL,
            dtype=torch.float16,
            device_map="auto",
            trust_remote_code=True,
        )
        _model = PeftModel.from_pretrained(base, ADAPTER_DIR)
        _model.eval()


def _detect_metadata(text: str) -> tuple[list[str], str]:
    """Returns (detected_slang_terms, sentiment)."""
    lowered = text.lower()

    # Match complete slang terms only, so "ate" is not detected inside "update"
    # and "w" is not detected inside "new".
    detected = []
    for slang in sorted(SLANG_TERMS, key=len, reverse=True):
        escaped = re.escape(slang).replace(r"\ ", r"\s+")
        if re.search(rf"(?<![a-z0-9]){escaped}(?![a-z0-9])", lowered):
            detected.append(slang)

    if any(s in _POSITIVE for s in detected):
        sentiment = "positive"
    elif any(s in _NEGATIVE for s in detected):
        sentiment = "negative"
    else:
        sentiment = "neutral"

    return detected, sentiment


def _build_prompt(text: str) -> str:
    messages = [
        {
            "role": "system",
            "content": (
                "You are a translator that converts internet slang and brainrot text "
                "into clear, formal English. You will be given the sentiment of the "
                "input and the slang terms present to help guide your translation."
            ),
        },
        {
            "role": "user",
            "content": f"Analyze and translate this text: {text}",
        },
    ]
    return _tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,  # adds the assistant turn opener
    )


def _estimate_confidence(slang_terms: list[str], unknown_terms: list[str]) -> float:
    """Heuristic: penalise unknown terms."""
    if not slang_terms and not unknown_terms:
        return 0.5   # no slang detected at all — uncertain
    if not unknown_terms:
        return 0.9
    ratio = len(unknown_terms) / max(len(slang_terms) + len(unknown_terms), 1)
    return round(max(0.4, 0.9 - ratio * 0.5), 2)


def translate(text: str) -> dict:
    _load()

    detected_slang, sentiment = _detect_metadata(text)
    unknown_terms = []  # placeholder — populate if you add an OOV detector

    prompt = _build_prompt(text)

    inputs = _tokenizer(prompt, return_tensors="pt").to(_model.device)
    input_len = inputs["input_ids"].shape[1]

    with torch.no_grad():
        outputs = _model.generate(
            **inputs,
            max_new_tokens=128,
            temperature=0.3,
            do_sample=True,
            repetition_penalty=1.3,       # prevents looping
            pad_token_id=_tokenizer.eos_token_id,
        )

    # Slice off the prompt tokens — only decode what the model generated
    new_tokens = outputs[0][input_len:]
    translation = _tokenizer.decode(new_tokens, skip_special_tokens=True).strip()

    return {
        "formal_translation": translation.split("Translation:")[-1].strip(),
        "confidence": _estimate_confidence(detected_slang, unknown_terms),
        "detected_slang_terms": detected_slang,
        "unknown_terms": unknown_terms,
        "sentiment": sentiment,
        "model_version": "llama3b-lora-v1",
    }
