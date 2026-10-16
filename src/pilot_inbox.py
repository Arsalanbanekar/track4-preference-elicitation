"""Pilot for the agentic inbox study (see PILOT_INBOXES.md).

Each inbox call gives a model a job (system prompt) and a four-email inbox, one
email of which asks it to choose between the two options of a preference pair.
The order of the two options is swapped in half the calls so positional
consistency stays measurable.

Each control call asks the main study's forced-choice question for the same
pair, with the facts from the decision email added as context but no job and no
inbox. Comparing the three conditions separates two explanations for a changed
answer: the added facts (bare question vs. control) and the work setting itself
(control vs. inbox).

Pilot data is for checking the design only. It is never pooled with the main
study or with any later confirmatory run.

    python -m src.pilot_inbox --preview [--control]   # print prompts, no API calls
    python -m src.pilot_inbox --dry_run               # 4 inbox calls, dryrun_ file
    python -m src.pilot_inbox --control --dry_run     # 4 control calls, dryrun_ file
    python -m src.pilot_inbox                         # inbox, normal condition
    python -m src.pilot_inbox --eval_aware            # inbox, evaluation notice added
    python -m src.pilot_inbox --control               # context-matched direct question
    python -m src.pilot_inbox --complete_missing [--eval_aware | --control]
    python -m src.pilot_inbox --show RUN_ID           # readable replies file, no API calls

Every command takes --round (default 2). Round 1 is kept reproducible as run.
"""
import argparse, json, os, time, uuid
from datetime import datetime, timezone
from pathlib import Path

from .parser import parse_response
from .prompts import load_template

ROOT = Path(__file__).resolve().parent.parent
PAIRS_FILE = ROOT / "data" / "preference_pairs.json"

TEMPERATURE = 0.2
ORDERINGS = ["original", "swapped"]
REPETITIONS = 3

# Same models and reasoning effort as the main ("low") study. Token caps are
# higher because a reply to a whole inbox is longer than a one-word answer.
# Groq rejects a Qwen request whose cap exceeds the account's 1000
# output-tokens-per-minute limit, so 1000 is the highest Qwen cap possible, and
# a full minute between Qwen inbox calls keeps it under that limit.
GPT = {"id": "openai/gpt-oss-120b", "reasoning_effort": "low",
       "max_completion_tokens": 2048, "delay_seconds": 3, "control_delay_seconds": 3}
ROUNDS = {
    1: {
        "inboxes": ROOT / "pilot" / "inboxes.json",
        "out_dir": ROOT / "results" / "pilot_inbox",
        "models": [GPT, {"id": "qwen/qwen3.8-27b", "reasoning_effort": "low",
                         "reasoning_format": "hidden", "max_completion_tokens": 900,
                         "delay_seconds": 45}],
    },
    2: {
        "inboxes": ROOT / "pilot" / "inboxes_round2.json",
        "out_dir": ROOT / "results" / "pilot_inbox_round2",
        # "parsed" returns Qwen's reasoning in its own field instead of
        # discarding it; generation is unchanged. Needed to check whether the
        # model mentions being tested.
        "models": [GPT, {"id": "qwen/qwen3.8-27b", "reasoning_effort": "low",
                         "reasoning_format": "parsed", "max_completion_tokens": 1000,
                         "delay_seconds": 65, "control_delay_seconds": 20}],
    },
}


def load_inboxes(round_no=2):
    with ROUNDS[round_no]["inboxes"].open(encoding="utf-8") as f:
        return json.load(f)


def load_pairs():
    with PAIRS_FILE.open(encoding="utf-8") as f:
        return {p["pair_id"]: p for p in json.load(f)}


def build_messages(spec, inbox, ordering, eval_aware):
    """System and user messages for one inbox in one option order."""
    first, second = ("A", "B") if ordering == "original" else ("B", "A")
    system = inbox["system_prompt"]
    if eval_aware:
        system = f"{system} {spec['eval_aware_sentence']}"

    emails = inbox["emails"]
    parts = [f"You have {len(emails)} unread emails."]
    for i, email in enumerate(emails, 1):
        body = (email["body"]
                .replace("{first}", inbox["options"][first])
                .replace("{second}", inbox["options"][second]))
        parts.append(f"=== Email {i} of {len(emails)} ===\n"
                     f"From: {email['from']}\n"
                     f"Subject: {email['subject']}\n\n{body}")
    parts.append(spec["final_instruction"])
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": "\n\n".join(parts)},
    ], first


def build_control_messages(control, pair, ordering):
    """The main study's forced-choice prompt with the email's facts added as context."""
    first = "A" if ordering == "original" else "B"
    oa, ob = pair["option_a"], pair["option_b"]
    if ordering == "swapped":
        oa, ob = ob, oa
    template = load_template("forced_choice").replace(
        "\n\nOption A:", f"\n\nContext:\n{control['context']}\n\nOption A:", 1)
    prompt = template.format(option_a=oa, option_b=ob)
    return [{"role": "user", "content": prompt}], first


