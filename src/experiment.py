import argparse, json, time, uuid
from datetime import datetime, timezone
from pathlib import Path
import yaml
from .client import GroqClient
from .parser import parse_response
from .prompts import build_prompt, flip_pair

ROOT = Path(__file__).resolve().parent.parent

def load_config():
    with open(ROOT/"config.yaml", encoding="utf-8") as f:
        return yaml.safe_load(f)

def load_pairs(path):
    with open(ROOT/path, encoding="utf-8") as f:
        return json.load(f)

def run(smoke_test=True, recover_qwen_ps=False, qwen_test=False, qwen_all_methods_test=False, qwen_ps_test=False, qwen_ei_test=False, recover_qwen_fc_ei=False):
    cfg = load_config()
    pairs = load_pairs(cfg["experiment"]["pairs_file"])
    models = [m for m in cfg["models"] if m.get("enabled", True)]
    methods = cfg["experiment"]["methods"]
    orderings = cfg["experiment"]["orderings"]
    reps = cfg["experiment"]["repetitions"]

    if qwen_ei_test:
        pairs = pairs[:1]
        models = [m for m in models if m["id"] == "qwen/qwen3.6-27b"]
        methods = ["explicit_indifference"]
        reps = 2
    elif qwen_ps_test:
        pairs = pairs[:1]
        models = [m for m in models if m["id"] == "qwen/qwen3.6-27b"]
        methods = ["preference_strength"]
        reps = 2
    elif qwen_all_methods_test:
        pairs = pairs[:1]
        models = [m for m in models if m["id"] == "qwen/qwen3.6-27b"]
        methods = ["forced_choice", "explicit_indifference", "preference_strength"]
        reps = 2
    elif qwen_test:
        pairs = pairs[:1]
        models = [m for m in models if m["id"] == "qwen/qwen3.6-27b"]
        methods = ["forced_choice"]
        reps = 3
    elif recover_qwen_fc_ei:
        models = [m for m in models if m["id"] == "qwen/qwen3.6-27b"]
        methods = ["forced_choice", "explicit_indifference"]
    elif recover_qwen_ps:
        models = [m for m in models if m["id"] == "qwen/qwen3.6-27b"]
        methods = ["preference_strength"]
    elif smoke_test:
        pairs = pairs[:cfg["experiment"]["smoke_test_pairs"]]
        models = models[:1]
        reps = 1

    calls = len(pairs) * len(models) * len(methods) * len(orderings) * reps
    print(f"Planned API calls: {calls}")

    confirm = input(f"Type RUN-{calls} to make these API calls: ").strip()
    if confirm != f"RUN-{calls}":
        print("Cancelled. No API calls made.")
        return

    client = GroqClient(cfg["api"]["base_url"])
    run_id = uuid.uuid4().hex[:12]
    runs_dir = ROOT / cfg["output"].get("runs_dir", "results/runs")
    runs_dir.mkdir(parents=True, exist_ok=True)
    out = runs_dir / f"raw_responses_{run_id}.jsonl"

    with out.open("w", encoding="utf-8") as f:
        for model_info in models:
            for pair in pairs:
                for method in methods:
                    for ordering in orderings:
                        oa, ob = pair["option_a"], pair["option_b"]
                        if ordering == "flipped":
                            oa, ob = flip_pair(oa, ob)
                        prompt = build_prompt(method, oa, ob)
                        for rep in range(1, reps + 1):
                            ts = datetime.now(timezone.utc).isoformat()
                            try:
                                result = client.chat(
                                    model_info["id"], prompt,
                                    temperature=cfg["api"]["temperature"],
                                    # max_completion_tokens=cfg["api"].get("max_completion_tokens", 512),
                                    max_completion_tokens=model_info.get(
                                        "max_completion_tokens",
                                        cfg["api"].get("max_completion_tokens", 512)
                                    ),
                                    reasoning_effort=model_info.get("reasoning_effort", cfg["api"].get("reasoning_effort")),
                                    reasoning_format=model_info.get("reasoning_format", cfg["api"].get("reasoning_format")),
                                )
                                parsed = parse_response(method, result["text"], ordering=ordering)
                                record = {
                                    "run_id": run_id,
                                    "timestamp_utc": ts,
                                    "model": model_info["id"],
                                    "pair_id": pair["pair_id"],
                                    "method": method,
                                    "ordering": ordering,
                                    "repetition": rep,
                                    "option_a_presented": oa,
                                    "option_b_presented": ob,
                                    "prompt": prompt,
                                    "raw_response": result["text"],
                                    "parsed": parsed,
                                    "canonical_choice": parsed.get("canonical_choice"),
                                    "strength": parsed.get("strength"),
                                    "usage": result["usage"],
                                }
                            except Exception as e:
                                record = {
                                    "run_id": run_id,
                                    "timestamp_utc": ts,
                                    "model": model_info["id"],
                                    "pair_id": pair["pair_id"],
                                    "method": method,
                                    "ordering": ordering,
                                    "repetition": rep,
                                    "prompt": prompt,
                                    "error": repr(e),
                                }
                            f.write(json.dumps(record, ensure_ascii=False) + "\n")
                            f.flush()
                            time.sleep(0.05)
    print(f"Finished. Raw results written to: {out}")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--main", action="store_true", help="Run full 540-call experiment")
    ap.add_argument("--recover_qwen_ps", action="store_true", help="Run 90-call Qwen preference_strength recovery")
    ap.add_argument("--qwen_test", action="store_true", help="Run 6-call temporary Qwen smoke test")
    ap.add_argument("--qwen_all_methods_test", action="store_true", help="Run 12-call temporary Qwen all-methods smoke test")
    ap.add_argument("--qwen_ps_test", action="store_true", help="Run 4-call temporary Qwen preference_strength smoke test")
    ap.add_argument("--qwen_ei_test", action="store_true", help="Run 4-call temporary Qwen explicit_indifference smoke test")
    ap.add_argument(
        "--recover_qwen_fc_ei",
        action="store_true",
        help="Run 180-call Qwen forced_choice + explicit_indifference recovery"
    )
    args = ap.parse_args()
    smoke = not (args.main or args.recover_qwen_ps or args.qwen_test or args.qwen_all_methods_test or args.qwen_ps_test or args.qwen_ei_test or args.recover_qwen_fc_ei)
    run(
        smoke_test=smoke,
        recover_qwen_ps=args.recover_qwen_ps,
        qwen_test=args.qwen_test,
        qwen_all_methods_test=args.qwen_all_methods_test,
        qwen_ps_test=args.qwen_ps_test,
        qwen_ei_test=args.qwen_ei_test,
        recover_qwen_fc_ei=args.recover_qwen_fc_ei
    )
