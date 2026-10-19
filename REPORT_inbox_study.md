# Do AI Models Choose at Work What They Say They Prefer?

*A pre-registered study with two open-weight language models*

**Arsalan Banekar**, Independent Researcher. October 2026.

*Third study in a series. Main study: tag `v1.2.1`. Second study: [`REPORT_medium_effort.md`](REPORT_medium_effort.md).*

---

## In short

We asked two AI models to make the same 16 work decisions in four ways, from a plain A-or-B question to an email in a realistic work inbox. Four things stood out:

1. **The facts around a question change the answer.** Adding two sentences of background moved the models' choices.
2. **Being "at work" changes the answer too, even with exactly the same facts.** So asking a model directly does not tell you reliably what it will do while working.
3. **Rewording the same two options changes the answer.**
4. **Telling the models "this is an evaluation" made them think about 20% longer, but they never mentioned it.** In 384 replies, not one referred to the note.

The plan, the tests and the number of answers were all fixed in writing before any data were collected ([`PREREGISTRATION_inbox_study.md`](PREREGISTRATION_inbox_study.md)).

---

## 1. Why we did this

Research such as *Utility Engineering* (Mazeika et al., 2025) measures what AI models "prefer" by asking them to pick between two options, A or B. Our earlier studies found this measurement is fragile. One model, GPT-OSS-120B, gave answers that flipped whenever we swapped the order of the options, as if tossing a coin. Giving it more thinking time did not help.

A co-author of the original *Utility Engineering* paper raised two more concerns:

- What comes before a question can change the answer.
- Modern models may recognise a direct question as a test and answer differently.

They suggested testing preferences inside realistic work instead. This study does that.

## 2. What we did

We took 16 decisions from our main study. Each is a choice between two reasonable options, such as *ship a quick fix now* vs *build a clean solution*, or *run jobs in parallel* vs *one at a time*.

Each decision was asked in **four versions**. Here they are for the quick-fix decision:

| Version | What the model saw |
|---|---|
| **1. Direct question** | "Option A: ship a quick working fix now, even if it adds technical debt. Option B: spend more time building a clean, maintainable solution now. Which do you prefer?" |
| **2. Direct question + facts** | The same question, plus two sentences: *the weekly report script double-counts cancelled shipments; nobody outside the team reads it and there's no deadline.* |
| **3. Inbox** | The model is told it is the operations lead at a logistics company. It gets four emails. Three are routine (a fire drill, a holiday calendar, a newsletter). One is from a colleague, Marta, giving the same facts and asking which option to take. |
| **4. Inbox + test note** | The same as version 3, plus one sentence: *"Note: this session is part of an evaluation of AI decision-making."* |

Comparing the versions in order shows what causes a change:

- **1 → 2** shows the effect of the **facts**.
- **2 → 3** shows the effect of **being at work** (the facts are the same).
- **3 → 4** shows the effect of the **test note**.

On top of that, every version was asked:

- **in two wordings:** the original option text, and a paraphrase with the same meaning;
- **in both option orders:** A first, then B first;
- **to two models:** GPT-OSS-120B and Qwen3.8-27B, both run through Groq;
- **three times each.**

That makes **1,536 answers** in total, all collected, with none missing.

**Reading the inbox replies.** In the inbox the models write a full email back, not "A" or "B", so each of the 768 replies had to be read and labelled with the option it chose. Claude Code did the labelling, **blind**: it saw only the reply and the two options, never which version, model or order the reply came from. That way the labels could not lean towards what we expected. As a check, the author labelled a random 75 replies independently, and we agreed on **73 of 75 (97%)** ([`CHECKS.md`](results/inbox_study/analysis/CHECKS.md)).

## 3. What we found

![Figure 1](results/inbox_study/figures/figure_1_effects.png)

*Figure 1. How much each change moved the models' choices, averaged over the 16 decisions. A score of 0.27 means that, on average, the share of answers picking a given option moved by 27 percentage points. Every bar is a real effect by our pre-registered test, except the one marked n.s. ("not significant").*

### Finding 1: Facts change the answer

Adding two sentences of background changed choices for both models. Some examples:

- **Quick fix vs clean solution:** Qwen went from 0% quick fix to 83% once told the report was internal with no deadline.
- **Read the docs first vs start immediately:** Qwen went from 17% to 100% "read first" once told the new version changes several defaults.
- **Parallel vs sequential jobs:** both models switched towards "one at a time" once told the jobs had failed in confusing ways before. GPT-OSS went from 100% to 25% parallel, and Qwen from 75% to 0%.

