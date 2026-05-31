import torch
from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForCausalLM, EarlyStoppingCallback
from peft import LoraConfig
from trl import SFTTrainer, SFTConfig

BASE_MODEL = "meta-llama/Llama-3.2-3B-Instruct"
TRAIN_FILE = "data_pipeline/data/processed/train.jsonl"
VAL_FILE = "data_pipeline/data/processed/validation.jsonl"
OUTPUT_DIR = "model_service/outputs/llama3b-slang-lora"
MAX_SEQ_LEN = 256

# def lora_quantization():
#     bnb_config = BitsAndBytesConfig(
#         load_in_4bit=True,
#         bnb_4bit_quant_type="nf4",
#         bnb_4bit_compute_dtype=torch.float16,
#         bnb_4bit_use_double_quant=True,
#     )
#     return bnb_config

def load_tokenizer():
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL, trust_remote_code=True)
    return tokenizer

def load_model():
    model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL,
        device_map=None,
        trust_remote_code=True,
    ).to("cuda")
    model.enable_input_require_grads()
    return model

def prep_dataset(tokenizer):
    dataset = load_dataset("json", data_files={
        "train": TRAIN_FILE,
        "validation": VAL_FILE,
    })
    dataset = dataset.map(lambda ex: format_prompt(ex, tokenizer))
    return dataset

def format_prompt(example, tokenizer):
    meta = example.get("metadata", {})
    sentiment = meta.get("sentiment", "neutral")
    slang_terms = meta.get("detected_slang_terms", [])

    slang_str = ", ".join(slang_terms) if slang_terms else "none"

    messages = [
        {
            "role": "system",
            "content": (
                "You are a translator that converts internet slang and brainrot text "
                "into clear, formal English. You will be given the sentiment of the "
                "input and the slang terms present to help guide your translation."
            )
        },
        {
            "role": "user",
            "content": (
                f"Sentiment: {sentiment}\n"
                f"Slang terms: {slang_str}\n"
                f"Translate: {example['input']}"
            )
        },
        {
            "role": "assistant",
            "content": example["output"]
        }
    ]
    return {"text": tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=False)}


def build_trainer(model, tokenizer, dataset):
    lora_config = LoraConfig(
        r=8,
        lora_alpha=16,
        target_modules=["q_proj", "v_proj", "k_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM",
    )

    sftconfig = SFTConfig(
        output_dir=OUTPUT_DIR,
        num_train_epochs=7,
        per_device_train_batch_size=2,
        gradient_accumulation_steps=4,
        warmup_steps=10,
        learning_rate=1.5e-4,
        lr_scheduler_type="cosine",
        fp16=True,
        logging_steps=5,
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        report_to="none",
        max_length=MAX_SEQ_LEN,
        dataset_text_field="text",
        gradient_checkpointing=True,
        gradient_checkpointing_kwargs={"use_reentrant": False}
    )

    return SFTTrainer(
        model=model,
        train_dataset=dataset["train"],
        eval_dataset=dataset["validation"],
        peft_config=lora_config,
        processing_class=tokenizer,
        args=sftconfig,
        callbacks=[EarlyStoppingCallback(early_stopping_patience=3)]
    )

def main() -> None:
    print("Loading tokenizer...")
    tokenizer = load_tokenizer()
    print("Loading model...")
    model = load_model()
    print("Prepping dataset...")
    dataset = prep_dataset(tokenizer)
    print("Building trainer...")
    trainer = build_trainer(model, tokenizer, dataset)

    print("Starting training...")
    trainer.train()

    print(f"Saving adapters to {OUTPUT_DIR}")
    trainer.save_model(OUTPUT_DIR)
    print("Done.")


if __name__ == "__main__":
    main()
