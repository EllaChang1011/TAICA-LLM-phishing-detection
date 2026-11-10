#!/usr/bin/env python3
"""
Merge LoRA adapter and export as GGUF for Ollama via unsloth.
"""

import os
os.environ["TORCHDYNAMO_DISABLE"] = "1"

# unsloth must come first
from unsloth import FastLanguageModel

import sys
from pathlib import Path

ADAPTER_PATH   = "training_runs/results/lora_adapter"
GGUF_OUTPUT    = "gguf_export_gguf"
QUANT_METHOD   = "q4_k_m"
MAX_SEQ_LENGTH = 2048

# Skip if already done
if next(Path(GGUF_OUTPUT).glob("*.gguf"), None):
    gguf = next(Path(GGUF_OUTPUT).glob("*.gguf"))
    if gguf.stat().st_size > 1_000_000_000:  # > 1 GB = valid
        print(f"GGUF already exists: {gguf}  ({gguf.stat().st_size/1e9:.1f} GB)")
        sys.exit(0)

print(f"Loading {ADAPTER_PATH} ...")
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name=ADAPTER_PATH,
    max_seq_length=MAX_SEQ_LENGTH,
    load_in_4bit=True,
    dtype=None,
)

if hasattr(tokenizer, "tokenizer"):
    tokenizer = tokenizer.tokenizer
im_end_id = tokenizer.convert_tokens_to_ids("<|im_end|>")
tokenizer.eos_token    = "<|im_end|>"
tokenizer.eos_token_id = im_end_id
if tokenizer.pad_token is None:
    tokenizer.pad_token    = "<|im_end|>"
    tokenizer.pad_token_id = im_end_id

Path(GGUF_OUTPUT).mkdir(exist_ok=True)
print(f"\nExporting GGUF ({QUANT_METHOD}) → {GGUF_OUTPUT}/")
model.save_pretrained_gguf(GGUF_OUTPUT, tokenizer, quantization_method=QUANT_METHOD)

gguf_file = next(Path(GGUF_OUTPUT).glob("*.gguf"), None)
if gguf_file and gguf_file.stat().st_size > 1_000_000_000:
    print(f"\nGGUF saved: {gguf_file}  ({gguf_file.stat().st_size/1e9:.1f} GB)")

    modelfile = f"""FROM ./{gguf_file.name}

SYSTEM "You are a phishing email classifier. Classify emails as phishing or legitimate."

PARAMETER stop "<|im_end|>"
PARAMETER temperature 0.0
"""
    mf_path = Path(GGUF_OUTPUT) / "Modelfile"
    mf_path.write_text(modelfile)
    print(f"Modelfile saved: {mf_path}")
    print("\n── Next steps ──")
    print(f"  cd {GGUF_OUTPUT}")
    print(f"  ollama create phishing-detector -f Modelfile")
    print(f"  ollama run phishing-detector")
else:
    print("ERROR: GGUF not found or too small.")
    sys.exit(1)
