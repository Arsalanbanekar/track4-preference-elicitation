import json
from pathlib import Path
from collections import Counter

import pandas as pd


ROOT = Path(__file__).resolve().parent.parent

# ============================================================
# FINAL PRODUCTION RUNS
# ============================================================
# a93f24c3a163 = original production run
# 6dc0ba8b0f3e = Qwen forced_choice + explicit_indifference recovery
# e58a410e3b33 = Qwen preference_strength recovery
#
# These three runs together form the final 540-record dataset.
# ============================================================

FINAL_RUN_IDS = {
    "a93f24c3a163",
    "6dc0ba8b0f3e",
    "e58a410e3b33",
}


RUNS_DIR = ROOT / "results" / "runs"
MAIN_RAW = ROOT / "results" / "raw_responses.jsonl"
ANALYSIS_DIR = ROOT / "results" / "analysis"

ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# LOAD JSONL
# ============================================================

def load_jsonl(path):
    rows = []

    if not path.exists():
        return rows

    with open(path, encoding="utf-8") as f:
        for line_number, line in enumerate(f, start=1):
            line = line.strip()

            if not line:
                continue

            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                print(
                    f"WARNING: Could not parse {path.name} "
                    f"line {line_number}"
                )

    return rows


def load_final_dataset():
    """
    Load only the explicitly selected production/recovery runs.

    Duplicate experimental cells are resolved by keeping the
    latest timestamp. This allows the Qwen recovery runs to
    replace the failed Qwen records from the original production
    run.
    """

    rows = []

    # Main production file
    if MAIN_RAW.exists():
        rows.extend(load_jsonl(MAIN_RAW))

    # All run files
    if RUNS_DIR.exists():
        for path in RUNS_DIR.glob("raw_responses_*.jsonl"):
            rows.extend(load_jsonl(path))

    # Keep only selected run IDs
    rows = [
        row
        for row in rows
        if row.get("run_id") in FINAL_RUN_IDS
    ]

    if not rows:
        raise RuntimeError(
            "No records found for the selected final production runs."
        )

    df = pd.json_normalize(rows)

    required_columns = [
        "run_id",
        "timestamp_utc",
        "model",
        "pair_id",
        "method",
        "ordering",
        "repetition",
    ]

    missing = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing:
        raise RuntimeError(
            f"Missing required columns: {missing}"
        )

    # Sort chronologically so the latest recovery result wins
    df = df.sort_values("timestamp_utc")

    # One experimental cell =
    # model + pair + method + ordering + repetition
    df = df.drop_duplicates(
        subset=[
            "model",
            "pair_id",
            "method",
            "ordering",
            "repetition",
        ],
        keep="last",
    )

    return df.reset_index(drop=True)


# ============================================================
# BASIC VALIDATION
# ============================================================

def validate_dataset(df):

    print("\n" + "=" * 70)
    print("DATASET VALIDATION")
    print("=" * 70)

    print(f"Final records: {len(df)}")

    print("\nModels:")
    print(df["model"].value_counts().to_string())

    print("\nMethods:")
    print(df["method"].value_counts().to_string())

    print("\nOrderings:")
    print(df["ordering"].value_counts().to_string())

    print("\nPairs:")
    print(df["pair_id"].nunique())

    print("\nRepetitions:")
    print(sorted(df["repetition"].unique()))

    if "parsed.valid" in df.columns:
        valid = df["parsed.valid"].astype(bool)
        print(f"\nValid responses: {int(valid.sum())}")
        print(f"Invalid responses: {int((~valid).sum())}")

    if "error" in df.columns:
        errors = df["error"].notna()
        print(f"Errors: {int(errors.sum())}")
    else:
        print("Errors: 0")

    if "canonical_choice" in df.columns:
        print(
            f"Missing canonical choices: "
            f"{int(df['canonical_choice'].isna().sum())}"
        )