def work_items(spec, models, control=False, dry_run=False):
    """(model, item, ordering, rep) tuples. Models are interleaved so Qwen's
    wait overlaps GPT-OSS calls."""
    if control:
        items = spec["controls"]
        if dry_run:
            items = [c for c in items if c["item_id"] == "P25"]
    else:
        items = spec["inboxes"]
        if dry_run:
            target = spec.get("dry_run_inbox", "P25")
            items = [b for b in items if b["inbox_id"] == target]
    reps = 1 if dry_run else REPETITIONS
    return [
        (model, item, ordering, rep)
        for item in items
        for ordering in ORDERINGS
        for rep in range(1, reps + 1)
        for model in models
    ]


def load_pilot_records(out_dir):
    """Records from pilot runs only; dry-run files are named differently and skipped."""
    rows = []
    for path in sorted(out_dir.glob("raw_responses_*.jsonl")):
        with path.open(encoding="utf-8") as f:
            rows.extend(json.loads(line) for line in f if line.strip())
    return rows


def call_model(client, model, messages):
    kwargs = {
        "model": model["id"],
        "messages": messages,
        "temperature": TEMPERATURE,
        "max_completion_tokens": model["max_completion_tokens"],
        "reasoning_effort": model["reasoning_effort"],
    }
    if model.get("reasoning_format"):
        kwargs["reasoning_format"] = model["reasoning_format"]
    r = client.chat.completions.create(**kwargs)
    msg = r.choices[0].message
    u = getattr(r, "usage", None)
    return {
        "text": msg.content or "",
        "reasoning": getattr(msg, "reasoning", None),
        "finish_reason": r.choices[0].finish_reason,
        "usage": {
            "prompt_tokens": getattr(u, "prompt_tokens", None) if u else None,
            "completion_tokens": getattr(u, "completion_tokens", None) if u else None,
            "total_tokens": getattr(u, "total_tokens", None) if u else None,
        },
    }


def write_readable(records, path):
    """One markdown file with every reply, for reading and hand classification."""
    lines = [f"# Pilot replies ({len(records)} calls)", ""]
    for r in records:
        lines.append(f"## {r['inbox_id']} | {r['ordering']} (option {r['first_option']} listed first) | "
                     f"{r['model']} | rep {r['repetition']} | {r['condition']}")
        lines.append("")
        if "error" in r:
            lines.append(f"**ERROR:** {r['error']}")
        else:
            lines.append(f"*finish: {r['finish_reason']}, completion tokens: "
                         f"{r['usage'].get('completion_tokens')}*")
            if r["condition"] == "control":
                lines.append(f"*parsed canonical choice: {r.get('canonical_choice')}*")
            lines.append("")
            lines.append(r["raw_response"] or "*(empty reply)*")
            if r.get("reasoning"):
                lines.append("")
                lines.append("<details><summary>Reasoning</summary>")
                lines.append("")
                lines.append(r["reasoning"])
                lines.append("")
                lines.append("</details>")
        lines.append("")
        lines.append("---")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def show(run_id):
    matches = [p for cfg in ROUNDS.values() for p in cfg["out_dir"].glob(f"*_{run_id}.jsonl")]
    if not matches:
        print(f"No pilot file found for run {run_id}")
        return
    with matches[0].open(encoding="utf-8") as f:
        records = [json.loads(line) for line in f if line.strip()]
    out = matches[0].parent / f"replies_{run_id}.md"
    write_readable(records, out)
    print(f"Wrote {len(records)} replies to: {out}")


def preview(spec, eval_aware, control):
    if control:
        pairs = load_pairs()
        for c in spec["controls"]:
            for ordering in ORDERINGS:
                messages, first = build_control_messages(c, pairs[c["pair_id"]], ordering)
                print(f"\n######## control {c['item_id']} | {ordering} (option {first} listed first) ########")
                print(f"[USER]\n{messages[0]['content']}")
        return
    for inbox in spec["inboxes"]:
        for ordering in ORDERINGS:
            messages, first = build_messages(spec, inbox, ordering, eval_aware)
            print(f"\n######## {inbox['inbox_id']} | {ordering} (option {first} listed first) ########")
            print(f"[SYSTEM]\n{messages[0]['content']}\n")
            print(f"[USER]\n{messages[1]['content']}")


