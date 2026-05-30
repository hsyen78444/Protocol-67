import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel

BASE_MODEL  = "Qwen/Qwen2.5-0.5B-Instruct"
ADAPTER_DIR = "model_service/outputs/qwen0.5b-slang-lora"

_model = None
_tokenizer = None

def _load():
    global _model, _tokenizer
    if _model is None:
        _tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL, trust_remote_code=True)
        _tokenizer.pad_token = _tokenizer.eos_token
        base_model = AutoModelForCausalLM.from_pretrained(
            BASE_MODEL,
            dtype=torch.float16,
            device_map="auto",
            trust_remote_code=True,
        )
        _model = PeftModel.from_pretrained(base_model, ADAPTER_DIR)
        _model.eval()

def translate_text(text: str) -> dict:
    _load()
    prompt = (
        f"Instruction: Translate the following internet slang or brainrot text "
        f"into clear formal English.\n"
        f"Input: {text}\n"
        f"Output:"
    )
    inputs = _tokenizer(prompt, return_tensors="pt").to(_model.device)
    with torch.no_grad():
        outputs = _model.generate(
            **inputs,
            max_new_tokens=128,
            temperature=0.3,
            do_sample=True,
            pad_token_id=_tokenizer.eos_token_id,
        )
    decoded = _tokenizer.decode(outputs[0], skip_special_tokens=True)
    translation = decoded.split("Output:")[-1].strip()

    return {
        "formal_translation": translation,
        "confidence": 0.85,
        "detected_slang_terms": [],
        "unknown_terms": [],
        "model_version": "qwen0.5b-lora-v1"
    }
