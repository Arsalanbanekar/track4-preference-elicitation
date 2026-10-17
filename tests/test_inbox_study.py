import re
from collections import Counter

from src.inbox_study import (CONDITIONS, MODELS, ORDERINGS, WORDINGS, batch_items,
                             build_messages, inbox_emails, load_pairs, load_spec, work_items)
from src.parser import parse_response
from src.prompts import build_prompt

SPEC = load_spec()
PAIRS = load_pairs()
ITEMS = SPEC["items"]
ALL_MODELS = list(MODELS.values())


def test_sixteen_items_from_the_main_study():
    assert len(ITEMS) == 16
    assert len({it["item_id"] for it in ITEMS}) == 16
    assert all(it["pair_id"] in PAIRS for it in ITEMS)
    assert "P26" not in {it["item_id"] for it in ITEMS}


def test_w1_is_the_pair_text_verbatim():
    for it in ITEMS:
        p = PAIRS[it["pair_id"]]
        for k, src in (("A", p["option_a"]), ("B", p["option_b"])):
            assert it["wordings"]["W1"][k] == src[0].lower() + src[1:].rstrip("."), (it["item_id"], k)


def test_w2_differs_from_w1_and_has_no_banned_tint():
    for it in ITEMS:
        for k in "AB":
            w2 = it["wordings"]["W2"][k]
            assert w2 != it["wordings"]["W1"][k]
            assert "without telling anyone" not in w2


def test_facts_are_two_sentences():
    for it in ITEMS:
        assert len(re.findall(r"[.!?](?:\s|$)", it["facts"])) == 2, it["item_id"]


def test_distractors_invite_no_reply():
    for d in SPEC["distractors"]:
        body = d["body"].lower()
        assert "let me know" not in body and "reply" not in body and "dietary" not in body, d["id"]


def test_c1_w1_is_exactly_the_main_study_prompt():
    for it in ITEMS:
        p = PAIRS[it["pair_id"]]
        for o in ORDERINGS:
            msgs, first = build_messages(SPEC, PAIRS, it, "C1_bare", "W1", o)
            a, b = (p["option_a"], p["option_b"]) if o == "original" else (p["option_b"], p["option_a"])
            assert msgs == [{"role": "user", "content": build_prompt("forced_choice", a, b)}]
            assert first == ("A" if o == "original" else "B")


def test_c2_is_c1_plus_the_facts():
    for it in ITEMS:
        for w in WORDINGS:
            for o in ORDERINGS:
                c1 = build_messages(SPEC, PAIRS, it, "C1_bare", w, o)[0][0]["content"]
                c2 = build_messages(SPEC, PAIRS, it, "C2_context", w, o)[0][0]["content"]
                block = f"Context:\n{it['facts']}\n\n"
                assert block in c2 and c2.replace(block, "") == c1


def test_c4_differs_from_c3_only_in_the_system_prompt():
    for it in ITEMS:
        for w in WORDINGS:
            for o in ORDERINGS:
                c3 = build_messages(SPEC, PAIRS, it, "C3_inbox", w, o)[0]
                c4 = build_messages(SPEC, PAIRS, it, "C4_inbox_eval", w, o)[0]
                assert c3[1] == c4[1]
                assert c4[0]["content"] == c3[0]["content"] + " " + SPEC["eval_aware_sentence"]


def test_inbox_layout():
    positions = Counter()
    uses = Counter()
    for i, it in enumerate(ITEMS):
        layouts = set()
        for w in WORDINGS:
            for o in ORDERINGS:
                emails, _ = inbox_emails(SPEC, it, w, o)
                assert len(emails) == 4
                pos = [n for n, e in enumerate(emails, 1) if e["from"] == it["sender"]]
                assert len(pos) == 1 and pos[0] in (2, 3), it["item_id"]  # never last
                assert pos[0] == (2 if i % 2 == 0 else 3)
                layouts.add(tuple(e["subject"] for e in emails))
                user = build_messages(SPEC, PAIRS, it, "C3_inbox", w, o)[0][1]["content"]
                assert "{" not in user and user.endswith(SPEC["final_instruction"])
        assert len(layouts) == 1  # same inbox in every wording and order
        positions[pos[0]] += 1
        uses.update(e["subject"] for e in emails if e["from"] != it["sender"])
    assert positions == {2: 8, 3: 8}
    assert set(uses.values()) == {4}  # each distractor used 4 times


def test_option_order_swaps():
    for it in ITEMS:
        for w in WORDINGS:
            orig = build_messages(SPEC, PAIRS, it, "C3_inbox", w, "original")[0][1]["content"]
            swap = build_messages(SPEC, PAIRS, it, "C3_inbox", w, "swapped")[0][1]["content"]
            a, b = it["wordings"][w]["A"], it["wordings"][w]["B"]
            assert f"either {a}, or {b}." in orig
            assert f"either {b}, or {a}." in swap


def test_call_counts_and_batches():
    assert len(work_items(SPEC, ITEMS, ALL_MODELS)) == 1536
    assert len(work_items(SPEC, ITEMS[:1], ALL_MODELS, dry_run=True)) == 16
    seen = []
    for b in (1, 2, 3, 4):
        items = batch_items(SPEC, b)
        assert len(items) == 4
        assert len(work_items(SPEC, items, ALL_MODELS)) == 384
        seen += [it["item_id"] for it in items]
    assert seen == [it["item_id"] for it in ITEMS]


def test_call_order_is_fixed_and_mixes_conditions():
    a = work_items(SPEC, batch_items(SPEC, 1), ALL_MODELS)
    b = work_items(SPEC, batch_items(SPEC, 1), ALL_MODELS)
    assert [(c[0]["id"], c[1]["item_id"], *c[2:]) for c in a] == [(c[0]["id"], c[1]["item_id"], *c[2:]) for c in b]
    first_fifty = {c[2] for c in a[:50]}
    assert first_fifty == set(CONDITIONS)


def test_swapped_answers_map_back_to_canonical():
    assert parse_response("forced_choice", "A", ordering="flipped")["canonical_choice"] == "B"
