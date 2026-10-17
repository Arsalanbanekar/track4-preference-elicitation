"""Runner for the full inbox study (design: STUDY_DESIGN_inbox.md).

Every item is asked in four conditions, crossed with two wordings, two option
orders, two models and three repetitions:

    C1  bare direct question        (main study's forced-choice prompt)
    C2  context-matched direct      (same prompt plus the email's facts)
    C3  inbox                       (role, four emails, natural request)
    C4  inbox + evaluation notice   (one sentence added to the system prompt)

    python -m src.inbox_study --preview P01          # print every prompt for one item
    python -m src.inbox_study --dry_run              # 16 calls, written to a dryrun_ file
    python -m src.inbox_study --batch 1              # 384 calls (items 1-4)
    python -m src.inbox_study --batch 1 --complete_missing
    python -m src.inbox_study --batch 1 --model qwen # one model only

No API call is made until the exact confirmation code is typed.
"""
import argparse, json, os, random, time, uuid
from datetime import datetime, timezone
from pathlib import Path

from .parser import parse_response
from .pilot_inbox import call_model
from .prompts import load_template

ROOT = Path(__file__).resolve().parent.parent
ITEMS_FILE = ROOT / "study" / "inbox_items.json"
PAIRS_FILE = ROOT / "data" / "preference_pairs.json"
OUT_DIR = ROOT / "results" / "inbox_study"

CONDITIONS = ["C1_bare", "C2_context", "C3_inbox", "C4_inbox_eval"]
WORDINGS = ["W1", "W2"]
ORDERINGS = ["original", "swapped"]
REPETITIONS = 3
BATCH_SIZE = 4
ORDER_SEED = 20261017

# Same settings as pilot round 2. Qwen's gap after an inbox call is a full
# minute because one long reply can use most of its 1000 output tokens per
# minute; after a short direct answer 20 s is enough. GPT-OSS-120B's gap keeps
# it under 8K tokens per minute.
MODELS = {
    "gpt": {"id": "openai/gpt-oss-120b", "reasoning_effort": "low",
            "max_completion_tokens": 2048, "gap_after": {"direct": 3, "inbox": 5}},
    "qwen": {"id": "qwen/qwen3.8-27b", "reasoning_effort": "low", "reasoning_format": "parsed",
             "max_completion_tokens": 1000, "gap_after": {"direct": 20, "inbox": 65}},
}


def load_spec():
    with ITEMS_FILE.open(encoding="utf-8") as f:
        return json.load(f)


def load_pairs():
    with PAIRS_FILE.open(encoding="utf-8") as f:
        return {p["pair_id"]: p for p in json.load(f)}


def item_index(spec, item_id):
    return [it["item_id"] for it in spec["items"]].index(item_id)


def options_shown(item, wording, ordering):
    """(first, second) option texts as embedded in a sentence, and which canonical option is first."""
    w = item["wordings"][wording]
    return ((w["A"], w["B"], "A") if ordering == "original" else (w["B"], w["A"], "B"))


def as_sentence(text):
    return text[0].upper() + text[1:] + "."


def direct_messages(item, pair, wording, ordering, with_context):
    first, second, first_key = options_shown(item, wording, ordering)
    if wording == "W1":
        # The main study's exact option text.
        a, b = (pair["option_a"], pair["option_b"]) if ordering == "original" else (pair["option_b"], pair["option_a"])
    else:
        a, b = as_sentence(first), as_sentence(second)
    template = load_template("forced_choice")
    if with_context:
        template = template.replace("\n\nOption A:", f"\n\nContext:\n{item['facts']}\n\nOption A:", 1)
    return [{"role": "user", "content": template.format(option_a=a, option_b=b)}], first_key


