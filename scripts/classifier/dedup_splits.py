#!/usr/bin/env python3
"""
Build duplicate-free splits in data/dedup/ from the existing data/{train,val,test}.

The original split did not dedupe: ~1/3 of val and test were copies of train emails.
New test = old test minus anything in old train (val likewise), so the old model
never trained on the new test either and its scores stay comparable.
data/{train,val,test} are left untouched: demo_eval refers to them by index.
"""

import json
from pathlib import Path

OUT = Path("data/dedup")


def key(rec):
    return " ".join(rec["input"].split()).lower()


def load(split):
    return json.loads(Path(f"data/{split}/data.json").read_text(encoding="utf-8"))


def unique(records, seen):
    out = []
    for i, r in enumerate(records):
        k = key(r)
        if k not in seen:
            seen.add(k)
            out.append({**r, "orig_index": i})  # index into the old split
    return out


def main():
    train, val, test = load("train"), load("val"), load("test")
    seen = {key(r) for r in train}
    new_test = unique(test, seen)
    new_val = unique(val, seen)
    new_train = unique(train, set())

    keys = [{key(r) for r in s} for s in (new_train, new_val, new_test)]
    assert not (keys[0] & keys[1] or keys[0] & keys[2] or keys[1] & keys[2])

    for name, recs in [("train", new_train), ("val", new_val), ("test", new_test)]:
        (OUT / name).mkdir(parents=True, exist_ok=True)
        (OUT / name / "data.json").write_text(json.dumps(recs, ensure_ascii=False, indent=2), encoding="utf-8")
        counts = {}
        for r in recs:
            counts[f"{r['source']}_{r['label']}"] = counts.get(f"{r['source']}_{r['label']}", 0) + 1
        print(f"{name}: {len(recs)}  {dict(sorted(counts.items()))}")


if __name__ == "__main__":
    main()
