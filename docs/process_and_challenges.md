# 釣魚郵件偵測系統：開發過程與困境紀錄

## 一、專案目標

以 QLoRA 微調 Qwen3-14B 進行釣魚郵件二元分類，並整合 RAG 威脅情報檢索與 Chain-of-Thought（CoT）安全分析，最終部署為 Streamlit 互動式 demo。

---

## 二、資料集準備

### 資料來源與結構

使用 Kaggle 上的 Human-LLM Generated Phishing-Legitimate Emails 資料集，共 4,000 封郵件，四個類別各 1,000 封：

| 類別 | 描述 |
|---|---|
| Human-Phishing | 人工撰寫的釣魚郵件 |
| Human-Legitimate | 真實的正常郵件（來自 Enron、學術郵件清單等） |
| LLM-Phishing | AI 生成的釣魚郵件 |
| LLM-Legitimate | AI 生成的正常郵件 |

切分策略採 stratified 分層抽樣，80% 訓練 / 10% 驗證 / 10% 測試，確保各類別在每個 split 中比例相同。

### 遭遇的問題

**LLM-Legitimate 的標籤雜訊**：部分 LLM 生成的「正常郵件」實際上包含邊緣案例（例如中獎通知、投資邀請），這些郵件在語意上與釣魚郵件高度相似，卻被標記為 legitimate，對模型造成混淆，是後續 human-legitimate 類別誤判率偏高的原因之一。

---

## 三、訓練：QLoRA 微調

### 環境設定

使用 Unsloth 加速 QLoRA 訓練，硬體為 RTX 4090（24GB VRAM）。

### 困境一：Unsloth Import 順序問題

**問題**：一開始在 `train.py` 中，`import unsloth` 寫在 `from trl import SFTTrainer` 之後，導致執行時出現：

```
ValueError: eos_token '<EOS_TOKEN>' not in vocabulary
```

**原因**：Unsloth 在 import 時會對 `transformers` 和 `trl` 進行 monkey-patch，若 `trl` 先被 import，patch 無法生效，tokenizer 的 EOS token 設定就會異常。

**解決方式**：將 `from unsloth import FastLanguageModel` 移到所有其他 ML 套件的 import 之前，並在 `pyproject.toml`/程式頂部加上明確的順序說明：

```python
# unsloth must be imported before trl/transformers so its patches apply first
from unsloth import FastLanguageModel

import torch
from trl import SFTTrainer, SFTConfig
```

### 困境二：Qwen3 的 EOS Token 設定

**問題**：Qwen3 系列模型使用 `<|im_end|>` 作為結束 token（而非標準的 `</s>`），但從 Unsloth 載入後，tokenizer 的 `eos_token` 不一定自動設定正確，導致模型在推論時生成不止一個詞的輸出（例如 `phishing\n\n` 或大量重複 token）。

**解決方式**：在載入 tokenizer 後手動設定：

```python
im_end_id = tokenizer.convert_tokens_to_ids("<|im_end|>")
tokenizer.eos_token    = "<|im_end|>"
tokenizer.eos_token_id = im_end_id
if tokenizer.pad_token is None:
    tokenizer.pad_token    = "<|im_end|>"
    tokenizer.pad_token_id = im_end_id
EOS_TOKEN = "<|im_end|>"
```

### 困境三：TorchDynamo 編譯衝突

**問題**：Unsloth 內部使用 torch compile 優化，但在某些環境下會觸發 TorchDynamo 的 graph break 錯誤，導致訓練中斷。

**解決方式**：在程式最頂部加上環境變數，停用 TorchDynamo：

```python
import os
os.environ["TORCHDYNAMO_DISABLE"] = "1"
```

### 訓練超參數決策

| 超參數 | 值 | 理由 |
|---|---|---|
| LoRA r | 16 | 14B 模型分類任務，r=16 足夠捕捉任務 specific 特徵 |
| LoRA alpha | 16 | alpha/r=1，標準設定 |
| Target modules | q, k, v, o proj | attention layer 對分類任務影響最大 |
| Batch size | 2 | 14B 4-bit 量化約 8GB，4090 能跑 batch=2 |
| Gradient accumulation | 4 | 有效 batch size = 8 |
| Learning rate | 2e-4 | QLoRA 常用範圍 |
| Epochs | 3 | val loss 在第 3 epoch 收斂，無明顯過擬合 |

