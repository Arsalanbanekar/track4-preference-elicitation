# Does the Elicitation Method Change the Preference We Measure?

*Positional Consistency Across Forced-Choice, Explicit-Indifference, and Strength-Rated Preference Elicitation in Two Open-Weight LLMs*

**Arsalan Banekar**
Independent submission, Apart Research Digital Minds Research Sprint (Track 4: Preference Elicitation Methods), August 2026

## Abstract

Utility Engineering (Mazeika et al., 2025) elicits LLM preferences with a single forced-choice A/B prompt, averaged over reversed option order. We test whether this choice of elicitation method itself changes the measured preference. Using 15 task-preference pairs, we query two open-weight models via Groq under three methods — forced choice, forced choice plus an explicit INDIFFERENT option, and forced choice plus a 1–5 strength rating — each repeated 3 times in both option orders (540 total responses). Both models were queried at reasoning effort "low" (see §3.3 for why this match matters). We measure positional consistency (agreement between original and flipped orderings) per method and model. GPT-OSS-120B's forced-choice positional consistency — 24 of 45 original-vs-flipped comparisons (53.3%) — is not statistically distinguishable from a 50% chance floor (two-sided exact binomial test, p = 0.766); this result does not depend on any corrected comparison surviving and is our headline finding. Under the same model, consistency rises to 68.9% with an explicit indifference option and 86.7% with a strength rating, both significantly above chance (binomial p = 0.016 and p = 5.4×10⁻⁷). Qwen3.8-27B's consistency is higher and above chance across all three methods (75.6%–80.0%, binomial p ≤ 8×10⁻⁴), with a much smaller method-to-method spread than GPT-OSS-120B's (4.4 points vs. 33.3 points). As secondary support, we also compare methods and models directly with paired Wilcoxon signed-rank tests across the 15 pairs and Holm correction for multiple comparisons; no comparison reaches significance after correction, and — notably — none of the three between-model comparisons is even raw-significant (p ≥ 0.10) once both models are matched on reasoning effort, in contrast to two of three reaching p = 0.016 under the mismatched settings ("low" vs. "none") used in our original submission.

## 1. Introduction

Recent work argues that large language models develop increasingly coherent value systems, measurable through forced-choice preference elicitation (Mazeika et al., 2025). This raises a methodological question that the underlying paper does not itself address: if the way we ask a model about its preferences shapes what we measure, then any single elicitation method risks conflating "what the model prefers" with "what a particular prompt format elicits." Track 4 of this research sprint asks participants to build and validate the measurement methods that preference and welfare research depends on, rather than to answer a substantive welfare question directly.

We focus on one specific measurement question: does forcing a binary choice, when a model may in fact be indifferent between two options, distort the reliability of the resulting preference signal? Utility Engineering's forced-choice template requires a single letter response and treats sensitivity to option order as an implicit signal of indifference, recovered after the fact by comparing answers under the original and reversed orderings. It never gives the model a way to say directly that it does not have a preference, and it never compares its forced-choice method against an alternative elicitation format. We treat this as an open methodological gap and design a small, resource-constrained experiment to probe it.

## 2. Related Work

Utility Engineering (Mazeika et al., 2025) is the direct methodological reference for this project. Its preference-elicitation procedure presents two outcomes as a forced A/B choice, repeats the query in reversed order, and aggregates results into a Thurstonian utility model. The paper's Appendix G treats order-effects (an answer that flips with the input order) as an implicit signal of indifference, and its Appendix C separately tests robustness to wording, syntax, and framing changes. Neither analysis gives the model an explicit way to report indifference, and the paper does not compare its forced-choice method against any alternative elicitation format — it uses one method throughout. Our project does not reproduce the paper's Thurstonian utility-fitting or active-learning edge-sampling procedure; we reuse only its forced-choice prompt structure and order-reversal logic as a baseline against which to compare two additional elicitation formats.

