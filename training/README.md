# Training

Fine-tune a small open model so it produces the structured, uncertainty-aware
interpretations the Between interface expects. The default target is
[`Qwen/Qwen3-4B-Instruct-2507`](https://huggingface.co/Qwen/Qwen3-4B-Instruct-2507)
(Apache-2.0), trained with a LoRA or QLoRA adapter via Hugging Face TRL + PEFT.

## Layout

```text
training/
├── common.py            # shared system prompt, prompt builder, output validator
├── schema.json          # JSON Schema for the interpretation contract
├── data/
│   ├── build_seed.py    # generates seed.jsonl from hand-authored fixtures
│   └── seed.jsonl       # conversational SFT data (generated)
├── validate_data.py     # dataset validator (CI-safe, exits non-zero on errors)
├── sft_lora.py          # LoRA / QLoRA fine-tuning script
├── infer.py             # run the base model or adapter on a message
├── eval_set.py          # canonical 14-scenario held-out evaluation set
├── api_baseline.py      # run the same eval through an OpenRouter-hosted model
├── notebooks/
│   ├── kaggle_eval.py   # base-model evaluation script (paste into a Kaggle cell)
│   └── kaggle_eval.ipynb # the same as an importable Kaggle notebook
└── requirements.txt
```


### Kaggle evaluation (recommended first run)

`notebooks/kaggle_eval.ipynb` scores a candidate base model against 14 held-out synthetic
scenarios and reports schema validity, confidence spread, and whether sincere messages get
wrongly flagged as ironic. Run it on Kaggle's free T4 GPUs before spending time on the
server or on fine-tuning. Supports Gemma 4 E4B (attach via Add Input → Models), Qwen3-4B,
and Qwen3-0.6B.

### Hosted baseline (optional quality ceiling)

`api_baseline.py` sends the same synthetic scenarios to any OpenRouter model and writes
the same CSV columns, so hosted results sit next to the Kaggle ones. Use it only as a
calibration target: Between's deployed engine must stay open weights, and real user
messages must never be sent to a hosted API.

```bash
export OPENROUTER_API_KEY=sk-or-...
python3 api_baseline.py --model openrouter/auto
```

## Quickstart
```bash
cd training
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 1. Build and validate the seed dataset
python3 data/build_seed.py
python3 validate_data.py

# 2. Fine-tune (see hardware notes below)
python3 sft_lora.py --qlora          # NVIDIA GPU
python3 sft_lora.py                  # LoRA elsewhere (slower)

# 3. Try the adapter
python3 infer.py --adapter out/between-lora \
  --message "Wow thanks for telling me 🙃" \
  --context "Maya: I thought you were going to tell me if the time changed."
```

## Data format

One JSON object per line, TRL conversational format:

- `system` — the fixed prompt from `common.py` (possibilities not verdicts, JSON only)
- `user` — minimal context (oldest first) + the target message
- `assistant` — exactly one JSON object matching `schema.json`

The interpretation contract:

| Field | Meaning |
|---|---|
| `literalMeaning` | what the words say on their face |
| `possibleImpliedMeanings` | 1–3 alternative readings |
| `possibleEmotions` | hedged emotion possibilities |
| `speechAct` | what the message does in the conversation |
| `literalness` | `literal` / `possibly-nonliteral` / `unclear` |
| `confidence` | 0–1; high values should be rare |
| `evidence` | contextual cues actually used |
| `missingContext` | what would change the reading |
| `suggestedAction` | a reversible, low-pressure next step |
| `suggestedMessage` | optional example phrasing, or `null` |

## Data policy

- The seed dataset is **synthetic and hand-authored**. No real conversations.
- Any future real data requires **informed consent** and **de-identification**
  (strip names, handles, links, and identifying details) before it touches a
  training pipeline.
- Never train on or infer anything about users' identities, diagnoses, or
  neurotype. The tool assists communication; it does not profile people.
- Keep literal examples in the mix. A model trained only on sarcasm will
  over-flag sincere messages, which is worse than no tool at all.
- For ambiguous messages, preserve annotator disagreement instead of forcing a
  single gold label.

## Hardware notes

- **NVIDIA GPU (≥16 GB):** use `--qlora`. A 4B model trains comfortably on a
  T4/A10-class GPU; Colab and Kaggle free tiers work.
- **Apple Silicon (this project's dev machine):** bitsandbytes/QLoRA is not
  available. Plain LoRA runs via MPS/CPU but is slow; prefer a cloud GPU for
  the 4B model, or use `--model Qwen/Qwen3-0.6B` for a fast local baseline.
- Training on the 0.6B baseline is a good end-to-end pipeline check before
  spending real GPU time on the 4B model.

## Evaluation roadmap

Classification accuracy is the wrong primary metric here. Before shipping any
model into the UI, measure:

1. **Schema validity rate** — fraction of outputs that parse and validate.
2. **Calibration** — does `confidence` track human agreement? (Reliability
   diagrams; overconfident wrong readings are the product's worst failure.)
3. **Literal preservation** — when the literal reading is plausible, does the
   output include it?
4. **Harmless-failure check** — on sincere positive messages, does the model
   wrongly imply irony?
5. **Human preference** — do autistic adults find the readings useful and
   non-patronizing compared with emotion-only labels and no assistance?
