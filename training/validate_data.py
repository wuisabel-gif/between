#!/usr/bin/env python3
"""Validate a Between conversational JSONL dataset before training.

Checks every row for structure (roles, ordering), parses the assistant turn as
JSON, and validates it against the interpretation contract in common.py.
Exits non-zero on any error so it can gate CI.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import SYSTEM_PROMPT, validate_interpretation  # noqa: E402


def validate_file(path):
    errors = []
    stats = {"rows": 0, "literalness": {}, "confidence": []}

    text = Path(path).read_text(encoding="utf-8")
    for number, line in enumerate(text.splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"line {number}: invalid JSON ({exc})")
            continue

        messages = row.get("messages")
        if not isinstance(messages, list) or len(messages) != 3:
            errors.append(f"line {number}: expected messages=[system,user,assistant]")
            continue

        roles = [m.get("role") for m in messages]
        if roles != ["system", "user", "assistant"]:
            errors.append(f"line {number}: unexpected roles {roles}")
            continue

        if not messages[0]["content"].startswith(SYSTEM_PROMPT[:60]):
            errors.append(f"line {number}: system prompt does not match common.SYSTEM_PROMPT")

        try:
            obj = json.loads(messages[2]["content"])
        except json.JSONDecodeError as exc:
            errors.append(f"line {number}: assistant content is not valid JSON ({exc})")
            continue

        for problem in validate_interpretation(obj):
            errors.append(f"line {number}: {problem}")

        stats["rows"] += 1
        literalness = obj.get("literalness", "?")
        stats["literalness"][literalness] = stats["literalness"].get(literalness, 0) + 1
        if isinstance(obj.get("confidence"), (int, float)):
            stats["confidence"].append(obj["confidence"])

    return errors, stats


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else str(Path(__file__).resolve().parent / "data" / "seed.jsonl")
    errors, stats = validate_file(path)

    mean = sum(stats["confidence"]) / len(stats["confidence"]) if stats["confidence"] else 0
    print(f"rows: {stats['rows']}")
    print(f"literalness: {stats['literalness']}")
    print(f"confidence: min={min(stats['confidence'], default=0):.2f} "
          f"max={max(stats['confidence'], default=0):.2f} mean={mean:.2f}")

    if errors:
        print(f"\n{len(errors)} problem(s):")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)
    print("\ndataset OK")


if __name__ == "__main__":
    main()
