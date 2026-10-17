import random

import numpy as np
import pandas as pd

from src.inbox_analysis import (LABELS, analyse, build_choices, cohen_kappa, export_for_labelling,
                                holm, load_labels, permutation_test)
from src.inbox_study import CONDITIONS, MODELS, ORDERINGS, WORDINGS, load_spec

SPEC = load_spec()


def _df(px, py, cells=40, reps=3, seed=0):
    rng = random.Random(seed)
    rows = []
    for c in range(cells):
        for cond, p in (("X", px), ("Y", py)):
            for _ in range(reps):
                rows.append({"cell": c, "condition": cond, "choice": "A" if rng.random() < p else "B"})
    return pd.DataFrame(rows)


def test_permutation_no_difference_is_not_significant():
    r = permutation_test(_df(0.5, 0.5), "condition", "X", "Y", ["cell"], ["A", "B"], n_perm=2000)
    assert r["p_value"] > 0.05 and r["cells"] == 40


def test_permutation_detects_a_large_difference():
    r = permutation_test(_df(0.9, 0.1), "condition", "X", "Y", ["cell"], ["A", "B"], n_perm=2000)
    assert r["p_value"] < 0.001


def test_permutation_is_direction_free():
    # Half the cells shift one way and half the other: a signed test would cancel out.
    a = _df(0.9, 0.1, cells=20, seed=1)
    b = _df(0.1, 0.9, cells=20, seed=2).assign(cell=lambda d: d.cell + 20)
    r = permutation_test(pd.concat([a, b]), "condition", "X", "Y", ["cell"], ["A", "B"], n_perm=2000)
    assert r["p_value"] < 0.001


def test_identical_choices_give_p_of_one():
    df = pd.DataFrame([{"cell": c, "condition": k, "choice": "A"} for c in range(5) for k in "XY" for _ in range(3)])
    assert permutation_test(df, "condition", "X", "Y", ["cell"], ["A", "B"], n_perm=500)["p_value"] == 1.0


def test_holm():
    assert np.allclose(holm(np.array([0.01, 0.04, 0.03])), [0.03, 0.06, 0.06])


def test_kappa():
    assert cohen_kappa(list("ABAB"), list("ABAB")) == 1.0
    assert cohen_kappa(list("AABB"), list("ABAB")) == 0.0


def _fake_records(seed=0):
    """A complete fake study: every cell, with plausible fields. No API involved."""
    rng = random.Random(seed)
    recs = []
    for m in MODELS.values():
        for it in SPEC["items"]:
            for c in CONDITIONS:
                for w in WORDINGS:
                    for o in ORDERINGS:
                        for rep in (1, 2, 3):
                            choice = rng.choice("AB")
                            rec = {"run_id": "fake", "model": m["id"], "item_id": it["item_id"],
                                   "pair_id": it["pair_id"], "condition": c, "wording": w, "ordering": o,
                                   "first_option": "A" if o == "original" else "B", "repetition": rep,
                                   "raw_response": f"Go with option {choice}.",
                                   "reasoning": "x" * rng.randint(100, 300) * (2 if c == "C4_inbox_eval" else 1),
                                   "finish_reason": "stop", "usage": {"completion_tokens": rng.randint(100, 900)}}
                            if c in ("C1_bare", "C2_context"):
                                rec["canonical_choice"] = choice
                            rec["_truth"] = choice
                            recs.append(rec)
    return recs


def test_labelling_round_trip(tmp_path):
    recs = _fake_records()
    n = export_for_labelling(recs, label_dir=tmp_path, spec=SPEC)
    assert n == 768
    sheet = (tmp_path / "to_label.md").read_text(encoding="utf-8")
    for hidden in ("C3_inbox", "C4_inbox_eval", "swapped", "gpt-oss", "qwen"):
        assert hidden not in sheet  # the labeller cannot see condition, order or model
    # Fill the labels from the hidden truth, as a perfect labeller would.
    key = pd.read_csv(tmp_path / "labelling_key.csv")
    truth = {(r["model"], r["item_id"], r["condition"], r["wording"], r["ordering"], r["repetition"]): r["_truth"]
             for r in recs}
    key["label"] = [truth[(k.model, k.item_id, k.condition, k.wording, k.ordering, k.repetition)]
                    for k in key.itertuples()]
    key[["label_id", "label"]].assign(note="").to_csv(tmp_path / "labels.csv", index=False)
    labels = load_labels(tmp_path)
    df = build_choices(recs, labels)
    merged = all(df.choice.tolist()[i] == r["_truth"] for i, r in enumerate(recs))
    assert merged and set(df.choice) <= set(LABELS)


def test_refuses_to_overwrite_labelling(tmp_path):
    recs = _fake_records()
    export_for_labelling(recs, label_dir=tmp_path, spec=SPEC)
    try:
        export_for_labelling(recs, label_dir=tmp_path, spec=SPEC)
        assert False, "should refuse"
    except SystemExit:
        pass


def test_full_analysis_runs_on_fake_data(tmp_path):
    recs = _fake_records()
    labels = {(r["model"], r["item_id"], r["condition"], r["wording"], r["ordering"], r["repetition"]): r["_truth"]
              for r in recs if r["condition"] in ("C3_inbox", "C4_inbox_eval")}
    primary = analyse(records=recs, labels=labels, out_dir=tmp_path, n_perm=200)
    assert len(primary) == 10
    # Random choices: no choice test should be significant after Holm.
    assert not primary[primary.question != "Q3 notice (deliberation)"].significant.any()
    # Reasoning doubled in C4 in the fake data: the deliberation tests should find it.
    assert primary[primary.question == "Q3 notice (deliberation)"].significant.all()
    for f in ("choices.csv", "primary_tests.csv", "positional_consistency.csv",
              "sensitivity_without_pilot_items.csv", "sensitivity_all_response_types.csv"):
        assert (tmp_path / f).exists()
