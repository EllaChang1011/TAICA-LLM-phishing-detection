"""Evaluate the advice-generation step (rules: eval_results/advice_eval/rules.md).

    .venv/bin/python scripts/advice_eval.py practice --tag v0   # P01-P10, may be re-run after prompt edits
    .venv/bin/python scripts/advice_eval.py validate            # G01-G20, runs ONCE

Both run demo/pipeline.run_pipeline() with advice on, exactly as the demo does, and
write a labelling sheet that shows the email, each displayed sentence and its quotes,
but not the classification result.
"""
import argparse
import json
import random
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "demo"))
from alert_rag import EMBEDDING_MODEL, AlertIndex  # noqa: E402
from CoT_Module import load_tactics  # noqa: E402
from pipeline import ADVICE_MODEL, ADVICE_OPTIONS, run_pipeline  # noqa: E402

OUT_DIR = ROOT / "eval_results/advice_eval"
SEED = 42
N_PRACTICE, N_VALIDATE = 10, 20
TRIAL_TEST_INDICES = {144, 15, 148, 109}          # advice_trial.py cases; E07 is looked up below


def exam_index(exam_id):
    text = (ROOT / "eval_results/tactic_exam/answers.md").read_text(encoding="utf-8")
    return int(re.search(rf"## {exam_id}\s+\(test index (\d+)\)", text).group(1))


def used_val_indices():
    text = (ROOT / "eval_results/alert_rag/validation/answers.md").read_text(encoding="utf-8")
    return {int(i) for i in re.findall(r"^## [VW]\d+\s+\(val index (\d+)\)", text, flags=re.M)}


def practice_indices():
    rows = [json.loads(line) for line in (ROOT / "eval_results/pipeline/results.jsonl").open(encoding="utf-8")]
    excluded = TRIAL_TEST_INDICES | {exam_index("E07")}
    pool = sorted(r["test_index"] for r in rows if r["alerts"] and r["test_index"] not in excluded)
    return sorted(random.Random(SEED).sample(pool, N_PRACTICE))


def git_commit():
    out = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True, text=True)
    dirty = subprocess.run(["git", "status", "--porcelain", "demo/"], cwd=ROOT, capture_output=True, text=True)
    return out.stdout.strip() + (" (demo/ has uncommitted changes)" if dirty.stdout.strip() else "")


def run_one(email, tactics, index):
    out = run_pipeline(email, tactics, index, with_advice=True)
    advice = out["advice"]
    return {
        "classification": out["classification"],
        "alerts": [(a["ref"], round(a["score"], 3)) for a in out["alerts"] or []],
        "advice": None if advice is None else {k: advice.get(k) for k in ("match", "advice", "rejected", "parse_error", "raw_output")},
        "seconds_advice": round(out["timings"].get("advice", 0.0), 1),
    }


def sentences(advice):
    """Displayed sentences, in display order: (kind, text, quotes)."""
    if not advice or advice.get("parse_error"):
        return []
    rows = []
    if advice["match"]:
        m = advice["match"]
        rows.append(("match", m["text"], [("信中原句", m["email_quote"]), (f"警示原句 {m['alert']}", m["alert_quote"])]))
    for a in advice["advice"]:
        rows.append(("advice", a["text"], [(f"警示原句 {a['alert']}", a["quote"])]))
    return rows