---

## 四、評估結果與分析

### Baseline 的完全失敗

Zero-shot baseline（未微調的 Qwen3-14B）整體準確率只有 **50%**，等同於隨機猜測。

深入觀察後發現，模型對所有輸入都傾向回答 `phishing`（預設「高風險」偏見），導致：
- Human-Phishing、LLM-Phishing：100%（全押對，但方法錯誤）
- Human-Legitimate、LLM-Legitimate：**0%**（全部誤判）

### 微調後的改善

| 類別 | Baseline | Fine-tuned |
|---|---|---|
| Human-Phishing | 100% | 94% |
| Human-Legitimate | **0%** | **62%** |
| LLM-Phishing | 100% | 100% |
| LLM-Legitimate | **0%** | **99%** |

整體準確率從 50% 提升至 **88.75%**，但 Human-Legitimate 仍是最弱的類別（62%），是主要的錯誤來源。

### Human-Legitimate 誤判分析

錯誤樣本分析顯示，被誤判的正常郵件有共同特徵：

1. **來自學術郵件清單**（UAI、Python-Dev、SpamAssassin 社群）：含有 URL、技術術語，surface-level 特徵與釣魚郵件重疊。
2. **含有行動呼籲語**（"click here", "join us", "register"）：被模型視為釣魚指標。
3. **年代久遠的正常郵件**（2004–2008 年學術會議通知）：格式與現代郵件差異大，可能超出訓練分布。

根本原因在於，模型學到的特徵（URL、CTA、urgency 語氣）在正常學術郵件中也普遍存在，缺乏區分能力。

### 14B vs 27B

將 LoRA 適配器套用到更大的基礎模型後：

| 指標 | 14B | 27B |
|---|---|---|
| Accuracy | 88.75% | **99.0%** |
| F1 | 0.896 | 0.990 |

27B 模型在 Human-Legitimate 類別的誤判幾乎消失，說明更大的模型有更強的語意理解能力，能區分「具備行動呼籲但內容合法」的郵件。

---

## 五、RAG 的效果與侷限

### 知識庫來源

- APWG 季度釣魚趨勢報告（PDF）
- MITRE ATT&CK 釣魚相關技術頁面

使用 BAAI/bge-large-en-v1.5 進行 embedding，存入 ChromaDB。

### 困境：RAG 沒有提升分類準確率

加入 RAG 後，直接分類準確率反而從 88.75% **下降**至 80.75%（RAG 注入的上下文干擾了分類 prompt）。

#### 嘗試過的方法

| 方法 | 結果 |
|---|---|
| 將 RAG 檢索結果注入直接分類 prompt | 準確率從 88.75% 降到 80.75%，放棄 |
| 將 RAG 注入 CoT prompt（作為 threat intel section） | CoT 整體準確率 80.75%，無顯著改善 |
| 調整相似度門檻（distance > 0.5 / 0.6 / 0.7） | 0.6 時 false positive 最少，最終採用 |
| 只在 CoT 分析中用 RAG，直接分類不用 | 採用此設計，RAG 作為解釋層而非決策層 |

**分析**：

RAG 檢索到的是關於「釣魚攻擊手法」的通用描述（例如 "spear phishing targets executives"），而非針對當前郵件的具體判斷依據。這些資訊注入 prompt 後，反而可能讓模型更傾向輸出 phishing，對正常郵件造成額外的 false positive。

**結論**：RAG 的價值不在於提升分類準確率，而在於**提供可解釋的威脅情報來源**，讓使用者理解「為什麼這封郵件危險」，而非單純告訴使用者一個二元結果。因此 demo 中保留 RAG，但分類決策以直接分類為準，RAG 僅作為輔助說明。

### 額外實驗：Few-shot 範例檢索 RAG

除了「威脅情報文件」式的 RAG，我們也測試了另一種設計：將訓練集 3,200 筆**帶標籤的郵件**向量化存入獨立的 ChromaDB collection（`phishing_examples`），分類時檢索 k=3 筆最相似的範例郵件（含標籤），以 few-shot 形式注入分類 prompt（[scripts/build_rag_chroma_examples.py](../scripts/build_rag_chroma_examples.py)、[scripts/fewshot_rag_eval.py](../scripts/fewshot_rag_eval.py)）。

