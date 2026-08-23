"""Between base-model evaluation — designed to run in a Kaggle notebook.

Paste this whole file into one Kaggle code cell, enable a GPU accelerator
(T4 x2 is plenty) and Internet in the notebook settings, then run.

What it does:
  1. Loads one candidate base model (Gemma 4 E4B, Qwen3-4B, or Qwen3-0.6B).
  2. Runs 14 held-out synthetic scenarios through the Between prompt contract.
  3. Validates each JSON output against the interpretation contract.
  4. Writes between_base_eval_<model>.csv and prints a summary.

No real conversations are used anywhere in this file.
"""

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# One of: "gemma4_e4b" | "qwen3_4b" | "qwen3_06b"
MODEL_KEY = "gemma4_e4b"

RUN_PIP = True          # set False if the cell was already installed
SHOW_OUTPUTS = True     # print every raw interpretation as it runs

HF_FALLBACK_IDS = {
    # If the model is not attached under /kaggle/input, load from HF instead.
    # Adjust the gemma id if Google's repo name differs; attaching the model
    # via Kaggle's "Add Input -> Models" avoids the guesswork entirely.
    "gemma4_e4b": "google/gemma-4-E4B-it",
    "qwen3_4b": "Qwen/Qwen3-4B-Instruct-2507",
    "qwen3_06b": "Qwen/Qwen3-0.6B",
}

import subprocess
import sys

if RUN_PIP:
    # -U matters: Kaggle preinstalls a transformers 4.x that already satisfies
    # ">=4.53", so without --upgrade pip silently keeps the old one and new
    # architectures (e.g. gemma4) fail with KeyError in CONFIG_MAPPING.
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "-q", "-U",
         "transformers", "accelerate", "sentencepiece"],
        check=True,
    )


def _supports_model_type(model_type):
    try:
        from transformers.models.auto.configuration_auto import CONFIG_MAPPING_NAMES
        return model_type in CONFIG_MAPPING_NAMES
    except Exception:
        return True  # never block the run on introspection failure


# Gemma 4 checkpoints declare model_type "gemma4" (transformers >= 5.5.0).
if MODEL_KEY.startswith("gemma") and not _supports_model_type("gemma4"):
    print("installed transformers lacks 'gemma4' (needs >= 5.5); upgrading ...")
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "-q", "-U",
         "git+https://github.com/huggingface/transformers.git"],
        check=True,
    )

import csv
import glob
import json
import os

try:  # pull an HF token from Kaggle secrets if one exists (needed for gated repos)
    from kaggle_secrets import UserSecretsClient
    os.environ.setdefault("HF_TOKEN", UserSecretsClient().get_secret("HF_TOKEN"))
except Exception:
    pass

import torch
from transformers import AutoTokenizer

# ---------------------------------------------------------------------------
# Prompt contract (mirrors training/common.py)
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """\
You are Between, a user-controlled communication aid for autistic people who \
want another way to examine an ambiguous text message. You help a reader \
consider what an incoming message might mean beyond its literal words. Do not \
assume that autistic people share one communication style, and never assume or \
disclose anyone's neurotype, diagnosis, or identity.

Rules:
- Offer possibilities, never verdicts. You cannot know the sender's intent.
- Always include the literal reading when it is plausible.
- Describe communication moves (speech acts) before emotion labels, and hedge \
emotions ("possibly frustrated").
- Treat conversation context as evidence, not proof. If context is insufficient, \
lower confidence and say what is missing.
- Confidence is a number between 0 and 1 reflecting how strongly the context \
supports the most likely nonliteral reading. High confidence should be rare.
- Suggest a reversible, low-pressure next step, usually a clarifying question.
- Output exactly one JSON object matching the schema. No markdown, no extra text."""

REQUIRED_KEYS = (
    "literalMeaning", "possibleImpliedMeanings", "possibleEmotions",
    "speechAct", "literalness", "confidence", "evidence",
    "missingContext", "suggestedAction", "suggestedMessage",
)
LITERALNESS_VALUES = {"literal", "possibly-nonliteral", "unclear"}