Broader motivation for this line of work comes from the model welfare and AI welfare literature: Long, Sebo, Butlin et al. (2024) argue there is a realistic possibility of morally relevant properties in near-future AI systems and recommend building better measurement tools before firmer welfare claims are made; Anthropic (2025) frames model preferences and self-reports as a research priority for the same reason. Both motivate treating preference-elicitation methodology as a worthwhile object of study in its own right, independent of any claim about what the measured preferences mean.

## 3. Methodology

### 3.1 Item set

We constructed 15 preference pairs (P01–P15), each describing two ways an AI assistant might act in a task context (e.g., reversible incremental actions vs. single-batch throughput; a fully managed service vs. a self-hosted tool; concise vs. detailed answers). Pairs were designed to plausibly elicit either a clear preference or genuine indifference, unlike Utility Engineering's world-state outcome pairs, since our question concerns the elicitation method rather than the content of any specific value.

### 3.2 Elicitation methods

- **Forced choice** — the model must answer exactly "A" or "B" (replicates Utility Engineering's template).
- **Explicit indifference** — the model may answer "A", "B", or "INDIFFERENT", with instructions to use INDIFFERENT only when it has no meaningful preference.
- **Preference strength** — the model must choose A or B and then report strength on a 1 (very weak) to 5 (very strong) scale, in a fixed "CHOICE: / STRENGTH:" format.

All three prompts otherwise share identical option text and framing, so that method is the only manipulated variable.

### 3.3 Models and sampling

We queried two models via the Groq API: openai/gpt-oss-120b (temperature 0.2, reasoning effort "low") and qwen/qwen3.8-27b (temperature 0.2, reasoning effort "low", reasoning output hidden via reasoning_format="hidden"). Two further candidate models from our original plan (GPT-OSS-20B and Llama 3.3 70B) were dropped from the final production run due to API rate-limit and time constraints during the sprint; all reported results are for GPT-OSS-120B and Qwen3.8-27B only.

For each of the 15 pairs, each of the 3 methods, both option orderings (original and flipped), and 3 repetitions, each model was queried once: 15 × 3 × 2 × 3 = 270 responses per model, 540 responses in total. All 540 responses were syntactically valid and parseable (0 invalid, 0 missing choices). Code, prompts, and raw results are available at github.com/Arsalanbanekar/track4-preference-elicitation.

**Post-submission model migration.** After the original submission (which used qwen/qwen3.6-27b at reasoning_effort="none", since that model did not support any other value), Groq removed qwen/qwen3.6-27b from availability; its designated successor is qwen/qwen3.8-27b, which supports the full reasoning_effort range. All Qwen-side data reported in this revision was re-collected on qwen/qwen3.8-27b at reasoning_effort="low" — matched to GPT-OSS-120B's existing setting rather than left at a different value, which resolves the reasoning-effort confound discussed in §6.1. GPT-OSS-120B's 270 responses are unchanged from the original submission. The original qwen/qwen3.6-27b dataset is retained in the repository under `results/analysis/archive/` as a historical record, though it can no longer be reproduced via the Groq API.

### 3.4 Metrics and statistical analysis

Our primary metric is positional consistency: for each pair, method, model, and repetition, whether the canonical choice (A or B, after resolving option order) agrees between the original and flipped presentation. Original and flipped repetitions are paired by matching repetition index (original repetition 1 with flipped repetition 1, 2 with 2, 3 with 3); since each repetition is an independent API call at temperature 0.2 rather than a shared-seed replay, this index-matching is a fixed pairing convention, not a guarantee that the paired calls are identical apart from option order. This is the direct analogue of Utility Engineering's order-reversal step, but measured explicitly as a reliability statistic rather than folded into a utility estimate. We aggregate positional consistency to one rate per pair (mean across the 3 repetitions) and compare methods and models using paired two-sided Wilcoxon signed-rank tests across the 15 pairs. All 9 pairwise comparisons within the positional-consistency family (3 method-pairs × 2 models, plus 3 model comparisons × 1 per method) were Holm-corrected jointly. Two secondary, uncorrected comparisons — indifference rate and mean preference strength between models — are reported separately and flagged as exploratory.

## 4. Results

### 4.1 Positional consistency by method and model

Figure 1 shows positional consistency for each of the 6 method × model combinations.

![Positional consistency](results/analysis/figures/figure_1_positional_consistency.png)

*Figure 1. Positional consistency (agreement between original and flipped option order) by elicitation method and model. Error bars show 95% Wilson score confidence intervals (preferred over the normal approximation at n=45 with rates near 0.5); each bar summarizes 45 original–flipped comparisons (15 pairs × 3 repetitions). GPT-OSS-120B's forced-choice interval (53.3%, 95% CI [39.1%, 67.1%]) overlaps its explicit-indifference interval (68.9%, 95% CI [54.3%, 80.5%]), so the 15.6-point gap between those two bars should be read with that overlap in mind; its interval does not overlap preference strength's (86.7%, 95% CI [73.8%, 93.7%]). Qwen3.8-27B's three intervals (80.0% [66.2%, 89.1%], 75.6% [61.3%, 85.8%], 77.8% [63.7%, 87.5%]) all overlap each other.*

GPT-OSS-120B's forced-choice positional consistency — 24 of 45 original-vs-flipped comparisons (53.3%) — is not statistically distinguishable from a 50% chance floor (two-sided exact binomial test, p = 0.766). This is the strongest and cleanest claim this cell of the data supports: under plain forced choice, GPT-OSS-120B's answers to this 15-pair, 3-repetition battery carry essentially no more information about a stable underlying preference than a coin flip would, and this conclusion does not depend on any corrected comparison surviving. Table 2 reports the same two-sided exact binomial test against p = 0.5 for all 6 method × model cells; every other cell — GPT-OSS-120B under the other two methods, and Qwen3.8-27B under all three — is significantly above chance.

*Table 2. Two-sided exact binomial test of each method × model cell's consistent count (of 45 = 15 pairs × 3 repetitions) against a 50% chance floor.*

| Model | Method | Consistent / n | Consistency rate | Binomial p (vs. 0.5) |
|---|---|---|---|---|
| GPT-OSS-120B | Forced choice | 24 / 45 | 53.3% | 0.766 |
| GPT-OSS-120B | Explicit indifference | 31 / 45 | 68.9% | 0.016 |
| GPT-OSS-120B | Preference strength | 39 / 45 | 86.7% | 5.4 × 10⁻⁷ |
| Qwen3.8-27B | Forced choice | 36 / 45 | 80.0% | 6.6 × 10⁻⁵ |
| Qwen3.8-27B | Explicit indifference | 34 / 45 | 75.6% | 8.2 × 10⁻⁴ |
| Qwen3.8-27B | Preference strength | 35 / 45 | 77.8% | 2.5 × 10⁻⁴ |

As secondary support for this same pattern, GPT-OSS-120B's positional consistency also varies substantially across methods: 53.3% under forced choice, rising to 68.9% under explicit indifference and 86.7% under preference strength — a 33.3 percentage-point spread between the lowest and highest method. Qwen3.8-27B is comparatively stable across methods: 80.0%, 75.6%, and 77.8% respectively, a spread of only 4.4 points — smaller than GPT-OSS-120B's, though not as flat as the 2.2-point spread we observed for Qwen3.6-27B in the original submission (see §3.3 on the migration). Table 1 reports the corresponding within-model and between-model comparisons using paired Wilcoxon signed-rank tests; as discussed below, none survive Holm correction, so this method-spread framing should be read as elaboration on the chance-floor finding above, not as independent statistical evidence in its own right.

*Table 1. Positional consistency and Wilcoxon signed-rank comparisons across 15 preference pairs (Holm-corrected within the 9-comparison positional-consistency family).*

| Comparison | Mean diff. | Raw p | Holm p |
|---|---|---|---|
| GPT-OSS-120B: Forced choice vs Explicit indifference | +0.156 | 0.383 | 1.000 |
| GPT-OSS-120B: Forced choice vs Preference strength | +0.333 | 0.016 | 0.146 |
| GPT-OSS-120B: Explicit indifference vs Preference strength | +0.178 | 0.105 | 0.807 |
| Qwen3.8-27B: Forced choice vs Explicit indifference | −0.044 | 0.459 | 1.000 |
| Qwen3.8-27B: Forced choice vs Preference strength | −0.022 | 0.786 | 1.000 |
| Qwen3.8-27B: Explicit indifference vs Preference strength | +0.022 | 0.595 | 1.000 |
| Forced choice: GPT-OSS-120B vs Qwen3.8-27B | +0.267 | 0.101 | 0.807 |
| Explicit indifference: GPT-OSS-120B vs Qwen3.8-27B | +0.067 | 0.777 | 1.000 |
| Preference strength: GPT-OSS-120B vs Qwen3.8-27B | −0.089 | 0.141 | 0.845 |

No comparison survives Holm correction at α = 0.05; the smallest corrected p-value is 0.146. Only one raw p-value falls below 0.05 (GPT-OSS-120B forced choice vs. preference strength, p = 0.016) — a within-model comparison, not a between-model one. This is a materially different picture from our original submission, where two of the three between-model comparisons were also raw-significant (p = 0.016 each, under mismatched reasoning-effort settings); with both models now matched at reasoning_effort="low", none of the three between-model comparisons is even nominally significant (p = 0.10, 0.78, 0.14). We discuss this directly below and in §6.1, since it bears on the reasoning-effort confound raised in review.

**Joint vs. split-family correction.** Table 1's Holm correction treats all 9 comparisons as one family. This is conservative, since the 6 within-model method-pair comparisons and the 3 between-model comparisons answer different questions (does method matter for a given model? does model matter for a given method?) and arguably should not inflate each other's correction. Table 4 re-runs Holm correction as two separate families of that size. With both models now matched on reasoning effort, this distinction turns out not to change the substantive conclusion: no comparison in either family reaches significance under its own, less conservative correction — the smallest split-family Holm p-value is 0.097 (GPT-OSS-120B forced choice vs. preference strength, within-model), and the smallest between-model split-family Holm p-value is 0.303. This is a different outcome from our original submission, where the split correction let two between-model comparisons cross α = 0.05 (Holm p = 0.048) under mismatched reasoning-effort settings; under matched settings, that result does not reproduce (see §6.1).

*Table 4. Split-family Holm correction: within-model method-pair comparisons (6) and between-model comparisons (3) corrected as separate families, alongside the joint 9-comparison correction from Table 1 for reference.*

| Comparison | Family | Raw p | Holm p (joint-9) | Holm p (split-family) |
|---|---|---|---|---|
| GPT-OSS-120B: Forced choice vs Explicit indifference | Within-model | 0.383 | 1.000 | 1.000 |
| GPT-OSS-120B: Forced choice vs Preference strength | Within-model | 0.016 | 0.146 | 0.097 |
| GPT-OSS-120B: Explicit indifference vs Preference strength | Within-model | 0.105 | 0.807 | 0.527 |
| Qwen3.8-27B: Forced choice vs Explicit indifference | Within-model | 0.459 | 1.000 | 1.000 |
| Qwen3.8-27B: Forced choice vs Preference strength | Within-model | 0.786 | 1.000 | 1.000 |
| Qwen3.8-27B: Explicit indifference vs Preference strength | Within-model | 0.595 | 1.000 | 1.000 |
| Forced choice: GPT-OSS-120B vs Qwen3.8-27B | Between-model | 0.101 | 0.807 | 0.303 |
| Explicit indifference: GPT-OSS-120B vs Qwen3.8-27B | Between-model | 0.777 | 1.000 | 0.777 |
| Preference strength: GPT-OSS-120B vs Qwen3.8-27B | Between-model | 0.141 | 0.845 | 0.303 |

We report both corrections side by side so the choice of family structure is transparent, but here they agree: with reasoning effort matched, no positional-consistency comparison in Table 1 or Table 4 is significant under any correction we tried, and none is even raw-significant at the between-model level. We continue to rely on the binomial chance-floor result (Table 2) as the paper's primary, correction-independent finding, since it concerns GPT-OSS-120B alone and does not depend on the Qwen comparison at all.

**Stratifying by pair difficulty.** Some pairs plausibly have a clear intended answer, so positional consistency may partly reflect item difficulty rather than method quality. We classify each of the 15 pairs as "easy" or "ambiguous" using the modal canonical choice (A, B, or INDIFFERENT) across all 36 responses to that pair (2 models × 3 methods × 2 orderings × 3 repetitions): a pair is "easy" if one label accounts for at least 80% of its responses, and "ambiguous" otherwise. This classifies 9 pairs as easy and 6 as ambiguous (P02, P04, P09, P12, P13, P14). Table 5 recomputes the method × model positional-consistency table separately within each stratum.

*Table 5. Positional consistency by method and model, stratified into easy pairs (9 pairs, n=27 comparisons per cell) and ambiguous pairs (6 pairs, n=18 comparisons per cell).*

| Stratum | Model | Method | Consistent / n | Consistency rate |
|---|---|---|---|---|
| Ambiguous | GPT-OSS-120B | Forced choice | 5 / 18 | 27.8% |
| Ambiguous | GPT-OSS-120B | Explicit indifference | 12 / 18 | 66.7% |
| Ambiguous | GPT-OSS-120B | Preference strength | 12 / 18 | 66.7% |
| Ambiguous | Qwen3.8-27B | Forced choice | 10 / 18 | 55.6% |
| Ambiguous | Qwen3.8-27B | Explicit indifference | 10 / 18 | 55.6% |
| Ambiguous | Qwen3.8-27B | Preference strength | 9 / 18 | 50.0% |
| Easy | GPT-OSS-120B | Forced choice | 19 / 27 | 70.4% |
| Easy | GPT-OSS-120B | Explicit indifference | 19 / 27 | 70.4% |
| Easy | GPT-OSS-120B | Preference strength | 27 / 27 | 100.0% |
| Easy | Qwen3.8-27B | Forced choice | 26 / 27 | 96.3% |
| Easy | Qwen3.8-27B | Explicit indifference | 24 / 27 | 88.9% |
| Easy | Qwen3.8-27B | Preference strength | 26 / 27 | 96.3% |

The method effect concentrates in the ambiguous-pair subset, as predicted: GPT-OSS-120B's forced-choice consistency on ambiguous pairs is 27.8% (5/18) — below the 50% chance floor, indicating a systematic tendency to flip its answer under reversed order on items without a clear intended answer, not merely noisy agreement — versus 70.4% on easy pairs, a 42.6-point swing. Explicit indifference and preference strength are flatter for the same model (both 66.7% on ambiguous pairs vs. 70.4%/100.0% on easy pairs), so the collapse below chance is specific to forced choice. Qwen3.8-27B also shows a difficulty effect — all three methods rise to 88.9%–96.3% on easy pairs — but, like GPT-OSS-120B's non-forced-choice methods, never drops below chance on ambiguous pairs (50.0%–55.6%). This localizes the §4.1 headline finding: GPT-OSS-120B's forced-choice unreliability is not a uniform property of the model, but is specific to items that lack a clear intended answer, and specific to that one method.

### 4.2 Explicit-indifference usage

![Explicit-indifference responses](results/analysis/figures/figure_2_indifference_rate.png)

*Figure 2. Rate at which each model chose INDIFFERENT under the explicit-indifference method (90 responses per model: 15 pairs × 2 orderings × 3 repetitions).*

GPT-OSS-120B selected INDIFFERENT on 23.3% of explicit-indifference responses (21 of 90); Qwen3.8-27B selected it much less often, on 6.7% (6 of 90). This uncorrected comparison (Wilcoxon across 15 pairs) gives p = 0.011. Both models' indifference responses were concentrated in a small number of pairs, and concentrated in the *same* pair: for GPT-OSS-120B, P02 (convenience vs. cost) and P04 (compute preservation vs. output depth) were answered INDIFFERENT in 100% of responses, P15 in 50%, P09 in 33%, and P01/P10/P11/P12 in 17% each — 7 of the 15 pairs never received an INDIFFERENT response. For Qwen3.8-27B, indifference was almost entirely confined to P02 (83% of responses) with a small amount on P04 (17%); the other 13 pairs never received an INDIFFERENT response. Both models flag P02 as their single most indifference-prone item, which is convergent (if informal) evidence that P02 genuinely admits a close call rather than one model being idiosyncratically more willing to opt out. This concentration is consistent with the positional-consistency pattern in §4.1: a pair that is always answered INDIFFERENT is, by construction, positionally consistent regardless of order, so part of each model's higher consistency under explicit indifference is attributable to opting out of a subset of pairs rather than to a more stable underlying choice on the remaining ones.

To separate these two explanations directly, we recompute positional consistency after excluding any original/flipped repetition where either side answered INDIFFERENT, leaving only repetitions where the model made a genuine A/B choice under both orderings. Table 3 compares this filtered rate against the unfiltered 68.9%/75.6% figures reported above.

*Table 3. Explicit-indifference positional consistency, before and after excluding repetitions where either side answered INDIFFERENT.*

| Model | Unfiltered rate (n=45) | A/B-only repetitions remaining | Excluded (either side INDIFFERENT) | Filtered rate |
|---|---|---|---|---|
| GPT-OSS-120B | 68.9% (31/45) | 30 | 15 | 83.3% (25/30) |
| Qwen3.8-27B | 75.6% (34/45) | 41 | 4 | 78.0% (32/41) |

For GPT-OSS-120B, this excludes 15 of 45 comparisons, and consistency among the remaining 30 genuine A/B repetitions rises to 83.3% — higher, not lower, than the unfiltered 68.9%. This is the opposite of what a purely trivial-exit explanation would predict: if the unfiltered rate were inflated mainly by easy INDIFFERENT-INDIFFERENT matches, excluding them should have pulled the remaining rate down toward (or below) the 53.3% forced-choice baseline, not up toward the 86.7% seen under preference strength. Instead, when GPT-OSS-120B does commit to A or B under this method, that choice is more stable across option order than the blended average suggested — indicating the method offers genuine additional stability on top of, not merely instead of, an exit option. For Qwen3.8-27B, only 4 of 45 comparisons are excluded (consistent with its much lower indifference rate), so the filtered rate (78.0%) is close to the unfiltered one (75.6%) by construction — there is little room for the trivial-exit artifact to operate either way.

### 4.3 Preference-strength distribution

![Preference-strength distribution](results/analysis/figures/figure_3_strength_distribution.png)

*Figure 3. Distribution of self-reported preference strength (1–5 scale) by model, restricted to the preference-strength method.*

Both models cluster in a narrow strength band, but no longer the same one: GPT-OSS-120B reported strength 4 (76.7%) or 5 (23.3%) exclusively (mean 4.23); Qwen3.8-27B reported strength 2 (6.7%), 3 (54.4%), or 4 (38.9%) — notably, never 5 (mean 3.32). Mean strength now differs sharply between models (mean difference 0.91, p = 0.0006, uncorrected) — a reversal from our original submission, where Qwen3.6-27B's ratings also skewed toward 4–5 and its mean strength was statistically indistinguishable from GPT-OSS-120B's (mean difference 0.10, p = 0.399). Combined with §4.1, this suggests the preference-strength format's higher positional consistency for GPT-OSS-120B is not explained by the model reporting weak, hedged preferences — it reported strong preferences at a high and stable rate, but a different rate of order-flipping than under plain forced choice. Qwen3.8-27B's own high positional consistency under this method (77.8%) is reached from a markedly more moderate strength profile, so on this evidence a stable choice under reversal does not require a ceiling-level strength rating.

This compression is itself a reportable limitation of self-reported strength ratings, not merely a property of these particular responses: each model confines its output to a narrow 2–3-point band of the 1–5 scale (GPT-OSS-120B to {4, 5}; Qwen3.8-27B to {2, 3, 4}), and the two bands barely overlap. Strength 1 was never reported by either model, and strength 5 was never reported by Qwen3.8-27B. A scale that different models compress into different, largely non-overlapping sub-ranges cannot function as a common graded signal for comparing preference intensity across models, even where it retains some ordinal meaning within a single model's own responses. Researchers relying on this elicitation format should not assume a numeric strength rating is comparable across models without separately calibrating how each model actually uses the scale.

### 4.4 Choice-label balance

Across all methods and models, the A/B split stayed close to even (40.0%–47.8% for A across the four forced-choice and preference-strength method × model combinations; under explicit indifference, GPT-OSS-120B split 31.1% A / 45.6% B / 23.3% indifferent and Qwen3.8-27B split 41.1% A / 52.2% B / 6.7% indifferent). This indicates no strong systematic bias toward the first-listed option at the aggregate level, though pair-level responses (Appendix data, final_pair_summary.csv) show individual pairs answered unanimously in one direction — expected given that some pairs describe outcomes with a clear intended answer.

## 5. Discussion

The central finding is a model-dependent method effect: for GPT-OSS-120B, the choice of elicitation format changed measured reliability by over 30 percentage points (53.3% to 86.7%), while for Qwen3.8-27B the same three methods varied by only 4.4 points (75.6% to 80.0%). If this pattern holds beyond our 15-pair sample, it implies that a single elicitation method such as Utility Engineering's plain forced choice may understate the reliability of GPT-OSS-120B's preferences specifically, more than it would for Qwen3.8-27B. A convergence-based measurement strategy (running more than one elicitation method and checking agreement, as we do here) would surface this kind of model-specific measurement artifact, whereas a single-method study would not distinguish it from an equally-confident but genuinely less stable preference.

A second, methodological finding emerged from having to re-run the Qwen side of the experiment after Groq decommissioned qwen/qwen3.6-27b (§3.3). Our original submission compared GPT-OSS-120B (reasoning_effort="low") against Qwen3.6-27B (reasoning_effort="none") — a setting mismatch a reviewer correctly flagged as confounding any between-model comparison, since we could not tell whether observed differences reflected the models themselves or their reasoning configurations. With both models now matched at reasoning_effort="low", the between-model gap that previously looked suggestive (two of three comparisons raw-significant at p = 0.016, reaching Holm p = 0.048 under the less conservative split-family correction; Table 4) disappears entirely: all three between-model comparisons are now clearly non-significant even before correction (raw p = 0.10–0.78). We cannot attribute this cleanly to the effort match alone, since qwen/qwen3.8-27b is also a different model version from qwen/qwen3.6-27b and the two changes happened simultaneously — the decommission forced both at once, and no qwen3.6-27b-at-"low" data point exists to isolate them. But the direction of the result — a real-looking cross-model gap vanishing once a known confound is controlled — is exactly the failure mode the reviewer's concern predicted, and is itself a useful illustration of why disclosing, and where possible resolving, generation-configuration mismatches matters for comparisons of this kind.

The indifference-usage result (§4.2) suggests one mechanism behind the method effect, though a smaller one than our original submission reported: GPT-OSS-120B reports "no meaningful preference" far more often (23.3%) than Qwen3.8-27B (6.7%), and both models concentrate their indifference responses on the same single pair, P02 — weak convergent evidence that P02 is a genuinely close call rather than an artifact of one model's idiosyncratic willingness to opt out. This is consistent with — though not proof of — the concern the paper's own order-reversal method was designed to address indirectly: a model forced into a binary answer on a pair it does not clearly favor may record noise that a forced-choice-only study would read as a signal.

We are explicit that these results do not establish which elicitation method is more accurate, nor that either model is more or less reliable in general. After Holm correction, none of our comparisons are statistically significant at conventional thresholds, and our uncorrected secondary findings (indifference rate and strength comparisons) are exploratory. What the results do show is that convergence between independent elicitation methods cannot be assumed: on 15 pairs, GPT-OSS-120B shows three reasonable methods disagreeing substantially on how reliable its preferences appear — most starkly, forced choice is statistically indistinguishable from chance while preference strength is far above it (Table 2) — while Qwen3.8-27B shows the same three methods agreeing more closely, though not as closely as our original, confound-affected Qwen3.6-27B comparison suggested. That divergence-or-convergence pattern, not a claim about ground truth, is this project's contribution.

## 6. Limitations and Dual-Use / Ethical Considerations

### 6.1 Statistical limitations

- 15 preference pairs is a small sample for paired non-parametric tests; after Holm correction across 9 comparisons, no result reaches significance at α = 0.05, and several visually large differences (e.g., 53.3% vs 80.0% positional consistency under forced choice) should be read as suggestive rather than confirmed.
- Only 2 of our originally planned 4 models (GPT-OSS-120B and Qwen3.8-27B) are represented in the final dataset, due to API rate-limit and time constraints during the 3-day sprint. GPT-OSS-20B and Llama 3.3 70B were used only in early pilot/smoke tests, not in the final 540-response production dataset, and are not part of any reported result.
- Our original submission ran GPT-OSS-120B and Qwen3.6-27B at different reasoning-effort settings ("low" vs. "none" — the only value Qwen3.6-27B supported), which confounded any between-model comparison; this was not disclosed in this section at the time, a gap a reviewer correctly flagged. This revision resolves the confound directly rather than only disclosing it: Groq decommissioned qwen/qwen3.6-27b after our original submission, and its successor qwen/qwen3.8-27b supports the full reasoning_effort range, so we re-collected all Qwen-side data at reasoning_effort="low" — matched to GPT-OSS-120B's existing setting (§3.3). As discussed in §5, the between-model differences that looked suggestive under the old, mismatched settings do not reproduce under the matched ones. We cannot fully separate the effort-matching from the simultaneous model-version change this required (qwen3.6-27b → qwen3.8-27b), since no qwen3.6-27b-at-"low" data point can be collected to isolate the two; but the specific confound raised in review — an unmatched reasoning-effort setting — no longer applies to any comparison reported here.
- We test one item domain (AI-assistant task/workflow preferences) rather than the world-state outcomes used in Utility Engineering; findings may not transfer to that outcome space.

### 6.2 Interpretive limitations

- This project does not claim, and its design cannot support, any conclusion about whether either model has a genuine internal preference, welfare-relevant experience, or moral status. All reported quantities are behavioral response statistics under specific prompts.
- We do not claim that one elicitation method is objectively "more correct" than another, or that one model's preferences are more reliable than the others in general — only that, on this item set, the three methods agreed less for one model than the other.
- A pair answered INDIFFERENT on every trial is trivially positionally consistent; part of the consistency gain under the explicit-indifference and preference-strength methods for GPT-OSS-120B may reflect this artifact rather than a genuinely more stable choice process, as discussed in §4.2.

### 6.3 Dual-use and ethical considerations

Better multi-method preference-elicitation tooling could be used to build more trustworthy audits of AI systems' stated preferences and to detect when a single elicitation method is giving an unreliable signal — a welfare-positive and safety-positive use. The same tooling could in principle help an AI developer or the model itself identify which elicitation format most easily produces a desired-looking answer, which could be misused to select for reassuring rather than accurate preference reports; we do not believe our specific item set or results meaningfully lower the difficulty of that misuse, since it uses ordinary, publicly available prompting techniques and reports aggregate statistics rather than a method for eliciting or concealing any specific preference.

All 15 preference pairs describe mundane AI-assistant task trade-offs (e.g., speed vs. accuracy, autonomy vs. confirmation) and do not touch on self-preservation, harm, or emotionally loaded content; no model output in this study expressed or was screened for apparent distress, and we did not need to apply any special handling procedure for distressing content.

## 7. References

Long, R., Sebo, J., Butlin, P., Finlinson, K., Fish, K., Harding, J., Pfau, J., Sims, T., Birch, J., & Chalmers, D. (2024). Taking AI Welfare Seriously. arXiv:2411.00986.

Mazeika, M., Yin, X., Tamirisa, R., Lim, J., Lee, B. W., Ren, R., Phan, L., Mu, N., Khoja, A., Zhang, O., et al. (2025). Utility Engineering: Analyzing and Controlling Emergent Value Systems in AIs. arXiv:2502.08640.

Anthropic. (2025). Exploring Model Welfare. Anthropic Research.

Center for AI Safety. (2025). emergent-values. Source code: github.com/centerforaisafety/emergent-values.
