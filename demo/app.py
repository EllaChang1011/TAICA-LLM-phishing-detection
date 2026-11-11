import streamlit as st
import os

from CoT_Module import load_tactics
from alert_rag import ALERTS_PATH, EMBEDDING_MODEL, THRESHOLD, AlertIndex
from pipeline import ADVICE_MODEL, MAX_ANALYSIS_CHARS, MODEL_NAME, run_pipeline

EMBED_DEVICE = os.environ.get("EMBED_DEVICE", "cuda")


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


def render_advice(advice, classification):
    st.subheader("🧭 該怎麼辦")
    st.caption("只根據上面顯示的 FTC 警示產生，每句都標出處。出處已自動檢查：每句都對得到警示原文；"
               "但中文說法是否忠實沒有自動檢查，請以警示原文為準。")
    if advice.get("parse_error"):
        st.warning("模型輸出格式異常，無法產生建議。")
        return
    if classification == "legitimate":
        st.info("分類模型判定為正常郵件；如果這封信不是你預期會收到的，可參考以下建議。")
    match = advice["match"]
    if match:
        st.markdown(f"**相同手法**：{match['text']}　（出處：[{match['alert_title']}]({match['alert_url']})）")
    if advice["advice"]:
        st.markdown("\n".join(f"- {a['text']}　（出處：[{a['alert_title']}]({a['alert_url']})）"
                               for a in advice["advice"]))
    elif not match:
        st.info("沒有通過出處檢查的建議。")
    with st.expander("查看引用的原文"):
        if match:
            st.markdown(f"- 信中原句：「{match['email_quote']}」\n- 警示原句（{match['alert']}）：「{match['alert_quote']}」")
        for a in advice["advice"]:
            st.markdown(f"- {a['alert']}：「{a['quote']}」")
        if advice["rejected"]:
            st.caption(f"沒有通過出處檢查而被丟掉的句子：{len(advice['rejected'])} 句")
            for x in advice["rejected"]:
                st.markdown(f"  - `{x['reason']}`：{x['item']}")


st.set_page_config(
    page_title="釣魚郵件偵測系統",
    page_icon="🛡️",
    layout="wide"
)

st.title("🛡️ 釣魚郵件偵測系統")
st.caption("Fine-tuned Qwen3-14B 分類 + 招數卡分析 + FTC 詐騙警示檢索與建議生成")

alert_index = load_alert_index()
tactics = load_tactic_cards()

with st.sidebar:
    st.header("系統資訊")
    st.markdown(f"**分類 / 招數分析**: `{MODEL_NAME}`")
    st.markdown(f"**建議生成**: `{ADVICE_MODEL}`")
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
    with st.spinner("分析中（分類 → 招數分析 → 詐騙警示 → 建議）..."):
        result = run_pipeline(email_input, tactics, alert_index)
    classification, analysis, alerts = result["classification"], result["analysis"], result["alerts"]
    homoglyphs = result["homoglyphs"]

    # ── 判定結果 ──────────────────────────────────────────────────────────────
    st.divider()
    if classification == "phishing":
        st.error("⚠️ 判定結果：**釣魚郵件 (Phishing)**")
    else:
        st.success("✅ 判定結果：**正常郵件 (Legitimate)**")
    st.caption("判定只由微調的分類模型決定；下方的招數分析與詐騙警示只用來解釋，不會改變判定。")

    if result["phishing_without_tactic"]:
        st.warning("⚠️ 判斷與分析不一致：分類模型判定為釣魚，但招數分析沒有找到可疑招數。建議人工確認。")
    if result["legit_with_tactic"]:
        # milder wording: catches every missed phishing email on the test split, but most hits are legitimate mail
        st.info("ℹ️ 這封信有類似詐騙的寫法，請留意。")

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
    render_alerts(alerts, skipped=result["lure_is_none"])
    if result["advice"] is not None:
        st.divider()
        render_advice(result["advice"], classification)

    with st.expander("查看模型原始輸出"):
        st.code(analysis.get("raw_output", ""))

elif analyze_btn:
    st.warning("請先輸入郵件內容。")