def user_content(context, target_author, target_text):
    lines = []
    if context:
        lines.append("Conversation context (oldest first):")
        lines.extend(f"{author}: {text}" for author, text in context)
    else:
        lines.append("Conversation context: (none provided)")
    lines += ["", f"Target message (from {target_author}):", target_text, "",
              "Interpret the target message for the reader. Reply with the JSON object only."]
    return "\n".join(lines)


def strip_code_fences(text):
    t = (text or "").strip()
    if t.startswith("```"):
        t = t.strip("`")
        nl = t.find("\n")
        if nl != -1 and t[:nl].strip().lower() in ("", "json"):
            t = t[nl + 1:]
        close = t.rfind("```")
        if close != -1:
            t = t[:close]
    return t.strip()


def validate_interpretation(obj):
    errors = []
    if not isinstance(obj, dict):
        return ["not a JSON object"]
    for key in REQUIRED_KEYS:
        if key not in obj:
            errors.append(f"missing key: {key}")
    if obj.get("literalness") not in (None,) | LITERALNESS_VALUES:
        errors.append("bad literalness")
    conf = obj.get("confidence")
    if conf is not None and not (isinstance(conf, (int, float)) and 0 <= conf <= 1):
        errors.append("confidence out of range")
    return errors


# ---------------------------------------------------------------------------
# Held-out evaluation set (synthetic; deliberately different from seed data)
# ---------------------------------------------------------------------------

EVAL_SET = [
    dict(id="late_party", expect="ironic/pointed",
         context=[("You", "(hosting, guest arrives 40 minutes late)")],
         author="Guest", target="Nice of you to join us."),
    dict(id="early_coworker", expect="likely literal smalltalk",
         context=[], author="Coworker", target="You're here early."),
    dict(id="not_hungry", expect="possible polite decline at dinner",
         context=[("You", "dinner's ready!")],
         author="Guest", target="I'm not hungry right now."),
    dict(id="if_you_say_so", expect="skepticism / unresolved feelings",
         context=[("You", "I'm sorry again — it won't happen again."), ("You", "I really mean it.")],
         author="Friend", target="If you say so."),
    dict(id="didnt_have_to", expect="genuine gratitude, maybe surprised",
         context=[("You", "(cleaned the whole kitchen while your roommate was out)")],
         author="Roommate", target="You didn't have to do that!"),
    dict(id="whatever_works", expect="ambiguous: flexible or disengaged",
         context=[("Sam", "sorry I keep going quiet about saturday")],
         author="Sam", target="Whatever works for you :)"),
    dict(id="now_you_have_time", expect="sarcastic resentment",
         context=[("Group chat", "(teammate silent for two weeks, replies today)")],
         author="Teammate", target="Oh, NOW you have time?"),
    dict(id="see_you_8", expect="literal logistics",
         context=[("You", "what time tonight?")],
         author="Ben", target="See you at 8."),
    dict(id="something_different", expect="ambiguous compliment or tease",
         context=[("You", "(got a very short haircut over the weekend)")],
         author="Priya", target="Wow, you did something different!"),
    dict(id="boss_weekend", expect="soft obligation request",
         context=[], author="Manager", target="Are you around this weekend?"),
    dict(id="send_notes", expect="literal request",
         context=[("You", "i took notes in class today")],
         author="Classmate", target="Can you send me the notes?"),
    dict(id="totally_fine", expect="possible hurt behind insistence",
         context=[("You", "really sorry i canceled on you again")],
         author="Riley", target="No no, it's totally fine!!"),
    dict(id="one_way_to_look", expect="softened disagreement",
         context=[("You", "i think the design is perfect as is")],
         author="Colleague", target="That's one way to look at it."),
    dict(id="exam_moved", expect="venting, possibly ironic stress",
         context=[("Casey", "(studying for weeks)")],
         author="Casey", target="My exam got moved to tomorrow 🙃"),
]
EXPECT_LITERAL = {"early_coworker", "see_you_8", "send_notes"}

# ---------------------------------------------------------------------------
# Model loading
# ---------------------------------------------------------------------------


def resolve_model_id():
    local_dirs = sorted(glob.glob("/kaggle/input/*/config.json")) + \
                 sorted(glob.glob("/kaggle/input/*/*/config.json"))
    if MODEL_KEY.startswith("gemma") and local_dirs:
        print(f"using attached Kaggle model input: {os.path.dirname(local_dirs[0])}")
        return os.path.dirname(local_dirs[0])
    return HF_FALLBACK_IDS[MODEL_KEY]