# ============================================================
# OVERALL METHOD SUMMARY
# ============================================================

def create_overall_summary(df):

    work = df.copy()

    work["valid"] = (
        work["parsed.valid"].astype(bool)
        if "parsed.valid" in work.columns
        else False
    )

    work["indifferent"] = (
        work["parsed.indifferent"].astype(bool)
        if "parsed.indifferent" in work.columns
        else False
    )

    if "parsed.strength" in work.columns:
        work["strength"] = pd.to_numeric(
            work["parsed.strength"],
            errors="coerce",
        )
    else:
        work["strength"] = pd.NA

    summary = (
        work
        .groupby(["model", "method"], dropna=False)
        .agg(
            responses=("model", "size"),
            valid_responses=("valid", "sum"),
            valid_rate=("valid", "mean"),
            indifferent_responses=("indifferent", "sum"),
            indifference_rate=("indifferent", "mean"),
            mean_strength=("strength", "mean"),
            median_strength=("strength", "median"),
            min_strength=("strength", "min"),
            max_strength=("strength", "max"),
        )
        .reset_index()
    )

    # Explicitly show N/A where strength is not applicable
    summary["mean_strength"] = summary["mean_strength"].round(4)
    summary["median_strength"] = summary["median_strength"].round(4)

    strength_methods = {"preference_strength"}

    summary.loc[
        ~summary["method"].isin(strength_methods),
        [
            "mean_strength",
            "median_strength",
            "min_strength",
            "max_strength",
        ],
    ] = pd.NA

    return summary


# ============================================================
# STRENGTH DISTRIBUTION
# ============================================================

def create_strength_distribution(df):

    work = df[
        df["method"] == "preference_strength"
    ].copy()

    if work.empty:
        return pd.DataFrame()

    work["strength"] = pd.to_numeric(
        work["parsed.strength"],
        errors="coerce",
    )

    result = (
        work
        .groupby(["model", "strength"])
        .size()
        .reset_index(name="responses")
    )

    # Add percentages
    result["percentage"] = (
        result.groupby("model")["responses"]
        .transform(lambda x: 100 * x / x.sum())
    )

    result["percentage"] = result["percentage"].round(2)

    return result.sort_values(
        ["model", "strength"]
    )


# ============================================================
# CHOICE DISTRIBUTION
# ============================================================

def create_choice_distribution(df):

    work = df.copy()

    work["choice"] = work["canonical_choice"]

    result = (
        work
        .groupby(["model", "method", "choice"])
        .size()
        .reset_index(name="responses")
    )

    result["percentage"] = (
        result.groupby(["model", "method"])["responses"]
        .transform(lambda x: 100 * x / x.sum())
    )

    result["percentage"] = result["percentage"].round(2)

    return result.sort_values(
        ["model", "method", "choice"]
    )


# ============================================================
# INDIFFERENCE ANALYSIS
# ============================================================

def create_indifference_summary(df):

    work = df[
        df["method"] == "explicit_indifference"
    ].copy()

    if work.empty:
        return pd.DataFrame()

    work["indifferent"] = (
        work["parsed.indifferent"].astype(bool)
    )

    result = (
        work
        .groupby(["model", "pair_id"])
        .agg(
            responses=("model", "size"),
            indifferent_responses=("indifferent", "sum"),
        )
        .reset_index()
    )

    result["indifference_rate"] = (
        result["indifferent_responses"]
        / result["responses"]
    )

    result["indifference_rate"] = (
        result["indifference_rate"] * 100
    ).round(2)

    return result.sort_values(
        ["model", "indifference_rate"],
        ascending=[True, False],
    )


# ============================================================
# POSITIONAL CONSISTENCY
# ============================================================

