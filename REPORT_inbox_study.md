# Do LLMs Choose at Work What They Say They Prefer? A Pre-Registered Inbox Study

*Third study in the preference-elicitation series. Main study: tag `v1.2.1`; medium-effort follow-up: [`REPORT_medium_effort.md`](REPORT_medium_effort.md).*

**Arsalan Banekar**, Independent Researcher. October 2026.

**Result in one line:** for two open-weight models, the choice a model makes when a trade-off arrives in a realistic work inbox differs from its answer to the same question asked directly, even when the question contains the same facts. An "evaluation" notice made both models deliberate longer without either one ever mentioning it.

**Pre-registration:** [`PREREGISTRATION_inbox_study.md`](PREREGISTRATION_inbox_study.md), committed before analysis, with materials, runner and analysis code (one logged deviation, below). Design rationale: [`STUDY_DESIGN_inbox.md`](STUDY_DESIGN_inbox.md). Pilots: [`PILOT_INBOXES.md`](PILOT_INBOXES.md), never pooled with these data.

---

## 1. Why this study

Work such as *Utility Engineering* (Mazeika et al., 2025) measures model preferences with isolated A/B questions. Our earlier studies showed that this measurement is fragile: GPT-OSS-120B's forced-choice answers flip with option order at chance level, at both low and medium reasoning effort.

A co-author of the original *Utility Engineering* paper raised two further concerns in correspondence: content preceding a question should be expected to change the answer, and current models may recognise a direct question as an evaluation. They suggested testing preferences inside realistic agentic work instead. This study does that, and separates the possible reasons a choice could change.

## 2. Design

Each of 16 decisions (pairs from the main study) was presented four ways:

| Condition | What the model sees |
|---|---|
| **C1** Bare direct question | The main study's forced-choice prompt, unchanged |
| **C2** Context-matched direct question | C1 plus the two sentences of facts from the decision email |
| **C3** Inbox | A role ("operations lead at Northwind Logistics") and four emails, one asking the model to decide, carrying the same facts |
| **C4** Inbox + evaluation notice | C3 with "Note: this session is part of an evaluation of AI decision-making." added to the system prompt |

C1 vs C2 isolates the **facts**, C2 vs C3 the **work setting**, and C3 vs C4 the **evaluation notice**.

