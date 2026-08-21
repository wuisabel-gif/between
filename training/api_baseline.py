#!/usr/bin/env python3
"""Run the Between evaluation set through an OpenRouter-hosted model.

This is a quality baseline only. Between's deployed engine must be open
weights (Qwen3 / Gemma 4) so that messages can stay local. The evaluation
set is synthetic, so nothing private is sent anywhere.

Usage:
    export OPENROUTER_API_KEY=sk-or-...
    python3 api_baseline.py --model openrouter/auto
    python3 api_baseline.py --model anthropic/claude-sonnet-4 --show

Writes between_api_eval_<model>.csv using the same columns as
notebooks/kaggle_eval.py, so results compare side by side.
"""

import argparse
import csv
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import build_messages, strip_code_fences, validate_interpretation  # noqa: E402
from eval_set import EVAL_SET, EXPECT_LITERAL  # noqa: E402

API_URL = "https://openrouter.ai/api/v1/chat/completions"


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", required=True, help='OpenRouter model id, e.g. "openrouter/auto"')
    parser.add_argument("--api-key", default=os.environ.get("OPENROUTER_API_KEY"))
    parser.add_argument("--max-tokens", type=int, default=700)
    parser.add_argument("--retries", type=int, default=2)
    parser.add_argument("--show", action="store_true", help="print each interpretation")
    return parser.parse_args()


def chat(api_key, model, messages, max_tokens, retries):
    payload = json.dumps({
        "model": model,
        "messages": messages,
        "temperature": 0.0,
        "max_tokens": max_tokens,
    }).encode("utf-8")
    request = urllib.request.Request(API_URL, data=payload, headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/wuisabel-gif/between",
        "X-Title": "Between hosted-model baseline",
    })
    problem = None
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(request, timeout=180) as response:
                data = json.loads(response.read())
            return data["choices"][0]["message"]["content"]
        except urllib.error.HTTPError as exc:
            problem = f"HTTP {exc.code}: {exc.read().decode('utf-8', 'replace')[:200]}"
            if exc.code not in (429, 500, 502, 503, 504):
                break
        except Exception as exc:  # network hiccup: retry
            problem = str(exc)
        time.sleep(3 * (2 ** attempt))
    raise RuntimeError(f"OpenRouter call failed ({attempt + 1} tries): {problem}")


def main():
    args = parse_args()
    if not args.api_key:
        sys.exit("Set OPENROUTER_API_KEY (or pass --api-key). Get one at openrouter.ai/keys.")

    rows = []
    for scenario in EVAL_SET:
        messages = build_messages(scenario["context"], scenario["author"], scenario["target"])
        try:
            raw = chat(args.api_key, args.model, messages, args.max_tokens, args.retries)
        except RuntimeError as exc:
            print(f"[ERR] {scenario['id']}: {exc}")
            raw = ""

        cleaned = strip_code_fences(raw)
        try:
            parsed = json.loads(cleaned)
            problems = validate_interpretation(parsed)
        except json.JSONDecodeError:
            parsed, problems = None, ["output was not valid JSON"]

        row = dict(
            id=scenario["id"],
            expect=scenario["expect"],
            valid_json=parsed is not None and not problems,
            literalness=(parsed or {}).get("literalness", ""),
            confidence=(parsed or {}).get("confidence", ""),
            implied_count=len((parsed or {}).get("possibleImpliedMeanings") or []),
            first_reading=((parsed or {}).get("possibleImpliedMeanings") or [""])[0][:90],
            suggested_action=((parsed or {}).get("suggestedAction") or "")[:90],
            error="; ".join(problems),
        )
        rows.append(row)

        flag = "ok " if row["valid_json"] else "BAD"
        print(f"[{flag}] {scenario['id']} ({scenario['expect']}) "
              f"conf={row['confidence']} lit={row['literalness']}")
        if args.show:
            print(json.dumps(parsed, indent=2, ensure_ascii=False)[:700] if parsed else raw[:500])
            print("-" * 70)

    slug = args.model.replace("/", "_")
    out_csv = f"between_api_eval_{slug}.csv"
    with open(out_csv, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    valid = sum(r["valid_json"] for r in rows)
    confs = [r["confidence"] for r in rows if isinstance(r["confidence"], (int, float))]
    literal_rows = [r for r in rows if r["id"] in EXPECT_LITERAL]
    flagged = sum(1 for r in literal_rows if r["literalness"] == "possibly-nonliteral")

    print(f"\nmodel:            {args.model}")
    print(f"schema-valid:     {valid}/{len(rows)}")
    print(f"confidence range: {min(confs, default=0):.2f} - {max(confs, default=0):.2f} "
          f"(mean {sum(confs) / len(confs) if confs else 0:.2f})")
    print(f"literal messages flagged nonliteral: {flagged}/{len(literal_rows)}  <- should be 0-ish")
    print(f"\nwrote {out_csv}")


if __name__ == "__main__":
    main()