def inbox_emails(spec, item, wording, ordering):
    """The four emails: three fixed distractors plus the decision email at position 2 or 3."""
    i = item_index(spec, item["item_id"])
    pool = spec["distractors"]
    distractors = [pool[(3 * i + k) % len(pool)] for k in range(3)]
    first, second, first_key = options_shown(item, wording, ordering)
    decision = {
        "from": item["sender"], "subject": item["subject"],
        "body": f"Hi,\n\n{item['facts']}\n\n{item['chooser']} can either {first}, or {second}. {item['question']}",
    }
    position = 2 if i % 2 == 0 else 3
    emails = distractors[:position - 1] + [decision] + distractors[position - 1:]
    return emails, first_key


def inbox_messages(spec, item, wording, ordering, eval_aware):
    emails, first_key = inbox_emails(spec, item, wording, ordering)
    system = spec["system_prompt"] + (f" {spec['eval_aware_sentence']}" if eval_aware else "")
    parts = [f"You have {len(emails)} unread emails."]
    for n, e in enumerate(emails, 1):
        parts.append(f"=== Email {n} of {len(emails)} ===\nFrom: {e['from']}\nSubject: {e['subject']}\n\n{e['body']}")
    parts.append(spec["final_instruction"])
    return [{"role": "system", "content": system},
            {"role": "user", "content": "\n\n".join(parts)}], first_key


def build_messages(spec, pairs, item, condition, wording, ordering):
    pair = pairs[item["pair_id"]]
    if condition == "C1_bare":
        return direct_messages(item, pair, wording, ordering, with_context=False)
    if condition == "C2_context":
        return direct_messages(item, pair, wording, ordering, with_context=True)
    return inbox_messages(spec, item, wording, ordering, eval_aware=(condition == "C4_inbox_eval"))


def batch_items(spec, batch):
    items = spec["items"]
    if batch is None:
        return items
    return items[(batch - 1) * BATCH_SIZE: batch * BATCH_SIZE]


def work_items(spec, items, models, dry_run=False):
    """Every cell for these items, in a fixed random order per model."""
    orderings = ["swapped"] if dry_run else ORDERINGS
    reps = 1 if dry_run else REPETITIONS
    cells = [(m, it, c, w, o, r)
             for m in models for it in items for c in CONDITIONS
             for w in WORDINGS for o in orderings for r in range(1, reps + 1)]
    rng = random.Random(ORDER_SEED)
    rng.shuffle(cells)
    return cells


def cell_key(model_id, item_id, condition, wording, ordering, rep):
    return (model_id, item_id, condition, wording, ordering, rep)


def load_records():
    rows = []
    for path in sorted(OUT_DIR.glob("raw_responses_*.jsonl")):
        with path.open(encoding="utf-8") as f:
            rows.extend(json.loads(line) for line in f if line.strip())
    return rows


def preview(spec, pairs, item_id):
    item = next(it for it in spec["items"] if it["item_id"] == item_id)
    for c in CONDITIONS:
        for w in WORDINGS:
            for o in ORDERINGS:
                messages, first = build_messages(spec, pairs, item, c, w, o)
                print(f"\n######## {item_id} | {c} | {w} | {o} (option {first} first) ########")
                for m in messages:
                    print(f"[{m['role'].upper()}]\n{m['content']}\n")


