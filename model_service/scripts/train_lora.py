import torch
from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import LoraConfig
from trl import SFTTrainer, SFTConfig

BASE_MODEL = "Qwen/Qwen2.5-0.5B-Instruct"
TRAIN_FILE = "data_pipeline/data/processed/train.jsonl"
VAL_FILE = "data_pipeline/data/processed/validation.jsonl"
OUTPUT_DIR = "model_service/outputs/qwen0.5b-slang-lora"
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
    tokenizer.pad_token = tokenizer.eos_token
    return tokenizer

def load_model():
    model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL,
        device_map="auto",
        trust_remote_code=True,
    )
    return model

def prep_dataset():
    dataset = load_dataset("json", data_files={
        "train": TRAIN_FILE,
        "validation": VAL_FILE,
    })
    dataset = dataset.map(format_prompt)
    return dataset

def format_prompt(example):
    return {
        "text": (
            f"Instruction: Translate the following internet slang or brainrot text "
            f"into clear formal English.\n"
            f"Input: {example['input']}\n"
            f"Output: {example['output']}"
        )
    }


def build_trainer(model, tokenizer, dataset):
    lora_config = LoraConfig(
        r=8,
        lora_alpha=16,
        target_modules=["q_proj", "v_proj"],
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM",
    )

    sftconfig = SFTConfig(
        output_dir=OUTPUT_DIR,
        num_train_epochs=4,
        per_device_train_batch_size=2,
        gradient_accumulation_steps=4,
        warmup_steps=10,
        learning_rate=2e-4,
        fp16=True,
        logging_steps=10,
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        report_to="none",
        max_length=MAX_SEQ_LEN,
        dataset_text_field="text"
    )

    return SFTTrainer(
        model=model,
        train_dataset=dataset["train"],
        eval_dataset=dataset["validation"],
        peft_config=lora_config,
        processing_class=tokenizer,
        args=sftconfig
    )

def main() -> None:
    print("Loading tokenizer...")
    tokenizer = load_tokenizer()
    print("Loading model...")
    model = load_model()
    print("Prepping dataset...")
    dataset = prep_dataset()
    print("Building trainer...")
    trainer = build_trainer(model, tokenizer, dataset)

    print("Starting training...")
    trainer.train()

    print(f"Saving adapters to {OUTPUT_DIR}")
    trainer.save_model(OUTPUT_DIR)
    print("Done.")


if __name__ == "__main__":
    main()
