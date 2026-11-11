#!/usr/bin/env python3
"""
QLoRA fine-tuning of Qwen3-14B for phishing email detection using Unsloth.
"""

import os
os.environ["TORCHDYNAMO_DISABLE"] = "1"
os.environ["UNSLOTH_RETURN_LOGITS"] = "1"  # unsloth drops eval logits otherwise; compute_metrics needs them

# unsloth must be imported before trl/transformers so its patches apply first
from unsloth import FastLanguageModel

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import torch
from datasets import Dataset
from trl import SFTTrainer, SFTConfig

# ── Config ────────────────────────────────────────────────────────────────────
MODEL_NAME = "unsloth/Qwen3-14B"
MAX_SEQ_LENGTH = 2048
MAX_EMAIL_TOKENS = MAX_SEQ_LENGTH - 64  # room for the template + answer
LOAD_IN_4BIT = True

LORA_R = 16
LORA_ALPHA = 16
LORA_DROPOUT = 0.05
TARGET_MODULES = ["q_proj", "k_proj", "v_proj", "o_proj"]

OUTPUT_DIR = Path("training_runs/results_dedup")  # keep the old run for comparison
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
TOKENIZER = None


def load_jsonl(path: str) -> Dataset:
    with open(path, encoding="utf-8") as f:
        records = json.load(f)
    return Dataset.from_list(records)


def format_example(examples):
    # prompt/completion split -> TRL computes loss on the answer only
    prompts, completions = [], []
    for inp, out in zip(examples["input"], examples["output"]):
        # cut the email, not the answer, so long emails keep their label
        ids = TOKENIZER(inp, add_special_tokens=False)["input_ids"][:MAX_EMAIL_TOKENS]
        prompts.append(ALPACA_PROMPT.format(TOKENIZER.decode(ids), ""))
        completions.append(out + EOS_TOKEN)
    return {"prompt": prompts, "completion": completions}


def preprocess_logits_for_metrics(logits, labels):
    return logits.argmax(-1)


def compute_metrics(eval_pred):
    # first answer token ("ph" vs "leg") decides the class; logits at t predict token t+1
    preds, labels = eval_pred.predictions, eval_pred.label_ids
    first = (labels != -100).argmax(1)
    rows = np.arange(len(labels))
    return {"accuracy": float((preds[rows, first - 1] == labels[rows, first]).mean())}


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

    global EOS_TOKEN, TOKENIZER
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
    TOKENIZER = tokenizer

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
    train_ds = load_jsonl("data/dedup/train/data.json")
    train_ds = train_ds.map(format_example, batched=True, remove_columns=train_ds.column_names)
    val_ds = load_jsonl("data/dedup/val/data.json")
    val_ds = val_ds.map(format_example, batched=True, remove_columns=val_ds.column_names)

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
        metric_for_best_model="accuracy",  # val accuracy, not eval_loss
        greater_is_better=True,
        label_names=["labels"],  # PeftModel hides labels from Trainer's auto-detection
        completion_only_loss=True,
        fp16=not torch.cuda.is_bf16_supported(),
        bf16=torch.cuda.is_bf16_supported(),
        optim="adamw_8bit",
        lr_scheduler_type="cosine",
        weight_decay=0.01,
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
        compute_metrics=compute_metrics,
        preprocess_logits_for_metrics=preprocess_logits_for_metrics,
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
    plot_loss(trainer.state.log_history, str(OUTPUT_DIR / "training_loss.png"))

    # Save training metrics
    with open(OUTPUT_DIR / "training_metrics.json", "w") as f:
        json.dump(result.metrics, f, indent=2)

    print("\nAll done.")


if __name__ == "__main__":
    main()
