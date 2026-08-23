# Between

**Between** is an experimental communication aid that helps autistic and neurodivergent users make sense of ambiguous digital messages.

Instead of trying to *detect someone's emotion* or decide what a message "really means," Between gives the user a structured second look at a conversation: **what the words literally say, what else they might imply, which contextual cues support those interpretations, and how uncertain those interpretations are.**

For example, a message like:

> **“Wow, thanks for telling me 🙃”**

could be sincere, sarcastic, disappointed, playful, or something else entirely. Between keeps multiple interpretations visible rather than collapsing them into a single label.

The goal is not to replace a user's judgment. It is to make hidden social and pragmatic cues easier to inspect.

> **Between is an optional thinking aid, not a mind reader.** It does not diagnose people, determine someone's true intentions, or provide clinical advice.

## Try it

**Live demo:** https://wuisabel-gif.github.io/between/

The current prototype includes three contextual examples:

- “Wow thanks for telling me 🙃”
- “Do whatever you want.”
- “It’s fine.”

You can also enter your own message and experiment with the interpretation interface.

## What Between shows

Rather than returning a single emotion label, Between breaks an ambiguous message into several dimensions:

**Literal meaning**  
What the words say directly.

**Possible implied meanings**  
Other plausible interpretations given the surrounding conversation.

**Possible emotions**  
Emotional readings that *might* fit, presented as possibilities rather than facts.

**Speech act**  
What the message may be doing conversationally—for example, agreeing, declining, expressing frustration, joking, or indirectly requesting something.

**Literalness**  
Whether the message appears literal, possibly nonliteral, or unclear.

**Evidence**  
The specific contextual cues that contributed to an interpretation.

**Missing context**  
Information that could substantially change the interpretation.

**Confidence**  
How strongly the available context supports the reading.

**Suggested next step**  
A reversible, low-pressure response, often involving clarification rather than assuming the interpretation is correct.

## Why not just detect emotion?

Digital communication is rarely a simple classification problem.

Consider:

> “It’s fine.”

Depending on the conversation, this could mean:

- everything is genuinely okay;
- the person is disappointed but does not want to continue discussing it;
- reluctant acceptance;
- frustration;
- reassurance;
- or simply exactly what the words say.

An emotion classifier might return **“negative”** or **“frustrated.”**

Between instead asks:

> **What are the plausible readings, what evidence supports them, and how certain can we reasonably be?**

That distinction is central to the project.

## Design principles

### Possibilities, not verdicts

Between should never present an inferred intention or emotion as a fact about another person.

Multiple interpretations remain visible when the evidence is ambiguous.

### Context before labels

Meaning often depends on what happened before a message.

Between therefore shows the context used to generate an interpretation instead of presenting an isolated emotion label.

Context is treated as **evidence, not proof**.

### Ask before assuming

When uncertainty remains, asking the other person is usually more reliable than trusting an AI interpretation.

Suggested responses therefore favor low-pressure clarification:

> “Just checking—did you mean that literally, or are you frustrated with what happened?”

The interpretation helps the user decide what to ask; it does not replace the conversation.

### User control

Between is intended to be activated by the person receiving the message.

It is not designed to automatically monitor conversations or silently analyze other people.

### Privacy by default

A future version of Between should:

- read the minimum conversation context necessary;
- show exactly what context is being analyzed;
- avoid retaining conversations by default;
- never train on private messages without explicit consent;
- support local processing where practical;
- make automatic analysis opt-in;
- clearly expose the model/provider being used;
- allow the interpretation layer to be disabled at any time.

The current static prototype keeps fixture data and custom text inside the page. Only display settings are stored in `localStorage`. Messages are not stored or sent to a model provider.

## Current prototype

The first version includes:

- contextual conversation examples;
- an interactive message view;
- literal and implied interpretations;
- possible emotion and speech-act descriptions;
- uncertainty/confidence indicators;
- evidence from surrounding context;
- suggested clarification strategies;
- a custom-message input;
- a deterministic local heuristic for custom messages;
- configurable context length and analysis modes;
- click-to-analyze controls;
- responsive layout;
- keyboard-accessible interactions;
- semantic headings and labels;
- reduced-motion support.

