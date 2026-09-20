import argparse
from pathlib import Path
import itertools
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import wilcoxon, binomtest
from statsmodels.stats.multitest import multipletests
from statsmodels.stats.proportion import proportion_confint


MODELS = {
    "openai/gpt-oss-120b": "GPT-OSS-120B",
    "qwen/qwen3.8-27b": "Qwen3.8-27B",
}

METHODS = [
    "forced_choice",
    "explicit_indifference",
    "preference_strength",
]

METHOD_LABELS = {
    "forced_choice": "Forced choice",
    "explicit_indifference": "Explicit indifference",
    "preference_strength": "Preference strength",
}


def wilcoxon_paired(a, b):
    """Paired Wilcoxon signed-rank test; returns NaN if all differences are zero."""
    a = pd.Series(a).astype(float)
    b = pd.Series(b).astype(float)
    mask = a.notna() & b.notna()
    a, b = a[mask], b[mask]
    if len(a) == 0 or np.allclose((a - b).to_numpy(), 0):
        return np.nan
    return float(wilcoxon(a, b, alternative="two-sided", method="auto").pvalue)


def load_data(path):
    df = pd.read_csv(path)

    required = {
        "model", "pair_id", "method", "ordering", "repetition",
        "canonical_choice", "parsed.indifferent", "strength"
    }
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    return df


def build_positional_consistency(df):
    """Build one original-vs-flipped comparison per model/pair/method/repetition."""
    keys = ["model", "pair_id", "method", "repetition"]

    original = df[df["ordering"] == "original"][keys + ["canonical_choice"]].copy()
    flipped = df[df["ordering"] == "flipped"][keys + ["canonical_choice"]].copy()

    merged = original.merge(
        flipped,
        on=keys,
        suffixes=("_original", "_flipped"),
        validate="one_to_one",
    )

    merged["consistent"] = (
        merged["canonical_choice_original"].notna()
        & merged["canonical_choice_flipped"].notna()
        & (
            merged["canonical_choice_original"]
            == merged["canonical_choice_flipped"]
        )
    )

    return merged


def pair_level_consistency(consistency):
    # Three repetitions are averaged within each preference pair.
    return (
        consistency.groupby(["model", "method", "pair_id"], as_index=False)
        ["consistent"]
        .mean()
        .rename(columns={"consistent": "consistency_rate"})
    )


