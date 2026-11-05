"""Run the demo pipeline (demo/pipeline.py) end to end on the whole test split.

This is a system check, not a tuning step: it reports how the demo behaves on
400 emails — classification metrics, how often the tactic analysis and the
classifier disagree (the demo's "please review manually"), how often alerts
are shown, evidence-check rejections, look-alike character flags, and latency.

Part of the test split was used earlier to tune things (the 20-email tactic
practice set, the 30-email alert practice set), so the tactic/alert numbers
here are not fully held-out; the per-subset breakdown in the report shows this.

Usage:
  python scripts/pipeline_eval.py            # all 400 (resumes if interrupted)
  python scripts/pipeline_eval.py --limit 5  # quick check

Outputs (eval_results/pipeline/):
  results.jsonl   one line per email (appended as it runs)
  report.md       summary
"""

import argparse
import json
import re
import sys
import time
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "demo"))
sys.path.insert(0, str(ROOT / "scripts"))
from alert_rag import EMBEDDING_MODEL, THRESHOLD, AlertIndex  # noqa: E402
from CoT_Module import load_tactics  # noqa: E402
from pipeline import MODEL_NAME, run_pipeline  # noqa: E402

TEST_PATH    = ROOT / "data/test/data.json"
OUT_DIR      = ROOT / "eval_results/pipeline"
RESULTS_PATH = OUT_DIR / "results.jsonl"
REPORT_PATH  = OUT_DIR / "report.md"


def tuning_subsets() -> dict[int, str]:
    """test index -> which earlier experiment looked at it."""
    from tactic_cards_eval import sample_emails
    tags = {item["test_index"]: "招數練習集" for item in sample_emails()}
    for path, tag in [(ROOT / "eval_results/tactic_exam/answers.md", "招數考試集"),
                      (ROOT / "eval_results/alert_rag/answers.md", "警示練習集")]:
        for idx in map(int, re.findall(r"test index (\d+)", path.read_text(encoding="utf-8"))):
            tags.setdefault(idx, tag)
    return tags


def slim(idx: int, record: dict, result: dict, seconds: float) -> dict:
    a = result["analysis"]
    lure = a.get("lure")
    return {
        "test_index": idx, "label": record["label"], "source": record["source"],
        "classification": result["classification"],
        "parse_error": bool(a.get("parse_error")),
        "lure": lure["id"] if lure else None,
        "techniques": [t["id"] for t in a.get("techniques", [])],
        "rejected": [x["reason"] for x in a.get("rejected", [])],
        "alerts": None if result["alerts"] is None else [(x["ref"], round(x["score"], 4)) for x in result["alerts"]],
        "homoglyph_words": [w["looks_like"] for w in result["homoglyphs"]],
        "phishing_without_tactic": result["phishing_without_tactic"],
        "legit_with_tactic": result["legit_with_tactic"],
        "seconds": round(seconds, 2),
    }


def pct(n: int, d: int) -> str:
    return f"{n}/{d}（{100 * n / d:.1f}%）" if d else "—"