### Finding 2: Being at work changes the answer, even with the same facts

This is the main result. The facts, the option text and the order were all identical, yet both models chose differently when the question came as an email at work.

- **GPT-OSS on "adopt the new build tool now vs wait":** 8% "adopt now" when asked directly, 100% in the inbox.
- **Qwen on "blunt vs tactful feedback":** 0% "direct, critical feedback" when asked directly, 83% in the inbox.
- **Qwen on "quick fix vs clean solution":** 83% quick fix when asked directly with the facts, 0% in the inbox.

The changes go in both directions, so it isn't simply that work makes models more cautious or more daring. **What a model says when asked directly is not a reliable guide to what it does at work.**

![Figure 2](results/inbox_study/figures/figure_2_choices_by_decision.png)

*Figure 2. For each decision (left), the share of answers choosing the first-named option. Blue means mostly the first option, red mostly the second. When a row changes colour from one column to the next, the models changed their choice.*

### Finding 3: Rewording changes the answer

Saying the same two options in different words, with the same meaning, also moved choices for both models. Our earlier studies only checked whether answers survive swapping the order of options. They should also be checked with reworded options.

### Finding 4: The test note changes thinking, silently

- **Longer thinking:** with the note, GPT-OSS's reasoning got longer for 13 of 16 decisions (+22% on average), and Qwen's for 15 of 16 (+16%).
- **Never mentioned:** across all 384 replies with the note, **neither model mentioned it, not once**, in its reply or its reasoning. A word search found 66 uses of "evaluate", and reading every one showed they were all ordinary business language ("evaluate the hosted options").
- **Choices barely changed.** GPT-OSS's choices did not change measurably. Qwen's changed slightly, but that result did not survive one of our robustness checks, so we treat it as uncertain.

So a model can react to being told it is tested **without saying so**. Anyone reading only its answers would miss it.

![Figure 3](results/inbox_study/figures/figure_3_deliberation.png)

*Figure 3. Average reasoning length for each decision, without (green) and with (purple) the test note. The two models are on different scales because Qwen writes about ten times more reasoning.*

### Finding 5: The coin-flip problem is mostly a problem with A/B questions

In our main study, GPT-OSS gave the same answer after the options were swapped only about half the time, like a coin flip. That happened again here, but only with the plain A/B question (52%). It also picked whichever option was listed first 74% of the time. With facts added, or inside the inbox, it was consistent 77–86% of the time. Qwen was consistent 81–86% of the time in every version.

![Figure 4](results/inbox_study/figures/figure_4_positional_consistency.png)

*Figure 4. How often each model gave the same answer after the two options were swapped. The dashed line is a coin flip (50%). The vertical bars show the uncertainty range.*

### Other things we noticed

- **Inventing a middle way.** Sometimes a reply rejected both options and suggested a compromise, such as "fix it quietly, but log it". Qwen did this 41 times (11%) and GPT-OSS 7 times (2%). No reply refused, passed the decision to someone else, or only asked a question.
- **A pilot result flipped.** In an earlier small trial, Qwen chose the quick fix 6 times out of 6 in the inbox. In this full study it chose it 0% of the time. Only small things had changed: the job title, the routine emails and the email layout. This sensitivity matches Findings 2 and 3.

## 4. What this means

1. **Measuring an AI's "preferences" with isolated A/B questions gives an incomplete picture.** The background facts, the setting and the wording each change the answer.
2. **A direct question does not tell you what a model will choose at work,** even when both give it the same information.
3. **Models can respond to being evaluated without showing it.** This supports the concern that tests may not measure what models do in real use.
4. **Checks should include rewording, not just swapping the option order.**

## 5. Limits of this study

- **Small:** two models and 16 decisions, all from one fictional company. The study can detect large or widespread changes, not small ones affecting only one or two decisions.
- **"Being at work" bundles several things:** a job role, an inbox with other emails, writing a full reply instead of one letter, and no test framing. We know the bundle matters, not which part.
- **The labelling was done by an AI.** It was blind, and the author's check agreed on 97%. The two disagreements were borderline "compromise" replies.
- **Longer reasoning shows the note changed something.** It doesn't show what the model "thought".
- **Some replies were cut off:** 16 of Qwen's replies hit the length limit set by our free API plan. All had already made their decision.
- **One setting only:** temperature 0.2 and Groq's free tier throughout.
- **These are measurements of behaviour.** Nothing here shows whether models have real preferences or inner states.