def create_positional_consistency(df):

    work = df.copy()

    pivot = work.pivot_table(
        index=[
            "model",
            "pair_id",
            "method",
            "repetition",
        ],
        columns="ordering",
        values="canonical_choice",
        aggfunc="first",
    ).reset_index()

    if "original" not in pivot.columns:
        return pd.DataFrame()

    if "flipped" not in pivot.columns:
        return pd.DataFrame()

    # A response is positionally consistent when the model
    # chooses the same canonical option after the options are flipped.
    pivot["consistent"] = (
        (pivot["original"] == pivot["flipped"])
        & pivot["original"].notna()
        & pivot["flipped"].notna()
    )

    summary = (
        pivot
        .groupby(["model", "method"])
        .agg(
            comparisons=("consistent", "size"),
            consistent_comparisons=("consistent", "sum"),
            positional_consistency_rate=("consistent", "mean"),
        )
        .reset_index()
    )

    summary["positional_consistency_rate"] = (
        summary["positional_consistency_rate"] * 100
    ).round(2)

    return summary


# ============================================================
# PAIR-LEVEL PREFERENCE SUMMARY
# ============================================================

def create_pair_summary(df):

    work = df.copy()

    result = (
        work
        .groupby(
            ["model", "method", "pair_id"]
        )
        .agg(
            responses=("model", "size"),
            choice_A=(
                "canonical_choice",
                lambda x: (x == "A").sum(),
            ),
            choice_B=(
                "canonical_choice",
                lambda x: (x == "B").sum(),
            ),
            indifference=(
                "parsed.indifferent",
                lambda x: x.fillna(False).astype(bool).sum(),
            ),
        )
        .reset_index()
    )

    result["choice_A_pct"] = (
        result["choice_A"]
        / result["responses"]
        * 100
    ).round(2)

    result["choice_B_pct"] = (
        result["choice_B"]
        / result["responses"]
        * 100
    ).round(2)

    result["indifference_pct"] = (
        result["indifference"]
        / result["responses"]
        * 100
    ).round(2)

    return result


# ============================================================
# PAIR-LEVEL POSITIONAL CONSISTENCY
# ============================================================

def create_pair_consistency(df):

    pivot = df.pivot_table(
        index=[
            "model",
            "pair_id",
            "method",
            "repetition",
        ],
        columns="ordering",
        values="canonical_choice",
        aggfunc="first",
    ).reset_index()

    if (
        "original" not in pivot.columns
        or "flipped" not in pivot.columns
    ):
        return pd.DataFrame()

    pivot["consistent"] = (
        (pivot["original"] == pivot["flipped"])
        & pivot["original"].notna()
        & pivot["flipped"].notna()
    )

    result = (
        pivot
        .groupby(["model", "method", "pair_id"])
        .agg(
            comparisons=("consistent", "size"),
            consistent=("consistent", "sum"),
            consistency_rate=("consistent", "mean"),
        )
        .reset_index()
    )

    result["consistency_rate"] = (
        result["consistency_rate"] * 100
    ).round(2)

    return result.sort_values(
        ["model", "method", "consistency_rate"]
    )


# ============================================================
# MODEL COMPARISON
# ============================================================

def create_model_comparison(df):

    rows = []

    for method in sorted(df["method"].unique()):

        method_df = df[
            df["method"] == method
        ]

        for model in sorted(
            method_df["model"].unique()
        ):

            model_df = method_df[
                method_df["model"] == model
            ]

            row = {
                "method": method,
                "model": model,
                "responses": len(model_df),
                "A_rate": round(
                    (
                        model_df["canonical_choice"]
                        .eq("A")
                        .mean()
                        * 100
                    ),
                    2,
                ),
                "B_rate": round(
                    (
                        model_df["canonical_choice"]
                        .eq("B")
                        .mean()
                        * 100
                    ),
                    2,
                ),
            }

            if method == "explicit_indifference":
                row["indifference_rate"] = round(
                    (
                        model_df["parsed.indifferent"]
                        .fillna(False)
                        .astype(bool)
                        .mean()
                        * 100
                    ),
                    2,
                )
            else:
                row["indifference_rate"] = pd.NA

            if method == "preference_strength":
                strength = pd.to_numeric(
                    model_df["parsed.strength"],
                    errors="coerce",
                )

                row["mean_strength"] = round(
                    strength.mean(),
                    4,
                )

                row["median_strength"] = round(
                    strength.median(),
                    4,
                )
            else:
                row["mean_strength"] = pd.NA
                row["median_strength"] = pd.NA

            rows.append(row)

    return pd.DataFrame(rows)


