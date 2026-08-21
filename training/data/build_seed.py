#!/usr/bin/env python3
"""Generate the Between seed dataset (training/data/seed.jsonl).

Each example is a hand-authored, synthetic conversation fixture with a
calibrated interpretation. No real conversations are used. The examples
deliberately include literal messages so the model learns not to over-flag.

Run:  python3 training/data/build_seed.py
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import build_messages  # noqa: E402


def ex(context, author, text, **analysis):
    return {"context": context, "author": author, "text": text, "analysis": analysis}


EXAMPLES = [
    # --- irony / sarcasm -------------------------------------------------
    ex(
        [("Maya", "I thought you were going to tell me if the time changed."),
         ("You", "I only found out this morning.")],
        "Maya", "Wow thanks for telling me 🙃",
        literalMeaning="Maya is thanking you for telling her about the change.",
        possibleImpliedMeanings=[
            "She may be pointing out that the update came too late and expressing frustration.",
            "If teasing is normal between you, this could be playful rather than a serious complaint.",
        ],
        possibleEmotions=["frustrated", "disappointed", "possibly playful"],
        speechAct="Calling attention to a late update",
        literalness="possibly-nonliteral",
        confidence=0.72,
        evidence=[
            "Positive wording ('wow thanks') conflicts with the preceding complaint.",
            "The upside-down emoji often signals irony, though it can also be playful.",
        ],
        missingContext=["Whether teasing is normal in this relationship", "How much the changed plan mattered to Maya"],
        suggestedAction="Acknowledge the late notice instead of debating whether the sarcasm is real.",
        suggestedMessage="You're right — I should have told you sooner. Sorry about that.",
    ),
    ex(
        [("Alex", "my car broke down on the freeway"),
         ("You", "oh no, are you ok?"),
         ("Alex", "just got towed. $300 later…")],
        "Alex", "Great. Just great 🙃",
        literalMeaning="Alex is saying the situation is great.",
        possibleImpliedMeanings=[
            "Venting frustration — 'great' is ironic given the breakdown and towing cost.",
            "Possibly self-mocking humor to cope, rather than anger directed at you.",
        ],
        possibleEmotions=["frustrated", "stressed", "possibly self-deprecating"],
        speechAct="Venting about a bad situation",
        literalness="possibly-nonliteral",
        confidence=0.78,
        evidence=[
            "'Great' clashes sharply with the events described.",
            "The upside-down emoji reinforces an ironic reading after a costly mishap.",
        ],
        missingContext=["Whether Alex tends to joke when stressed"],
        suggestedAction="Respond to the stress, not to the word 'great'.",
        suggestedMessage="That sounds awful — anything I can do from here?",
    ),
    ex(
        [("Sam", "sorry i double-booked us again"),
         ("You", "again?")],
        "Sam", "Sure, because that's exactly what I needed today 🙃",
        literalMeaning="Sam is glad this happened today.",
        possibleImpliedMeanings=[
            "Ironic complaint: the double-booking added unwanted stress to an already hard day.",
            "A gentle jab implying your 'again?' came out sharper than you intended.",
        ],
        possibleEmotions=["annoyed", "embarrassed", "possibly hurt"],
        speechAct="Ironic complaint with a mild rebuke",
        literalness="possibly-nonliteral",
        confidence=0.70,
        evidence=[
            "'Exactly what I needed' is a common ironic formula after setbacks.",
            "The upside-down emoji plus your pointed 'again?' suggests mixed annoyance and embarrassment.",
        ],
        missingContext=["How Sam usually responds to being called out"],
        suggestedAction="Soften your own tone and acknowledge the slip before moving on.",
        suggestedMessage="Sorry — that came out sharper than I meant. Rough day?",
    ),
    ex(
        [("Riley", "are we still on for friday?"),
         ("You", "(no reply for three days)"),
         ("You", "so sorry for the slow reply!")],
        "Riley", "Oh wow, you finally replied.",
        literalMeaning="Riley is noting that you replied.",
        possibleImpliedMeanings=[
            "Mild reproach about the three-day silence.",
            "Light teasing, depending on your usual dynamic.",
        ],
        possibleEmotions=["mildly hurt", "impatient", "possibly playful"],
        speechAct="Calling out a delayed response",
        literalness="possibly-nonliteral",
        confidence=0.65,
        evidence=[
            "'Finally' implies the wait was noticed and felt longer than expected.",
            "'Oh wow' adds emphasis typical of pointed remarks.",
        ],
        missingContext=["Whether Riley jokes like this normally", "Whether Friday plans were time-sensitive"],
        suggestedAction="Acknowledge the delay briefly, then answer the actual question.",
        suggestedMessage="Fair — I dropped the ball. Yes, Friday still works!",
    ),
    ex(
        [("Jordan", "wanna grab dinner tomorrow?"),
         ("You", "ah sorry, swamped this week")],
        "Jordan", "I guess you were too busy again.",
        literalMeaning="Jordan observes that you are busy again.",
        possibleImpliedMeanings=[
            "Hurt that rescheduling feels like a pattern rather than a one-off.",
            "A guilt-signaling framing that asks for reassurance more than explanation.",
        ],
        possibleEmotions=["hurt", "disappointed", "possibly resentful"],
        speechAct="Expressing hurt through accusation",
        literalness="possibly-nonliteral",
        confidence=0.60,
        evidence=[
            "'Again' frames this as a repeated pattern, not just this week.",
            "Accusatory phrasing after canceled plans often signals an unmet need for connection.",
        ],
        missingContext=["How many plans have actually been canceled", "How directly Jordan usually speaks"],
        suggestedAction="Address the feeling and propose something concrete rather than defending yourself.",
        suggestedMessage="You're right, I've been flaky lately. Tuesday dinner, my treat?",
    ),

    # --- indirect requests ------------------------------------------------
    ex(
        [("Priya", "(arrives at your place and sits down)")],
        "Priya", "I'm so thirsty",
        literalMeaning="Priya states that she is thirsty.",
        possibleImpliedMeanings=[
            "Likely an indirect request for something to drink.",
            "Simple small talk with no expectation — possible but less likely from a guest.",
        ],
        possibleEmotions=["neutral", "mildly uncomfortable"],
        speechAct="Indirect request",
        literalness="possibly-nonliteral",
        confidence=0.75,
        evidence=[
            "Guests rarely announce thirst idly; stating a need to a host conventionally requests action.",
            "No other topic is active that would make this purely informational.",
        ],
        missingContext=["Whether drinks were already offered and declined"],
        suggestedAction="Offer a drink directly — no decoding needed beyond that.",
        suggestedMessage="Water, tea, coffee?",
    ),
    ex(
        [("You", "make yourself at home!")],
        "Guest", "It's freezing in here.",
        literalMeaning="The guest reports that the room is cold.",
        possibleImpliedMeanings=[
            "Polite indirect request to close a window or turn up the heat.",
            "A plain observation — possible, but guests usually expect the host to act.",
        ],
        possibleEmotions=["cold", "uncomfortable", "neutral"],
        speechAct="Indirect request about comfort",
        literalness="possibly-nonliteral",
        confidence=0.70,
        evidence=[
            "Stating discomfort in someone else's home conventionally prompts the host to fix it.",
            "'Freezing' intensifies beyond neutral description.",
        ],
        missingContext=["Whether a window is visibly open", "Whether the guest knows where the thermostat is"],
        suggestedAction="Adjust the temperature and confirm comfort.",
        suggestedMessage="Let me close that window — better?",
    ),
    ex(
        [("Roommate", "The trash is getting pretty full.")],
        "Roommate", "Just saying.",
        literalMeaning="The roommate adds that they are merely making an observation.",
        possibleImpliedMeanings=[
            "An indirect request for you to take the trash out.",
            "A reminder tied to your agreed chore split, possibly with mild irritation.",
        ],
        possibleEmotions=["neutral", "mildly annoyed"],
        speechAct="Indirect request / chore reminder",
        literalness="possibly-nonliteral",
        confidence=0.80,
        evidence=[
            "Housemates rarely report bin status out of interest; it typically delegates action.",
            "'Pretty full' hedges a nudge to avoid sounding demanding.",
        ],
        missingContext=["Whose turn it is this week"],
        suggestedAction="Either take it out or make the arrangement explicit instead of debating the hint.",
        suggestedMessage="My turn, I've got it.",
    ),

    # --- permission / ambiguity -------------------------------------------
    ex(
        [("Maya", "I don't know if I want to go anymore."),
         ("You", "I can stay home if you'd rather.")],
        "Maya", "Do whatever you want.",
        literalMeaning="Maya says you are free to choose.",
        possibleImpliedMeanings=[
            "Genuine flexibility — she may be fine either way.",
            "Frustrated withdrawal: handing the decision back to avoid more negotiation.",
        ],
        possibleEmotions=["neutral", "possibly frustrated", "resigned"],
        speechAct="Returning the decision to you",
        literalness="unclear",
        confidence=0.55,
        evidence=[
            "It follows her own expressed ambivalence, so plain permission is plausible.",
            "Short, flat phrasing can signal reluctance to keep negotiating.",
        ],
        missingContext=["Her energy level right now", "Whether she tends to withdraw when upset"],
        suggestedAction="Ask one specific, low-pressure question instead of guessing.",
        suggestedMessage="Do you want me to come, or would space feel better?",
    ),
    ex(
        [("Dana", "movie night at mine saturday?"),
         ("You", "maybe! who's going?")],
        "Dana", "Yeah, you can come if you want.",
        literalMeaning="Attendance is permitted and optional.",
        possibleImpliedMeanings=[
            "A relaxed open invite with no pressure attached.",
            "Slight cooling after you asked who else was coming — 'if you want' may hedge enthusiasm.",
        ],
        possibleEmotions=["neutral", "possibly lukewarm"],
        speechAct="Hedged invitation",
        literalness="unclear",
        confidence=0.50,
        evidence=[
            "'If you want' marks optionality, which can read as relaxed or distancing.",
            "Your question about attendees may have sounded like evaluating the guest list.",
        ],
        missingContext=["How Dana usually phrases invites", "Whether Dana keeps details vague with everyone"],
        suggestedAction="Decide based on your own interest; if worried, confirm simply without over-reading.",
        suggestedMessage="Count me in!",
    ),
    ex(
        [("You", "would you be ok presenting our project thursday?")],
        "Kai", "sure lol",
        literalMeaning="Kai agrees to present on Thursday.",
        possibleImpliedMeanings=[
            "Casual genuine agreement — 'lol' softens formality among peers.",
            "Less likely: nervous laughter masking reluctance about public speaking.",
        ],
        possibleEmotions=["easygoing", "possibly nervous"],
        speechAct="Agreement (hedged)",
        literalness="unclear",
        confidence=0.45,
        evidence=[
            "The agreement word comes first, supporting a real yes.",
            "'lol' commonly marks casual tone rather than dismissal in peer chat.",
        ],
        missingContext=["Kai's comfort with presenting", "Whether 'lol' is a constant verbal habit for Kai"],
        suggestedAction="Treat it as a yes, and offer an easy out once.",
        suggestedMessage="Awesome — happy to swap if Thursday gets hairy.",
    ),
    ex(
        [("You", "italian or thai tonight?")],
        "Noor", "Up to you :)",
        literalMeaning="Noor delegates the dinner choice to you.",
        possibleImpliedMeanings=[
            "Genuinely flexible preference.",
            "Polite deferral hiding a mild preference — possible, but there are no markers of that here.",
        ],
        possibleEmotions=["content", "relaxed"],
        speechAct="Warmly delegating a choice",
        literalness="literal",
        confidence=0.80,
        evidence=[
            "The smiley supports friendly flexibility.",
            "There is no preceding conflict that would make deferral loaded.",
        ],
        missingContext=[],
        suggestedAction="Just pick and confirm — no hidden meaning needs decoding.",
        suggestedMessage="Thai it is — 7pm?",
    ),

    # --- soft rejection / boundaries ---------------------------------------
    ex(
        [("You", "I can change the plan if this isn't working."),
         ("Maya", "I don't want to make this a whole thing.")],
        "Maya", "It's fine.",
        literalMeaning="Maya says the situation is acceptable.",
        possibleImpliedMeanings=[
            "De-escalation: she wants the topic closed, though feelings may remain.",
            "Genuine reassurance that it truly is fine.",
        ],
        possibleEmotions=["possibly disappointed", "tired", "neutral"],
        speechAct="Closing or de-escalating the conversation",
        literalness="unclear",
        confidence=0.49,
        evidence=[
            "The preceding message signals limited capacity for a bigger discussion, not resolution.",
            "Minimal elaboration keeps both readings open.",
        ],
        missingContext=["Whether she raises it again later", "Her baseline expressiveness"],
        suggestedAction="Accept the pause and leave the door open without pressing.",
        suggestedMessage="Okay — here if you ever do want to talk.",
    ),
    ex(
        [("You", "come to the party saturday?")],
        "Eli", "Maybe another time! 😊",
        literalMeaning="Eli declines this Saturday and vaguely references the future.",
        possibleImpliedMeanings=[
            "A polite soft no with no firm intention to reschedule (a common reading).",
            "Genuine interest blocked by a real scheduling conflict.",
        ],
        possibleEmotions=["friendly", "avoidant"],
        speechAct="Soft rejection",
        literalness="possibly-nonliteral",
        confidence=0.60,
        evidence=[
            "Vague future reference without proposing a date typically softens refusal.",
            "The warm emoji reduces chance of offense but not likelihood of refusal.",
        ],
        missingContext=["Whether Eli follows up later with a concrete alternative"],
        suggestedAction="Accept gracefully and let Eli initiate next time.",
        suggestedMessage="No problem — next one then!",
    ),
    ex(
        [("You", "still good for the hike sunday?")],
        "Sam", "I'll let you know.",
        literalMeaning="Sam will confirm later.",
        possibleImpliedMeanings=[
            "Likely a soft decline — commitment is being avoided.",
            "Genuine uncertainty about weekend availability.",
        ],
        possibleEmotions=["noncommittal", "possibly reluctant"],
        speechAct="Deferring (probable soft no)",
        literalness="possibly-nonliteral",
        confidence=0.55,
        evidence=[
            "A direct question met with deferral often signals reluctance.",
            "No counter-proposal or alternative time is offered.",
        ],
        missingContext=["Sam's actual schedule constraints", "The pattern across previous invites"],
        suggestedAction="Give space; propose an alternative only if attending matters to you.",
        suggestedMessage="Sure — just ping me Saturday night.",
    ),
    ex(
        [("You", "could you review my draft this week?")],
        "Theo", "Hmm, I'm pretty slammed this week.",
        literalMeaning="Theo says he is very busy this week.",
        possibleImpliedMeanings=[
            "A soft no — declining without refusing outright.",
            "A real time crunch; he might accept a much smaller ask.",
        ],
        possibleEmotions=["stressed", "apologetic-leaning"],
        speechAct="Soft refusal",
        literalness="possibly-nonliteral",
        confidence=0.70,
        evidence=[
            "The hedge 'Hmm' plus vague 'slammed' typically preface declines.",
            "No alternative time is offered.",
        ],
        missingContext=["How urgent the review is", "Whether Theo owes you a reciprocal favor"],
        suggestedAction="Relieve the pressure and offer a smaller ask or later deadline.",
        suggestedMessage="Totally get it — even two bullet comments would help, or next week?",
    ),
    ex(
        [("You", "can we talk about what happened yesterday?")],
        "Maya", "I don't really want to talk about it right now.",
        literalMeaning="Maya declines to have the conversation right now.",
        possibleImpliedMeanings=[
            "A boundary, likely temporary — respect it without assuming lasting anger.",
            "She may need processing time before discussing it.",
        ],
        possibleEmotions=["overwhelmed", "guarded", "possibly upset"],
        speechAct="Setting a boundary",
        literalness="literal",
        confidence=0.80,
        evidence=[
            "The statement is explicit and leaves little interpretive doubt.",
            "'Right now' scopes the refusal to this moment, not forever.",
        ],
        missingContext=["Whether she wants space or a check-in later"],
        suggestedAction="Honor the boundary and name your availability without pressing.",
        suggestedMessage="Understood. I'm around whenever you're ready.",
    ),

    # --- playful / teasing --------------------------------------------------
    ex(
        [("You", "my dog ate the ethernet cable, no wifi 😅")],
        "Casey", "Oh sure, blame the dog 🐶😂",
        literalMeaning="Casey jokingly comments on you blaming the dog.",
        possibleImpliedMeanings=[
            "Playful teasing — a shared joke with no criticism intended.",
            "Very slight skepticism of the excuse, wrapped in humor.",
        ],
        possibleEmotions=["amused", "affectionate"],
        speechAct="Teasing / rapport-building",
        literalness="possibly-nonliteral",
        confidence=0.70,
        evidence=[
            "The dog and laughing emojis frame the reply as banter.",
            "Echoing your excuse back is classic playful mirroring.",
        ],
        missingContext=["Inside jokes about that dog"],
        suggestedAction="Play along — no repair is needed.",
        suggestedMessage="He shows no remorse.",
    ),
    ex(
        [("You", "i think pineapple belongs on pizza 🍍")],
        "Morgan", "You WOULD say that 😄",
        literalMeaning="Morgan links your opinion to your character in a mock-exasperated way.",
        possibleImpliedMeanings=[
            "Affectionate teasing about a known quirk of yours.",
            "Light disagreement signaled through performed outrage rather than argument.",
        ],
        possibleEmotions=["amused", "fond"],
        speechAct="Banter / mock exasperation",
        literalness="possibly-nonliteral",
        confidence=0.65,
        evidence=[
            "Capital letters plus the laughing emoji perform exaggerated outrage typical of jokes.",
            "'Would' implies familiarity, i.e., established rapport.",
        ],
        missingContext=["Whether Morgan actually minds the pineapple debate"],
        suggestedAction="Banter back; nothing needs clarifying.",
        suggestedMessage="Correct. Pineapple supremacy.",
    ),

    # --- literal / genuine (negative examples) ------------------------------
    ex(
        [("You", "(helped Sam move all day)")],
        "Sam", "Thanks so much for today!! Genuinely a lifesaver 💛",
        literalMeaning="Sam expresses sincere gratitude for your help.",
        possibleImpliedMeanings=[
            "Just thanks — there is no hidden layer worth surfacing.",
            "Mild awareness of imposing, so warm reassurance would land well.",
        ],
        possibleEmotions=["grateful", "warm"],
        speechAct="Sincere thanks",
        literalness="literal",
        confidence=0.88,
        evidence=[
            "Specific wording, doubled punctuation, and a heart emoji align with sincerity.",
            "It follows a concrete favor completed the same day.",
        ],
        missingContext=[],
        suggestedAction="Receive it plainly — no decoding needed.",
        suggestedMessage="Anytime! Pizza next weekend on me.",
    ),
    ex(
        [("You", "meeting tuesday 10am?")],
        "Ana", "That works for me 👍",
        literalMeaning="Ana confirms the proposed meeting time.",
        possibleImpliedMeanings=[
            "Plain confirmation.",
            "Reluctant acceptance — unlikely; there are no markers of reluctance.",
        ],
        possibleEmotions=["neutral-positive"],
        speechAct="Confirmation",
        literalness="literal",
        confidence=0.85,
        evidence=[
            "Standard scheduling formula plus a thumbs-up.",
            "No hedging words are present.",
        ],
        missingContext=[],
        suggestedAction="Lock it in.",
        suggestedMessage="Booked — calendar invite sent.",
    ),
    ex(
        [("You", "what time are you coming over?")],
        "Ben", "I'll be there at 6.",
        literalMeaning="Ben states his arrival time.",
        possibleImpliedMeanings=["None beyond logistics."],
        possibleEmotions=["neutral"],
        speechAct="Information / commitment",
        literalness="literal",
        confidence=0.90,
        evidence=[
            "A plain declarative answering a direct question.",
            "No tonal markers are present.",
        ],
        missingContext=[],
        suggestedAction="Treat as straightforward; no clarification needed.",
        suggestedMessage=None,
    ),
    ex(
        [("You", "presented the quarterly numbers today")],
        "Jules", "You looked good today 😉",
        literalMeaning="Jules compliments how you came across today.",
        possibleImpliedMeanings=[
            "Possible flirtation — the wink adds personal charge beyond workplace praise.",
            "Supportive colleague complimenting your composure during the presentation.",
        ],
        possibleEmotions=["friendly", "possibly flirtatious"],
        speechAct="Compliment (ambiguous register)",
        literalness="unclear",
        confidence=0.45,
        evidence=[
            "The wink pushes past neutral workplace praise.",
            "Timing right after your presentation supports the performance-compliment reading.",
        ],
        missingContext=["How Jules talks to other teammates", "Your workplace norms about such messages"],
        suggestedAction="Keep the response warm and neutral; you do not need to resolve the ambiguity now.",
        suggestedMessage="Thanks! Glad the numbers landed.",
    ),

    # --- indirect disappointment ---------------------------------------------
    ex(
        [("You", "can't make friday anymore, sorry")],
        "Alex", "Oh. Okay then.",
        literalMeaning="Alex acknowledges the cancellation.",
        possibleImpliedMeanings=[
            "Disappointment or withdrawal — the flat minimal reply follows canceled plans.",
            "Simple acknowledgment with no feelings attached — less likely given the brevity contrast.",
        ],
        possibleEmotions=["disappointed", "hurt", "withdrawn"],
        speechAct="Expressing disappointment indirectly",
        literalness="possibly-nonliteral",
        confidence=0.60,
        evidence=[
            "Period-punctuated fragments convey flatness in texting norms.",
            "Abrupt brevity after bad news often signals an unspoken reaction.",
        ],
        missingContext=["Alex's usual texting punctuation", "How much Friday mattered to Alex"],
        suggestedAction="Acknowledge the impact and offer an alternative.",
        suggestedMessage="I'm sorry to bail — does next Friday work instead?",
    ),
]


def main():
    rows = []
    for item in EXAMPLES:
        rows.append({
            "messages": build_messages(item["context"], item["author"], item["text"])
                        + [{"role": "assistant", "content": json.dumps(item["analysis"], ensure_ascii=False)}],
        })

    out = Path(__file__).resolve().parent / "seed.jsonl"
    out.write_text("\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n", encoding="utf-8")

    counts = {}
    for row in rows:
        key = json.loads(row["messages"][2]["content"])["literalness"]
        counts[key] = counts.get(key, 0) + 1
    print(f"wrote {len(rows)} examples to {out}")
    print(f"literalness distribution: {counts}")


if __name__ == "__main__":
    main()
