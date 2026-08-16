import argparse, json
from pathlib import Path
import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parent.parent

def load_config():
    with open(ROOT / "config.yaml", encoding="utf-8") as f:
        return yaml.safe_load(f)

def load_records_from_files(file_paths):
    rows = []
    for fp in file_paths:
        if fp.exists():
            with open(fp, encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        try:
                            rows.append(json.loads(line))
                        except json.JSONDecodeError:
                            pass
    if not rows:
        return pd.DataFrame()
    return pd.json_normalize(rows)

def load_run(run_id):
    runs_dir = ROOT / "results" / "runs"
    target_file = runs_dir / f"raw_responses_{run_id}.jsonl"
    files = []
    if target_file.exists():
        files.append(target_file)
    
    # Fallback to checking main raw_responses.jsonl and all run files
    main_raw = ROOT / "results" / "raw_responses.jsonl"
    if main_raw.exists():
        files.append(main_raw)
    
    df = load_records_from_files(files)
    if df.empty or "run_id" not in df.columns:
        return pd.DataFrame()
    return df[df["run_id"] == run_id].copy()

def load_final(target_run_ids=None):
    cfg = load_config()
    if target_run_ids is None:
        target_run_ids = cfg.get("analysis", {}).get("final_production_runs", ["a93f24c3a163"])
    
    files = []
    runs_dir = ROOT / "results" / "runs"
    if runs_dir.exists():
        files.extend(list(runs_dir.glob("raw_responses_*.jsonl")))
    
    main_raw = ROOT / "results" / "raw_responses.jsonl"
    if main_raw.exists():
        files.append(main_raw)

    df = load_records_from_files(files)
    if df.empty or "run_id" not in df.columns:
        return pd.DataFrame()

    df = df[df["run_id"].isin(target_run_ids)].copy()
    if "timestamp_utc" in df.columns and {"model", "pair_id", "method", "ordering", "repetition"}.issubset(df.columns):
        df = df.sort_values("timestamp_utc")
        df = df.drop_duplicates(
            subset=["model", "pair_id", "method", "ordering", "repetition"],
            keep="last"
        )
    return df

def summarize(df):
    if df.empty:
        return pd.DataFrame()
    
    df = df.copy()
    if "parsed.valid" in df.columns:
        df["valid"] = df["parsed.valid"].fillna(False)
    else:
        df["valid"] = False

    if "parsed.indifferent" in df.columns:
        df["indifferent"] = df["parsed.indifferent"].fillna(False)
    else:
        df["indifferent"] = False

    if "parsed.strength" in df.columns:
        df["strength"] = df["parsed.strength"]
    else:
        df["strength"] = None

    summary = df.groupby(["model", "method"], dropna=False).agg(
        responses=("model", "size"),
        valid_rate=("valid", "mean"),
        indifference_rate=("indifferent", "mean"),
        mean_strength=("strength", "mean")
    ).reset_index()
    # Strength is only applicable to the preference_strength method.
    # Display N/A for methods that do not collect a strength score.
    summary["mean_strength"] = summary["mean_strength"].apply(
        lambda x: f"{x:.6f}" if pd.notna(x) else "N/A"
    )
    return summary

def compute_positional_consistency(df):
    if df.empty or "canonical_choice" not in df.columns:
        return pd.DataFrame()
    
    pivot = df.pivot_table(
        index=["model", "pair_id", "method", "repetition"],
        columns="ordering",
        values="canonical_choice",
        aggfunc="first"
    ).reset_index()

    if "original" not in pivot.columns or "flipped" not in pivot.columns:
        return pd.DataFrame()

    pivot["consistent"] = (pivot["original"] == pivot["flipped"]) & (pivot["original"].notna())
    return pivot.groupby(["model", "method"]).agg(
        total_pairs=("pair_id", "count"),
        positional_consistency_rate=("consistent", "mean")
    ).reset_index()

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", type=str, help="Analyze specific run_id")
    ap.add_argument("--final", action="store_true", help="Analyze final production dataset")
    args = ap.parse_args()

    analysis_dir = ROOT / "results" / "analysis"
    analysis_dir.mkdir(parents=True, exist_ok=True)

    if args.run:
        df = load_run(args.run)
        out_csv = analysis_dir / f"summary_{args.run}.csv"
        print(f"--- ANALYZING RUN: {args.run} ---")
    else:
        df = load_final()
        out_csv = analysis_dir / "summary_final.csv"
        main_summary_csv = ROOT / "results" / "summary.csv"
        print("--- ANALYZING FINAL PRODUCTION DATASET ---")

    if not df.empty:
        summary_df = summarize(df)
        summary_df.to_csv(out_csv, index=False)
        if not args.run:
            try:
                summary_df.to_csv(main_summary_csv, index=False)
            except Exception as e:
                print(f"Warning: Could not update {main_summary_csv} (file may be open/locked): {e}")
        
        print("Summary:")
        print(summary_df.to_string(index=False))
        print(f"\nSaved summary to: {out_csv}")
        
        pos_df = compute_positional_consistency(df)
        if not pos_df.empty:
            print("\nPositional Consistency:")
            print(pos_df.to_string(index=False))
    else:
        print("No matching response records found to analyze.")

