"""LoRA fine-tuning entrypoint placeholder.

Member 2 should wire this to the chosen base model after confirming available
hardware. Keep output artifacts under `model_service/outputs/` or
`model_service/models/`, both ignored by Git.
"""


def main() -> None:
    print("TODO: load train.jsonl, tokenize prompts, fine-tune with PEFT/LoRA, save adapter.")


if __name__ == "__main__":
    main()
