# Model Service

This folder belongs to the model-training member.

Goal: produce a reusable translator that the FastAPI backend can call.

## Data Inputs

Use the processed files from:

```text
data_pipeline/data/processed/
|-- train.csv
|-- validation.csv
|-- test.csv
|-- train.jsonl
|-- validation.jsonl
`-- test.jsonl
```

The JSONL files are already instruction-style records:

```json
{
  "instruction": "Translate the following internet slang or brainrot text into clear formal English.",
  "input": "bro is cooked fr",
  "output": "He is in serious trouble, for real."
}
```

## Recommended Fine-Tuning Steps

1. Start with the baseline translator in `src/baseline_translator.py`.
2. Run evaluation against `test.jsonl` to get a baseline score.
3. Pick a small instruction or causal model that fits available hardware.
4. Fine-tune with LoRA/QLoRA using `train.jsonl` and validate on `validation.jsonl`.
5. Save adapters under `model_service/models/` or `model_service/outputs/`.
6. Update `src/translator.py` so backend can call one stable function: `translate_text(text)`.
7. Document model name, dataset version, hyperparameters, and sample outputs.

## Suggested Models

- CPU/light demo: keep the baseline translator.
- Small local GPU: try a small instruction model with LoRA.
- If compute is limited: use a hosted model for generation and keep local code as the integration wrapper.

Do not commit model weights or adapters.
