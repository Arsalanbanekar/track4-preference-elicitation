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

# Does the Way We Ask Change an AI Model's Preference?

1,620 answers from two AI models. The models were asked the same 45 choices in three different formats, to test whether the format of the question changes the preference we measure.

The plain A/B format comes from *Utility Engineering* (Mazeika et al., 2025). This is an independent study, not affiliated with that paper's authors.

- **Code, analysis and full report:** https://github.com/Arsalanbanekar/track4-preference-elicitation. Tag `v1.2-45pairs-scaleup` matches this dataset exactly.

## What was asked

- **45 choices** (`preference_pairs.json`): everyday trade-offs for an AI assistant, such as *small steps that can be undone* vs *one batch for speed*. Nothing sensitive.
- **3 formats:**
  - `forced_choice`: must answer A or B
  - `explicit_indifference`: A, B or INDIFFERENT
  - `preference_strength`: A or B, plus a 1–5 strength rating
- **Both option orders** (`original`, `flipped`), **3 repeats** each.
- **2 models via Groq:** `openai/gpt-oss-120b` and `qwen/qwen3.8-27b`, both at temperature 0.2 and reasoning effort "low". Qwen's reasoning text is hidden.
- **Total:** 45 × 3 × 2 × 3 × 2 = **1,620 rows**, all valid.

## Files

- `final_dataset_1620.csv`: one row per answer.
- `preference_pairs.json`: the 45 choices (`pair_id`, `category`, `option_a`, `option_b`).

## Main columns

| Column | Meaning |
|---|---|
| `model`, `pair_id`, `method`, `ordering`, `repetition` | Which question this row answers |
| `option_a_presented`, `option_b_presented` | The options in the order the model saw them |
| `prompt`, `raw_response` | The exact question and the model's exact reply |
| `canonical_choice` | The answer mapped back to the original A/B labels, so swapped-order answers can be compared (or `INDIFFERENT`) |
| `strength` | The 1–5 rating (strength format only) |
| `parsed.valid`, `parsed.indifferent` | Whether the reply could be read, and whether it said "indifferent" |
| `usage.*_tokens` | Token counts reported by the API |

**The main measure, positional consistency:** whether `canonical_choice` is the same for the `original` and `flipped` order, for the same `pair_id`, `method`, `model` and `repetition`.

## Main result

**Under the plain A/B question:**
- **`openai/gpt-oss-120b`** gave the same answer after the options were swapped only 51.1% of the time (69 of 135). That is no different from a coin flip (p = 0.86).
- **Other formats:** with a "no preference" option or a strength rating, it was consistent 71–74% of the time.
- **`qwen/qwen3.8-27b`** was consistent 78–83% of the time in all three formats.

## Things to know

- **Small:** 45 choices, two models, one kind of choice. Results may not hold elsewhere.
- **The study grew in stages** (15 → 30 → 45 choices). The report discusses this, and one result that changed as data was added.
- **A few API calls failed** on rate limits and were re-sent unchanged until they worked. No answer was collected under different settings.
- **These numbers describe behaviour under specific prompts.** They say nothing about whether models have real preferences or inner states.
- **The answers came through Groq's API.** Check the model and service terms before reusing them.

## Provenance

The experiments were run and analysed by the dataset author.

## Citation

Banekar, A. (2026). *Does the Elicitation Method Change the Preference We Measure?* GitHub: Arsalanbanekar/track4-preference-elicitation, tag v1.2-45pairs-scaleup.