def write_report(rows: list[dict], tags: dict[int, str]):
    n = len(rows)
    tp = sum(r["classification"] == "phishing" and r["label"] == "phishing" for r in rows)
    fp = sum(r["classification"] == "phishing" and r["label"] == "legitimate" for r in rows)
    fn = sum(r["classification"] == "legitimate" and r["label"] == "phishing" for r in rows)
    acc = sum(r["classification"] == r["label"] for r in rows) / n
    prec = tp / (tp + fp) if tp + fp else 0.0
    rec = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0.0

    groups = [(lab, src) for lab in ("phishing", "legitimate") for src in ("human", "llm")]
    def sub(lab, src): return [r for r in rows if r["label"] == lab and r["source"] == src]

    lines = [
        "# Demo 流程全測試集評測", "",
        f"模型 `{MODEL_NAME}`、embedding `{EMBEDDING_MODEL}`、警示門檻 {THRESHOLD:.2f}。共 {n} 封（data/test）。", "",
        "## 1. 分類（決定判定結果的唯一一步）", "",
        "| 指標 | 數值 | README 記錄（14B） |", "|---|---|---|",
        f"| Accuracy | {acc:.4f} | 0.8875 |",
        f"| Precision | {prec:.3f} | 0.833 |",
        f"| Recall | {rec:.3f} | 0.970 |",
        f"| F1 | {f1:.3f} | 0.896 |", "",
        "| 類別 | 分類正確 |", "|---|---|",
    ]
    lines += [f"| {lab} / {src} | {pct(sum(r['classification'] == lab for r in sub(lab, src)), len(sub(lab, src)))} |"
              for lab, src in groups]

    lines += ["", "## 2. 判斷與分析不一致（demo 顯示「建議人工確認」）", "",
              "| 類別 | 判釣魚但沒找到招數 | 判正常但找到招數或警示 |", "|---|---|---|"]
    for lab, src in groups:
        s = sub(lab, src)
        lines.append(f"| {lab} / {src} | {pct(sum(r['phishing_without_tactic'] for r in s), len(s))} | "
                     f"{pct(sum(r['legit_with_tactic'] for r in s), len(s))} |")
    lines.append(f"| **全部** | {pct(sum(r['phishing_without_tactic'] for r in rows), n)} | "
                 f"{pct(sum(r['legit_with_tactic'] for r in rows), n)} |")

    lines += ["", "## 3. 招數分析", "",
              "| 類別 | 有招數 | 誘餌 = none | 誘餌無效（被檢查擋掉） | JSON 解析失敗 |", "|---|---|---|---|---|"]
    for lab, src in groups:
        s = sub(lab, src)
        lines.append(f"| {lab} / {src} | {pct(sum(bool(r['lure'] not in (None, 'none') or r['techniques']) and not r['parse_error'] for r in s), len(s))} | "
                     f"{pct(sum(r['lure'] == 'none' for r in s), len(s))} | "
                     f"{pct(sum(r['lure'] is None and not r['parse_error'] for r in s), len(s))} | "
                     f"{pct(sum(r['parse_error'] for r in s), len(s))} |")
    reasons = Counter(x for r in rows for x in r["rejected"])
    lines += ["", f"被檢查丟掉的推論：{dict(reasons) or '無'}", "",
              "誘餌分布（釣魚信）：" + ", ".join(f"{k} {v}" for k, v in
                                          Counter(r["lure"] for r in rows if r["label"] == "phishing").most_common()), ""]

    lines += ["## 4. 詐騙警示", "",
              "| 類別 | 不查詢（誘餌 none） | 查了但沒有警示過門檻 | 顯示至少 1 則 |", "|---|---|---|---|"]
    for lab, src in groups:
        s = sub(lab, src)
        lines.append(f"| {lab} / {src} | {pct(sum(r['alerts'] is None for r in s), len(s))} | "
                     f"{pct(sum(r['alerts'] == [] for r in s), len(s))} | "
                     f"{pct(sum(bool(r['alerts']) for r in s), len(s))} |")
    top = Counter(r["alerts"][0][0] for r in rows if r["alerts"])
    lines += ["", "第一名警示的分布：" + ", ".join(f"{k} {v}" for k, v in top.most_common()), ""]

    lines += ["## 5. 外型相近字元", "", "| 類別 | 被標記 |", "|---|---|"]
    lines += [f"| {lab} / {src} | {pct(sum(bool(r['homoglyph_words']) for r in sub(lab, src)), len(sub(lab, src)))} |"
              for lab, src in groups]

    secs = sorted(r["seconds"] for r in rows)
    lines += ["", "## 6. 速度", "",
              f"每封平均 {sum(secs) / n:.1f} 秒，中位數 {secs[n // 2]:.1f} 秒，最慢 {secs[-1]:.1f} 秒。", ""]

    tagged = Counter(tags.get(r["test_index"], "未用過") for r in rows)
    untouched = [r for r in rows if r["test_index"] not in tags]
    lines += ["## 7. 哪些信之前看過", "",
              "部分測試集信件之前用來調整 prompt 或門檻，所以招數與警示的數字不完全是獨立結果。", "",
              "| 子集 | 封數 |", "|---|---|"] + [f"| {k} | {v} |" for k, v in tagged.most_common()]
    if untouched:
        lines += ["", f"只看「未用過」的 {len(untouched)} 封：判正常但找到招數或警示 "
                  f"{pct(sum(r['legit_with_tactic'] for r in untouched), len(untouched))}；"
                  f"判釣魚但沒找到招數 {pct(sum(r['phishing_without_tactic'] for r in untouched), len(untouched))}。"]
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()

    records = json.loads(TEST_PATH.read_text(encoding="utf-8"))
    todo = list(range(len(records)))[: args.limit]
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    done = {}
    if RESULTS_PATH.exists():
        for line in RESULTS_PATH.read_text(encoding="utf-8").splitlines():
            row = json.loads(line)
            done[row["test_index"]] = row

    from sentence_transformers import SentenceTransformer
    alert_index = AlertIndex(SentenceTransformer(EMBEDDING_MODEL, device="cuda"))
    tactics = load_tactics()

    with RESULTS_PATH.open("a", encoding="utf-8") as out:
        for n, idx in enumerate(todo, 1):
            if idx in done:
                continue
            start = time.time()
            result = run_pipeline(records[idx]["input"], tactics, alert_index, with_advice=False)
            row = slim(idx, records[idx], result, time.time() - start)
            out.write(json.dumps(row, ensure_ascii=False) + "\n")
            out.flush()
            done[idx] = row
            print(f"[{n}/{len(todo)}] idx={idx} {row['label']}/{row['source']} -> {row['classification']} "
                  f"lure={row['lure']} alerts={len(row['alerts'] or [])} ({row['seconds']}s)", flush=True)

    write_report([done[i] for i in todo], tuning_subsets())
    print(f"Wrote {REPORT_PATH}")


if __name__ == "__main__":
    main()