**結果（400 筆測試集）**：

| | 純分類（無範例） | + Few-shot 範例 RAG (k=3) |
|---|---|---|
| Accuracy | 88.25% | **72.0%** |
| Precision | 0.828 | 0.824 |
| Recall | 0.965 | **0.560** |
| F1 | 0.891 | 0.667 |

| 類別 | 純分類 | + Few-shot RAG |
|---|---|---|
| human-phishing | 93% | **50%** |
| human-legitimate | 60% | 76% |
| llm-phishing | 100% | **62%** |
| llm-legitimate | 100% | 100% |

**分析**：注入 few-shot 範例後 recall 從 96.5% 暴跌至 56%，模型開始把大量 phishing 郵件誤判為 legitimate。human-legitimate 雖然提升（60%→76%），但 phishing 兩個類別大幅崩盤，整體明顯退步。推測原因是這個微調模型已經針對「直接分類」這個固定格式的任務做過優化，額外注入的範例郵件反而稀釋了模型對輸入郵件本身的注意力，形同雜訊。

**結論**：這個結果與威脅情報 RAG 的發現一致——對這個微調模型而言，無論是注入威脅情報描述還是帶標籤的範例郵件，額外的上下文都會干擾分類，而非提供有用訊號。因此最終維持「RAG 僅作為解釋層、不參與分類決策」的設計，原本的威脅情報 RAG 程式碼也保留下來（更名為 `*_threat_intel.py`），與此處的 few-shot 範例 RAG 程式碼並存，作為兩種設計方向的對照記錄。

---

## 六、Chain-of-Thought 評估

### CoT vs 直接分類

CoT 模式要求模型輸出結構化 JSON（含風險評分、釣魚指標、最終判定），整體準確率低於直接分類：

| 模式 | 準確率 |
|---|---|
| 直接分類 | 86.75% |
| CoT | 83.25% |
| 兩者一致率 | 70.5% |

### 困境：CoT 對 LLM-Legitimate 的災難性失敗

CoT 模式在 LLM-Legitimate 類別的準確率只有 **39%**，遠低於直接分類的 97%。

**原因推測**：CoT prompt 要求模型「分析釣魚指標」，對於 LLM 生成的正常郵件，模型會強迫自己找出「疑似釣魚」的特徵（因為 prompt 引導方向），最終 hallucinate 出不存在的風險點，導致大量 false positive。

#### 嘗試過的方法

| 方法 | 結果 |
|---|---|
| CoT 單獨作為最終分類器 | LLM-Legitimate 39%，整體 83.25%，比直接分類差 |
| 加入 `enforce_consistency()` 確保 risk/label 一致 | 減少矛盾輸出，但 false positive 仍高 |
| 以 CoT 為主、直接分類為輔 | 整體更差，放棄 |
| 直接分類為主，CoT 僅在 risk < 40 且 label=legitimate 時修正 false positive | 採用此 ensemble 設計，保留 CoT 的優點（減少 false positive）同時避免它的缺點 |

**處置方式**：在 demo 的 ensemble 邏輯中，設定若 CoT 風險評分 < 40 且判定為 legitimate，才允許 CoT 修正直接分類的 phishing 判定，避免 CoT 的 false positive 污染最終結果。

---

## 七、GGUF 匯出與 Ollama 部署

### 為何要匯出 GGUF

fine-tuned 模型以 HuggingFace LoRA adapter 存在，直接推論需要 GPU。為了讓 demo 能在本機執行（包含 CPU 推論），需要透過 llama.cpp 的 GGUF 格式，並用 Ollama 作為推論後端。

### 困境：GGUF 匯出流程

Unsloth 的 `save_pretrained_gguf` 會在背景呼叫 llama.cpp 的 `quantize` 工具，若未安裝 llama.cpp 或路徑不對，會靜默失敗或輸出過小的 GGUF 檔案。

