from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
PROCESSED = ROOT / "data_pipeline" / "data" / "processed"


def main() -> None:
    for name in ["train", "validation", "test"]:
        path = PROCESSED / f"{name}.jsonl"
        if not path.exists():
            raise FileNotFoundError(f"Missing {path}. Run the data pipeline first.")
        frame = pd.read_json(path, lines=True)
        print(f"{name}: {len(frame)} rows")
        print(frame.head(2).to_string(index=False))


if __name__ == "__main__":
    main()