def run(batch=None, dry_run=False, complete_missing=False, model_filter=None):
    spec, pairs = load_spec(), load_pairs()
    models = [MODELS[k] for k in (model_filter or MODELS)]
    items = [spec["items"][0]] if dry_run else batch_items(spec, batch)
    cells = work_items(spec, items, models, dry_run=dry_run)

    if complete_missing:
        # Done = any study run holds a record for the cell with no "error" key.
        # A truncated or unparseable answer is a result, not a failure.
        done = {cell_key(r["model"], r["item_id"], r["condition"], r["wording"], r["ordering"], r["repetition"])
                for r in load_records() if "error" not in r}
        before = len(cells)
        cells = [c for c in cells
                 if cell_key(c[0]["id"], c[1]["item_id"], c[2], c[3], c[4], c[5]) not in done]
        print(f"Completion check: {before} cells in scope, {before - len(cells)} already done, {len(cells)} missing.")

    calls = len(cells)
    scope = "dry run" if dry_run else (f"batch {batch}" if batch else "all items")
    print(f"Scope: {scope}, items {', '.join(it['item_id'] for it in items)}, "
          f"models {', '.join(m['id'] for m in models)}")
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
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / f"{'dryrun' if dry_run else 'raw_responses'}_{run_id}.jsonl"
    print(f"Run ID: {run_id}\nWriting to: {out}")

    # One queue per model; always run whichever model can go soonest, so
    # GPT-OSS calls fill Qwen's waits.
    queues = {m["id"]: [c for c in cells if c[0]["id"] == m["id"]] for m in models}
    ready_at = {mid: 0.0 for mid in queues}
    done_n = errors = truncated = 0
    with out.open("w", encoding="utf-8") as f:
        while any(queues.values()):
            mid = min((m for m in queues if queues[m]), key=lambda m: ready_at[m])
            wait = ready_at[mid] - time.monotonic()
            if wait > 0:
                time.sleep(wait)
            model, item, condition, wording, ordering, rep = queues[mid].pop(0)
            messages, first = build_messages(spec, pairs, item, condition, wording, ordering)
            kind = "direct" if condition in ("C1_bare", "C2_context") else "inbox"
            record = {
                "run_id": run_id, "study": "inbox_study_v1",
                "batch": None if dry_run else batch,
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                "model": model["id"], "item_id": item["item_id"], "pair_id": item["pair_id"],
                "condition": condition, "wording": wording, "ordering": ordering,
                "first_option": first, "repetition": rep, "messages": messages,
            }
            done_n += 1
            prefix = f"[{done_n}/{calls}] {model['id']} {item['item_id']} {condition} {wording} {ordering} rep{rep}"
            try:
                result = call_model(client, model, messages)
                record.update({"raw_response": result["text"], "reasoning": result["reasoning"],
                               "finish_reason": result["finish_reason"], "usage": result["usage"]})
                extra = ""
                if kind == "direct":
                    parsed = parse_response("forced_choice", result["text"],
                                            ordering="flipped" if ordering == "swapped" else "original")
                    record["parsed"] = parsed
                    record["canonical_choice"] = parsed.get("canonical_choice")
                    extra = f" valid={parsed.get('valid')} canonical={parsed.get('canonical_choice')}"
                truncated += result["finish_reason"] == "length"
                print(f"{prefix} -> finish={result['finish_reason']} "
                      f"completion_tokens={result['usage'].get('completion_tokens')}{extra}")
            except Exception as e:
                record["error"] = repr(e)
                errors += 1
                print(f"{prefix} -> ERROR: {e!r}")
            ready_at[mid] = time.monotonic() + model["gap_after"][kind]
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
            f.flush()

    print(f"Finished. {done_n}/{calls} calls, {errors} errors, {truncated} cut off at the token cap.")
    print(f"Raw results: {out}")
    if errors:
        print("Re-run the same command with --complete_missing to fill the gaps.")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Inbox study runner (see STUDY_DESIGN_inbox.md)")
    ap.add_argument("--preview", metavar="ITEM", help="Print every prompt for one item; no API calls")
    ap.add_argument("--dry_run", action="store_true", help="16-call check on the first item")
    ap.add_argument("--batch", type=int, choices=[1, 2, 3, 4], help="Run one batch of 4 items")
    ap.add_argument("--complete_missing", action="store_true", help="Run only cells with no successful record")
    ap.add_argument("--model", choices=sorted(MODELS), help="Run one model only")
    args = ap.parse_args()
    if args.preview:
        preview(load_spec(), load_pairs(), args.preview)
    elif args.dry_run or args.batch:
        run(batch=args.batch, dry_run=args.dry_run, complete_missing=args.complete_missing,
            model_filter=[args.model] if args.model else None)
    else:
        ap.error("choose --preview ITEM, --dry_run, or --batch N")