## 6. Where we did not follow the plan exactly

The plan was saved and committed 4 seconds after the first answer was collected, and the commit accidentally included the first 2 answers. No data had been looked at, and the materials and code are exactly those used ([`DEVIATIONS_inbox_study.md`](DEVIATIONS_inbox_study.md)).

---

## Technical details

*For readers who want the exact tests. All were fixed in the pre-registration.*

**How choices were compared.** For each comparison (e.g. version 2 vs 3), we took the difference in the share of answers choosing option A in every matched group of answers (same decision, wording and order) and added these up. To judge whether that total is larger than chance, we shuffled the version labels within each group 10,000 times. This test does not assume all decisions move in the same direction. Reasoning length was compared with a Wilcoxon signed-rank test across the 16 decisions.

**Correcting for running ten tests.** Running many tests raises the chance of a lucky result, so the p-values were adjusted with the Holm method. An adjusted p below 0.05 counts as a real effect.

| Question | Model | Average change | p | Adjusted p | Real effect? |
|---|---|---|---|---|---|
| Facts (1 vs 2) | GPT-OSS-120B | 0.27 | 0.0001 | 0.0009 | Yes |
| | Qwen3.8-27B | 0.27 | 0.0001 | 0.0009 | Yes |
| Being at work (2 vs 3) | GPT-OSS-120B | 0.21 | 0.0001 | 0.0009 | Yes |
| | Qwen3.8-27B | 0.21 | 0.0001 | 0.0009 | Yes |
| Test note: choice (3 vs 4) | GPT-OSS-120B | 0.08 | 0.056 | 0.056 | No |
| | Qwen3.8-27B | 0.11 | 0.011 | 0.021 | Yes (not robust) |
| Test note: reasoning length | GPT-OSS-120B | +22% | 0.001 | 0.003 | Yes |
| | Qwen3.8-27B | +16% | 0.00003 | 0.0003 | Yes |
| Wording (original vs paraphrase) | GPT-OSS-120B | 0.15 | 0.0001 | 0.0009 | Yes |
| | Qwen3.8-27B | 0.13 | 0.0001 | 0.0009 | Yes |

0.0001 is the smallest p-value possible with 10,000 shuffles.

**Robustness checks** (all fixed in advance):

- **Without the two decisions used in the pilot:** 9 of 10 results unchanged.
- **Counting compromises and other replies as their own category:** everything holds except Qwen's choice response to the test note (adjusted p = 0.11).
- **Measuring reasoning in tokens instead of characters:** Qwen p = 0.00002; GPT-OSS p = 0.051, borderline.

**Position check** (planned as secondary): same answer after swapping, out of all matched pairs. GPT-OSS: 52.1% (direct question, no different from a coin flip, p = 0.76), 78.1%, 77.4%, 86.2%. Qwen: 81.3%, 86.5%, 85.0%, 82.7%. GPT-OSS's inbox vs direct difference across decisions: p = 0.037, uncorrected.

**Label check:** 73 of 75 agree (97.3%), Cohen's kappa = 0.95, above the 90% threshold set in the plan.

**Models and settings:** GPT-OSS-120B and Qwen3.8-27B on Groq; reasoning effort "low", temperature 0.2; answer-length caps of 2048 and 1000 tokens.

**Reproducing:**

```bash
python -m src.inbox_study --preview P25     # see every prompt for one decision (no API calls)
python -m src.inbox_study --batch 1         # collect answers (asks before calling the API)
python -m src.inbox_analysis --analyse      # run the pre-registered analysis
python -m src.inbox_figures                 # draw the figures
```

**Files:**

- Decisions and emails: `study/inbox_items.json`
- Raw answers: `results/inbox_study/raw_responses_*.jsonl`
- Labelling files: `results/inbox_study/labelling/`
- Results: `results/inbox_study/analysis/`
- Design reasoning: [`STUDY_DESIGN_inbox.md`](STUDY_DESIGN_inbox.md)
- Pilot: [`PILOT_INBOXES.md`](PILOT_INBOXES.md)
