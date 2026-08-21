# Between

**Between** is a user-controlled communication aid for autistic people: not an emotion detector, but an uncertainty-aware second look at messages whose literal words may not tell the whole story.

> The prototype is an optional thinking aid for autistic users. It does not speak for autistic people, read minds, diagnose anyone, or provide clinical advice.

## Run it

Live site: **https://wuisabel-gif.github.io/between/**

To run it locally, clone this repo and serve the folder with any static server:

```bash
cd between
python3 -m http.server 4173
```

Then open <http://127.0.0.1:4173>. The small `package.json` only provides a JavaScript syntax check:

```bash
npm run check
```

You can also open `index.html` directly, although a local server gives the browser the same origin behavior a future extension prototype will have.

## What is in this first cut

- Three contextual conversation fixtures:
  - “Wow thanks for telling me 🙃”
  - “Do whatever you want.”
  - “It’s fine.”
- A message view showing the nearby context that the reading uses.
- A structured interpretation with:
  - literal meaning;
  - possible implied meanings;
  - possible emotions;
  - speech act;
  - a literal/nonliteral caution;
  - confidence;
  - evidence from context;
  - a low-pressure suggested next step.
- A custom-message box with a small deterministic local heuristic. It does not call an API and does not claim to understand intent.
- A privacy/settings dialog with click-to-analyze, context-length, and analysis-mode controls.
- Responsive layout, keyboard focus styles, semantic headings and labels, reduced-motion support, and a visible uncertainty boundary.

## Product principles

Between is designed for autistic people who want extra support examining ambiguous messages. It does not assume that autistic people share one communication style, and it never tries to detect, label, or disclose whether a person is autistic.

### Possibilities, not verdicts

A message can be sarcastic, playful, tired, indirect, or literal. The UI keeps more than one reading visible and avoids turning a plausible inference into a fact about another person.

### Context before labels

The prototype shows the small context window used for a reading. It treats context as evidence, not proof. The literal words stay visible instead of being replaced by an emotion label.

### Ask before assuming

The suggested next step is framed as an option. A direct, low-pressure clarification is more reliable than teaching someone to trust an AI interpretation of another person.

### Privacy as a product feature

The intended default is click-to-analyze. A future surface should:

- read the minimum context needed;
- show what it read and when;
- avoid retaining conversations by default;
- avoid training on messages;
- offer local processing where practical;
- make automatic analysis opt-in;
- let a person turn the layer off without losing access to the conversation.

This static demo keeps fixture data and custom text in the current page only. It stores only the selected display settings in `localStorage`; it does not store messages, call a model provider, or send network requests.

## What it is not yet

This is a product and research prototype, not a validated interpretation system. The sample analyses are hand-authored fixtures, and custom analysis is a transparent keyword heuristic. It should not be used to make decisions about safety, consent, employment, relationships, or a person’s diagnosis.

The prototype deliberately does **not** include:

- a Discord bot or browser extension;
- a server-side model;
- automatic reading of a real conversation;
- identity or relationship memory;
- claims of clinical efficacy or interpretation accuracy.

## Suggested next steps

1. **Co-design the vocabulary.** Work with autistic adults and other neurodivergent users to decide whether labels such as “speech act,” “literal meaning,” and “possible emotion” are useful, overwhelming, or need different wording.
2. **Build a privacy-preserving extension shell.** Start with a Chrome content script for a local test surface. Add an explicit context preview and a click-to-read interaction before considering automatic analysis.
3. **Define a structured interpretation contract.** Keep the output schema close to the UI: literal reading, alternatives, evidence, uncertainty, and suggested clarification. Require the model to say when context is insufficient.
4. **Evaluate calibration, not just classification.** Test interpretation accuracy, confidence calibration, time, cognitive load, trust, preference, and whether users feel more able to ask clarifying questions. Include an emotion-only comparison and a no-assistance control.
5. **Add a model behind a privacy boundary.** Compare a local model, a user-controlled provider, and a carefully scoped hosted service. Make the provider, retention behavior, context window, and cost visible.
6. **Pilot one surface.** Discord Web is a plausible research surface, but its DOM and policy constraints change. A small mock messaging surface or extension test page should come before a live integration.

## Training scaffold

The [`training/`](training/) folder contains an experimental fine-tuning pipeline for the interpretation model: a shared prompt contract, a synthetic seed dataset (`training/data/build_seed.py`), a dataset validator, a TRL + LoRA/QLoRA script targeting [`Qwen/Qwen3-4B-Instruct-2507`](https://huggingface.co/Qwen/Qwen3-4B-Instruct-2507), and an inference/eval CLI. See [`training/README.md`](training/README.md) for the data policy and hardware notes.

## Contributing

Issues and pull requests are welcome. Please keep contributions consistent with the product principles above: possibilities over verdicts, visible uncertainty, and privacy-first defaults. Do not open issues containing real private conversations.

## License

[MIT](LICENSE)

## A possible interpretation schema

```json
{
  "literalMeaning": "What the words say on their face",
  "possibleImpliedMeanings": ["At least one alternative", "Another plausible reading"],
  "possibleEmotions": ["Use cautious descriptors, not a diagnosis"],
  "speechAct": "What the message may be doing in the conversation",
  "literalness": "literal | possibly-nonliteral | unclear",
  "confidence": 0,
  "evidence": ["Contextual cues actually used"],
  "missingContext": ["What would change the reading"],
  "suggestedAction": "A reversible, low-pressure next step"
}
```

The schema is intentionally about **pragmatic interpretation** rather than a single emotion class. The most important field is still uncertainty.
