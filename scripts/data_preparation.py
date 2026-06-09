#!/usr/bin/env python3
"""
Prepare phishing email dataset for QLoRA fine-tuning.
Outputs train/val/test splits in Alpaca JSON format.
"""

import json
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

ARCHIVE = Path("data/archive")
SEED = 42

INSTRUCTION = (
    "Classify the following email as phishing or legitimate. "
    "Reply with a single word: phishing or legitimate."
)


def read_llm_csv_robust(path: str) -> pd.DataFrame:
    """Read LLM-generated CSV where text may contain unescaped commas."""
    rows = []
    with open(path, encoding="utf-8-sig") as f:
        lines = f.readlines()
    for line in lines[1:]:  # skip header
        line = line.rstrip("\r\n")
        if not line:
            continue
        parts = line.rsplit(",", 1)
        if len(parts) == 2 and parts[1].strip() in ("0", "1"):
            rows.append({"text": parts[0].strip(), "label": int(parts[1].strip())})
    return pd.DataFrame(rows)


def load_all_data() -> pd.DataFrame:
    frames = []

    # Human-generated (subject + body merged into text)
    for csv_path, label_str in [
        (ARCHIVE / "human-generated" / "phishing_human-generated.csv", "phishing"),
        (ARCHIVE / "human-generated" / "legit_human-generated.csv", "legitimate"),
    ]:
        df = pd.read_csv(csv_path)
        df["text"] = (
            df["subject"].fillna("").astype(str)
            + "\n\n"
            + df["body"].fillna("").astype(str)
        ).str.strip()
        df["label"] = label_str
        df["source"] = "human"
        frames.append(df[["text", "label", "source"]])

    # LLM-generated
    for csv_path, label_str in [
        (ARCHIVE / "llm-generated" / "phishing_llm-generated.csv", "phishing"),
        (ARCHIVE / "llm-generated" / "legit_llm-generated.csv", "legitimate"),
    ]:
        df = read_llm_csv_robust(str(csv_path))
        df["label"] = label_str
        df["source"] = "llm"
        frames.append(df[["text", "label", "source"]])

    combined = pd.concat(frames, ignore_index=True)
    combined["text"] = combined["text"].fillna("").astype(str).str.strip()
    combined = combined[combined["text"] != ""].reset_index(drop=True)
    return combined


def to_alpaca(df: pd.DataFrame) -> list[dict]:
    records = []
    for _, row in df.iterrows():
        text = row["text"]
        if len(text) > 6000:
            text = text[:6000]
        records.append(
            {
                "instruction": INSTRUCTION,
                "input": text,
                "output": row["label"],   # just "phishing" or "legitimate"
                "label": row["label"],
                "source": row["source"],
            }
        )
    return records


def main():
    print("Loading data...")
    df = load_all_data()

    # Build a stratified split key: source × label
    df["stratum"] = df["source"] + "_" + df["label"]
    print("\nData distribution:")
    print(df["stratum"].value_counts().to_string())
    print(f"\nTotal: {len(df)} emails")

    # Stratified split: 80/10/10
    train_df, temp_df = train_test_split(
        df, test_size=0.2, stratify=df["stratum"], random_state=SEED
    )
    val_df, test_df = train_test_split(
        temp_df, test_size=0.5, stratify=temp_df["stratum"], random_state=SEED
    )

    print(f"\nSplit sizes — train: {len(train_df)}, val: {len(val_df)}, test: {len(test_df)}")

    for split_name, split_df in [("train", train_df), ("val", val_df), ("test", test_df)]:
        out_dir = Path("data") / split_name
        out_dir.mkdir(exist_ok=True)
        records = to_alpaca(split_df.reset_index(drop=True))
        out_path = out_dir / "data.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(records, f, ensure_ascii=False, indent=2)
        print(f"Saved {len(records)} records → {out_path}")

    print("\nDone.")


if __name__ == "__main__":
    main()
