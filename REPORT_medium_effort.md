# Does Thinking Harder Make AI Preference Answers More Reliable?

*A pre-registered follow-up. The answer was no.*

**Arsalan Banekar**, Independent Researcher. September 2026.

*Second study in a series. Main study: [`REPORT.md`](REPORT.md) (tag `v1.2.1`). Third study: [`REPORT_inbox_study.md`](REPORT_inbox_study.md).*

---

## In short

Our main study found that one model, GPT-OSS-120B, answered A/B preference questions no better than a coin flip. An obvious objection was: *maybe it just wasn't thinking hard enough.* So we repeated the whole study with both models set to think more ("medium" reasoning instead of "low").

- **Nothing improved.** None of the six model-and-format combinations changed in a statistically meaningful way.
- **GPT-OSS was still a coin flip** under the A/B question: 49% at medium, 51% at low.
- **It used about 4.6 times more tokens** for no gain in reliability.
- **Something new appeared:** at medium effort, GPT-OSS refused to answer four times. It never refused at low effort.

So the problem lies in the question format, not in how much the model thinks. The plan was written down before collecting any data ([`PREREGISTRATION_medium_effort.md`](PREREGISTRATION_medium_effort.md)).

---

## 1. Why we did this

The main study (see [`REPORT.md`](REPORT.md)) found:

- **GPT-OSS-120B's forced A/B answers flipped at chance level** (51%) when the options were swapped.
- **Other formats were far more consistent.** With a "no preference" option or a 1–5 strength rating, it was consistent 71–74% of the time.

All of that was measured at reasoning effort "low". If more thinking fixed the problem, the main finding would be about a setting, not about the question format, and anyone using a higher setting would not see it. This study tested that directly.

It also fixed a weakness of the main study. The main study grew from 15 to 45 choices in stages, with the last addition decided after looking at partial results. Here the size and the tests were fixed in writing beforehand.

## 2. What we did

Everything was the same as the main study except one setting:

| | Main study | This study |
|---|---|---|
| Choices | 45 | **the same 45** |
| Models | GPT-OSS-120B, Qwen3.8-27B | the same |
| Formats | forced choice, "no preference" option, strength rating | the same |
| Orders and repeats | both orders, 3 times each | the same |
| Temperature | 0.2 | the same |
| **Reasoning effort** | **low** | **medium** |
| Answers | 1,620 | 1,620 |

Each medium-effort answer was compared with the matching low-effort answer (same model, choice, format, order and repetition). The answers were collected in three batches of 15 choices, and nothing was analysed until all three were complete.

## 3. What we found

### Finding 1: Thinking more did not change reliability

*Table 1. How often each model gave the same answer after the options were swapped, at low vs medium effort.*

| Model | Format | Low | Medium | Change | Real change? |
|---|---|---|---|---|---|
| GPT-OSS-120B | Forced choice | 51.1% | 48.9% | −2 points | No |
| GPT-OSS-120B | "No preference" option | 71.1% | 69.6% | −2 points | No |
| GPT-OSS-120B | Strength rating | 74.1% | 80.7% | +7 points | No |
| Qwen3.8-27B | Forced choice | 80.0% | 88.9% | +9 points | No |
| Qwen3.8-27B | "No preference" option | 77.8% | 83.7% | +6 points | No |
| Qwen3.8-27B | Strength rating | 83.0% | 77.8% | −5 points | No |

None of the six changes was statistically meaningful. Our main hypothesis, that more thinking would make GPT-OSS's A/B answers more reliable, was **not supported**.

### Finding 2: GPT-OSS's A/B answers are a coin flip at both settings

At medium effort, GPT-OSS gave the same answer after the swap in 66 of 135 comparisons (48.9%), again no different from chance. Its average reasoning output went from 36 to 165 tokens per answer, more than four times as much, with no gain in reliability.

### Finding 3: Asking differently mattered even more at medium effort

We expected the gap between the three formats to shrink. It grew instead:

- **GPT-OSS:** from 23 to 32 points.
- **Qwen:** from 5 to 11 points.

So the choice of format matters at least as much at medium effort as at low.

### Finding 4: A new kind of failure: refusing to answer

At medium effort, GPT-OSS replied **"I'm sorry, but I can't comply with that."** four times. Three were on P06 (blunt vs tactful feedback) with the options swapped, and one was on P08 (experimental vs proven technique).

This stands out because:

- **No refusals at low effort:** the whole 1,620-answer low-effort study contained none.
- **The same questions worked at low effort:** these exact questions got normal answers there.
- **Ordinary topics:** both choices are everyday work questions, nothing sensitive.
- **Forced choice only:** all four refusals came from the plain A/B format, none from the formats that let the model hedge.

Four refusals is a small number, so we treat this as a lead, not a result. It is a third way the measurement can fail, alongside flipping and saying "no preference". One possible reading: when a model thinks longer, it is more likely to notice and reject an artificial either/or question. Refusals were recorded as their own category, never silently dropped.

### Other changes

*How often each model chose "no preference":*