def write_sheet(path, title, cases, email_chars=2500):
    lines = [f"# {title}", "",
             "依 rules.md 第 3、4 節標註。每句填：忠實／誇大／錯誤；再填這句放在這封信上是否適用（是／否）。",
             "只拿這句跟它自己引用的原句比。分類結果刻意不顯示。", ""]
    for c in cases:
        lines += ["---", "", f"## {c['id']}  ({c['split']} index {c['index']})", "",
                  f"顯示的警示：{', '.join(f'{r} {s}' for r, s in c['alerts'])}", "", "<details><summary>信件原文</summary>", "",
                  "```", c["email"][:email_chars] + ("\n…（以下省略）" if len(c["email"]) > email_chars else ""), "```", "",
                  "</details>", ""]
        rows = sentences(c["advice"])
        if not rows:
            lines += ["**無輸出**（沒有句子通過檢查，或格式錯誤）", ""]
        for n, (kind, text, quotes) in enumerate(rows, 1):
            lines.append(f"### {c['id']}-{n}  {'相同手法' if kind == 'match' else '建議'}")
            lines.append(f"- 說明：{text}")
            lines += [f"- {name}：「{q}」" for name, q in quotes]
            lines += ["- 忠實度：", "- 適用：", ""]
        rejected = (c["advice"] or {}).get("rejected") or []
        if rejected:
            lines.append(f"被程式擋下 {len(rejected)} 句：" + "、".join(x["reason"] for x in rejected))
            lines.append("")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def load_index():
    from sentence_transformers import SentenceTransformer
    return AlertIndex(SentenceTransformer(EMBEDDING_MODEL, device="cuda"))


def practice(tag):
    tactics, index = load_tactics(), load_index()
    records = json.loads((ROOT / "data/test/data.json").read_text(encoding="utf-8"))
    cases = []
    for n, idx in enumerate(practice_indices(), 1):
        email = records[idx]["input"]
        case = {"id": f"P{n:02d}", "split": "test", "index": idx, "label": records[idx]["label"],
                "source": records[idx]["source"], "email": email, **run_one(email, tactics, index)}
        cases.append(case)
        print(f"{case['id']} test {idx}: alerts={case['alerts']} sentences={len(sentences(case['advice']))} "
              f"rejected={len((case['advice'] or {}).get('rejected') or [])} ({case['seconds_advice']}s)", flush=True)
    meta = {"tag": tag, "commit": git_commit(), "model": ADVICE_MODEL, "options": ADVICE_OPTIONS}
    (OUT_DIR / f"practice_{tag}.json").write_text(json.dumps({"meta": meta, "cases": cases}, ensure_ascii=False, indent=2),
                                                   encoding="utf-8")
    write_sheet(OUT_DIR / f"practice_{tag}.md", f"建議生成 練習組（{tag}）", cases)
    print(f"Wrote {OUT_DIR / f'practice_{tag}.md'}")


def validate():
    out_json = OUT_DIR / "validation.json"
    if out_json.exists():
        sys.exit(f"{out_json} already exists: the validation set runs once (rules.md section 6).")
    tactics, index = load_tactics(), load_index()
    records = json.loads((ROOT / "data/val/data.json").read_text(encoding="utf-8"))
    order = [i for i in range(len(records)) if i not in used_val_indices()]
    random.Random(SEED).shuffle(order)
    cases, skipped = [], []
    for idx in order:
        if len(cases) == N_VALIDATE:
            break
        email = records[idx]["input"]
        result = run_one(email, tactics, index)
        if not result["alerts"]:
            skipped.append(idx)
            continue
        case = {"id": f"G{len(cases) + 1:02d}", "split": "val", "index": idx, "label": records[idx]["label"],
                "source": records[idx]["source"], "email": email, **result}
        cases.append(case)
        print(f"{case['id']} val {idx}: alerts={case['alerts']} sentences={len(sentences(case['advice']))} "
              f"rejected={len((case['advice'] or {}).get('rejected') or [])} ({case['seconds_advice']}s)", flush=True)
    meta = {"commit": git_commit(), "model": ADVICE_MODEL, "options": ADVICE_OPTIONS,
            "skipped_without_alerts": skipped}
    out_json.write_text(json.dumps({"meta": meta, "cases": cases}, ensure_ascii=False, indent=2), encoding="utf-8")
    write_sheet(OUT_DIR / "validation_author_G01-G10.md", "建議生成 驗證組 G01～G10（作者從頭標）", cases[:10])
    write_sheet(OUT_DIR / "validation_sheet.md", "建議生成 驗證組 G01～G20", cases)
    print(f"Wrote {out_json}; {len(skipped)} emails skipped because no alert was shown")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("practice")
    p.add_argument("--tag", default="v0")
    sub.add_parser("validate")
    args = ap.parse_args()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    practice(args.tag) if args.cmd == "practice" else validate()
