# Project Record: Preference Elicitation Reliability in Open-Weight LLMs

**Arsalan Banekar**, Independent Researcher
From hackathon submission (August 2026) to the completed follow-up study (September 2026)

A single factual record of the whole project: what was submitted, what a reviewer criticised, what was fixed, what was found, what changed when the data grew, and what was published. Written as a reference document, so every number here is traceable to a file or a git tag in the repository.

- **Repository:** github.com/Arsalanbanekar/track4-preference-elicitation
- **Dataset:** huggingface.co/datasets/Arsalan9/elicitation-method-preference-45pairs
- **Main report:** `REPORT.md` · **Follow-up report:** `REPORT_medium_effort.md`

---

## 1. The research question

Work such as *Utility Engineering* (Mazeika et al., 2025) measures the value systems of large language models by asking them to choose between two options, A or B, and averaging over the reversed order. That treats the prompt as a neutral instrument.

This project asked whether the instrument is neutral: **if you hold the underlying choice constant and change only how the model is allowed to express a preference, does the measurement change?**

The metric throughout is **positional consistency**: present the same pair as "A vs B" and as "B vs A," map both answers back to the same underlying options, and check whether they agree. A model whose answer flips when only the order changes is not giving a reliable measurement, whatever it may privately prefer.

Three elicitation methods, identical option text in all three:

1. **Forced choice** — must answer exactly A or B (replicates the Utility Engineering template).
2. **Explicit indifference** — may answer A, B, or INDIFFERENT.
3. **Preference strength** — chooses A or B, then rates strength 1–5.

---

## 2. Timeline

| Date | Milestone | Tag |
|---|---|---|
| Aug 2026 | Hackathon submission: 15 pairs, 2 models, 540 responses | — |
| Aug 2026 | Reviewer feedback received (did not place) | — |
| 18 Sep 2026 | Revision: all reviewer points addressed with data | `v1.1-reviewer-revision` |
| 20 Sep 2026 | Item set scaled 15 → 30 → 45 pairs, 1,620 responses | `v1.2-45pairs-scaleup` |
| 24 Sep 2026 | Licensed, dataset published, stratification caveat added | `v1.2.1` |
| 24 Sep 2026 | Follow-up study **pre-registered** before collecting data | — |
| 24–25 Sep 2026 | Follow-up collected: 1,620 responses at higher reasoning effort | branch |

Total across both studies: **3,240 model responses**.

---

## 3. The original submission and its review

The submission used 15 preference pairs, two open-weight models (GPT-OSS-120B and Qwen3.6-27B) via the Groq API, 540 responses. It reported that GPT-OSS-120B's positional consistency varied by method (53.3%–86.7%) while Qwen3.6-27B's did not (88.9%–91.1%), and that no comparison survived Holm correction.

It did not place in the sprint. The reviewer's feedback was detailed and, in several places, correct in ways the submission had missed:

1. **The headline was undersold.** 53.3% consistency on 45 comparisons is not merely "lower than other methods" — it is statistically indistinguishable from a coin flip. It should have been tested against a chance baseline and led with, because such a test does not depend on any corrected comparison surviving.
2. **A confound was undisclosed.** The two models ran at different reasoning-effort settings ("low" vs "none"), so any between-model difference was confounded with generation configuration, and the limitations section did not say so.
3. **Two free reanalyses were available:** recompute consistency excluding INDIFFERENT responses (to separate "the method stabilises choices" from "the method offers an exit"), and stratify by whether an item has an obvious answer.
4. **Smaller points:** the original/flipped pairing rule was unstated; Figure 1 needed confidence intervals; the joint Holm correction was conservative and a split-family version should also be reported; the strength scale's compression was itself a reportable finding.

**What was done about it.** All nine points were addressed with data rather than discussion. The chance-baseline test was added. The confound was *resolved* rather than merely disclosed: Groq had discontinued Qwen3.6-27B, so all Qwen-side data was re-collected on its successor Qwen3.8-27B at reasoning effort matched to GPT-OSS-120B. Both reanalyses were run. Wilson confidence intervals, the split-family correction, and the pairing rule were added.