The custom-message analyzer is intentionally simple. It uses transparent local heuristics and **does not claim to infer a person's actual intent**.

## Interpretation schema

Between is built around a structured pragmatic interpretation rather than an emotion class.

```json
{
  "literalMeaning": "What the words say on their face",
  "possibleImpliedMeanings": [
    "One plausible interpretation",
    "Another plausible interpretation"
  ],
  "possibleEmotions": [
    "Cautious emotional descriptors"
  ],
  "speechAct": "What the message may be doing conversationally",
  "literalness": "literal | possibly-nonliteral | unclear",
  "confidence": 0,
  "evidence": [
    "Contextual cues actually used"
  ],
  "missingContext": [
    "Information that could change the interpretation"
  ],
  "suggestedAction": "A reversible, low-pressure next step"
}
```

The most important part of the schema is not the predicted emotion.

It is **uncertainty**.

## Research direction

Between is also an HCI/NLP research prototype exploring a broader question:

> **Can language models help users inspect pragmatic and contextual meaning without encouraging them to over-trust the model's interpretation?**

Future evaluation should therefore measure more than classification accuracy.

Useful outcomes include:

- interpretation accuracy;
- confidence calibration;
- cognitive load;
- time required to understand a message;
- user trust;
- preference;
- perceived usefulness;
- whether users become more comfortable asking for clarification;
- and whether displaying uncertainty reduces inappropriate reliance on the model.

A future study could compare:

1. no assistance;
2. emotion classification only;
3. Between-style contextual interpretation.

## Model training

The [`training/`](training/) directory contains an experimental fine-tuning pipeline for exploring model-based interpretation.

It currently includes:

- a shared interpretation/prompt contract;
- a synthetic seed dataset generator;
- dataset validation;
- TRL-based training;
- LoRA/QLoRA support;
- an inference/evaluation CLI;
- and experiments targeting [`Qwen/Qwen3-4B-Instruct-2507`](https://huggingface.co/Qwen/Qwen3-4B-Instruct-2507).

See [`training/README.md`](training/README.md) for the training setup, data policy, and hardware notes.

The training scaffold is experimental and is **not** evidence that the model has been validated for real-world interpretation.

## Roadmap

### 1. Co-design with autistic users

Work with autistic adults and other neurodivergent users to determine which concepts are actually useful and whether terms such as *speech act*, *literal meaning*, and *possible emotion* should be simplified or replaced.

### 2. Build a privacy-preserving extension

Prototype a browser extension with explicit click-to-analyze behavior and a visible preview of the context being shared.

### 3. Connect a language model

Compare:

- local models;
- user-controlled model providers;
- and carefully scoped hosted inference.

The UI should always expose which provider receives the context and what its retention policy is.

### 4. Evaluate uncertainty

Test not only whether interpretations are correct, but whether the model knows when it **doesn't have enough information**.

### 5. Pilot a messaging surface

Discord Web is one possible research environment, although a controlled messaging mock-up or extension test surface should come first.

## Run locally

Clone the repository and serve it with any static HTTP server:

```bash
git clone https://github.com/wuisabel-gif/between.git
cd between
python3 -m http.server 4173
```

Then open:

```text
http://127.0.0.1:4173
```

To run the JavaScript syntax check:

```bash
npm run check
```

The prototype can also be opened directly through `index.html`, although using a local server more closely matches the browser-origin behavior needed for a future extension.

## What Between is not

Between is currently a **product and research prototype**, not a validated interpretation system.

It should not be used to make high-stakes judgments involving safety, consent, employment, relationships, medical decisions, or diagnosis.

The current version does not include:

- automatic monitoring of conversations;
- a Discord bot;
- a production browser extension;
- a server-side interpretation model;
- identity or relationship profiling;
- claims of clinical efficacy;
- claims that inferred emotions or intentions are objectively correct.

## Contributing

Issues and pull requests are welcome.

Contributions should follow three core principles:

**possibilities over verdicts, uncertainty over false confidence, and user control over automatic analysis.**

Please do not include real private conversations in issues, examples, datasets, or pull requests.

## License

[MIT](LICENSE)
