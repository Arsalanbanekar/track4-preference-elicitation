import re

def norm(text):
    return (text or "").strip().upper()

def canonicalize_choice(choice, ordering):
    if choice is None:
        return None
    if choice == "INDIFFERENT":
        return "INDIFFERENT"
    if choice not in {"A", "B"}:
        return None
    if ordering == "flipped":
        return "B" if choice == "A" else "A"
    return choice

def parse_forced_choice(text):
    raw = norm(text)
    # Check exact single token match or markdown wrapped token (e.g. **A**, Option A)
    if raw in {"A", "B", "**A**", "**B**"}:
        clean = "A" if "A" in raw else "B"
        return {"raw_choice": clean, "valid": True, "indifferent": False, "strength": None}
    
    # Check "OPTION A" or "OPTION B"
    opt_match = re.search(r"\bOPTION\s+([AB])\b", raw)
    if opt_match:
        return {"raw_choice": opt_match.group(1), "valid": True, "indifferent": False, "strength": None}

    matches = re.findall(r"\b([AB])\b", raw)
    if len(matches) == 1:
        return {"raw_choice": matches[0], "valid": True, "indifferent": False, "strength": None}
    return {"raw_choice": None, "valid": False, "indifferent": False, "strength": None}

def parse_indifference(text):
    raw = norm(text)
    if any(phrase in raw for phrase in ["INDIFFERENT", "NO STRONG PREFERENCE", "NO PREFERENCE", "NEITHER", "EQUAL"]):
        return {"raw_choice": "INDIFFERENT", "valid": True, "indifferent": True, "strength": None}
    
    forced_res = parse_forced_choice(text)
    if forced_res["valid"]:
        return {"raw_choice": forced_res["raw_choice"], "valid": True, "indifferent": False, "strength": None}
    
    return {"raw_choice": None, "valid": False, "indifferent": False, "strength": None}

def parse_strength(text):
    raw = norm(text)
    # Search for CHOICE: A|B or OPTION A|B or simple A|B declaration
    cm = re.search(r"\b(?:CHOICE|OPTION)?\s*:?\s*([AB])\b", raw)
    sm = re.search(r"\b(?:STRENGTH)?\s*:?\s*([1-5])\b", raw)
    if not cm or not sm:
        # Secondary pattern check: "A, 4" or "Choice A, Strength 3"
        cm_alt = re.search(r"\b([AB])\b", raw)
        sm_alt = re.search(r"\b([1-5])\b", raw)
        if cm_alt and sm_alt:
            return {"raw_choice": cm_alt.group(1), "valid": True, "indifferent": False, "strength": int(sm_alt.group(1))}
        return {"raw_choice": None, "valid": False, "indifferent": False, "strength": None}
    return {"raw_choice": cm.group(1), "valid": True, "indifferent": False, "strength": int(sm.group(1))}

def parse_response(method, text, ordering="original"):
    if method == "forced_choice":
        parsed = parse_forced_choice(text)
    elif method == "explicit_indifference":
        parsed = parse_indifference(text)
    elif method == "preference_strength":
        parsed = parse_strength(text)
    else:
        raise ValueError(f"Unknown method: {method}")

    parsed["canonical_choice"] = canonicalize_choice(parsed.get("raw_choice"), ordering)
    return parsed