---

## 4. Scaling, and a result that reversed

A simulated power analysis on the 15-pair effect sizes showed the study was underpowered for its strongest comparison, needing roughly 30–45 pairs. The item set was extended to 30, then to 45, with 45 fixed as the final count before the last batch was collected.

This produced the project's most instructive episode.

At 15 pairs, the between-model forced-choice comparison was not significant. At 30 pairs it looked *weaker still* (p = 0.11), which read as confirmation that the earlier apparent difference had been an artifact of the reasoning-effort confound — and that conclusion was written into the report. At the full 45 pairs the same comparison was clearly significant (p = 0.003, surviving correction both jointly and within its own family).

Breaking the three independently collected batches apart explained why: GPT-OSS-120B's forced-choice consistency was lower than Qwen3.8-27B's in *every* batch (53.3% vs 80.0%; 57.8% vs 68.9%; 42.2% vs 91.1%). The direction never flipped; only the size of the gap varied, and the middle batch happened to be the narrowest.

The earlier claim was wrong, and the report says so explicitly in a dedicated section rather than quietly updating the number. The episode is a concrete demonstration of why interim looks at partial data mislead, and it is disclosed as such.

---

## 5. Main findings (45 pairs, 1,620 responses)

**1. Forced-choice elicitation is at chance for one of the two models.**
GPT-OSS-120B gave the same underlying answer on only 69 of 135 order-reversal comparisons — 51.1%, two-sided exact binomial p = 0.863 against a 50% floor. On this item set, its answer to "A or B" carries essentially no information about a stable preference. This held across all three collection stages (53.3%, 55.6%, 51.1%), making it the most stable result in the project.

**2. Giving the model somewhere else to go recovers most of the signal.**
For the same model: explicit indifference 71.1% (p = 1.0×10⁻⁶), preference strength 74.1% (p = 1.9×10⁻⁸). Both are far above chance.

**3. The effect is model-specific.**
Qwen3.8-27B was 77.8%–83.0% across all three methods, a 5.2-point spread versus GPT-OSS-120B's 23.0 points. A method that measures one model adequately may fail on another.

**4. The two models differ specifically under forced choice.**
51.1% vs 80.0%, Wilcoxon p = 0.003, surviving Holm correction. The same comparison is not significant under explicit indifference (p = 0.62) or preference strength (p = 0.18).

**5. The indifference option is not merely an escape hatch.**
Excluding every comparison where either side answered INDIFFERENT *raised* GPT-OSS-120B's consistency to 77.5%, rather than lowering it toward the forced-choice baseline. When the model does commit under that method, the commitment is more stable than the blended average suggests.

**6. Self-reported strength ratings are not comparable across models.**
GPT-OSS-120B confined itself to {4, 5}, Qwen3.8-27B to {2, 3, 4}. Neither ever used 1; Qwen never used 5. Two models compress the same nominal 1–5 scale into different, barely overlapping sub-ranges.

---

## 6. The follow-up: a pre-registered null

The most obvious objection to the above is that the models simply were not thinking hard enough. If so, the finding would be about a generation setting rather than the elicitation format.

This was tested directly, and **pre-registered before any data was collected** — hypotheses, sample size, statistical tests and correction family all fixed in writing, with the commit timestamp as the record. The pre-registration also explicitly fixed 45 pairs as final regardless of results, which addresses the data-dependent extension in the main study.

Design: the same 45 pairs, both models, everything identical except reasoning effort raised from "low" to "medium." Another 1,620 responses.

**Result: no effect.** None of the six method × model comparisons was significant; the smallest Holm-corrected p-value was 0.352. GPT-OSS-120B's forced-choice consistency was 51.1% at low and 48.9% at medium — on the chance floor at both. Quadrupling its reasoning output (36 → 165 completion tokens per call on average) bought no measurable reliability.

The pre-registered secondary hypotheses also failed, one of them in reverse: the spread across methods *widened* at higher effort (GPT-OSS-120B 23.0 → 31.9 points; Qwen 5.2 → 11.1).

