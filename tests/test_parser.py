from src.parser import parse_forced_choice, parse_indifference, parse_strength, parse_response, canonicalize_choice

def test_forced_choice_parsing():
    assert parse_forced_choice("A")["raw_choice"] == "A"
    assert parse_forced_choice("**B**")["raw_choice"] == "B"
    assert parse_forced_choice("Option A")["raw_choice"] == "A"
    assert parse_forced_choice("Invalid response")["valid"] is False

def test_indifference_parsing():
    assert parse_indifference("INDIFFERENT")["indifferent"] is True
    assert parse_indifference("I have no strong preference")["indifferent"] is True
    assert parse_indifference("A")["raw_choice"] == "A"
    assert parse_indifference("A")["indifferent"] is False

def test_strength_parsing():
    r1 = parse_strength("CHOICE: B\nSTRENGTH: 4")
    assert r1["raw_choice"] == "B" and r1["strength"] == 4
    
    r2 = parse_strength("Option A, Strength: 5")
    assert r2["raw_choice"] == "A" and r2["strength"] == 5

def test_canonical_normalization():
    # In original ordering: Presented A -> Canonical A, Presented B -> Canonical B
    assert canonicalize_choice("A", "original") == "A"
    assert canonicalize_choice("B", "original") == "B"
    assert canonicalize_choice("INDIFFERENT", "original") == "INDIFFERENT"

    # In flipped ordering: Presented A -> Canonical B, Presented B -> Canonical A
    assert canonicalize_choice("A", "flipped") == "B"
    assert canonicalize_choice("B", "flipped") == "A"
    assert canonicalize_choice("INDIFFERENT", "flipped") == "INDIFFERENT"

def test_parse_response_integration():
    res_orig = parse_response("forced_choice", "A", ordering="original")
    assert res_orig["raw_choice"] == "A" and res_orig["canonical_choice"] == "A"

    res_flip = parse_response("forced_choice", "A", ordering="flipped")
    assert res_flip["raw_choice"] == "A" and res_flip["canonical_choice"] == "B"

