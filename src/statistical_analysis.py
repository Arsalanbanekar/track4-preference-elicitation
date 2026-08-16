import argparse
from pathlib import Path
import itertools
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import wilcoxon
from statsmodels.stats.multitest import multipletests


MODELS = {
    "openai/gpt-oss-120b": "GPT-OSS-120B",
    "qwen/qwen3.6-27b": "Qwen3.6-27B",
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
                "comparison": (
                    f"{MODELS.get(model, model)}: "
                    f"{METHOD_LABELS[method_a]} vs {METHOD_LABELS[method_b]}"
                ),
                "unit": "15 preference pairs",
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
            "comparison": (
                f"{METHOD_LABELS[method]}: "
                f"{MODELS.get(model_a, model_a)} vs {MODELS.get(model_b, model_b)}"
            ),
            "unit": "15 preference pairs",
            "n_pairs": int(diff.notna().sum()),
            "mean_difference": float(diff.mean()),
            "median_difference": float(diff.median()),
            "p_value": p,
        })

    stats = pd.DataFrame(rows)

    # Holm correction within the positional-consistency family.
    mask = stats["family"] == "positional_consistency"
    valid = stats.loc[mask, "p_value"].notna()

    if valid.any():
        adjusted = multipletests(
            stats.loc[mask & stats["p_value"].notna(), "p_value"],
            method="holm",
        )[1]

        stats.loc[mask & stats["p_value"].notna(), "p_value_holm"] = adjusted

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
            "unit": "15 preference pairs",
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
            "unit": "15 preference pairs",
            "n_pairs": int(strength_diff.notna().sum()),
            "mean_difference": float(strength_diff.mean()),
            "median_difference": float(strength_diff.median()),
            "p_value": wilcoxon_paired(
                strength_wide[model_a], strength_wide[model_b]
            ),
        }])
    ], ignore_index=True)

    return stats


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
        .mean()
    )
    summary["percentage"] = summary["consistent"] * 100
    summary["model_label"] = summary["model"].map(MODELS)
    summary["method_label"] = summary["method"].map(METHOD_LABELS)

    fig, ax = plt.subplots(figsize=(7.2, 4.5))

    x = np.arange(len(METHODS))
    width = 0.36

    for i, model in enumerate(MODELS):
        vals = []
        for method in METHODS:
            row = summary[
                (summary["model"] == model) & (summary["method"] == method)
            ]
            vals.append(float(row["percentage"].iloc[0]))

        offset = (-width / 2) if i == 0 else (width / 2)
        ax.bar(
            x + offset,
            vals,
            width,
            label=MODELS[model],
            edgecolor="black",
            linewidth=0.6,
        )

        for xpos, val in zip(x + offset, vals):
            ax.text(
                xpos, val + 1.5, f"{val:.1f}%",
                ha="center", va="bottom", fontsize=9
            )

    ax.set_xticks(x)
    ax.set_xticklabels(
        [METHOD_LABELS[m] for m in METHODS],
        rotation=12,
        ha="right",
    )
    ax.set_ylabel("Positional consistency (%)")
    ax.set_ylim(0, 105)
    ax.set_title("Positional consistency by model and elicitation method")
    ax.legend(frameon=False)
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
    ax.set_ylim(0, 30)
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

    x = np.arange(3, 6)
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
    ax.set_xticklabels(["3", "4", "5"])
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
        help="Path to final_dataset_540.csv. Defaults to results/analysis/final_dataset_540.csv",
    )
    args = parser.parse_args()

    root = Path(__file__).resolve().parent.parent
    data_path = (
        Path(args.data)
        if args.data
        else root / "results" / "analysis" / "final_dataset_540.csv"
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

    plot_positional_consistency(df, consistency, fig_dir)
    plot_indifference(df, fig_dir)
    plot_strength_distribution(df, fig_dir)

    print("Statistical tests:")
    print(
        stats[
            [
                "family",
                "comparison",
                "n_pairs",
                "mean_difference",
                "median_difference",
                "p_value",
                "p_value_holm",
            ]
        ].to_string(index=False)
    )

    print()
    print(f"Saved: {stats_path}")
    print(f"Figures: {fig_dir}")
    print("  figure_1_positional_consistency.png/.svg")
    print("  figure_2_indifference_rate.png/.svg")
    print("  figure_3_strength_distribution.png/.svg")
    print()
    print(
        "Interpretation note: the inferential tests use 15 preference pairs "
        "as the paired unit, preserving the three repetitions within each pair."
    )


if __name__ == "__main__":
    main()
