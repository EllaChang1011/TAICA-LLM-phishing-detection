import streamlit as st
import requests
import os

from CoT_Module import (build_tactic_prompt, extract_json, find_homoglyph_words, load_tactics,
                        verify_tactic_report)
from alert_rag import ALERTS_PATH, EMBEDDING_MODEL, THRESHOLD, AlertIndex

OLLAMA_BASE_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
OLLAMA_URL = f"{OLLAMA_BASE_URL}/api/generate"
MODEL_NAME = os.environ.get("MODEL_NAME", "phishing-detector-14b")

EMBED_DEVICE = os.environ.get("EMBED_DEVICE", "cuda")
MAX_ANALYSIS_CHARS = 6000

# Repetition penalties stay on for classification (unchanged), but are off for the
# tactic analysis: they push the model to paraphrase, which breaks verbatim quotes.
CLASSIFY_OPTIONS = {"temperature": 0.0, "num_predict": 16, "repeat_penalty": 1.5, "frequency_penalty": 0.5}
TACTIC_OPTIONS = {"temperature": 0.0, "num_predict": 1024}


@st.cache_resource
def load_alert_index():
    try:
        from sentence_transformers import SentenceTransformer
        embed_model = SentenceTransformer(EMBEDDING_MODEL, device=EMBED_DEVICE)
        return AlertIndex(embed_model)
    except Exception as e:
        st.sidebar.warning(f"詐騙警示載入失敗：{e}")
        return None


@st.cache_resource
def load_tactic_cards():
    return load_tactics()


