from pathlib import Path

PROMPT_DIR = Path(__file__).resolve().parent.parent / "prompts"

METHOD_FILES = {
    "forced_choice": "forced_choice.txt",
    "explicit_indifference": "explicit_indifference.txt",
    "preference_strength": "preference_strength.txt",
}

def load_template(method: str) -> str:
    if method not in METHOD_FILES:
        raise ValueError(f"Unknown method: {method}")
    return (PROMPT_DIR / METHOD_FILES[method]).read_text(encoding="utf-8")

def build_prompt(method: str, option_a: str, option_b: str) -> str:
    return load_template(method).format(option_a=option_a, option_b=option_b)

def flip_pair(option_a: str, option_b: str):
    return option_b, option_a
