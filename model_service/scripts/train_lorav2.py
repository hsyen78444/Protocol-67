import torch
from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig, EarlyStoppingCallback
from peft import LoraConfig, prepare_model_for_kbit_training
from trl import SFTTrainer, SFTConfig

BASE_MODEL = "meta-llama/Llama-3.2-3B-Instruct"
TRAIN_FILE = "data_pipeline/data/processed/train.jsonl"
VAL_FILE = "data_pipeline/data/processed/validation.jsonl"
OUTPUT_DIR = "model_service/outputs/llama3b-slang-lora"
MAX_SEQ_LEN = 128

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
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float32,
        bnb_4bit_use_double_quant=True,
    )

    model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL,
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True,
        dtype=torch.float16
    )
    # model.enable_input_require_grads()
    model = prepare_model_for_kbit_training(model)
    model.config.use_cache = False
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
                "You are an expert linguistics assistant. Your task is to analyze internet "
                "slang and brainrot text, identify its sentiment, extract the slang terms "
                "present, and provide a clear, formal English translation."
            )
        },
        {
            "role": "user",
            "content": f"Analyze and translate this text: {example['input']}"
        },
        {
            "role": "assistant",
            "content": (
                f"Sentiment: {sentiment}\n"
                f"Slang terms: {slang_str}\n"
                f"Translation: {example['output']}"
            )
        }
    ]
    return {"text": tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=False)}


def build_trainer(model, tokenizer, dataset):
    lora_config = LoraConfig(
        r=8,
        lora_alpha=16,
        target_modules=["q_proj", "v_proj", "k_proj", "o_proj"],
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM",
    )

    sftconfig = SFTConfig(
        output_dir=OUTPUT_DIR,
        num_train_epochs=2,
        per_device_train_batch_size=1,
        gradient_accumulation_steps=8,
        warmup_steps=10,
        learning_rate=2e-4,
        lr_scheduler_type="cosine",
        fp16=False,
        bf16=False,
        optim="paged_adamw_8bit",
        logging_steps=5,
        eval_strategy="steps",
        eval_steps=100,
        save_strategy="steps",
        save_steps=100,
        load_best_model_at_end=True,
        report_to="none",
        max_length=MAX_SEQ_LEN,
        dataset_text_field="text",
        gradient_checkpointing=True,
        gradient_checkpointing_kwargs={"use_reentrant": False},
        packing=True
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
