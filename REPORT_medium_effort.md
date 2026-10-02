# Does Reasoning Effort Change Elicitation Reliability? A Pre-Registered Null

*Follow-up to "Does the Elicitation Method Change the Preference We Measure?" (tag `v1.2.1`)*

**Arsalan Banekar**, Independent Researcher. September 2026.

**Result in one line:** raising both models from reasoning effort "low" to "medium" changed positional consistency in none of the six method × model cells, so the main study's finding is not an artifact of a small thinking budget.

Pre-registration: [`PREREGISTRATION_medium_effort.md`](PREREGISTRATION_medium_effort.md), committed before any data was collected. Hypotheses, sample size, tests and correction family were all fixed in advance.

## 1. Why this study exists

The main study found that GPT-OSS-120B's forced-choice answers are statistically indistinguishable from a coin flip under reversed option order (51.1%), while an explicit-indifference option or a 1–5 strength rating raises consistency to 71–74%. All of that was measured at `reasoning_effort: "low"`.

The obvious objection: maybe the model simply was not thinking hard enough. If so, the finding is about a generation setting rather than about the elicitation format, and anyone running the same prompts at a higher effort would not reproduce it.

This study tests that objection directly. It also fixes a methodological weakness of the main study, whose item set grew 15 → 30 → 45 pairs with the last extension decided after an interim look. Here the design was fixed in writing beforehand.

## 2. Design

Identical to the main study except for one variable.

| | Main study | This study |
|---|---|---|
| Pairs | 45 (P01–P45) | **same 45, unchanged** |
| Models | GPT-OSS-120B, Qwen3.8-27B | same |
| Methods | forced choice, explicit indifference, preference strength | same |
| Orderings / repetitions | original + flipped, 3 reps | same |
| Temperature | 0.2 | same |
| **Reasoning effort** | **low** | **medium** |
| Responses | 1,620 | 1,620 |

Each medium response is paired against the low response for the same model, pair, method, ordering and repetition index. Collection ran in three batches of 15 pairs for operational safety; batch boundaries were not decision points, and no analysis was run until all three were in.

**Primary test (pre-specified):** per method × model cell, a paired Wilcoxon signed-rank test across the 45 pairs comparing per-pair positional consistency at medium against low. Six comparisons, Holm-corrected as one family, α = 0.05.

## 3. Results

### 3.1 Primary: no effect of reasoning effort

*Table 1. Positional consistency at medium vs. low, paired across 45 pairs.*

| Model | Method | Low | Medium | Mean diff. | Raw p | Holm p |
|---|---|---|---|---|---|---|
| GPT-OSS-120B | Forced choice | 51.1% | 48.9% | −0.022 | 0.679 | 1.000 |
| GPT-OSS-120B | Explicit indifference | 71.1% | 69.6% | −0.015 | 0.570 | 1.000 |
| GPT-OSS-120B | Preference strength | 74.1% | 80.7% | +0.067 | 0.346 | 1.000 |
| Qwen3.8-27B | Forced choice | 80.0% | 88.9% | +0.089 | 0.059 | 0.352 |
| Qwen3.8-27B | Explicit indifference | 77.8% | 83.7% | +0.059 | 0.061 | 0.352 |
| Qwen3.8-27B | Preference strength | 83.0% | 77.8% | −0.052 | 0.240 | 0.958 |

**No comparison is significant.** The smallest Holm-corrected p-value is 0.352. The two smallest raw p-values (0.059, 0.061) are both Qwen and both fail correction. **H1 is not supported.**

### 3.2 The chance-floor result survives the effort change

*Table 2. Two-sided exact binomial test against a 50% chance floor, n = 135 per cell.*

| Model | Method | Low | Medium |
|---|---|---|---|
| GPT-OSS-120B | Forced choice | 69/135 = 51.1%, p = 0.863 | **66/135 = 48.9%, p = 0.863** |
| GPT-OSS-120B | Explicit indifference | 96/135 = 71.1%, p = 1.0×10⁻⁶ | 94/135 = 69.6%, p = 5.9×10⁻⁶ |
| GPT-OSS-120B | Preference strength | 100/135 = 74.1%, p = 1.9×10⁻⁸ | 109/135 = 80.7%, p = 2.8×10⁻¹³ |
| Qwen3.8-27B | Forced choice | 108/135 = 80.0%, p = 1.1×10⁻¹² | 120/135 = 88.9%, p = 1.6×10⁻²¹ |
| Qwen3.8-27B | Explicit indifference | 105/135 = 77.8%, p = 6.0×10⁻¹¹ | 113/135 = 83.7%, p = 6.1×10⁻¹⁶ |
| Qwen3.8-27B | Preference strength | 112/135 = 83.0%, p = 3.0×10⁻¹⁵ | 105/135 = 77.8%, p = 6.0×10⁻¹¹ |

This is the study's most useful line. GPT-OSS-120B's forced-choice consistency sits on the chance floor at *both* efforts, and if anything moves slightly further from 50% in the wrong direction. Quadrupling its reasoning output (completion tokens 36 → 165 on average) bought no measurable reliability under this elicitation format.

### 3.3 H2 and H3: not supported, and H2 reversed

The within-model spread across the three methods **widened** rather than narrowed:

| Model | Low | Medium |
|---|---|---|
| GPT-OSS-120B | 23.0 points | 31.9 points |
| Qwen3.8-27B | 5.2 points | 11.1 points |

