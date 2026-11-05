# ── 基底：官方 Python 3.11 slim（比完整版小 ~700MB）────────────────────────
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    HF_HOME=/opt/huggingface

WORKDIR /app

# ── 相依套件 ───────────────────────────────────────────────────────────────
# 先裝 CPU 版 torch（預設 PyPI 的 torch 會帶 ~2.5GB CUDA 函式庫，容器裡用不到）
# 版本跟 host 的 .venv 一致，embedding 和評測時的結果才會相同
RUN pip install torch==2.6.0 --index-url https://download.pytorch.org/whl/cpu

# demo 只需要這幾個，不裝 train/export 的相依（unsloth、matplotlib 等）
RUN pip install \
    streamlit==1.66.1 \
    requests==2.34.2 \
    sentence-transformers==6.2.0 \
    transformers==5.9.0

# ── embedding 模型：建 image 時先下載（~1.3GB）──────────────────────────────
# 容器執行時不一定連得到 HuggingFace，所以先放進 image，執行時強制離線。
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('BAAI/bge-large-en-v1.5')"
ENV HF_HUB_OFFLINE=1

# ── 程式碼 ─────────────────────────────────────────────────────────────────
# 放在最後：改 app.py 時只有這一層要重建，上面的套件層會走快取
COPY knowledge_base/scam_alerts.json ./knowledge_base/scam_alerts.json
COPY demo/ ./demo/

WORKDIR /app/demo
EXPOSE 8501

CMD ["streamlit", "run", "app.py", \
     "--server.address=0.0.0.0", \
     "--server.port=8501"]