def run_statistics(df, consistency):
    rows = []

    # ---------------------------
    # Primary consistency tests
    # ---------------------------
    pair_cons = pair_level_consistency(consistency)

    # Method comparisons within each model.
    for model in df["model"].drop_duplicates():
        wide = (
            pair_cons[pair_cons["model"] == model]
            .pivot(index="pair_id", columns="method", values="consistency_rate")
        )

        for method_a, method_b in itertools.combinations(METHODS, 2):
            if method_a not in wide or method_b not in wide:
                continue

            p = wilcoxon_paired(wide[method_a], wide[method_b])
            diff = wide[method_b] - wide[method_a]

            rows.append({
                "family": "positional_consistency",
                "subfamily": "within_model_method",
                "comparison": (
                    f"{MODELS.get(model, model)}: "
                    f"{METHOD_LABELS[method_a]} vs {METHOD_LABELS[method_b]}"
                ),
                "unit": f"{int(diff.notna().sum())} preference pairs",
                "n_pairs": int(diff.notna().sum()),
                "mean_difference": float(diff.mean()),
                "median_difference": float(diff.median()),
                "p_value": p,
            })

    # Model comparisons within each method.
    for method in METHODS:
        wide = (
            pair_cons[pair_cons["method"] == method]
            .pivot(index="pair_id", columns="model", values="consistency_rate")
        )

        model_a, model_b = list(wide.columns)
        diff = wide[model_b] - wide[model_a]
        p = wilcoxon_paired(wide[model_a], wide[model_b])

        rows.append({
            "family": "positional_consistency",
            "subfamily": "between_model",
            "comparison": (
                f"{METHOD_LABELS[method]}: "
                f"{MODELS.get(model_a, model_a)} vs {MODELS.get(model_b, model_b)}"
            ),
            "unit": f"{int(diff.notna().sum())} preference pairs",
            "n_pairs": int(diff.notna().sum()),
            "mean_difference": float(diff.mean()),
            "median_difference": float(diff.median()),
            "p_value": p,
        })

    stats = pd.DataFrame(rows)

    # Joint Holm correction across all 9 positional-consistency comparisons.
    mask = stats["family"] == "positional_consistency"
    valid = stats.loc[mask, "p_value"].notna()

    if valid.any():
        adjusted = multipletests(
            stats.loc[mask & stats["p_value"].notna(), "p_value"],
            method="holm",
        )[1]

        stats.loc[mask & stats["p_value"].notna(), "p_value_holm"] = adjusted

    # Split-family Holm correction: within-model method comparisons (6) and
    # between-model comparisons (3) answer different questions, so correcting
    # them jointly (above) is conservative. Correct each subfamily on its own
    # as an additional, less conservative view.
    for subfamily in ["within_model_method", "between_model"]:
        sub_mask = mask & (stats["subfamily"] == subfamily)
        sub_valid = stats.loc[sub_mask, "p_value"].notna()
        if sub_valid.any():
            sub_adjusted = multipletests(
                stats.loc[sub_mask & stats["p_value"].notna(), "p_value"],
                method="holm",
            )[1]
            stats.loc[sub_mask & stats["p_value"].notna(), "p_value_holm_split"] = sub_adjusted

    # ---------------------------------
    # Secondary: explicit indifference
    # ---------------------------------
    ind = df[df["method"] == "explicit_indifference"].copy()
    ind["indifferent"] = ind["parsed.indifferent"].astype(bool)

    ind_pair = (
        ind.groupby(["model", "pair_id"], as_index=False)["indifferent"]
        .mean()
        .rename(columns={"indifferent": "indifference_rate"})
    )

    ind_wide = ind_pair.pivot(
        index="pair_id", columns="model", values="indifference_rate"
    )

    model_a, model_b = list(ind_wide.columns)
    ind_diff = ind_wide[model_b] - ind_wide[model_a]

    stats = pd.concat([
        stats,
        pd.DataFrame([{
            "family": "secondary",
            "comparison": (
                f"Indifference rate: {MODELS.get(model_a, model_a)} "
                f"vs {MODELS.get(model_b, model_b)}"
            ),
            "unit": f"{int(ind_diff.notna().sum())} preference pairs",
            "n_pairs": int(ind_diff.notna().sum()),
            "mean_difference": float(ind_diff.mean()),
            "median_difference": float(ind_diff.median()),
            "p_value": wilcoxon_paired(
                ind_wide[model_a], ind_wide[model_b]
            ),
        }])
    ], ignore_index=True)

    # -------------------------------
    # Secondary: preference strength
    # -------------------------------
    strength = df[df["method"] == "preference_strength"].copy()

    strength_pair = (
        strength.groupby(["model", "pair_id"], as_index=False)["strength"]
        .mean()
        .rename(columns={"strength": "mean_strength"})
    )

    strength_wide = strength_pair.pivot(
        index="pair_id", columns="model", values="mean_strength"
    )

    model_a, model_b = list(strength_wide.columns)
    strength_diff = strength_wide[model_b] - strength_wide[model_a]

    stats = pd.concat([
        stats,
        pd.DataFrame([{
            "family": "secondary",
            "comparison": (
                f"Preference strength: {MODELS.get(model_a, model_a)} "
                f"vs {MODELS.get(model_b, model_b)}"
            ),
            "unit": f"{int(strength_diff.notna().sum())} preference pairs",
            "n_pairs": int(strength_diff.notna().sum()),
            "mean_difference": float(strength_diff.mean()),
            "median_difference": float(strength_diff.median()),
            "p_value": wilcoxon_paired(
                strength_wide[model_a], strength_wide[model_b]
            ),
        }])
    ], ignore_index=True)

    return stats


def run_binomial_tests(consistency):
    """Two-sided exact binomial test of each method x model cell's consistent
    count (out of n_pairs x n_repetitions) against a 50% chance floor."""
    rows = []
    for (model, method), group in consistency.groupby(["model", "method"]):
        n = len(group)
        k = int(group["consistent"].sum())
        result = binomtest(k, n, 0.5, alternative="two-sided")
        rows.append({
            "model": MODELS.get(model, model),
            "method": METHOD_LABELS[method],
            "n_trials": n,
            "n_consistent": k,
            "consistency_rate": k / n,
            "p_value": result.pvalue,
        })
    return pd.DataFrame(rows).sort_values(["model", "method"]).reset_index(drop=True)


