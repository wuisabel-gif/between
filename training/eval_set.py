"""Canonical held-out evaluation set for Between base models.

Mirrored inside notebooks/kaggle_eval.py (which must stay self-contained for
Kaggle pasting). If you add or change scenarios here, update that copy too.

All conversations are synthetic. Never replace them with real messages.
"""

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

# Scenarios where the literal reading should dominate; a good model should NOT
# flag these as possibly-nonliteral.
EXPECT_LITERAL = {"early_coworker", "see_you_8", "send_notes"}