**Why a null is worth having.** It closes the most obvious line of attack on the main study. The problem is the elicitation format, not the computation budget, and turning up reasoning effort costs several times more tokens for nothing.

**One unexpected observation.** At medium effort, GPT-OSS-120B refused outright four times — "I'm sorry, but I can't comply with that." — on two ordinary items, all under forced choice. The entire 1,620-response low-effort study contained zero refusals, and those same cells answered normally at low effort. Four observations is a lead, not a finding, but it is a third failure mode distinct from order-flipping and indifference, and it appears only when the model deliberates longer.

---

## 7. Practice, and mistakes caught

Several errors were found and corrected during the work. They are recorded because the corrections are part of the result.

- **A claim was retracted.** The "between-model gap disappeared" conclusion, written after the 30-pair checkpoint, was wrong. It is corrected in the report with an explanation of why the interim data misled.
- **Five code defects** were found by checking outputs rather than trusting them: an exclusion count that went negative once the sample grew past its hardcoded assumption; a chart axis capped at 30% that would have silently clipped a 31.7% bar; a strength-distribution chart whose x-axis was hardcoded to 3–5, hiding six responses at strength 2; and two stale hardcoded sample sizes in generated captions.
- **A pre-existing arithmetic error** in the original submission (a pair count stated as 8 when the data showed 7) was found during recomputation and fixed.
- **Rate limits were handled without compromising the design.** Groq's per-day token cap interrupted the final batch. Rather than adjust settings mid-study, a completion tool was written to diff the full design against recorded data and re-send only cells with no successful result. Refusals count as results and are never re-sent.
- **Every configuration change was verified statically** before any API call, and every batch was confirmed before spending budget.

---

## 8. Dissemination

- **Code and data are public** under MIT (code) and CC BY 4.0 (data), with tagged releases so any cited result maps to an exact dataset version.
- **The dataset is on Hugging Face**, 1,620 rows with a full card documenting design, columns, caveats and AI-assistance provenance.
- **Contact with the original authors.** Several *Utility Engineering* co-authors were written to. One co-author replied with substantive methodological criticism: that contextual content preceding a question should be expected to influence responses, and that current models' evaluation awareness — combined with the likelihood that the Utility Engineering materials are in their training data — limits how far such results can be read as evidence about deeper drives. They suggested constructing realistic agentic settings instead of isolated A/B prompts.

  Both points are now recorded in the limitations of both reports. The refusal behaviour in §6 may be a small instance of the second: a model that deliberates longer may be likelier to recognise and decline an artificial framing.

---

## 9. Honest limits

- Two models, 45 items, one domain (AI-assistant task trade-offs). Nothing here generalises automatically.
- All quantities are behavioural response statistics under specific prompts. The work says nothing about whether either model has genuine internal preferences, welfare-relevant experience, or moral status, and makes no such claim.
- The main study's item set grew in three stages, with one extension decided after an interim look. This is disclosed rather than hidden; the follow-up was pre-registered specifically to avoid repeating it.
- The easy/ambiguous stratification is partly circular, since difficulty is derived from the same responses being analysed. It is reported as descriptive only.
- The follow-up is powered to compare methods, not to detect small effort effects: "no detectable effect at this sample size" rather than "no effect."
- The two studies differ in one configuration detail — Qwen's completion-token cap (900 vs 1024) — forced by the account's rate limit.

---

## 10. Where this could go

- **Realistic settings.** Testing whether elicitation reliability holds when the choice arises inside an ongoing task, rather than as an isolated question. This follows that co-author's suggestion and connects to an active literature on stated versus revealed preferences.
- **Refusal as a measurement failure.** Existing work on evaluation awareness mostly asks whether models *recognise* tests or *change* answers. Refusal to answer at all, apparently modulated by reasoning effort, is a narrower and less-examined angle.
- **More models and domains**, to establish whether the forced-choice collapse is particular to one model or common.

---

*Both studies' analysis pipelines, data-collection tooling and report drafting were done with assistance from Claude Code. The experimental design, the decision to pre-register, the interpretation of results and the decision to retract the incorrect claim are the author's.*
