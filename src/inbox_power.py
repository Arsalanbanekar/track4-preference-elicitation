"""Power simulation for the inbox study. No API calls.

Choice tests: baselines come from the main study's forced-choice answers for the
16 items (per model, item and order). A chosen fraction of items is shifted by
a chosen amount towards the other option, and the pre-registered permutation
test is run on simulated data. Deliberation test: per-item reasoning length
drawn around the pilot's Qwen values, with a chosen relative increase.

    python -m src.inbox_power
"""
import numpy as np
import pandas as pd
from scipy.stats import wilcoxon

from .inbox_analysis import permutation_test
from .inbox_study import OUT_DIR, ROOT, load_spec

SIMS = 200
N_PERM = 1000
SEED = 11
MODELS = {"openai/gpt-oss-120b": "GPT-OSS-120B", "qwen/qwen3.8-27b": "Qwen3.8-27B"}


def baselines(items):
    """P(canonical A) per model, item and order, from the main study's forced-choice answers."""
    df = pd.read_csv(ROOT / "results" / "analysis" / "final_dataset_1620.csv")
    fc = df[(df.method == "forced_choice") & df.pair_id.isin(items)]
    p = fc.assign(a=(fc.canonical_choice == "A").astype(float)).groupby(["model", "pair_id", "ordering"]).a.mean()
    return {(m, i, "original" if o == "original" else "swapped"): v for (m, i, o), v in p.items()}


def simulate_choices(rng, base, model, items, frac, shift):
    affected = set(rng.choice(items, size=int(round(frac * len(items))), replace=False)) if frac else set()
    rows = []
    for item in items:
        for w in ("W1", "W2"):
            for o in ("original", "swapped"):
                px = base[(model, item, o)]
                py = px
                if item in affected:
                    py = min(1.0, px + shift) if px <= 0.5 else max(0.0, px - shift)
                for cond, p in (("X", px), ("Y", py)):
                    for rep in range(3):
                        rows.append({"item_id": item, "wording": w, "ordering": o, "condition": cond,
                                     "choice": "A" if rng.random() < p else "B"})
    return pd.DataFrame(rows)


def choice_power(base, items, model, frac, shift, rng):
    hits05 = hits005 = 0
    for s in range(SIMS):
        df = simulate_choices(rng, base, model, items, frac, shift)
        p = permutation_test(df, "condition", "X", "Y", ["item_id", "wording", "ordering"], ["A", "B"],
                             n_perm=N_PERM, seed=int(rng.integers(1 << 30)))["p_value"]
        hits05 += p < 0.05
        hits005 += p < 0.005
    return hits05 / SIMS, hits005 / SIMS


def deliberation_power(n_items, rel_increase, rng, base_mean=1700, item_sd=150, call_cv=0.11, calls=12):
    hits05 = hits005 = 0
    for s in range(SIMS):
        mu = rng.normal(base_mean, item_sd, n_items)
        eff = rng.normal(rel_increase, rel_increase / 2, n_items)  # effect varies by item
        c3 = np.array([rng.normal(m, call_cv * m, calls).mean() for m in mu])
        c4 = np.array([rng.normal(m * (1 + e), call_cv * m * (1 + e), calls).mean() for m, e in zip(mu, eff)])
        p = wilcoxon(c4, c3, alternative="greater").pvalue
        hits05 += p < 0.05
        hits005 += p < 0.005
    return hits05 / SIMS, hits005 / SIMS


def main():
    rng = np.random.default_rng(SEED)
    items = [it["pair_id"] for it in load_spec()["items"]]
    base = baselines(items)
    rows = []
    for model, name in MODELS.items():
        for frac in (0.0, 2 / 16, 4 / 16, 8 / 16):
            for shift in ((0.0,) if frac == 0 else (0.33, 0.67)):
                p05, p005 = choice_power(base, items, model, frac, shift, rng)
                rows.append({"test": "choice (permutation)", "model": name,
                             "items_affected": f"{round(frac * 16)}/16", "shift": shift,
                             "power_at_0.05": p05, "power_at_0.005": p005})
                print(rows[-1])
    for rel in (0.0, 0.05, 0.10, 0.15, 0.35):
        p05, p005 = deliberation_power(len(items), rel, rng)
        rows.append({"test": "deliberation (Wilcoxon, one-sided)", "model": "Qwen3.8-27B",
                     "items_affected": "16/16", "shift": f"+{int(rel * 100)}%",
                     "power_at_0.05": p05, "power_at_0.005": p005})
        print(rows[-1])
    out = OUT_DIR / "power_simulation.csv"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(out, index=False)
    print(f"Written to {out}")


if __name__ == "__main__":
    main()
