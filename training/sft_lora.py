#!/usr/bin/env python3
"""Supervised fine-tuning for Between interpretations (LoRA or QLoRA).

Trains a small instruct model (default: Qwen/Qwen3-4B-Instruct-2507) on the
conversational seed dataset using TRL's SFTTrainer with a PEFT LoRA adapter.
Loss is computed on assistant messages only when the installed TRL supports it.

Examples:
    python3 training/sft_lora.py                          # LoRA on GPU/MPS/CPU
    python3 training/sft_lora.py --qlora                  # 4-bit QLoRA (NVIDIA)
    python3 training/sft_lora.py --model Qwen/Qwen3-0.6B  # cheap baseline
"""

import argparse
import dataclasses
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import SYSTEM_PROMPT  # noqa: E402

import torch  # noqa: E402
from datasets import load_dataset  # noqa: E402
from peft import LoraConfig  # noqa: E402
from transformers import AutoTokenizer, BitsAndBytesConfig  # noqa: E402
from trl import SFTConfig, SFTTrainer  # noqa: E402

DEFAULT_MODEL = "Qwen/Qwen3-4B-Instruct-2507"


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--dataset", default=str(Path(__file__).resolve().parent / "data" / "seed.jsonl"))
    parser.add_argument("--output-dir", default="training/out/between-lora")
    parser.add_argument("--epochs", type=float, default=3.0)
    parser.add_argument("--batch-size", type=int, default=2)
    parser.add_argument("--grad-accum", type=int, default=8)
    parser.add_argument("--lr", type=float, default=2e-4, help="LoRA-friendly rate (~10x full FT)")
    parser.add_argument("--max-length", type=int, default=2048)
    parser.add_argument("--lora-r", type=int, default=16)
    parser.add_argument("--lora-alpha", type=int, default=32)
    parser.add_argument("--lora-dropout", type=float, default=0.05)
    parser.add_argument("--qlora", action="store_true", help="4-bit QLoRA (NVIDIA GPUs only)")
    parser.add_argument("--seed", type=int, default=42)
    return parser.parse_args()


def main():
    args = parse_args()

    use_cuda = torch.cuda.is_available()
    bf16 = use_cuda and torch.cuda.is_bf16_supported()

    quantization_config = None
    if args.qlora:
        if not use_cuda:
            sys.exit("--qlora requires an NVIDIA GPU (bitsandbytes). Omit the flag for LoRA.")
        quantization_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.bfloat16 if bf16 else torch.float16,
            bnb_4bit_use_double_quant=True,
        )

    dataset = load_dataset("json", data_files=args.dataset, split="train")
    first_system = dataset[0]["messages"][0]["content"]
    if not first_system.startswith(SYSTEM_PROMPT[:60]):
        print("[warn] dataset system prompt differs from common.SYSTEM_PROMPT; regenerate the dataset")

    config_fields = {f.name for f in dataclasses.fields(SFTConfig)}
    length_key = "max_length" if "max_length" in config_fields else "max_seq_length"
    extra = {length_key: args.max_length}
    if "assistant_only_loss" in config_fields:
        extra["assistant_only_loss"] = True
    else:
        print("[warn] installed TRL lacks assistant_only_loss; loss will include prompt tokens")

    training_args = SFTConfig(
        output_dir=args.output_dir,
        num_train_epochs=args.epochs,
        per_device_train_batch_size=args.batch_size,
        gradient_accumulation_steps=args.grad_accum,
        learning_rate=args.lr,
        lr_scheduler_type="cosine",
        warmup_ratio=0.03,
        logging_steps=5,
        save_strategy="epoch",
        bf16=bf16,
        report_to="none",
        seed=args.seed,
        **extra,
    )

    peft_config = LoraConfig(
        r=args.lora_r,
        lora_alpha=args.lora_alpha,
        lora_dropout=args.lora_dropout,
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
    )

    trainer_kwargs = dict(
        model=args.model,
        args=training_args,
        train_dataset=dataset,
        peft_config=peft_config,
    )
    if quantization_config is not None:
        trainer_kwargs["quantization_config"] = quantization_config

    trainer = SFTTrainer(**trainer_kwargs)
    trainer.train()

    trainer.save_model(args.output_dir)
    AutoTokenizer.from_pretrained(args.model).save_pretrained(args.output_dir)
    print(f"\nadapter saved to {args.output_dir}")
    print("try it:  python3 training/infer.py --adapter "
          f"{args.output_dir} --message 'Wow thanks for telling me 🙃' "
          "--context 'Maya: I thought you were going to tell me if the time changed.'")


if __name__ == "__main__":
    main()
