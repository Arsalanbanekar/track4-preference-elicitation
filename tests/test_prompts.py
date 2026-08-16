from src.prompts import build_prompt, flip_pair

def test_all_prompts():
    for m in ["forced_choice", "explicit_indifference", "preference_strength"]:
        p = build_prompt(m, "AAA", "BBB")
        assert "AAA" in p and "BBB" in p

def test_flip_pair():
    oa, ob = "Free time", "Money"
    fa, fb = flip_pair(oa, ob)
    assert fa == "Money" and fb == "Free time"