# ============================================================
# DATASET SUMMARY BY RUN
# ============================================================

def create_run_summary(df):

    result = (
        df
        .groupby(["run_id", "model", "method"])
        .size()
        .reset_index(name="records")
    )

    return result


# ============================================================
# SAVE CSV
# ============================================================

def save_csv(df, filename):

    if df.empty:
        print(f"Skipping empty output: {filename}")
        return

    path = ANALYSIS_DIR / filename
    df.to_csv(path, index=False)
    print(f"Saved: {path}")


# ============================================================
# MAIN
# ============================================================

def main():

    print("\n")
    print("=" * 70)
    print("FINAL PREFERENCE ELICITATION ANALYSIS")
    print("=" * 70)

    print("\nSelected production runs:")
    for run_id in sorted(FINAL_RUN_IDS):
        print(f"  - {run_id}")

    # --------------------------------------------------------
    # Load
    # --------------------------------------------------------

    df = load_final_dataset()

    validate_dataset(df)

    # Save the exact final dataset used for analysis
    save_csv(
        df,
        "final_dataset_540.csv",
    )

    # --------------------------------------------------------
    # Analyses
    # --------------------------------------------------------

    overall = create_overall_summary(df)
    strength = create_strength_distribution(df)
    choices = create_choice_distribution(df)
    indifference = create_indifference_summary(df)
    consistency = create_positional_consistency(df)
    pair_summary = create_pair_summary(df)
    pair_consistency = create_pair_consistency(df)
    model_comparison = create_model_comparison(df)
    run_summary = create_run_summary(df)

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    save_csv(
        overall,
        "final_overall_summary.csv",
    )

    save_csv(
        strength,
        "final_strength_distribution.csv",
    )

    save_csv(
        choices,
        "final_choice_distribution.csv",
    )

    save_csv(
        indifference,
        "final_indifference_by_pair.csv",
    )

    save_csv(
        consistency,
        "final_positional_consistency.csv",
    )

    save_csv(
        pair_summary,
        "final_pair_summary.csv",
    )

    save_csv(
        pair_consistency,
        "final_pair_consistency.csv",
    )

    save_csv(
        model_comparison,
        "final_model_comparison.csv",
    )

    save_csv(
        run_summary,
        "final_run_summary.csv",
    )

    # --------------------------------------------------------
    # Print important results
    # --------------------------------------------------------

    print("\n")
    print("=" * 70)
    print("OVERALL SUMMARY")
    print("=" * 70)

    print(
        overall.to_string(index=False)
    )

    print("\n")
    print("=" * 70)
    print("POSITIONAL CONSISTENCY")
    print("=" * 70)

    print(
        consistency.to_string(index=False)
    )

    print("\n")
    print("=" * 70)
    print("STRENGTH DISTRIBUTION")
    print("=" * 70)

    if strength.empty:
        print("No preference-strength data found.")
    else:
        print(
            strength.to_string(index=False)
        )

    print("\n")
    print("=" * 70)
    print("MODEL COMPARISON")
    print("=" * 70)

    print(
        model_comparison.to_string(index=False)
    )

    print("\n")
    print("=" * 70)
    print("ANALYSIS COMPLETE")
    print("=" * 70)

    print(
        f"\nAll analysis files were written to:\n"
        f"{ANALYSIS_DIR}"
    )


if __name__ == "__main__":
    main()