def load_model():
    model_id = resolve_model_id()
    dtype_kw = {"dtype": torch.bfloat16} if torch.cuda.is_available() else {}

    def load_with(cls):
        try:
            return cls.from_pretrained(model_id, device_map="auto", **dtype_kw)
        except TypeError:  # older transformers: torch_dtype
            return cls.from_pretrained(model_id, device_map="auto", torch_dtype=torch.float16)

    print(f"loading {model_id} ...")
    tokenizer = AutoTokenizer.from_pretrained(model_id)

    # Gemma 4 is multimodal; which auto class fits depends on the transformers
    # version, so try the known candidates in order.
    import transformers
    last_exc = None
    model = None
    for name in ("AutoModelForCausalLM", "AutoModelForImageTextToText", "AutoModelForMultimodalLM"):
        cls = getattr(transformers, name, None)
        if cls is None:
            continue
        try:
            model = load_with(cls)
            print(f"loaded via {name}")
            break
        except Exception as exc:
            last_exc = exc
            print(f"{name} failed ({type(exc).__name__}); trying next loader ...")
    if model is None:
        raise last_exc
    model.eval()
    print("loaded.")
    return model, tokenizer


@torch.no_grad()
def interpret(model, tokenizer, scenario):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_content(scenario["context"], scenario["author"], scenario["target"])},
    ]
    inputs = tokenizer.apply_chat_template(
        messages, add_generation_prompt=True, tokenize=True, return_dict=True, return_tensors="pt"
    ).to(model.device)
    output = model.generate(**inputs, max_new_tokens=420, do_sample=False,
                            pad_token_id=tokenizer.eos_token_id)
    text = tokenizer.decode(output[0][inputs["input_ids"].shape[-1]:], skip_special_tokens=True)
    cleaned = strip_code_fences(text)
    try:
        parsed = json.loads(cleaned)
        problems = validate_interpretation(parsed)
    except json.JSONDecodeError:
        parsed, problems = None, ["output was not valid JSON"]
    return text, parsed, problems


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------

model, tokenizer = load_model()

rows = []
for scenario in EVAL_SET:
    raw, parsed, problems = interpret(model, tokenizer, scenario)
    row = dict(
        id=scenario["id"],
        expect=scenario["expect"],
        valid_json=parsed is not None and not problems,
        literalness=(parsed or {}).get("literalness", ""),
        confidence=(parsed or {}).get("confidence", ""),
        implied_count=len((parsed or {}).get("possibleImpliedMeanings", []) or []),
        first_reading=((parsed or {}).get("possibleImpliedMeanings") or [""])[0][:90],
        suggested_action=((parsed or {}).get("suggestedAction") or "")[:90],
        error="; ".join(problems),
    )
    rows.append(row)

    flag = "ok " if row["valid_json"] else "BAD"
    if SHOW_OUTPUTS:
        print(f"[{flag}] {scenario['id']} ({scenario['expect']})")
        if SHOW_OUTPUTS and parsed:
            print(json.dumps(parsed, indent=2, ensure_ascii=False)[:700])
        elif SHOW_OUTPUTS:
            print(raw[:500])
        print("-" * 70)

out_csv = f"between_base_eval_{MODEL_KEY}.csv"
with open(out_csv, "w", newline="", encoding="utf-8") as handle:
    writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)

valid = sum(r["valid_json"] for r in rows)
confs = [r["confidence"] for r in rows if isinstance(r["confidence"], (int, float))]
lit_rows = [r for r in rows if r["id"] in EXPECT_LITERAL]
lit_flagged = sum(1 for r in lit_rows if r["literalness"] == "possibly-nonliteral")

print(f"\nmodel:            {MODEL_KEY}")
print(f"schema-valid:     {valid}/{len(rows)}")
print(f"confidence range: {min(confs, default=0):.2f} - {max(confs, default=0):.2f} "
      f"(mean {sum(confs)/len(confs) if confs else 0:.2f})")
print(f"literal messages flagged nonliteral: {lit_flagged}/{len(lit_rows)}  <- should be 0-ish")
print(f"\nwrote {out_csv}")
