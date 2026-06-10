# Phishing Email Detection System｜釣魚郵件偵測系統

[English](#english) | [中文](#中文)

---

## English

Fine-tuned Qwen3-14B with QLoRA for phishing email binary classification, augmented with RAG-based threat intelligence retrieval and Chain-of-Thought (CoT) security analysis. Includes an interactive Streamlit demo.

### Architecture

```
User Input Email
    │
    ├─→ [Fine-tuned Model (Direct)]  → phishing / legitimate  (primary decision)
    ├─→ [RAG Retrieval]              → relevant threat intel from APWG / MITRE ATT&CK
    └─→ [CoT Module]                 → JSON report (risk score, indicators, analysis)

All three results are displayed in the Streamlit UI.
```

### Directory Structure

```
.
├── demo/            Streamlit demo (app.py, CoT_Module.py, chroma_db/)
├── scripts/         Training, evaluation, export, RAG scripts
├── data/            Train / val / test splits + raw archive
├── knowledge_base/  RAG sources (APWG PDFs, MITRE ATT&CK pages, chunks.json)
├── eval_results/    Evaluation outputs (baseline / fine-tuned / CoT, json, csv)
├── figures/         Training loss curves, confusion matrices
├── training_runs/   Training metrics (model weights hosted on HuggingFace)
└── docs/            Error analysis
```

### Dataset

[Human-LLM Generated Phishing-Legitimate Emails](https://www.kaggle.com/datasets/) — Kaggle

4,000 emails across 4 categories (1,000 each): Human-Phishing, Human-Legitimate, LLM-Phishing, LLM-Legitimate.  
Split: 80% train / 10% val / 10% test (stratified).

### Performance

#### 14B Fine-tuned Model (400-sample test set)

| Metric | Baseline | Fine-tuned |
|---|---|---|
| Accuracy | 50% | **88.75%** |
| Precision | 0.500 | 0.833 |
| Recall | 1.000 | 0.970 |
| F1-Score | 0.667 | 0.896 |

Per-category accuracy:

| Category | Baseline | Fine-tuned |
|---|---|---|
| Human-Phishing | 100% | 94% |
| Human-Legitimate | 0% | 62% |
| LLM-Phishing | 100% | 100% |
| LLM-Legitimate | 0% | 99% |

#### 14B vs 27B

| Metric | 14B | 27B |
|---|---|---|
| Accuracy | 88.75% | **99.0%** |
| Precision | 0.833 | 0.980 |
| Recall | 0.970 | 1.000 |
| F1-Score | 0.896 | 0.990 |

#### RAG Effect

Adding RAG does not significantly improve classification accuracy (80.75% vs 88.75%). Its primary value is providing interpretable threat intelligence sources alongside the prediction.

See [docs/error_analysis.md](docs/error_analysis.md) for detailed error analysis.

### Model Weights

| Model | Link |
|---|---|
| phishing-detector-14b (LoRA adapter) | [ellachang/phishing-detector-14b-lora](https://huggingface.co/ellachang/phishing-detector-14b-lora) |
| phishing-detector-14b (GGUF, Q4_K_M) | [ellachang/phishing-detector-14b-gguf](https://huggingface.co/ellachang/phishing-detector-14b-gguf) |
| phishing-detector-27b (LoRA adapter) | [ellachang/phishing-detector-27b-lora](https://huggingface.co/ellachang/phishing-detector-27b-lora) |

### Requirements

- Python 3.11+
- NVIDIA GPU (VRAM ≥ 8GB, for embedding model)
- [Ollama](https://ollama.com)
- [uv](https://docs.astral.sh/uv/) (recommended package manager)

### Running the Demo

1. Download the GGUF model and load it into Ollama:
   ```bash
   # Download GGUF + Modelfile from HuggingFace
   uv pip install huggingface_hub
   python - <<'EOF'
   from huggingface_hub import hf_hub_download
   hf_hub_download("ellachang/phishing-detector-14b-gguf", "qwen3-14b.Q4_K_M.gguf", local_dir="./ollama_model")
   hf_hub_download("ellachang/phishing-detector-14b-gguf", "Modelfile", local_dir="./ollama_model")
   EOF

   # Create Ollama model
   cd ollama_model
   ollama create phishing-detector-14b -f Modelfile
   cd ..
   ```

2. Install dependencies:
   ```bash
   uv pip install .
   ```

3. The RAG knowledge base (`demo/chroma_db/`) is included in the repo — no rebuild needed.  
   To rebuild from scratch, see **Rebuild RAG Knowledge Base** below.

4. Launch:
   ```bash
   cd demo
   streamlit run app.py
   ```
   Open `http://localhost:8501`, paste an email, and click **Analyze**.

### Rebuild RAG Knowledge Base

Sources: APWG quarterly phishing trend reports (PDF) + MITRE ATT&CK phishing technique pages, saved in `knowledge_base/`.

```bash
# 1. Extract text and chunk semantically → knowledge_base/chunks.json
python scripts/build_rag_chunks_threat_intel.py

# 2. Embed with BAAI/bge-large-en-v1.5 and write to ChromaDB → demo/chroma_db/
python scripts/build_rag_chroma_threat_intel.py
```

### Scripts

| Script | Purpose |
|---|---|
| `scripts/data_preparation.py` | Data preprocessing and splitting |
| `scripts/train.py` | QLoRA fine-tuning |
| `scripts/baseline.py` / `evaluate.py` | Baseline / fine-tuned model evaluation |
| `scripts/cot_evaluate.py` | Chain-of-Thought evaluation |
| `scripts/export_gguf.py` | Export to GGUF for Ollama |
| `scripts/build_rag_chunks_threat_intel.py` | RAG text extraction and chunking (threat-intel knowledge base) |
| `scripts/build_rag_chroma_threat_intel.py` | RAG embedding and ChromaDB construction (threat-intel knowledge base) |
| `scripts/build_rag_chroma_examples.py` | Embed labeled training emails into ChromaDB for few-shot exemplar RAG |
| `scripts/fewshot_rag_eval.py` | Evaluate plain vs few-shot exemplar-RAG direct classification |

> All scripts use paths relative to the project root. Run them as `python scripts/train.py` from the root directory.

---

## 中文

以 QLoRA 微調 Qwen3-14B 進行釣魚郵件二元分類，並結合 RAG 威脅情報檢索與 Chain-of-Thought（CoT）安全分析報告，提供 Streamlit 互動式 demo。

### 系統架構

```
使用者輸入郵件
    │
    ├─→ [微調模型 直接分類]   → phishing / legitimate（主要判斷）
    ├─→ [RAG 檢索]            → 從 APWG / MITRE ATT&CK 知識庫找相關威脅情報
    └─→ [CoT 模組]            → 生成 JSON 分析報告（風險評分、釣魚指標、建議）

三個結果一起顯示在 Streamlit 介面上，分類結果以微調模型的直接判斷為準。
```

### 目錄結構

```
.
├── demo/                  Streamlit demo（app.py、CoT_Module.py、chroma_db/）
├── scripts/               訓練、評估、匯出、RAG 建置腳本
├── data/                  訓練/驗證/測試資料集（train, val, test, archive）
├── knowledge_base/        RAG 知識庫來源（APWG 報告 PDF、MITRE ATT&CK 頁面、chunks.json）
├── eval_results/          各項評估結果（baseline / fine-tuned / CoT，json、csv）
├── figures/               訓練曲線、混淆矩陣等圖表
├── training_runs/         訓練紀錄（模型權重在 HuggingFace）
└── docs/                  專案文件（錯誤分析）
```

### 資料集

[Human-LLM Generated Phishing-Legitimate Emails](https://www.kaggle.com/datasets/) — Kaggle

共 4,000 封郵件，四個類別各 1,000 封：Human-Phishing、Human-Legitimate、LLM-Phishing、LLM-Legitimate。  
切分：80% 訓練 / 10% 驗證 / 10% 測試（stratified）。

### 模型表現

#### 14B 微調模型（400 筆測試集）

| 指標 | Baseline | Fine-tuned |
|---|---|---|
| Accuracy | 50% | **88.75%** |
| Precision | 0.500 | 0.833 |
| Recall | 1.000 | 0.970 |
| F1-Score | 0.667 | 0.896 |

各類別準確率：

| 類別 | Baseline | Fine-tuned |
|---|---|---|
| Human-Phishing | 100% | 94% |
| Human-Legitimate | 0% | 62% |
| LLM-Phishing | 100% | 100% |
| LLM-Legitimate | 0% | 99% |

#### 14B vs 27B 比較

| 指標 | 14B | 27B |
|---|---|---|
| Accuracy | 88.75% | **99.0%** |
| Precision | 0.833 | 0.980 |
| Recall | 0.970 | 1.000 |
| F1-Score | 0.896 | 0.990 |

#### RAG 效果

加入 RAG 後整體準確率無顯著提升（80.75% vs 88.75%），RAG 的主要價值在於提供可解釋的威脅情報來源。

詳細錯誤分析請見 [docs/error_analysis.md](docs/error_analysis.md)。

### 模型下載

| 模型 | 連結 |
|---|---|
| phishing-detector-14b（LoRA adapter） | [ellachang/phishing-detector-14b-lora](https://huggingface.co/ellachang/phishing-detector-14b-lora) |
| phishing-detector-14b（GGUF, Q4_K_M） | [ellachang/phishing-detector-14b-gguf](https://huggingface.co/ellachang/phishing-detector-14b-gguf) |
| phishing-detector-27b（LoRA adapter） | [ellachang/phishing-detector-27b-lora](https://huggingface.co/ellachang/phishing-detector-27b-lora) |

### 環境需求

- Python 3.11+
- NVIDIA GPU（VRAM ≥ 8GB，用於 embedding model）
- [Ollama](https://ollama.com)
- [uv](https://docs.astral.sh/uv/)（建議使用的套件管理工具）

### 啟動 Demo

1. 從 HuggingFace 下載 GGUF 並載入 Ollama：
   ```bash
   uv pip install huggingface_hub
   python - <<'EOF'
   from huggingface_hub import hf_hub_download
   hf_hub_download("ellachang/phishing-detector-14b-gguf", "qwen3-14b.Q4_K_M.gguf", local_dir="./ollama_model")
   hf_hub_download("ellachang/phishing-detector-14b-gguf", "Modelfile", local_dir="./ollama_model")
   EOF

   cd ollama_model
   ollama create phishing-detector-14b -f Modelfile
   cd ..
   ```

2. 安裝相依套件：
   ```bash
   uv pip install .
   ```

3. RAG 知識庫（`demo/chroma_db/`）已包含在 repo 中，無需重建。  
   若要從頭重建，參考下方「重建 RAG 知識庫」。

4. 執行：
   ```bash
   cd demo
   streamlit run app.py
   ```
   開啟瀏覽器至 `http://localhost:8501`，貼上郵件內容並點選「開始分析」。

### 重建 RAG 知識庫

知識庫來源：APWG 季度釣魚趨勢報告（PDF）+ MITRE ATT&CK 釣魚相關技術頁面，已下載至 `knowledge_base/`。

```bash
# 1. 文字提取與語意分塊 → knowledge_base/chunks.json
python scripts/build_rag_chunks_threat_intel.py

# 2. Embedding（BAAI/bge-large-en-v1.5）並寫入 ChromaDB → demo/chroma_db/
python scripts/build_rag_chroma_threat_intel.py
```

### 主要腳本

| 腳本 | 用途 |
|---|---|
| `scripts/data_preparation.py` | 資料前處理與切分 |
| `scripts/train.py` | QLoRA 微調訓練 |
| `scripts/baseline.py` / `evaluate.py` | Baseline / 微調模型分類評估 |
| `scripts/cot_evaluate.py` | Chain-of-Thought 模式評估 |
| `scripts/export_gguf.py` | 匯出 GGUF 供 Ollama 使用 |
| `scripts/build_rag_chunks_threat_intel.py` | RAG 知識庫文字提取與分塊（威脅情報知識庫） |
| `scripts/build_rag_chroma_threat_intel.py` | RAG 向量化並建立 ChromaDB（威脅情報知識庫） |
| `scripts/build_rag_chroma_examples.py` | 將標註過的訓練郵件向量化，供 few-shot 範例檢索 RAG 使用 |
| `scripts/fewshot_rag_eval.py` | 評估「純分類」vs「few-shot 範例檢索 RAG」分類效果 |

> 上述腳本內使用相對路徑，請從**專案根目錄**執行，例如 `python scripts/train.py`。
