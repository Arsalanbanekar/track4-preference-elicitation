---
license: cc-by-4.0
language:
- en
configs:
- config_name: responses
  data_files: final_dataset_1620.csv
  default: true
- config_name: pairs
  data_files: preference_pairs.json
pretty_name: Elicitation Method vs. Measured LLM Preference (45 pairs, 2 models)
tags:
- llm-evaluation
- preference-elicitation
- positional-bias
- reliability
size_categories:
- 1K<n<10K
---

# Elicitation Method vs. Measured LLM Preference

1,620 raw model responses from a study asking whether the *elicitation method* changes the preference measured from an LLM. The study uses the forced-choice A/B template from Utility Engineering (Mazeika et al., 2025) as a baseline and compares it with two variants. This is an independent follow-up and is not affiliated with that paper's authors.

- **Code, analysis and full write-up:** https://github.com/Arsalanbanekar/track4-preference-elicitation (tag `v1.2-45pairs-scaleup` matches this dataset exactly)

## Design

- **45 preference pairs** (`preference_pairs.json`): mundane AI-assistant task trade-offs, e.g. "reversible incremental actions vs. single-batch throughput". No safety-policy triggers.
- **3 elicitation methods:** `forced_choice` (must answer A or B), `explicit_indifference` (A, B or INDIFFERENT), `preference_strength` (A or B plus a 1-5 strength rating).
- **2 orderings** (`original`, `flipped`) and **3 repetitions** per condition.
- **2 models via Groq**, temperature 0.2, reasoning effort "low" for both: `openai/gpt-oss-120b` and `qwen/qwen3.8-27b` (reasoning output hidden).
- 45 pairs x 3 methods x 2 orderings x 3 reps x 2 models = **1,620 rows**. All responses parsed validly.

## Files

- `final_dataset_1620.csv`: one row per model response.
- `preference_pairs.json`: the 45 pairs (`pair_id`, `category`, `option_a`, `option_b`).

## Key columns (`final_dataset_1620.csv`)

| Column | Meaning |
|---|---|
| `model`, `pair_id`, `method`, `ordering`, `repetition` | The experimental cell |
| `option_a_presented`, `option_b_presented` | Option text in the order shown to the model |
| `prompt`, `raw_response` | Exact prompt sent and raw model reply |
| `canonical_choice` | Answer mapped back to the original A/B labels (so flipped-order answers are comparable); `INDIFFERENT` where applicable |
| `strength` | 1-5 rating (preference_strength only) |
| `parsed.valid`, `parsed.indifferent` | Parser flags |
| `usage.*_tokens` | Token counts reported by the API |

**Positional consistency** (the main metric) = whether `canonical_choice` is the same for the `original` and `flipped` orderings with the same `pair_id`, `method`, `model` and `repetition`.

## Headline result (see the repo for full statistics)

Under plain forced choice, `openai/gpt-oss-120b` is consistent under reversed option order on 51.1% of comparisons (69/135), not distinguishable from a 50% chance floor (binomial p = 0.86). With an explicit INDIFFERENT option or a strength rating it is 71-74%. `qwen/qwen3.8-27b` is 78-83% under all three methods.

## Caveats

- Small item set (45 pairs), two models, one item domain (AI-assistant task trade-offs). Results may not generalize.
- The item set was extended in stages (15 to 30 to 45 pairs); the repo report discusses this and one result that changed as data was added.
- A small number of API calls initially failed with rate-limit errors and were re-sent until they succeeded. No response was collected under different settings.
- All quantities are behavioral response statistics under specific prompts. Nothing here supports claims about genuine internal preferences or welfare-relevant states.
- Model outputs were produced through Groq's API; check the applicable model and service terms before reuse.

## Provenance and AI assistance

Experiments were run and analyzed by the dataset author. The analysis pipeline and this card were prepared with assistance from Claude Code.

## Citation

Banekar, A. (2026). *Does the Elicitation Method Change the Preference We Measure?* GitHub: Arsalanbanekar/track4-preference-elicitation, tag v1.2-45pairs-scaleup.