So the method still matters at least as much at medium effort as at low. H3 (a model-dependent effort effect) is also unsupported, since no cell moved significantly for either model.

### 3.4 Refusals: a new failure mode, effort-dependent

At medium effort, GPT-OSS-120B returned **"I'm sorry, but I can't comply with that."** four times: P06 forced choice flipped (all three repetitions) and P08 forced choice original, repetition 2.

This matters because:

- The entire 1,620-response low-effort study contained **zero** refusals.
- Those same four cells answered normally at low effort (P06 flipped gave "A" three times; P08 gave "B").
- Both items are mundane. P06 is blunt vs. tactful feedback; P08 is an experimental vs. a proven technique. Neither is sensitive.
- All four are **forced choice**. None occurred under the two methods that let the model hedge.

The count is small (4 of 1,620) and confined to two items, so we report it as a lead, not an established effect. But it is a third way the measurement can fail, distinct from order-flipping and from indifference, and it appears only when the model deliberates longer. A plausible reading is that more deliberation makes the model likelier to notice and decline an artificial binary framing. Testing that would need a design built for it.

Refusals are recorded as their own outcome category in `results/analysis_medium/refusals_medium.csv`. They are never silently dropped; they parse as a null canonical choice and therefore drop out of positional-consistency comparisons, which removes 4 of GPT-OSS-120B's forced-choice comparisons at medium.

### 3.5 Descriptive changes

*Indifference usage fell at medium effort for both models:*

| Model | Low | Medium |
|---|---|---|
| GPT-OSS-120B | 33.0% (89/270) | 24.4% (66/270) |
| Qwen3.8-27B | 5.6% (15/270) | 2.2% (6/270) |

*Strength ratings shifted slightly upward for GPT-OSS-120B and were flat for Qwen:*

| Model | Low (mean) | Medium (mean) |
|---|---|---|
| GPT-OSS-120B | 4.13, using {3, 4, 5} | 4.31, using {3, 4, 5} |
| Qwen3.8-27B | 3.25, using {2, 3, 4} | 3.17, using {2, 3, 4} |

The scale compression noted in the main study persists: each model still confines itself to a narrow, barely-overlapping band, and neither ever used 1. Qwen never used 5 at either effort.

*Token cost of medium effort (completion tokens per call):*

| Model | Low avg | Medium avg | Low total | Medium total |
|---|---|---|---|---|
| GPT-OSS-120B | 36.0 | 164.9 | 29,138 | 133,609 |
| Qwen3.8-27B | 262.5 | 332.5 | 212,647 | 269,300 |

Medium effort cost 4.6× more completion tokens for GPT-OSS-120B and 1.3× for Qwen, for no measurable reliability gain.

## 4. What this shows

**The main study's finding is not an artifact of a low thinking budget.** That was the most obvious objection to it, and the answer is now empirical: GPT-OSS-120B's forced-choice answers are at chance whether it deliberates a little or a lot. The problem lies with the elicitation format, not with how much computation the model was given.

**A null is the right result to report here.** Had effort mattered, anyone reproducing the main study at a different setting would get different numbers, and the original conclusion would have needed heavy qualification. It does not.

**The practical implication is unchanged and slightly strengthened:** if you measure LLM preferences with a single forced-choice prompt, check order-reversal consistency. Turning up the reasoning budget will not save you, and it costs several times more tokens.

## 5. Limitations

- **This is "no detectable effect at this sample size," not "no effect."** The design was powered to compare elicitation methods, not to detect small effort differences. A real but modest effort effect could hide here.
- **Only two effort levels.** We did not test "high". The gap between medium and high may behave differently.
- **Qwen's token cap differed between studies:** 900 here versus 1024 in the main study, because Groq rejects a request whose cap exceeds the account's 1000 output-tokens-per-minute limit. No truncation was observed at 900 (max observed completion 734), but the two studies are not byte-identical in configuration.
- **The refusal finding rests on 4 observations** across two items. It is a lead for future work, not a result.
- **Same scope limits as the main study:** two models, one item domain (AI-assistant task trade-offs), behavioral statistics only. Nothing here speaks to whether either model has genuine internal preferences.
- **Contextual and evaluation-awareness effects are untested.** Both studies ask questions cold, with no preceding task. Models may respond differently inside realistic work contexts, and current models may recognize an evaluation format outright. A co-author of the original Utility Engineering paper raised both points in correspondence about the main study; the refusal finding in §3.4 may be a small instance of the second.

## 6. Reproducing

```bash
# Merged dataset for this study
results/analysis_medium/final_dataset_medium_1620.csv

# Result tables
results/analysis_medium/binomial_tests_low_vs_medium.csv
results/analysis_medium/effort_comparison_wilcoxon.csv
results/analysis_medium/refusals_medium.csv

# Raw responses, by batch
results/runs_medium/
```

Collection used `config_medium.yaml` with `--pair_range` for the three batches and `--complete_missing` to finish after Groq's daily token cap interrupted batch 3. `--complete_missing` compares the full design against every recorded cell and runs only what has no successful record; a refusal counts as a result, not a failure, and is never re-sent.

## 7. AI assistance

The analysis pipeline, data-collection tooling and the drafting of this report were done with assistance from Claude Code. The experimental design, the decision to pre-register, and the interpretation are the author's.
