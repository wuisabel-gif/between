"""Shared helpers for Between training: system prompt, prompt building, validation.

Every script in training/ imports from here so the prompt, the user-message
format, and the output contract stay identical across dataset construction,
fine-tuning, and inference.
"""

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
    "literalMeaning",
    "possibleImpliedMeanings",
    "possibleEmotions",
    "speechAct",
    "literalness",
    "confidence",
    "evidence",
    "missingContext",
    "suggestedAction",
    "suggestedMessage",
)

LITERALNESS_VALUES = {"literal", "possibly-nonliteral", "unclear"}


def user_content(context, target_author, target_text):
    """Build the user turn: minimal context, the target message, the instruction."""
    context = list(context or [])
    lines = []
    if context:
        lines.append("Conversation context (oldest first):")
        lines.extend(f"{author}: {text}" for author, text in context)
    else:
        lines.append("Conversation context: (none provided)")
    lines += [
        "",
        f"Target message (from {target_author}):",
        target_text,
        "",
        "Interpret the target message for the reader. Reply with the JSON object only.",
    ]
    return "\n".join(lines)


def build_messages(context, target_author, target_text):
    """Return the chat-messages list expected by apply_chat_template / TRL."""
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_content(context, target_author, target_text)},
    ]


def strip_code_fences(text):
    """Remove markdown code fences if a model wraps its JSON anyway."""
    t = (text or "").strip()
    if t.startswith("```"):
        t = t.strip("`")
        first_newline = t.find("\n")
        if first_newline != -1 and t[:first_newline].strip().lower() in ("", "json"):
            t = t[first_newline + 1:]
        closing = t.rfind("```")
        if closing != -1:
            t = t[:closing]
    return t.strip()


def validate_interpretation(obj):
    """Validate one interpretation object; return a list of problems (empty = ok)."""
    errors = []
    if not isinstance(obj, dict):
        return ["interpretation must be a JSON object"]
    for key in REQUIRED_KEYS:
        if key not in obj:
            errors.append(f"missing key: {key}")

    literalness = obj.get("literalness")
    if literalness is not None and literalness not in LITERALNESS_VALUES:
        errors.append(f"literalness must be one of {sorted(LITERALNESS_VALUES)}")

    confidence = obj.get("confidence")
    if confidence is not None and not (isinstance(confidence, (int, float)) and 0 <= confidence <= 1):
        errors.append("confidence must be a number in [0, 1]")

    for key, minimum in (("possibleImpliedMeanings", 1), ("possibleEmotions", 1), ("evidence", 1)):
        value = obj.get(key)
        if value is not None and not (
            isinstance(value, list)
            and len(value) >= minimum
            and all(isinstance(item, str) and item.strip() for item in value)
        ):
            errors.append(f"{key} must be a list of at least {minimum} non-empty strings")

    missing = obj.get("missingContext")
    if missing is not None and not (isinstance(missing, list) and all(isinstance(i, str) for i in missing)):
        errors.append("missingContext must be a list of strings")

    suggestion = obj.get("suggestedMessage")
    if suggestion is not None and not isinstance(suggestion, str):
        errors.append("suggestedMessage must be a string or null")

    for key in ("literalMeaning", "speechAct", "suggestedAction"):
        value = obj.get(key)
        if value is not None and not (isinstance(value, str) and value.strip()):
            errors.append(f"{key} must be a non-empty string")
    return errors