def run_indifference_excluded_consistency(df):
    """Positional consistency for explicit_indifference, after dropping any
    original/flipped repetition where either side answered INDIFFERENT.
    Separates 'the method stabilizes choices' from 'the method offers an exit.'"""
    ei_all = df[df["method"] == "explicit_indifference"].copy()
    keys = ["model", "pair_id", "repetition"]

    def merged_consistency(sub):
        original = sub[sub["ordering"] == "original"][keys + ["canonical_choice"]]
        flipped = sub[sub["ordering"] == "flipped"][keys + ["canonical_choice"]]
        m = original.merge(
            flipped, on=keys, suffixes=("_original", "_flipped"), validate="one_to_one"
        )
        m["consistent"] = (
            m["canonical_choice_original"].notna()
            & (m["canonical_choice_original"] == m["canonical_choice_flipped"])
        )
        return m

    full = merged_consistency(ei_all)
    ei_ab = ei_all[~ei_all["parsed.indifferent"].astype(bool)]
    filtered = merged_consistency(ei_ab)

    rows = []
    for model in full["model"].unique():
        total = len(full[full["model"] == model])
        fgroup = filtered[filtered["model"] == model]
        n = len(fgroup)
        k = int(fgroup["consistent"].sum())
        rows.append({
            "model": MODELS.get(model, model),
            "n_ab_pairs": n,
            "n_excluded": total - n,
            "n_consistent": k,
            "consistency_rate": k / n if n else float("nan"),
        })
    return pd.DataFrame(rows).sort_values("model").reset_index(drop=True)


def classify_pair_difficulty(df, threshold=0.8):
    """Classify each pair as 'easy' (near-unanimous canonical choice across all
    methods/models/orderings/repetitions) or 'ambiguous' (mixed responses)."""
    rows = []
    for pair_id, group in df.groupby("pair_id"):
        counts = group["canonical_choice"].value_counts()
        total = len(group)
        modal_share = counts.max() / total
        rows.append({
            "pair_id": pair_id,
            "n_responses": total,
            "modal_choice": counts.idxmax(),
            "modal_share": modal_share,
            "difficulty": "easy" if modal_share >= threshold else "ambiguous",
        })
    return pd.DataFrame(rows).sort_values("pair_id").reset_index(drop=True)


def run_stratified_consistency(consistency, pair_difficulty):
    """Positional consistency by method x model, split into easy/ambiguous
    pair strata (see classify_pair_difficulty)."""
    merged = consistency.merge(pair_difficulty[["pair_id", "difficulty"]], on="pair_id")
    rows = []
    for (stratum, model, method), group in merged.groupby(["difficulty", "model", "method"]):
        n = len(group)
        k = int(group["consistent"].sum())
        rows.append({
            "stratum": stratum,
            "model": MODELS.get(model, model),
            "method": METHOD_LABELS[method],
            "n_trials": n,
            "n_consistent": k,
            "consistency_rate": k / n if n else float("nan"),
        })
    return pd.DataFrame(rows).sort_values(["stratum", "model", "method"]).reset_index(drop=True)


def publication_style():
    plt.rcParams.update({
        "figure.dpi": 150,
        "savefig.dpi": 300,
        "font.size": 10,
        "axes.titlesize": 13,
        "axes.labelsize": 11,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "legend.fontsize": 9,
        "axes.spines.top": False,
        "axes.spines.right": False,
    })


def save_figure(fig, out_dir, name):
    out_dir.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(out_dir / f"{name}.png", dpi=300, bbox_inches="tight")
    fig.savefig(out_dir / f"{name}.svg", bbox_inches="tight")
    plt.close(fig)


