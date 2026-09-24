# Pre-registration: does reasoning effort change elicitation reliability?

**Status:** written before any "medium" data was collected. Committed on the
`medium-reasoning-followup` branch; the commit timestamp is the record.

**Author:** Arsalan Banekar. Analysis pipeline built with assistance from Claude Code.

## Why pre-register this one

The completed study (45 pairs, both models at `reasoning_effort: "low"`,
tag `v1.2.1`) grew its item set in three stages, 15 to 30 to 45 pairs, and the
final extension was decided after seeing an interim result. That is a
data-dependent stopping rule and a fair criticism of that study. This follow-up
fixes its design in advance so the same criticism cannot apply.

## Question

Does the reasoning effort a model is run at change the reliability of
preference elicitation, measured as positional consistency?

The completed study found that GPT-OSS-120B's forced-choice answers are at the
50% chance floor (51.1%) under reversed option order, while its
explicit-indifference and preference-strength answers are not (71.1%, 74.1%),
and that Qwen3.8-27B does not show that collapse (77.8%-83.0%). All of that was
measured at effort "low". If those numbers move at "medium", reliability is
partly a function of generation configuration rather than of the elicitation
method alone, which would matter to anyone reporting elicited preferences
without stating the effort setting.

## Design, fixed in advance

- **Items:** the same 45 pairs (P01-P45), unchanged. No new pairs will be
  written for this study.
- **Models:** `openai/gpt-oss-120b` and `qwen/qwen3.8-27b`, both at
  `reasoning_effort: "medium"`. Every other setting matches the completed study
  (temperature 0.2, 3 methods, both orderings, 3 repetitions).
- **Sample size:** 45 x 2 x 3 x 2 x 3 = 1,620 responses. **This is the final
  number.** The item set will not be extended, whatever the results show.
- **Batching:** three batches of 15 pairs, for operational safety only. Batch
  boundaries are not decision points; all three will be collected before the
  confirmatory analysis is run.
- **Pairing:** each "medium" response is compared against the "low" response
  for the same model, pair, method, ordering and repetition index.

## Hypotheses

- **H1 (primary, directional):** GPT-OSS-120B's forced-choice positional
  consistency at "medium" is higher than at "low" (51.1%).
- **H2 (primary):** the within-model spread across the three methods for
  GPT-OSS-120B (23.0 points at "low") is smaller at "medium".
- **H3 (secondary):** Qwen3.8-27B's consistency changes less than
  GPT-OSS-120B's, i.e. the effort effect is model-dependent.

We have no strong prior on direction for H2 or H3. H1 is directional because
more deliberation plausibly stabilizes a near-random choice, but the opposite
result is a publishable answer to the same question.

## Analysis, fixed in advance

- **Primary test:** for each of the 6 method x model cells, a paired Wilcoxon
  signed-rank test across the 45 pairs, comparing per-pair positional
  consistency at "medium" against "low". Six comparisons, Holm-corrected as one
  family.
- **Chance-floor test:** a two-sided exact binomial test of each cell's
  consistent count out of 135 against p = 0.5, as in the completed study.
- **Descriptive:** the same indifference-rate, strength-distribution and
  token-usage summaries.
- **Excluded by design:** the easy/ambiguous stratification. As noted in the
  completed study's report, difficulty is derived from the same responses being
  analyzed, so it is descriptive only and will not be used for any claim here.
- **alpha = 0.05 throughout.**

## What would change our conclusion

- If no cell moves significantly, we report that effort does not measurably
  change elicitation reliability at this sample size, and the completed study's
  findings are not effort-specific.
- If GPT-OSS-120B's forced-choice consistency rises above chance at "medium",
  the completed study's headline result is specific to low effort, and we say so
  plainly, including in any updated version of that write-up.

## Known risks, recorded before collection

- **Truncation.** Higher effort means more hidden reasoning tokens. If reasoning
  fills `max_completion_tokens`, answers come back blank. Blank or unparseable
  responses will be reported as such, never silently dropped.
- **Qwen's token cap.** Groq rejects a request whose `max_completion_tokens`
  exceeds the account's 1000 output-tokens-per-minute limit, so Qwen is capped
  at 900 here versus 1024 in the completed study. This is a real difference
  between the two studies and will be disclosed. If truncation appears at 900,
  that is a finding about the feasibility of running this model at medium effort
  on this tier, not a reason to quietly change the cap mid-study.
- **Rate limits.** Individual calls that fail on rate limits will be re-sent
  unchanged until they succeed, as in the completed study.

## Isolation from the published study

Separate branch, separate config (`config_medium.yaml`), separate output
directories (`results/runs_medium/`, `results/analysis_medium/`). Nothing in
this study is added to `final_production_runs` or to
`results/analysis/final_dataset_1620.csv`. The published dataset and its tag
`v1.2.1` are unaffected.
