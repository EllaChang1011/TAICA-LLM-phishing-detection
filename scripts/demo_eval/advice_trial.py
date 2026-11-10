"""Try the advice-generation step with two candidate models on a few emails.

Not an evaluation — a side-by-side for reading, to decide which model to use
before building a proper practice / held-out test.

Usage:
  python scripts/demo_eval/advice_trial.py

Output: eval_results/advice_trial/trial.md and trial.json
"""

import json
import re
import sys
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "demo"))
from advice import generate_advice  # noqa: E402
from alert_rag import EMBEDDING_MODEL, AlertIndex  # noqa: E402
from pipeline import OLLAMA_URL  # noqa: E402

MODELS = ["phishing-detector-14b", "qwen3:14b"]
OPTIONS = {"temperature": 0.0, "num_predict": 1500}
OUT_DIR = ROOT / "eval_results/advice_trial"

# (label, test index) — emails that already retrieve alerts in the practice sets
CASES = [("T01 包裹運費", 144), ("T05 退稅", 15), ("T09 慈善捐款", 148), ("T10 Netflix 帳單", 109)]


def exam_index(exam_id: str) -> int:
    text = (ROOT / "eval_results/tactic_exam/answers.md").read_text(encoding="utf-8")
    return int(re.search(rf"## {exam_id}\s+\(test index (\d+)\)", text).group(1))


def make_call(model: str):
    def call(prompt: str) -> str:
        r = requests.post(OLLAMA_URL, json={"model": model, "prompt": prompt, "stream": False, "options": OPTIONS},
                          timeout=600)
        r.raise_for_status()
        return r.json().get("response", "")
    return call


def main():
    from sentence_transformers import SentenceTransformer
    index = AlertIndex(SentenceTransformer(EMBEDDING_MODEL, device="cuda"))
    records = json.loads((ROOT / "data/test/data.json").read_text(encoding="utf-8"))
    cases = CASES + [("E07 標成正常的退稅詐騙", exam_index("E07"))]

    results = []
    for name, idx in cases:
        email = records[idx]["input"]
        alerts = index.search(email)
        row = {"case": name, "test_index": idx, "alerts": [(a["ref"], round(a["score"], 3)) for a in alerts], "models": {}}
        for model in MODELS:
            if not alerts:
                continue
            start = time.time()
            out = generate_advice(email, alerts, make_call(model))
            out["seconds"] = round(time.time() - start, 1)
            row["models"][model] = out
            print(f"{name} | {model}: match={'ok' if out['match'] else 'none'} advice={len(out['advice'])} "
                  f"rejected={len(out['rejected'])} ({out['seconds']}s)", flush=True)
        results.append(row)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "trial.json").write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = ["# 生成步驟試用：兩個模型並排", "",
             "不是正式評測，只用來決定用哪個模型。每句都經過出處檢查；被丟掉的列在最後。", ""]
    for row in results:
        lines += ["---", "", f"## {row['case']}（test {row['test_index']}）", "",
                  f"顯示的警示：{', '.join(f'{r} {s}' for r, s in row['alerts']) or '無（不生成）'}", ""]
        for model, out in row["models"].items():
            lines += [f"### {model}（{out['seconds']} 秒）", ""]
            if out.get("parse_error"):
                lines += ["JSON 解析失敗。", "", "```", out["raw_output"][:1500], "```", ""]
                continue
            m = out["match"]
            lines.append(f"- **相同手法**：{m['text']}（{m['alert']}）" if m else "- **相同手法**：（沒有通過檢查）")
            if m:
                lines += [f"  - 信中原句：「{m['email_quote']}」", f"  - 警示原句：「{m['alert_quote']}」"]
            for a in out["advice"]:
                lines += [f"- **建議**：{a['text']}（{a['alert']}）", f"  - 警示原句：「{a['quote']}」"]
            for x in out["rejected"]:
                lines.append(f"- ❌ 丟掉（{x['reason']}，score {x.get('score', '-')}）：`{json.dumps(x['item'], ensure_ascii=False)[:200]}`")
            lines.append("")
    (OUT_DIR / "trial.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {OUT_DIR / 'trial.md'}")


if __name__ == "__main__":
    main()
