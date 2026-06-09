import streamlit as st
import requests
import json
import re
import os

from CoT_Module import build_cot_prompt, enforce_consistency

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "phishing-detector-14b"

USE_RAG = True
CHROMA_DB_PATH = "./chroma_db"
EMBEDDING_MODEL_NAME = "BAAI/bge-large-en-v1.5"


@st.cache_resource
def load_rag_components():
    if not USE_RAG:
        return None, None
    
    try:
        import chromadb
        from sentence_transformers import SentenceTransformer
        
        embed_model = SentenceTransformer(EMBEDDING_MODEL_NAME, device="cuda")
        client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
        collection = client.get_collection("phishing_knowledge")
        
        return embed_model, collection
    except Exception as e:
        st.sidebar.warning(f"RAG 載入失敗：{e}")
        return None, None


def call_ollama(prompt, temperature=0.0, max_tokens=10):
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens,
                    "repeat_penalty": 1.5,
                    "frequency_penalty": 0.5,
                }
            },
            timeout=120
        )
        return response.json().get("response", "")
    except requests.exceptions.ConnectionError:
        return "ERROR: 無法連線到 Ollama，請確認是否正在執行。"
    except Exception as e:
        return f"ERROR: {str(e)}"


def model_fn(prompt):
    return call_ollama(prompt, temperature=0.0, max_tokens=1024)


def classify_email(email_text):
    prompt = f"""/no_think
Classify the following email as phishing or legitimate. Reply with a single word: phishing or legitimate.

### Email:
{email_text}

### Classification:
"""

    result = call_ollama(prompt, temperature=0.0, max_tokens=16)
    result_lower = result.lower().strip()

    if "phishing" in result_lower:
        return "phishing"
    elif "legitimate" in result_lower:
        return "legitimate"
    else:
        return "phishing"  # safer default for security tasks


def retrieve_context(email_text, embed_model, collection, top_k=3):
    if embed_model is None or collection is None:
        return []
    
    try:
        query_embedding = embed_model.encode(email_text).tolist()
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )
        
        contexts = []
        for i in range(len(results["documents"][0])):
            distance = results["distances"][0][i]
            if distance > 0.6:  # cosine distance > 0.6 → similarity < 0.4，跳過不相關段落
                continue
            contexts.append({
                "text": results["documents"][0][i],
                "source": results["metadatas"][0][i].get("source", "unknown"),
                "distance": distance,
            })
        return contexts
    except Exception as e:
        st.warning(f"RAG 檢索失敗：{e}")
        return []



def generate_cot_report(email_text, rag_contexts=None):
    prompt = build_cot_prompt(email_text)
    result = model_fn(prompt)

    # strip thinking tokens, then find the first balanced JSON object
    cleaned = re.sub(r'<think>.*?</think>', '', result, flags=re.DOTALL)
    cleaned = re.sub(r'<think>.*', '', cleaned, flags=re.DOTALL)  # unclosed <think>
    cleaned = re.sub(r'```json\s*|```\s*', '', cleaned).strip()

    start = cleaned.find('{')
    if start != -1:
        depth, end = 0, -1
        for i, ch in enumerate(cleaned[start:], start):
            if ch == '{':
                depth += 1
            elif ch == '}':
                depth -= 1
                if depth == 0:
                    end = i
                    break
        if end != -1:
            try:
                report = json.loads(cleaned[start:end + 1])
                return enforce_consistency(report)
            except Exception:
                pass

    return {"raw_output": result, "parse_error": True}


st.set_page_config(
    page_title="釣魚郵件偵測系統",
    page_icon="🛡️",
    layout="wide"
)

st.title("🛡️ 釣魚郵件偵測系統")
st.caption("Fine-tuned Qwen3-14B + RAG + CoT Analysis")

embed_model, collection = load_rag_components()

with st.sidebar:
    st.header("系統資訊")
    st.markdown(f"**分類模型**: `{MODEL_NAME}`")
    st.markdown(f"**RAG**: {'啟用' if (embed_model is not None) else '未啟用'}")
    
    if embed_model is not None:
        st.divider()
        st.markdown(f"### RAG 知識庫")
        st.markdown(f"**Embedding**: `{EMBEDDING_MODEL_NAME}`")
        try:
            st.markdown(f"**文件數**: {collection.count()} 段")
        except:
            pass

