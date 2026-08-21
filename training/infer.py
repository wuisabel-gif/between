#!/usr/bin/env python3
"""Run interpretation inference with a Between adapter (or the base model).

Examples:
    # Base model, no adapter:
    python3 training/infer.py --message 'Do whatever you want.' \
        --context 'Maya: I don\'t know if I want to go anymore.' \
        --context 'You: I can stay home if you\'d rather.'

    # With a trained adapter:
    python3 training/infer.py --adapter training/out/between-lora \
        --message 'Wow thanks for telling me 🙃' \
        --context 'Maya: I thought you were going to tell me if the time changed.'
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import build_messages, strip_code_fences, validate_interpretation  # noqa: E402

import torch  # noqa: E402
from transformers import AutoModelForCausalLM, AutoTokenizer  # noqa: E402


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", default="Qwen/Qwen3-4B-Instruct-2507")
    parser.add_argument("--adapter", default=None, help="Path to a saved LoRA adapter")
    parser.add_argument("--message", required=True, help="The target message to interpret")
    parser.add_argument("--author", default="Them", help="Label for the target message sender")
    parser.add_argument("--context", action="append", default=[],
                        help='Repeatable. One prior message as "Author: text" (oldest first)')
    parser.add_argument("--max-new-tokens", type=int, default=420)
    return parser.parse_args()


def load_model_and_tokenizer(model_name, adapter):
    dtype = torch.bfloat16 if torch.cuda.is_available() and torch.cuda.is_bf16_supported() else torch.float32
    load_kwargs = {"device_map": "auto"}

    def load(pretrained, dtype_kw):
        if adapter:
            from peft import AutoPeftModelForCausalLM
            return AutoPeftModelForCausalLM.from_pretrained(pretrained, **{dtype_kw: dtype}, **load_kwargs)
        return AutoModelForCausalLM.from_pretrained(pretrained, **{dtype_kw: dtype}, **load_kwargs)

    try:
        model = load(adapter or model_name, "dtype")
    except TypeError:
        model = load(adapter or model_name, "torch_dtype")
    tokenizer = AutoTokenizer.from_pretrained(adapter or model_name)
    model.eval()
    return model, tokenizer


def main():
    args = parse_args()

    context = []
    for item in args.context:
        author, sep, text = item.partition(": ")
        context.append((author.strip() if sep else "Them", (text if sep else item).strip()))

    model, tokenizer = load_model_and_tokenizer(args.model, args.adapter)
    messages = build_messages(context, args.author, args.message)

    inputs = tokenizer.apply_chat_template(
        messages, add_generation_prompt=True, tokenize=True, return_dict=True, return_tensors="pt"
    ).to(model.device)

    with torch.no_grad():
        output = model.generate(
            **inputs,
            max_new_tokens=args.max_new_tokens,
            do_sample=False,
            pad_token_id=tokenizer.eos_token_id,
        )

    generated = tokenizer.decode(output[0][inputs["input_ids"].shape[-1]:], skip_special_tokens=True)
    raw = strip_code_fences(generated)

    try:
        interpretation = json.loads(raw)
    except json.JSONDecodeError:
        print("model output was not valid JSON:\n")
        print(generated)
        sys.exit(2)

    print(json.dumps(interpretation, indent=2, ensure_ascii=False))
    problems = validate_interpretation(interpretation)
    if problems:
        print("\nschema warnings:")
        for problem in problems:
            print(f"  - {problem}")
        sys.exit(1)


if __name__ == "__main__":
    main()