def plot_positional_consistency(df, consistency, out_dir):
    summary = (
        consistency.groupby(["model", "method"], as_index=False)["consistent"]
        .agg(n="size", k="sum")
    )
    summary["percentage"] = summary["k"] / summary["n"] * 100
    ci = summary.apply(
        lambda r: proportion_confint(r["k"], r["n"], alpha=0.05, method="wilson"),
        axis=1,
    )
    summary["ci_low"] = [c[0] * 100 for c in ci]
    summary["ci_high"] = [c[1] * 100 for c in ci]
    summary["model_label"] = summary["model"].map(MODELS)
    summary["method_label"] = summary["method"].map(METHOD_LABELS)

    fig, ax = plt.subplots(figsize=(7.2, 4.5))

    x = np.arange(len(METHODS))
    width = 0.36

    for i, model in enumerate(MODELS):
        vals, err_low, err_high = [], [], []
        for method in METHODS:
            row = summary[
                (summary["model"] == model) & (summary["method"] == method)
            ].iloc[0]
            vals.append(float(row["percentage"]))
            err_low.append(float(row["percentage"] - row["ci_low"]))
            err_high.append(float(row["ci_high"] - row["percentage"]))

        offset = (-width / 2) if i == 0 else (width / 2)
        ax.bar(
            x + offset,
            vals,
            width,
            yerr=[err_low, err_high],
            capsize=3,
            error_kw={"elinewidth": 1, "capthick": 1},
            label=MODELS[model],
            edgecolor="black",
            linewidth=0.6,
        )

        for xpos, val, eh in zip(x + offset, vals, err_high):
            ax.text(
                xpos, val + eh + 1.5, f"{val:.1f}%",
                ha="center", va="bottom", fontsize=9
            )

    ax.set_xticks(x)
    ax.set_xticklabels(
        [METHOD_LABELS[m] for m in METHODS],
        rotation=12,
        ha="right",
    )
    ax.set_ylabel("Positional consistency (%)")
    ax.set_ylim(0, 122)
    ax.set_yticks(range(0, 101, 20))
    ax.set_title("Positional consistency by model and elicitation method")
    n_per_bar = int(summary["n"].iloc[0])
    ax.text(
        0.5, -0.32,
        f"Error bars: 95% Wilson score confidence interval (n={n_per_bar} per bar)",
        transform=ax.transAxes, ha="center", va="top",
        fontsize=8, style="italic", color="dimgray",
    )
    ax.legend(frameon=False, loc="upper left")
    ax.grid(axis="y", alpha=0.25)

    save_figure(fig, out_dir, "figure_1_positional_consistency")


def plot_indifference(df, out_dir):
    summary = (
        df[df["method"] == "explicit_indifference"]
        .assign(indifferent=lambda x: x["parsed.indifferent"].astype(bool))
        .groupby("model", as_index=False)["indifferent"]
        .mean()
    )
    summary["percentage"] = summary["indifferent"] * 100

    fig, ax = plt.subplots(figsize=(5.8, 4.5))

    x = np.arange(len(summary))
    vals = summary["percentage"].to_numpy()

    ax.bar(
        x, vals, width=0.55,
        edgecolor="black", linewidth=0.6
    )

    for xpos, val in zip(x, vals):
        ax.text(
            xpos, val + 1.5, f"{val:.1f}%",
            ha="center", va="bottom", fontsize=10
        )

    ax.set_xticks(x)
    ax.set_xticklabels([MODELS[m] for m in summary["model"]])
    ax.set_ylabel("Indifference rate (%)")
    ax.set_ylim(0, max(float(vals.max()) * 1.35, 10))
    ax.set_title("Explicit-indifference responses")
    ax.grid(axis="y", alpha=0.25)

    save_figure(fig, out_dir, "figure_2_indifference_rate")


