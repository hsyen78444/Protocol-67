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

## Colab Notebooks

The Colab notebooks are in:

```text
model_service/notebooks/
```

Use Colab when the trained model is too large to train or serve locally.

### Train The LoRA Adapter

Open this notebook in Google Colab:

```text
model_service/notebooks/P67-Train.ipynb
```

Run the cells in order. The notebook:

1. Sets up a GPU runtime.
2. Clones the repository.
3. Installs model dependencies.
4. Authenticates with Hugging Face.
5. Verifies the processed dataset.
6. Runs `train_lorav2.py`.
7. Saves the trained adapter to Google Drive.

Default adapter output:

```text
model_service/outputs/llama3b-slang-lora
```

Default Google Drive storage path:

```text
/content/drive/MyDrive/protocol67-models/llama3b-slang-lora
```

If you use a different Drive path or adapter name, update the path variables near the top of the notebook.

### Serve The Model From Colab

Open this notebook in Google Colab:

```text
model_service/notebooks/P67-Serve-Model-Colab.ipynb
```

Run the cells in order. The notebook:

1. Sets up a GPU runtime.
2. Clones the repository.
3. Installs model and API dependencies.
4. Authenticates with Hugging Face.
5. Restores the trained adapter from Google Drive.
6. Loads and warms up the translator.
7. Starts a temporary FastAPI server through ngrok.
8. Prints a public `/translate` URL.

Use the printed ngrok `/translate` URL as the backend `MODEL_API_URL`:

```env
MODEL_API_URL=https://YOUR-NGROK-URL.ngrok-free.app/translate
```

The ngrok URL is temporary and changes when the Colab runtime or tunnel restarts.

## Evaluation Results

### Initial evaluation - Baseline
- Exact match rate: 1.0 (data is inflated, test outputs are generated from the same dictionary)

### Qwen2.5-0.5B-Instruct
- Exact match rate: 0

### Qwen2.5-3B-Instruct
- Exact match rate: 0

### Llama-3.2-3B-Instruct
- Exact match rate: 0.08333