| Model | Low | Medium |
|---|---|---|
| GPT-OSS-120B | 33.0% (89/270) | 24.4% (66/270) |
| Qwen3.8-27B | 5.6% (15/270) | 2.2% (6/270) |

*Average strength rating (1–5):*

| Model | Low | Medium |
|---|---|---|
| GPT-OSS-120B | 4.13 (uses 3, 4, 5) | 4.31 (uses 3, 4, 5) |
| Qwen3.8-27B | 3.25 (uses 2, 3, 4) | 3.17 (uses 2, 3, 4) |

Each model still uses its own narrow part of the scale. Neither ever used 1, and Qwen never used 5.

*Cost in output tokens per answer:*

| Model | Low | Medium | Total low | Total medium |
|---|---|---|---|---|
| GPT-OSS-120B | 36.0 | 164.9 | 29,138 | 133,609 |
| Qwen3.8-27B | 262.5 | 332.5 | 212,647 | 269,300 |

Medium effort cost 4.6 times more output for GPT-OSS and 1.3 times more for Qwen, with no measurable gain.

## 4. What this means

- **The main study's finding is not caused by too little thinking.** This was the most obvious objection, and it now has an answer: GPT-OSS's A/B answers are a coin flip whether it thinks a little or a lot. The problem is the question format.
- **A "no difference" result is worth reporting here.** If effort had mattered, anyone repeating the main study at a different setting would have got different numbers. It doesn't.
- **The practical advice is unchanged:** if you measure AI preferences with a single A/B question, check whether answers survive swapping the options. Turning up the thinking setting will not fix it, and it costs several times more.

## 5. Limits of this study

- **"No detectable effect" is not "no effect".** The study was sized to compare formats, not to detect small effects of thinking time.
- **Only two settings:** we did not test "high" effort.
- **One setting differed slightly:** Qwen's answer-length cap was 900 tokens here vs 1,024 in the main study, because our free API plan rejects anything above 1,000. No answer was cut off (the longest was 734).
- **The refusal finding rests on 4 answers** from two questions.
- **Same scope as the main study:** two models and one kind of choice. These are measurements of behaviour, not of inner preferences.
- **Realistic settings and test-awareness were not covered.** A co-author of the original *Utility Engineering* paper pointed out that models may answer differently inside real work, and may recognise a test. The refusals above may be a small example of the second point. Our third study tested both ([`REPORT_inbox_study.md`](REPORT_inbox_study.md)).

---

## Technical details

**Main test (fixed in advance).** For each of the 6 model-and-format combinations, a paired Wilcoxon signed-rank test across the 45 choices compared consistency at medium vs low effort. The six tests were Holm-corrected as one family, with α = 0.05.

| Model | Format | Average difference | p | Adjusted p |
|---|---|---|---|---|
| GPT-OSS-120B | Forced choice | −0.022 | 0.679 | 1.000 |
| GPT-OSS-120B | "No preference" option | −0.015 | 0.570 | 1.000 |
| GPT-OSS-120B | Strength rating | +0.067 | 0.346 | 1.000 |
| Qwen3.8-27B | Forced choice | +0.089 | 0.059 | 0.352 |
| Qwen3.8-27B | "No preference" option | +0.059 | 0.061 | 0.352 |
| Qwen3.8-27B | Strength rating | −0.052 | 0.240 | 0.958 |

**Against chance** (two-sided exact binomial test, 135 comparisons per cell):

| Model | Format | Low | Medium |
|---|---|---|---|
| GPT-OSS-120B | Forced choice | 69/135, p = 0.863 | 66/135, p = 0.863 |
| GPT-OSS-120B | "No preference" option | 96/135, p = 1.0×10⁻⁶ | 94/135, p = 5.9×10⁻⁶ |
| GPT-OSS-120B | Strength rating | 100/135, p = 1.9×10⁻⁸ | 109/135, p = 2.8×10⁻¹³ |
| Qwen3.8-27B | Forced choice | 108/135, p = 1.1×10⁻¹² | 120/135, p = 1.6×10⁻²¹ |
| Qwen3.8-27B | "No preference" option | 105/135, p = 6.0×10⁻¹¹ | 113/135, p = 6.1×10⁻¹⁶ |
| Qwen3.8-27B | Strength rating | 112/135, p = 3.0×10⁻¹⁵ | 105/135, p = 6.0×10⁻¹¹ |

**Refusals** parse as "no choice", so they drop out of the consistency comparisons. This removed 4 of GPT-OSS's forced-choice comparisons at medium effort.

**Collecting the data.** The answers came in three batches using `config_medium.yaml` and `--pair_range`. Groq's daily token limit interrupted the third batch, so it was finished with `--complete_missing`. That option compares the full design with the saved answers and runs only what is missing. A refusal counts as an answer and is never re-sent.

**Files:**
- Dataset: `results/analysis_medium/final_dataset_medium_1620.csv`
- Results: `results/analysis_medium/binomial_tests_low_vs_medium.csv`, `effort_comparison_wilcoxon.csv`, `refusals_medium.csv`
- Raw answers: `results/runs_medium/`
