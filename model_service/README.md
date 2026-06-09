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

## Training Model

1. The scripts to train the models are **train_lora.py** and **train_lorav2.py**, with models *Qwen2.5-3B-Instruct* and *Llama-3.2-3B-Instruct* respectively.

2. You may use another model for training, but since each model may have different tuning parameters, it is recommended that you create a new script for the new model. If you want to use another model, you may copy the existing scripts and make changes, but make sure to set the output directory as "model_service/outputs/<model-name>".

3. Once your virtual environment is setup (refer to README of the data_pipeline module), run **python -m model_service.scripts.train_lorav2** to train the model. Change the name of the script to your script if you have created a new one.

4. Use **python -m model_service.scripts.evaluate** to evaluate the model's exact match rate. Make sure to change the **BASE_MODEL** and **ADAPTER_DIR** in the *translator.py* file before you run the evaluate script. The **ADAPTER_DIR** can be found in the *outputs* folder under this model_service folder. The folder should appear only after you run the model training script.

## Colab Training Notebook

If local GPU training is not available, use the documented Colab notebook:

```text
model_service/notebooks/P67-Train.ipynb
```

The notebook clones the repo, installs model dependencies, authenticates with Hugging Face, verifies the processed dataset, runs `train_lorav2.py`, and saves the trained LoRA adapter to Google Drive.

## Evaluation Results

### Initial evaluation - Baseline
- Exact match rate: 1.0 (data is inflated, test outputs are generated from the same dictionary)

### Qwen2.5-0.5B-Instruct
- Exact match rate: 0

### Qwen2.5-3B-Instruct
- Exact match rate: 0

### Llama-3.2-3B-Instruct
- Exact match rate: 0.08333