def plot_strength_distribution(df, out_dir):
    strength = df[df["method"] == "preference_strength"].copy()
    strength["strength"] = pd.to_numeric(strength["strength"], errors="coerce")

    counts = (
        strength.groupby(["strength", "model"])
        .size()
        .reset_index(name="responses")
    )

    x = np.arange(1, 6)
    width = 0.36

    fig, ax = plt.subplots(figsize=(6.8, 4.5))

    for i, model in enumerate(MODELS):
        vals = []
        for s in x:
            row = counts[
                (counts["model"] == model)
                & (counts["strength"] == s)
            ]
            vals.append(int(row["responses"].iloc[0]) if not row.empty else 0)

        offset = (-width / 2) if i == 0 else (width / 2)
        bars = ax.bar(
            x + offset,
            vals,
            width,
            label=MODELS[model],
            edgecolor="black",
            linewidth=0.6,
        )

        for bar, val in zip(bars, vals):
            if val:
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    val + 1,
                    str(val),
                    ha="center",
                    va="bottom",
                    fontsize=9,
                )

    ax.set_xticks(x)
    ax.set_xticklabels(["1", "2", "3", "4", "5"])
    ax.set_xlabel("Preference strength")
    ax.set_ylabel("Responses (n)")
    ax.set_title("Preference-strength distribution")
    ax.legend(frameon=False)
    ax.grid(axis="y", alpha=0.25)

    save_figure(fig, out_dir, "figure_3_strength_distribution")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--data",
        default=None,
        help="Path to final_dataset_1620.csv. Defaults to results/analysis/final_dataset_1620.csv",
    )
    args = parser.parse_args()

    root = Path(__file__).resolve().parent.parent
    data_path = (
        Path(args.data)
        if args.data
        else root / "results" / "analysis" / "final_dataset_1620.csv"
    )

    out_dir = root / "results" / "analysis"
    fig_dir = out_dir / "figures"

    publication_style()

    df = load_data(data_path)
    consistency = build_positional_consistency(df)

    print("=" * 70)
    print("STATISTICAL ANALYSIS + PUBLICATION FIGURES")
    print("=" * 70)
    print(f"Dataset: {data_path}")
    print(f"Records: {len(df)}")
    print(f"Positional comparisons: {len(consistency)}")
    print()

    stats = run_statistics(df, consistency)

    stats_path = out_dir / "statistical_tests.csv"
    stats.to_csv(stats_path, index=False)

    binomial = run_binomial_tests(consistency)
    binomial_path = out_dir / "binomial_tests.csv"
    binomial.to_csv(binomial_path, index=False)

    ei_excl = run_indifference_excluded_consistency(df)
    ei_excl_path = out_dir / "indifference_excluded_consistency.csv"
    ei_excl.to_csv(ei_excl_path, index=False)

    pair_difficulty = classify_pair_difficulty(df)
    pair_difficulty_path = out_dir / "pair_difficulty.csv"
    pair_difficulty.to_csv(pair_difficulty_path, index=False)

    stratified = run_stratified_consistency(consistency, pair_difficulty)
    stratified_path = out_dir / "stratified_consistency.csv"
    stratified.to_csv(stratified_path, index=False)

    plot_positional_consistency(df, consistency, fig_dir)
    plot_indifference(df, fig_dir)
    plot_strength_distribution(df, fig_dir)

    print("Statistical tests (joint-9 vs. split-family Holm correction):")
    print(
        stats[
            [
                "family",
                "subfamily",
                "comparison",
                "n_pairs",
                "mean_difference",
                "median_difference",
                "p_value",
                "p_value_holm",
                "p_value_holm_split",
            ]
        ].to_string(index=False)
    )

    print()
    print("Binomial tests vs. chance (p=0.5):")
    print(binomial.to_string(index=False))

    print()
    print("Explicit-indifference positional consistency, INDIFFERENT responses excluded:")
    print(ei_excl.to_string(index=False))

    print()
    print("Pair difficulty classification (modal-choice share, threshold 0.8):")
    print(pair_difficulty.to_string(index=False))

    print()
    print("Positional consistency stratified by pair difficulty:")
    print(stratified.to_string(index=False))

    print()
    print(f"Saved: {stats_path}")
    print(f"Saved: {binomial_path}")
    print(f"Saved: {ei_excl_path}")
    print(f"Saved: {pair_difficulty_path}")
    print(f"Saved: {stratified_path}")
    print(f"Figures: {fig_dir}")
    print("  figure_1_positional_consistency.png/.svg")
    print("  figure_2_indifference_rate.png/.svg")
    print("  figure_3_strength_distribution.png/.svg")
    print()
    n_pairs = df["pair_id"].nunique()
    n_reps = df["repetition"].nunique()
    print(
        f"Interpretation note: the inferential tests use {n_pairs} preference pairs "
        f"as the paired unit, preserving the {n_reps} repetitions within each pair."
    )


if __name__ == "__main__":
    main()
