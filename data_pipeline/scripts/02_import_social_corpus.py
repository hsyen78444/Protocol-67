"""
Import Twitter/X-style and Twitch-style corpora.

This script intentionally does not scrape Twitter/X. X API access can require
authentication, paid tiers, and strict platform policy compliance. The pipeline
is connector-ready: provide local CSV or JSONL exports from approved public
datasets, or use the safe fallback corpus for coursework demonstrations.
"""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path
from typing import Iterable, List

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
COLUMNS = ["text", "platform", "source_type", "collection_date"]


TWITTER_TEMPLATES = [
    "lowkey the lecture notes hit different rn",
    "that group presentation ate ngl",
    "idk why the new update feels mid",
    "coffee after lab is a w fr",
    "the assignment deadline has me cooked",
    "this playlist slaps while studying",
    "the campus wifi is sus today",
    "valid take but the example was confusing",
    "the poster design is clean no cap",
    "my sleep schedule fell off this week",
    "locked in for finals rn",
    "the library vibe is calm today",
    "that explanation was based imo",
    "bruh the printer is tweaking again",
    "the cafeteria noodles are bussin",
    "this timetable is giving side quest energy",
    "group chat is yapping about fonts",
    "the demo worked first try, big w",
    "that bug is big yikes",
    "her analysis is on point",
    "this article lives rent free in my head",
    "the tutorial speedrun was wild",
    "that outfit had drip",
    "the intro slide understood the assignment",
    "my code got nerfed by one typo",
    "the new rubric is actually chill",
    "that hot take about exams is valid",
    "the edit was fire but the audio was mid",
    "main character energy walking into class early",
    "the meeting became a side quest",
]

TWITCH_TEMPLATES = [
    "chat this run is cooked fr",
    "w save by the support",
    "l timing on that jump",
    "let him cook he has a plan",
    "that combo was goated",
    "the boss music slaps",
    "npc pathing moment",
    "skill issue but respectfully",
    "clutch heal no cap",
    "stop yapping and watch the play",
    "aura farming before the match",
    "that dodge was clean",
    "bro is locked in rn",
    "chat is tweaking over one miss",
    "peak gameplay ngl",
    "the patch buffed the healer",
    "that map got nerfed hard",
    "camping the corner is cringe",
    "speedrun strats are wild",
    "valid reset after that mistake",
    "this lobby is full of sweats",
    "tryhard mode activated",
    "the carry was real",
    "that fanum tax joke sent chat",
    "skibidi comments took over",
    "the vibe check passed",
    "pookie with the clutch revive",
    "that was a canon event for the run",
    "sus door on the left",
    "boss move saving the ult",
]


def load_any(path: str | None, platform: str) -> pd.DataFrame | None:
    if not path:
        return None
    source = Path(path)
    if not source.exists():
        raise FileNotFoundError(f"Input file not found: {source}")

    if source.suffix.lower() == ".csv":
        df = pd.read_csv(source)
    elif source.suffix.lower() == ".jsonl":
        rows = [json.loads(line) for line in source.read_text(encoding="utf-8").splitlines() if line.strip()]
        df = pd.DataFrame(rows)
    else:
        raise ValueError("Only CSV and JSONL inputs are supported.")

    text_col = "text" if "text" in df.columns else df.columns[0]
    out = pd.DataFrame({"text": df[text_col].astype(str)})
    out["platform"] = platform
    out["source_type"] = f"local_{source.suffix.lower().lstrip('.')}"
    out["collection_date"] = date.today().isoformat()
    return out[COLUMNS]


def expand_templates(templates: Iterable[str], target_size: int) -> List[str]:
    template_list = list(templates)
    contexts = [
        "after class", "during revision", "in the group chat", "before the deadline",
        "while testing", "after the patch", "during practice", "on the bus",
    ]
    texts: List[str] = []
    for i in range(target_size):
        base = template_list[i % len(template_list)]
        suffix = contexts[i % len(contexts)]
        texts.append(f"{base} {suffix}" if i >= len(template_list) else base)
    return texts


def fallback_df(platform: str, templates: List[str]) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "text": expand_templates(templates, 100),
            "platform": platform,
            "source_type": "synthetic_coursework_fallback",
            "collection_date": date.today().isoformat(),
        }
    )[COLUMNS]


def save(df: pd.DataFrame, filename: str) -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    df.dropna(subset=["text"]).drop_duplicates(subset=["text"]).to_csv(RAW_DIR / filename, index=False)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--twitter-input", help="Optional CSV or JSONL file with a text column.")
    parser.add_argument("--twitch-input", help="Optional CSV or JSONL file with a text column.")
    args = parser.parse_args()

    twitter = load_any(args.twitter_input, "twitter_x")
    twitch = load_any(args.twitch_input, "twitch")
    if twitter is None:
        twitter = fallback_df("twitter_x", TWITTER_TEMPLATES)
    if twitch is None:
        twitch = fallback_df("twitch", TWITCH_TEMPLATES)

    save(twitter, "twitter_corpus_raw.csv")
    save(twitch, "twitch_corpus_raw.csv")
    print(f"Saved {len(twitter)} Twitter/X-style rows and {len(twitch)} Twitch-style rows.")


if __name__ == "__main__":
    main()