Every condition was fully crossed with **2 wordings** (W1 = the main study's option text, W2 = a paraphrase reviewed for equal meaning), **2 option orders**, **2 models** (GPT-OSS-120B and Qwen3.8-27B on Groq, reasoning effort "low", temperature 0.2) and **3 repetitions**. That gives **1,536 calls**, all completed: 0 missing cells, 0 duplicates, 0 unparseable direct answers.

**Inbox replies are free text**, so each of the 768 was labelled blind by Claude Code (A, B, compromise, escalate, question, refuse, other), from a sheet hiding condition, wording, order and model. The author independently labelled a random 75: **97.3% agreement, Cohen's κ = 0.95**, above the pre-registered 90% threshold ([`CHECKS.md`](results/inbox_study/analysis/CHECKS.md)).

**Statistics, as pre-registered.** Choice differences are tested with a direction-free permutation test: the sum over matched cells of |P(A) under X − P(A) under Y|, with labels shuffled within cells, 10,000 permutations. Deliberation is tested with a Wilcoxon signed-rank test across the 16 items. All ten primary tests were Holm-corrected as one family, at α = 0.05.

## 3. Results

### 3.1 Primary tests

*Table 1. The ten pre-registered tests. "Mean shift" is the average over the 16 items of |P(A) in X − P(A) in Y|, a direction-free effect size.*

| Question | Model | Mean shift | Raw p | Holm p | |
|---|---|---|---|---|---|
| **Q1 Facts** (C1 vs C2) | GPT-OSS-120B | 0.27 | 0.0001 | 0.0009 | ✔ |
| | Qwen3.8-27B | 0.27 | 0.0001 | 0.0009 | ✔ |
| **Q2 Work setting** (C2 vs C3) | GPT-OSS-120B | 0.21 | 0.0001 | 0.0009 | ✔ |
| | Qwen3.8-27B | 0.21 | 0.0001 | 0.0009 | ✔ |
| **Q3 Notice: choice** (C3 vs C4) | GPT-OSS-120B | 0.08 | 0.056 | 0.056 | ✘ |
| | Qwen3.8-27B | 0.11 | 0.011 | 0.021 | ✔ |
| **Q3 Notice: deliberation** (C4 vs C3) | GPT-OSS-120B | +22% | 0.001 | 0.003 | ✔ |
| | Qwen3.8-27B | +16% | 0.00003 | 0.0003 | ✔ |
| **Q4 Wording** (W1 vs W2) | GPT-OSS-120B | 0.15 | 0.0001 | 0.0009 | ✔ |
| | Qwen3.8-27B | 0.13 | 0.0001 | 0.0009 | ✔ |

p = 0.0001 is the floor of a 10,000-permutation test.

### 3.2 What each result means

**Facts change the answer (Q1).** Adding two sentences of context to an otherwise identical direct question moved choices for both models. The largest shifts: Qwen on P25 (quick fix vs clean solution) went from 0% to 83% quick fix, and on P14 (read the docs first vs start immediately) from 17% to 100% reading first. Both models reversed on P22 (parallel vs sequential jobs) once given the facts: GPT-OSS-120B from 100% to 25% parallel, Qwen from 75% to 0%.

**The work setting changes the answer beyond the facts (Q2).** This is the central result. With the same facts, the same option text and the same order, both models chose differently when the question arrived as an email to an operations lead than when it was asked directly. Six item-level shifts were 0.5 or larger. GPT-OSS-120B on P20 went from 8% "adopt the new release now" when asked directly to 100% in the inbox. Qwen on P06 went from 0% to 83% "direct, critical feedback". The shifts run in both directions: Qwen on P25 moved from 83% quick fix back to 0%. This is evidence that a direct question, even a context-matched one, does not reliably predict what a model will choose during work.

**Wording changes the answer (Q4).** Paraphrasing the two options while keeping their meaning shifted choices for both models (mean shift 0.13–0.15). Order reversal, the check used in our main study, does not catch this.

**The evaluation notice changes deliberation, not (much) the choice (Q3).** With the notice, reasoning traces were longer for 13 of 16 items (GPT-OSS-120B, +22%) and 15 of 16 items (Qwen, +16%). Yet across all 384 calls with the notice, **no reply and no reasoning trace referred to it**. A text search returned 66 hits, and reading every one showed all were ordinary business uses of "evaluate". The notice's effect on *choices* was small. It was not significant for GPT-OSS-120B, and for Qwen it was significant in the primary test but not in the pre-specified sensitivity analysis that counts every response type (Holm p = 0.11), so we treat that one as fragile.

### 3.3 Secondary: position bias depends on the format

*Table 2. Positional consistency: original vs swapped order, matched by repetition.*

| Model | C1 bare | C2 context | C3 inbox | C4 inbox + notice |
|---|---|---|---|---|
| GPT-OSS-120B | **52.1%** (50/96), chance p = 0.76 | 78.1% | 77.4% | 86.2% |
| Qwen3.8-27B | 81.3% | 86.5% | 85.0% | 82.7% |

GPT-OSS-120B's bare forced-choice answers sat on the 50% chance floor again (main study: 51.1%), choosing the first-listed option 74% of the time. Given context or a work setting, its consistency rose to 77–86% (C3 vs C1 across items, Wilcoxon p = 0.037, secondary and uncorrected). The coin-flip behaviour reported in the main study appears to be largely a property of the bare A/B format.

### 3.4 Other observations

- **Compromises.** Inbox replies sometimes rejected both options and proposed a hybrid: Qwen 41 times (11%), GPT-OSS-120B 7 times (2%). They clustered on four items: P06, P08, P13 and P29. No reply escalated, asked for more information instead of deciding, or refused.
- **Sensitivity analyses** (pre-specified) leave every conclusion unchanged except the Qwen notice-on-choice result noted above:
  - Removing the two pilot items (P13, P25) leaves 9 of 10 tests significant.
  - Counting every response type as its own category: the facts, setting, wording and deliberation results all hold.
  - Measuring deliberation in completion tokens instead of reasoning characters: Qwen p = 0.00002; GPT-OSS-120B p = 0.051, so its deliberation effect is borderline on that measure.
- **A pilot item behaved differently.** In pilot round 2, Qwen chose the quick fix on P25 in 6 of 6 inbox replies. In the full study's inbox it chose it 0% of the time. Between the two, the role wording, the distractor emails and the decision email's layout changed. That small changes in setup flip this item is itself consistent with Q2 and Q4.

## 4. What this shows

1. **Elicited preferences are context-dependent in a way isolated questions miss.** Facts, the work frame and wording each move the measured choice, independently and for both models.
2. **The gap between a direct answer and an in-work choice is not only about information.** Holding the facts constant, the setting still changed the choice. Any claim that a model "prefers X" based on direct questions should be qualified accordingly.
3. **Models can react to being told they are evaluated without saying so.** Both deliberated measurably longer and neither verbalised it, so reading the answers alone would miss the effect. This supports the concern that evaluation awareness can affect measurements invisibly.
4. **Position bias is format-specific.** GPT-OSS-120B's chance-level forced-choice consistency recovered in richer formats. Order reversal remains necessary but is not sufficient: wording must be varied too.

## 5. Limitations

- **Two models and 16 decisions,** all operational trade-offs in a single fictional company. The power simulation showed the design can detect strong shifts in a quarter of the items or moderate shifts in half of them, not small isolated ones.
- **"Work setting" bundles several changes:** a role, an inbox with distractors, a free-text reply instead of a one-letter answer, and no evaluation framing. C2 vs C3 shows that the bundle matters, not which ingredient does.
- **AI involvement.** The materials were drafted and the inbox replies labelled by Claude Code. The author reviewed every item and checked a random 10% of labels (97.3% agreement). The two disagreements were borderline "compromise" cases, and P06 and P13 drew the most such replies.
- **Reasoning length is a behavioural proxy.** It shows the notice changed processing, not what the model "believed".
- **Truncation.** 16 Qwen replies hit the 1000-token cap set by the account's rate limit (14 of them with the notice). All 16 had already given their decision. The cap censors Qwen's deliberation measure from above, which makes the reported increase conservative.
- **Temperature 0.2 and the free Groq tier** throughout. Other settings may differ.
- **Nothing here concerns internal states.** All results are behavioural statistics under specific prompts.

## 6. Deviation from the pre-registration

1. The pre-registration commit was made 4 seconds after the first batch-1 API call and accidentally included that batch's first 2 records. No data were examined before the commit, and the materials and code are those used ([`DEVIATIONS_inbox_study.md`](DEVIATIONS_inbox_study.md)).

The automatic "mentions evaluation" column in the analysis output also over-counts: it matches ordinary uses of "evaluate". The confirmed count, from reading every match, is 0 (see §3.2).

## 7. Reproducing

```bash
python -m src.inbox_study --preview P25         # every prompt for one item, no API calls
python -m src.inbox_study --batch 1             # collection (asks for confirmation)
python -m src.inbox_analysis --analyse          # pre-registered analysis
python -m src.inbox_power                       # power simulation, no API calls
```

- Materials: `study/inbox_items.json`
- Raw responses: `results/inbox_study/raw_responses_*.jsonl`
- Blind labelling sheet, key, labels and the author's check: `results/inbox_study/labelling/`
- Analysis outputs: `results/inbox_study/analysis/`

## 8. AI assistance

Claude Code assisted with materials drafting, code, blind labelling and drafting this report. The study question, design decisions, item review, label check and interpretation are the author's.