email_input = st.text_area(
    "貼上郵件內容",
    height=250,
    placeholder="在這裡貼上要分析的郵件內容..."
)

if email_input and len(email_input) > 6000:
    st.warning("郵件超過 6000 字元，分析時僅使用前 6000 字元。")

analyze_btn = st.button("🔍 開始分析", type="primary")

if analyze_btn and email_input.strip():

    # ── Step 1: 直接分類 ──────────────────────────────────────────────────────
    with st.spinner("分類中..."):
        classification = classify_email(email_input)

    # ── Step 2: RAG 檢索 ──────────────────────────────────────────────────────
    rag_contexts = []
    if embed_model is not None:
        with st.spinner("檢索威脅情報..."):
            rag_contexts = retrieve_context(email_input, embed_model, collection)

    # ── Step 3: CoT 分析 ──────────────────────────────────────────────────────
    with st.spinner("生成安全分析報告..."):
        report = generate_cot_report(email_input, rag_contexts=rag_contexts)

    # ── Ensemble：CoT 低風險時修正直接分類的 false positive ──────────────────
    final_classification = classification
    cot_overridden = False
    if classification == "phishing" and not report.get("parse_error"):
        cot_label = report.get("final", "").lower()
        risk = report.get("risk_score", 0)
        if isinstance(risk, str):
            try:
                risk = int(risk)
            except Exception:
                risk = 0
        if cot_label == "legitimate" and risk < 40:
            final_classification = "legitimate"
            cot_overridden = True

    # ── 顯示最終判定 ──────────────────────────────────────────────────────────
    st.divider()
    if final_classification == "phishing":
        st.error("⚠️ 判定結果：**釣魚郵件 (Phishing)**")
    elif final_classification == "legitimate":
        st.success("✅ 判定結果：**正常郵件 (Legitimate)**")
    else:
        st.warning("❓ 無法判定")

    if cot_overridden:
        st.info("ℹ️ 直接分類判定為 **phishing**，但 CoT 風險評分低（< 40）且判定為 legitimate，已修正為正常郵件。")

    # ── RAG 威脅情報 ──────────────────────────────────────────────────────────
    if rag_contexts:
        st.divider()
        st.subheader("📚 相關威脅情報")
        for i, ctx in enumerate(rag_contexts):
            similarity = 1 - ctx["distance"]
            with st.expander(f"參考 {i+1} — {ctx['source']}（相似度 {similarity:.2f}）"):
                st.markdown(ctx["text"])

    # ── CoT 安全分析報告 ──────────────────────────────────────────────────────
    st.divider()
    st.subheader("📋 安全分析報告")

    if report.get("parse_error"):
        st.warning("模型輸出格式異常，顯示原始回應：")
        st.code(report.get("raw_output", ""))
    else:
        risk = report.get("risk_score", 0)
        if isinstance(risk, str):
            try:
                risk = int(risk)
            except Exception:
                risk = 0

        cot_label = report.get("final", "unknown")

        col1, col2, col3 = st.columns(3)
        with col1:
            if risk >= 70:
                st.metric("風險評分", f"{risk}/100", delta="高風險", delta_color="inverse")
            elif risk >= 40:
                st.metric("風險評分", f"{risk}/100", delta="中風險", delta_color="off")
            else:
                st.metric("風險評分", f"{risk}/100", delta="低風險", delta_color="normal")
        with col2:
            st.metric("直接分類", classification)
        with col3:
            st.metric("CoT 判定", cot_label)

        indicators = report.get("phishing_indicators", [])
        if indicators and indicators != ["..."]:
            st.markdown("**🔎 釣魚指標：**")
            for ind in indicators:
                st.markdown(f"- {ind}")

        col4, col5 = st.columns(2)
        with col4:
            st.markdown(f"**⏰ 緊急戰術：** {report.get('urgency_tactics', 'N/A')}")
            st.markdown(f"**🎭 冒充對象：** {report.get('impersonation', 'N/A')}")
        with col5:
            st.markdown(f"**🔗 URL 分析：** {report.get('url_analysis', 'N/A')}")
            st.markdown(f"**🔑 憑證竊取：** {report.get('credential_harvesting', 'N/A')}")

        with st.expander("查看原始 JSON"):
            st.json(report)

elif analyze_btn:
    st.warning("請先輸入郵件內容。")
