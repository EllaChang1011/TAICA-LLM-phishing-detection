#!/usr/bin/env python3
"""
QLoRA fine-tuning of Qwen3-14B for phishing email detection using Unsloth.
"""

import os
os.environ["TORCHDYNAMO_DISABLE"] = "1"

# unsloth must be imported before trl/transformers so its patches apply first
from unsloth import FastLanguageModel

import json
from pathlib import Path

import matplotlib.pyplot as plt
import torch
from datasets import Dataset
from trl import SFTTrainer, SFTConfig

# ── Config ────────────────────────────────────────────────────────────────────
MODEL_NAME = "unsloth/Qwen3-14B"
MAX_SEQ_LENGTH = 2048
LOAD_IN_4BIT = True

LORA_R = 16
LORA_ALPHA = 16
LORA_DROPOUT = 0.05
TARGET_MODULES = ["q_proj", "k_proj", "v_proj", "o_proj"]

OUTPUT_DIR = Path("training_runs/results")
OUTPUT_DIR.mkdir(exist_ok=True)

TRAIN_EPOCHS = 3
BATCH_SIZE = 2        # 14B 模型 4-bit 約 8GB，4090 可以 batch_size=2
GRAD_ACCUM = 4        # 有效 batch size = 2×4 = 8
LEARNING_RATE = 2e-4
WARMUP_STEPS = 10
LOGGING_STEPS = 10
SAVE_STEPS = 100
EVAL_STEPS = 50

ALPACA_PROMPT = """Classify the following email as phishing or legitimate. Reply with a single word: phishing or legitimate.

### Email:
{}

### Classification:
{}"""

EOS_TOKEN = None  # set after tokenizer is loaded


def load_jsonl(path: str) -> Dataset:
    with open(path, encoding="utf-8") as f:
        records = json.load(f)
    return Dataset.from_list(records)


def format_example(examples):
    texts = []
    for inp, out in zip(examples["input"], examples["output"]):
        text = ALPACA_PROMPT.format(inp, out) + EOS_TOKEN
        texts.append(text)
    return {"text": texts}


def plot_loss(log_history: list, out_path: str):
    train_steps, train_losses = [], []
    eval_steps, eval_losses = [], []
    for entry in log_history:
        if "loss" in entry:
            train_steps.append(entry["step"])
            train_losses.append(entry["loss"])
        if "eval_loss" in entry:
            eval_steps.append(entry["step"])
            eval_losses.append(entry["eval_loss"])

    plt.figure(figsize=(10, 5))
    plt.plot(train_steps, train_losses, label="Train Loss", alpha=0.8)
    if eval_losses:
        plt.plot(eval_steps, eval_losses, label="Eval Loss", marker="o", alpha=0.8)
    plt.xlabel("Step")
    plt.ylabel("Loss")
    plt.title("Training Loss Curve")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Loss curve saved → {out_path}")


def main():
    print(f"CUDA available: {torch.cuda.is_available()}")
    print(f"GPU: {torch.cuda.get_device_name(0)}")

    # ── Load model ────────────────────────────────────────────────────────────
    print(f"\nLoading {MODEL_NAME} with 4-bit quantization...")
    model, tokenizer = FastLanguageModel.from_pretrained(
        MODEL_NAME,
        load_in_4bit=LOAD_IN_4BIT,
        max_seq_length=MAX_SEQ_LENGTH,
        dtype=None,  # auto
    )

    global EOS_TOKEN
    if hasattr(tokenizer, "tokenizer"):
        tokenizer = tokenizer.tokenizer
    # Ensure eos/pad tokens are set correctly
    im_end_id = tokenizer.convert_tokens_to_ids("<|im_end|>")
    tokenizer.eos_token = "<|im_end|>"
    tokenizer.eos_token_id = im_end_id
    if tokenizer.pad_token is None:
        tokenizer.pad_token = "<|im_end|>"
        tokenizer.pad_token_id = im_end_id
    EOS_TOKEN = "<|im_end|>"

    # ── Add LoRA adapters ─────────────────────────────────────────────────────
    model = FastLanguageModel.get_peft_model(
        model,
        r=LORA_R,
        lora_alpha=LORA_ALPHA,
        lora_dropout=LORA_DROPOUT,
        target_modules=TARGET_MODULES,
        bias="none",
        use_gradient_checkpointing="unsloth",
        random_state=42,
    )
    model.print_trainable_parameters()

    # ── Dataset ───────────────────────────────────────────────────────────────
    print("\nLoading datasets...")
    train_ds = load_jsonl("data/train/data.json").map(format_example, batched=True)
    val_ds = load_jsonl("data/val/data.json").map(format_example, batched=True)

    # ── Trainer ───────────────────────────────────────────────────────────────
    training_args = SFTConfig(
        output_dir=str(OUTPUT_DIR),
        num_train_epochs=TRAIN_EPOCHS,
        per_device_train_batch_size=BATCH_SIZE,
        per_device_eval_batch_size=BATCH_SIZE,
        gradient_accumulation_steps=GRAD_ACCUM,
        learning_rate=LEARNING_RATE,
        warmup_steps=WARMUP_STEPS,
        logging_steps=LOGGING_STEPS,
        save_steps=SAVE_STEPS,
        eval_strategy="steps",
        eval_steps=EVAL_STEPS,
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
        greater_is_better=False,
        fp16=not torch.cuda.is_bf16_supported(),
        bf16=torch.cuda.is_bf16_supported(),
        optim="adamw_8bit",
        lr_scheduler_type="cosine",
        weight_decay=0.01,
        dataset_text_field="text",
        max_length=MAX_SEQ_LENGTH,
        report_to="none",
        save_total_limit=2,
    )

    trainer = SFTTrainer(
        model=model,
        processing_class=tokenizer,
        train_dataset=train_ds,
        eval_dataset=val_ds,
        args=training_args,
    )

    # ── Train ─────────────────────────────────────────────────────────────────
    print("\nStarting training...")
    result = trainer.train()
    print(f"\nTraining complete. Runtime: {result.metrics['train_runtime']:.0f}s")

    # ── Save LoRA adapter ─────────────────────────────────────────────────────
    adapter_path = OUTPUT_DIR / "lora_adapter"
    model.save_pretrained(str(adapter_path))
    tokenizer.save_pretrained(str(adapter_path))
    print(f"LoRA adapter saved → {adapter_path}")

    # ── Plot loss ─────────────────────────────────────────────────────────────
    plot_loss(trainer.state.log_history, "training_loss.png")

    # Save training metrics
    with open(OUTPUT_DIR / "training_metrics.json", "w") as f:
        json.dump(result.metrics, f, indent=2)

    print("\nAll done.")


if __name__ == "__main__":
    main()