**解決方式**：在 `export_gguf.py` 加入大小驗證（> 1GB 才視為有效），並在轉換後自動生成 Ollama Modelfile：

```
FROM ./qwen3-14b.Q4_K_M.gguf
PARAMETER stop "<|im_end|>"
PARAMETER temperature 0.0
```

注意 `stop` token 必須設為 `<|im_end|>`，否則 Ollama 推論時模型會持續生成不止一個詞。

---

## 七之一、CoT 完整流程

### 架構概覽

CoT pipeline 分為兩條路徑並行執行，最後以 ensemble 合併結果：

```
Email
  ├─→ [直接分類路徑]
  │       │
  │       ├─ 建立 /no_think prompt
  │       ├─ Ollama 推論（max_tokens=16）
  │       └─ 關鍵字解析 → "phishing" / "legitimate"
  │
  └─→ [CoT 分析路徑]
          │
          ├─ [可選] RAG 檢索威脅情報
          │     └─ 查詢 ChromaDB → 過濾 distance > 0.6
          │
          ├─ 建立 CoT prompt（注入 threat intel section）
          ├─ Ollama 推論（max_tokens=300）
          ├─ 移除 <think>...</think>
          ├─ 移除 markdown fencing (```json```)
          ├─ 找第一個 { 追蹤括號深度 → 提取完整 JSON
          ├─ json.loads() → 取 "final" 欄位
          ├─ enforce_consistency()
          │     └─ 若 ≥2 個 indicators 或 risk_score ≥ 60
          │        但 final=legitimate → 強制改為 phishing
          └─ 返回 (label, report)

      ↓ Ensemble
      if direct=phishing AND CoT=legitimate AND risk_score < 40:
          final = legitimate  ← CoT 修正
      else:
          final = direct 分類結果（直接分類為主）
```

### CoT Prompt 結構

```
You are a cybersecurity SOC analyst.
[任務說明：輸出 phishing / legitimate]
[可選 threat intel section]
[Consistency Rules：
  - phishing → risk_score ≥ 60
  - legitimate → risk_score ≤ 40
  - 若有 ≥2 個 indicators → 不可輸出 legitimate]
[回傳純 JSON，禁止 JSON 外的說明]

EMAIL: {email_text}
```

輸出 JSON 格式：
```json
{
  "phishing_indicators": ["..."],
  "urgency_tactics": "...",
  "impersonation": "...",
  "url_analysis": "...",
  "credential_harvesting": "...",
  "final": "phishing or legitimate",
  "risk_score": 0
}
```

### 各階段嘗試過的方法

#### Prompt 設計的演進

| 版本 | 做法 | 問題 |
|---|---|---|
| v1 | 直接要求輸出 phishing/legitimate 再附上理由 | 輸出格式不固定，無法解析 |
| v2 | 要求輸出 JSON，但無 Consistency Rules | 出現「risk_score=80 但 final=legitimate」的矛盾輸出 |
| v3（最終） | 加入 Consistency Rules + `enforce_consistency()` 後處理 | 矛盾情況大幅減少 |

**核心問題**：模型在「我的推理說這是 phishing」但又「我不想太武斷」之間擺盪，導致 risk_score 高但 final 卻輸出 legitimate。解法是在 prompt 層面明確禁止這種矛盾，並用 `enforce_consistency()` 做最後防線。

#### 解析策略的演進

