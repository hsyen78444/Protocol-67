import json
from pathlib import Path

from model_service.src.translator import translate_text


ROOT = Path(__file__).resolve().parents[2]
TEST_FILE = ROOT / "data_pipeline" / "data" / "processed" / "test.jsonl"


def main() -> None:
    if not TEST_FILE.exists():
        raise FileNotFoundError(f"Missing {TEST_FILE}. Run the data pipeline first.")

    exact = 0
    total = 0
    for line in TEST_FILE.read_text(encoding="utf-8").splitlines():
        record = json.loads(line)
        prediction = translate_text(record["input"])["formal_translation"]
        if prediction.strip().lower() == record["output"].strip().lower():
            exact += 1
        total += 1
    print({"total": total, "exact_match": exact, "exact_match_rate": exact / total if total else 0})


if __name__ == "__main__":
    main()