def call_ollama(prompt, options):
    try:
        response = requests.post(
            OLLAMA_URL,
            json={"model": MODEL_NAME, "prompt": prompt, "stream": False, "options": options},
            timeout=120
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


def render_tactics(analysis):
    lure, techniques = analysis["lure"], analysis["techniques"]
    st.markdown(f"**摘要：** {analysis['summary']}")

    if lure is None:
        st.caption("誘餌：模型的判斷沒有通過檢查（id 不在清單或證據不在信裡），見下方「被丟掉的推論」。")
    elif lure["id"] != "none":
        card = lure["card"]
        with st.container(border=True):
            st.markdown(f"**🎣 誘餌：{card['name']}**　<small>{card['name_en']}</small>", unsafe_allow_html=True)
            st.caption(card["description"])
            st.markdown(f"> {lure['evidence']}")

    for t in techniques:
        card = t["card"]
        mitre = f"{card['mitre']['id']} {card['mitre']['name']}" if card.get("mitre") else "無對應的 ATT&CK 編號"
        with st.container(border=True):
            st.markdown(f"**🛠️ 手法：{card['name']}**　<small>{card['name_en']} · {mitre}</small>",
                        unsafe_allow_html=True)
            st.markdown(f"> {t['evidence']}")

    if analysis["rejected"]:
        with st.expander(f"被丟掉的推論（{len(analysis['rejected'])}）"):
            st.caption("模型選了這些，但 id 不在招數卡清單裡，或引用的句子在信裡找不到，所以不顯示在上面。")
            for x in analysis["rejected"]:
                st.markdown(f"- `{x['reason']}`：{x['pick']}")


def render_alerts(alerts, skipped):
    st.subheader("📰 相關詐騙警示")
    st.caption(f"初步設定：用信件原文搜尋 FTC 消費者警示，相似度 ≥ {THRESHOLD:.2f} 才顯示。"
               "獨立驗證時，有專屬警示的信找到 7/10，沒有專屬警示的信正確回答「找不到」5/6。")
    if skipped:
        st.info("招數分析判斷這封信沒有可疑招數，不搜尋警示。")
    elif alerts is None:
        st.info("詐騙警示資料未載入。")
    elif not alerts:
        st.info("目前沒有相關警示。")
    else:
        for a in alerts:
            with st.container(border=True):
                st.markdown(f"**[{a['title']}]({a['url']})**")
                st.caption(f"{a['source']} · {a['date']} · 相似度 {a['score']:.2f}")
                st.markdown(a["text"].split("\n\n")[0])


st.set_page_config(
    page_title="釣魚郵件偵測系統",
    page_icon="🛡️",
    layout="wide"
)

st.title("🛡️ 釣魚郵件偵測系統")
st.caption("Fine-tuned Qwen3-14B 分類 + 招數卡分析 + FTC 詐騙警示檢索")

alert_index = load_alert_index()
tactics = load_tactic_cards()

with st.sidebar:
    st.header("系統資訊")
    st.markdown(f"**分類模型**: `{MODEL_NAME}`")
    st.markdown(f"**招數卡**: 誘餌 {len(tactics['lures'])} 張、手法 {len(tactics['techniques'])} 張")
    st.divider()
    st.markdown("### 詐騙警示")
    st.markdown(f"**Embedding**: `{EMBEDDING_MODEL}`")
    if alert_index is not None:
        st.markdown(f"**警示數**: {len(alert_index.alerts)} 則（{ALERTS_PATH.name}）")
    st.markdown(f"**門檻**: {THRESHOLD:.2f}（初步設定）")

email_input = st.text_area(
    "貼上郵件內容",
    height=250,
    placeholder="在這裡貼上要分析的郵件內容..."
)

if email_input and len(email_input) > MAX_ANALYSIS_CHARS:
    st.warning(f"郵件超過 {MAX_ANALYSIS_CHARS} 字元，招數分析與警示搜尋僅使用前 {MAX_ANALYSIS_CHARS} 字元。")

analyze_btn = st.button("🔍 開始分析", type="primary")

if analyze_btn and email_input.strip():
    analysis_text = email_input[:MAX_ANALYSIS_CHARS]

    # ── Step 1: 分類（只有這一步決定判定結果）─────────────────────────────────
    with st.spinner("分類中..."):
        classification = classify_email(email_input)

    # ── Step 2: 招數分析（只負責解釋）──────────────────────────────────────────
    with st.spinner("分析招數..."):
        analysis = analyze_tactics(analysis_text, tactics)

    # ── Step 3: 詐騙警示（只有招數分析明確判斷 none 才不查）────────────────────
    lure_is_none = (not analysis.get("parse_error")) and analysis["lure"] is not None \
        and analysis["lure"]["id"] == "none"
    alerts = None
    if not lure_is_none and alert_index is not None:
        with st.spinner("搜尋詐騙警示..."):
            alerts = alert_index.search(analysis_text)

    homoglyphs = find_homoglyph_words(email_input)

    # ── 判定結果 ──────────────────────────────────────────────────────────────
    st.divider()
    if classification == "phishing":
        st.error("⚠️ 判定結果：**釣魚郵件 (Phishing)**")
    else:
        st.success("✅ 判定結果：**正常郵件 (Legitimate)**")
    st.caption("判定只由微調的分類模型決定；下方的招數分析與詐騙警示只用來解釋，不會改變判定。")

    has_tactic = (not analysis.get("parse_error")) and (
        (analysis["lure"] is not None and analysis["lure"]["id"] != "none") or bool(analysis["techniques"]))
    if classification == "phishing" and not analysis.get("parse_error") and not has_tactic:
        st.warning("⚠️ 判斷與分析不一致：分類模型判定為釣魚，但招數分析沒有找到可疑招數。建議人工確認。")
    if classification == "legitimate" and (has_tactic or alerts):
        st.warning("⚠️ 判斷與分析不一致：分類模型判定為正常郵件，但招數分析找到可疑招數或相關警示。建議人工確認。")

    if homoglyphs:
        st.warning("🔤 **這封信用了外型相近的字元來偽裝**：以下單字混用了英文字母和外型相同的西里爾／希臘字母，"
                   "正常郵件幾乎不會這樣寫。\n\n" +
                   "\n".join(f"- `{w['word']}` 看起來像 **{w['looks_like']}**（{', '.join(w['spoofed_chars'])}）"
                             for w in homoglyphs))

    # ── 招數分析 ──────────────────────────────────────────────────────────────
    st.divider()
    st.subheader("🔎 招數分析")
    if analysis.get("parse_error"):
        st.warning("模型輸出格式異常，顯示原始回應：")
        st.code(analysis.get("raw_output", ""))
    else:
        render_tactics(analysis)

    # ── 詐騙警示 ──────────────────────────────────────────────────────────────
    st.divider()
    render_alerts(alerts, skipped=lure_is_none)

    with st.expander("查看模型原始輸出"):
        st.code(analysis.get("raw_output", ""))

elif analyze_btn:
    st.warning("請先輸入郵件內容。")