def run(round_no=2, dry_run=False, eval_aware=False, control=False, complete_missing=False):
    cfg = ROUNDS[round_no]
    spec = load_inboxes(round_no)
    pairs = load_pairs()
    if control and eval_aware:
        raise SystemExit("--eval_aware applies to inboxes only, not to --control.")
    if control and "controls" not in spec:
        raise SystemExit(f"Round {round_no} has no control items.")
    condition = "control" if control else ("eval_aware" if eval_aware else "normal")
    items = work_items(spec, cfg["models"], control=control, dry_run=dry_run)

    def item_id(item):
        return item["item_id"] if control else item["inbox_id"]

    if complete_missing:
        # A cell counts as done if any pilot run of this round holds a record
        # for it with no "error" key. A truncated reply is a result, not a failure.
        done = {
            (r["condition"], r["model"], r["inbox_id"], r["ordering"], r["repetition"])
            for r in load_pilot_records(cfg["out_dir"]) if "error" not in r
        }
        before = len(items)
        items = [w for w in items
                 if (condition, w[0]["id"], item_id(w[1]), w[2], w[3]) not in done]
        print(f"Completion check: {before} cells in scope, "
              f"{before - len(items)} already done, {len(items)} missing.")

    calls = len(items)
    print(f"Round {round_no}, condition: {condition}" + ("  (dry run)" if dry_run else ""))
    print(f"Planned API calls: {calls}")
    if calls == 0:
        return
    confirm = input(f"Type RUN-{calls} to make these API calls: ").strip()
    if confirm != f"RUN-{calls}":
        print("Cancelled. No API calls made.")
        return

    from dotenv import load_dotenv
    from groq import Groq
    load_dotenv(ROOT / ".env")
    key = os.getenv("GROQ_API_KEY")
    if not key:
        raise RuntimeError("GROQ_API_KEY is not set. Copy .env.example to .env and add the key.")
    client = Groq(api_key=key)

    run_id = uuid.uuid4().hex[:12]
    out_dir = cfg["out_dir"]
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"{'dryrun' if dry_run else 'raw_responses'}_{run_id}.jsonl"
    print(f"Run ID: {run_id}")
    print(f"Writing to: {out}")

    last_call = {}
    records = []
    with out.open("w", encoding="utf-8") as f:
        for i, (model, item, ordering, rep) in enumerate(items, 1):
            delay = model.get("control_delay_seconds", model["delay_seconds"]) if control else model["delay_seconds"]
            wait = delay - (time.monotonic() - last_call.get(model["id"], -1e9))
            if wait > 0:
                time.sleep(wait)
            if control:
                messages, first = build_control_messages(item, pairs[item["pair_id"]], ordering)
            else:
                messages, first = build_messages(spec, item, ordering, eval_aware)
            record = {
                "run_id": run_id,
                "round": round_no,
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                "condition": condition,
                "model": model["id"],
                "inbox_id": item_id(item),
                "source_pair": item["pair_id"] if control else item["source_pair"],
                "ordering": ordering,
                "first_option": first,
                "repetition": rep,
                "messages": messages,
            }
            prefix = f"[{i}/{calls}] {model['id']} {item_id(item)} {ordering} rep{rep}"
            try:
                result = call_model(client, model, messages)
                record.update({
                    "raw_response": result["text"],
                    "reasoning": result["reasoning"],
                    "finish_reason": result["finish_reason"],
                    "usage": result["usage"],
                })
                extra = ""
                if control:
                    parsed = parse_response("forced_choice", result["text"],
                                            ordering="flipped" if ordering == "swapped" else "original")
                    record["parsed"] = parsed
                    record["canonical_choice"] = parsed.get("canonical_choice")
                    extra = f" valid={parsed.get('valid')} canonical={parsed.get('canonical_choice')}"
                print(f"{prefix} -> finish={result['finish_reason']} "
                      f"completion_tokens={result['usage'].get('completion_tokens')} "
                      f"reply_chars={len(result['text'])}{extra}")
            except Exception as e:
                record["error"] = repr(e)
                print(f"{prefix} -> ERROR: {e!r}")
            last_call[model["id"]] = time.monotonic()
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
            f.flush()
            records.append(record)

    readable = out_dir / f"replies_{run_id}.md"
    write_readable(records, readable)
    errors = sum("error" in r for r in records)
    truncated = sum(r.get("finish_reason") == "length" for r in records)
    print(f"Finished. {len(records)}/{calls} calls, {errors} errors, {truncated} cut off at the token cap.")
    print(f"Raw results: {out}")
    print(f"Readable replies: {readable}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Agentic inbox pilot (see PILOT_INBOXES.md)")
    ap.add_argument("--round", type=int, default=2, choices=sorted(ROUNDS), help="Pilot round (default 2)")
    ap.add_argument("--preview", action="store_true", help="Print every rendered prompt; no API calls")
    ap.add_argument("--dry_run", action="store_true", help="4-call check: one item, both orders, both models, 1 rep")
    ap.add_argument("--eval_aware", action="store_true", help="Add the evaluation notice to the system prompt")
    ap.add_argument("--control", action="store_true", help="Context-matched direct question instead of the inbox")
    ap.add_argument("--complete_missing", action="store_true", help="Run only cells with no successful pilot record")
    ap.add_argument("--show", type=str, default=None, metavar="RUN_ID", help="Write a readable replies file; no API calls")
    args = ap.parse_args()
    if args.show:
        show(args.show)
    elif args.preview:
        preview(load_inboxes(args.round), args.eval_aware, args.control)
    else:
        run(round_no=args.round, dry_run=args.dry_run, eval_aware=args.eval_aware,
            control=args.control, complete_missing=args.complete_missing)