| 版本 | 做法 | 問題 |
|---|---|---|
| 直接 `json.loads(response)` | 最簡單 | 模型常在 JSON 外多寫一段說明，導致 parse fail |
| `re.search(r'\{.*\}', ...)` | 抓第一個 JSON 物件 | Qwen3 的 `<think>` 內部有 JSON fragment，抓錯位置 |
| 先移除 `<think>` 再 regex | 改善但仍有 markdown fencing 問題 | ````json ... ``` 包住的 JSON 被錯誤解析 |
| 最終：移除 think → 移除 fencing → 追蹤括號深度找完整 JSON | 穩定 | 無 |

---

## 八、Demo 開發中的工程問題

### Qwen3 的 Thinking Mode

Qwen3 支援 Extended Thinking，推論時會先輸出 `<think>...</think>` 內容再給出答案，導致分類結果解析困難（答案被包在大量 thinking tokens 後面）。

#### 嘗試過的方法

| 方法 | 結果 |
|---|---|
| 直接解析模型輸出 | `<think>` 內容混入答案，無法正確提取 label |
| 用 regex 找最後一個 `phishing`/`legitimate` 詞 | `<think>` 區塊內容也含有這些詞，誤抓 |
| 直接分類加 `/no_think` 指令 | 有效，模型跳過 thinking 直接輸出 label |
| CoT 保留 thinking、解析前先 strip `<think>...</think>` | 有效，CoT 的推理仍可用於 JSON 生成 |

**解決方式一（直接分類）**：在 prompt 前加上 `/no_think` 指令，強制跳過 thinking mode：

```
/no_think
Classify the following email as phishing or legitimate...
```

**解決方式二（CoT 分析）**：CoT 分析需要模型的推理過程，因此保留 thinking mode，但在解析時用 regex 移除 `<think>...</think>` 區塊後再解析 JSON：

```python
cleaned = re.sub(r'<think>.*?</think>', '', result, flags=re.DOTALL)
cleaned = re.sub(r'<think>.*', '', cleaned, flags=re.DOTALL)  # unclosed <think>
```

### RAG 相似度過濾

初始版本的 RAG 檢索將所有返回文件都注入 prompt，包含相似度極低的段落，造成雜訊。

改進後加入 cosine distance 門檻過濾（distance > 0.6 的段落直接丟棄，約等於相似度 < 0.4），確保只有真正相關的威脅情報才出現在報告中。

### JSON 解析的健壯性

CoT prompt 要求模型輸出 JSON，但大型語言模型有時會輸出帶 markdown fencing 的 JSON（````json ... ```）、截斷的 JSON，或混有自然語言的 JSON。

採用分層解析策略：
1. 移除 markdown fencing 和 thinking tokens
2. 找到第一個 `{` 並追蹤括號深度，提取完整 JSON 物件
3. 若解析失敗，退回顯示 raw output，前端標示 parse error

---

## 九、整體困境總結

| 困境 | 根本原因 | 解決方案 |
|---|---|---|
| Unsloth EOS token 錯誤 | import 順序錯誤導致 patch 失效 | `import unsloth` 移到最前 |
| 模型持續生成不停止 | `<\|im_end\|>` 未設為 stop token | 手動設定 tokenizer 與 Modelfile |
| TorchDynamo 編譯錯誤 | Unsloth compile 與環境衝突 | `TORCHDYNAMO_DISABLE=1` |
| Human-Legitimate 誤判率高 | 正常學術郵件與釣魚郵件 surface feature 重疊 | 換用更大模型（27B）；CoT ensemble 修正 |
| RAG 降低準確率 | 通用威脅情報干擾分類 | RAG 僅作輔助說明，分類以直接模型為準 |
| CoT 在 LLM-Legitimate 失敗 | Prompt 引導強迫找出不存在的釣魚特徵 | Ensemble 設門檻，限制 CoT 覆蓋直接分類的條件 |
| GGUF 匯出驗證困難 | llama.cpp 工具鏈靜默失敗 | 加入檔案大小驗證（> 1GB） |
| CoT JSON 解析不穩定 | 模型輸出格式不一致 | 分層解析 + fallback raw output |

---

## 十、結語

這個專案最大的學習是：**在安全分類任務中，模型大小帶來的效能提升遠比複雜的 pipeline（RAG + CoT ensemble）顯著。** 14B 微調後 88.75%，27B 微調後 99%；而花在 RAG 和 CoT 上的工程成本，對最終分類準確率的貢獻幾乎可以忽略。

RAG 和 CoT 的真正價值在於**可解釋性**：能告訴使用者「這封郵件有哪些釣魚指標」、「相關的威脅情報是什麼」，這對實際資安場景中的決策輔助是有意義的，只是不能指望它提升二元分類的準確率。

另一個關鍵教訓是 **toolchain 的脆弱性**：Unsloth、Qwen3 的 thinking mode、llama.cpp 的 GGUF 流程，每個環節都有隱藏的「沒寫在文件裡的坑」，需要靠實際執行、觀察錯誤訊息，以及深入閱讀原始碼才能排除。
