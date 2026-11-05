"""The demo's analysis pipeline, without any Streamlit code, so the demo and
scripts/pipeline_eval.py run exactly the same logic.

1. classify   — fine-tuned model; the only step that decides the verdict
2. tactics    — tactic cards + verified evidence (explanation only)
3. alerts     — FTC scam alerts, skipped only when the tactic analysis says "none"
4. advice     — what to do, generated from the shown alerts only, every sentence sourced
5. homoglyphs — deterministic check for look-alike characters
"""

import os
import time

import requests

from CoT_Module import build_tactic_prompt, extract_json, find_homoglyph_words, verify_tactic_report
from advice import generate_advice

OLLAMA_BASE_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
OLLAMA_URL = f"{OLLAMA_BASE_URL}/api/generate"
MODEL_NAME = os.environ.get("MODEL_NAME", "phishing-detector-14b")
# The fine-tuned model only learned to answer one word; generation uses the base model,
# which followed the sourcing rules much better in eval_results/advice_trial/trial.md.
ADVICE_MODEL = os.environ.get("ADVICE_MODEL", "qwen3:14b")
MAX_ANALYSIS_CHARS = 6000

# Same options as scripts/evaluate.py, so the demo runs the evaluated setting. (The old
# demo added repeat/frequency penalties, which cost 0.75 points on the test split.)
# num_ctx: Ollama's default context here is 32768 tokens (~14 GB per 14B model), so the
# classifier and the generation model could not both stay on a 24 GB GPU and were
# reloaded on every request. The longest test/val email is ~2,100 tokens and the largest
# prompt + output ~4,500, so 8192 truncates nothing.
NUM_CTX = 8192
CLASSIFY_OPTIONS = {"temperature": 0.0, "num_predict": 16, "num_ctx": NUM_CTX}
# No repetition penalties: they push the model to paraphrase, which breaks verbatim quotes.
TACTIC_OPTIONS = {"temperature": 0.0, "num_predict": 1024, "num_ctx": NUM_CTX}
ADVICE_OPTIONS = {"temperature": 0.0, "num_predict": 1500, "num_ctx": NUM_CTX}


def call_ollama(prompt, options, model=MODEL_NAME, timeout=120):
    try:
        response = requests.post(
            OLLAMA_URL,
            json={"model": model, "prompt": prompt, "stream": False, "options": options},
            timeout=timeout
        )
        return response.json().get("response", "")
    except requests.exceptions.ConnectionError:
        return "ERROR: 無法連線到 Ollama，請確認是否正在執行。"
    except Exception as e:
        return f"ERROR: {str(e)}"


def classify_email(email_text):
    prompt = f"""/no_think
Classify the following email as phishing or legitimate. Reply with a single word: phishing or legitimate.

### Email:
{email_text}

### Classification:
"""

    result = call_ollama(prompt, CLASSIFY_OPTIONS)
    result_lower = result.lower().strip()

    if "phishing" in result_lower:
        return "phishing"
    elif "legitimate" in result_lower:
        return "legitimate"
    else:
        return "phishing"  # safer default for security tasks


def analyze_tactics(email_text, tactics):
    """Explanation only — never changes the classification."""
    raw = call_ollama(build_tactic_prompt(email_text, tactics), TACTIC_OPTIONS)
    report = extract_json(raw)
    if report is None:
        return {"raw_output": raw, "parse_error": True}
    return {**verify_tactic_report(report, email_text, tactics), "raw_output": raw}


def run_pipeline(email_text, tactics, alert_index, with_advice=True):
    timings = {}
    analysis_text = email_text[:MAX_ANALYSIS_CHARS]

    start = time.time()
    classification = classify_email(email_text)
    timings["classify"] = time.time() - start

    start = time.time()
    analysis = analyze_tactics(analysis_text, tactics)
    timings["tactics"] = time.time() - start

    parsed = not analysis.get("parse_error")
    lure = analysis.get("lure")
    lure_is_none = parsed and lure is not None and lure["id"] == "none"
    has_tactic = parsed and ((lure is not None and lure["id"] != "none") or bool(analysis["techniques"]))

    alerts = None
    if not lure_is_none and alert_index is not None:
        start = time.time()
        alerts = alert_index.search(analysis_text)
        timings["alerts"] = time.time() - start

    advice = None
    if with_advice and alerts:
        start = time.time()
        # generous timeout: the first call may have to load the second model
        advice = generate_advice(analysis_text, alerts,
                                 lambda prompt: call_ollama(prompt, ADVICE_OPTIONS, model=ADVICE_MODEL, timeout=300))
        timings["advice"] = time.time() - start

    return {
        "classification": classification,
        "analysis": analysis,
        "lure_is_none": lure_is_none,
        "has_tactic": has_tactic,
        "alerts": alerts,
        "advice": advice,
        "homoglyphs": find_homoglyph_words(email_text),
        # explanation and verdict disagree -> the demo asks for a manual check
        "phishing_without_tactic": classification == "phishing" and parsed and not has_tactic,
        "legit_with_tactic": classification == "legitimate" and (has_tactic or bool(alerts)),
        "timings": timings,
    }
