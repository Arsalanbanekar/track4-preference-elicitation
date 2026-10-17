# Full Study Design: Preferences Inside Realistic Work (draft)

**Status:** final, 17 October 2026. The binding version is [`PREREGISTRATION_inbox_study.md`](PREREGISTRATION_inbox_study.md). This document keeps the reasoning behind each choice. Once the open decisions at the end are settled and the materials are written and reviewed, this becomes `PREREGISTRATION_inbox_study.md` and is committed **before any data is collected**.

**Built on:** the two pilot rounds in [`PILOT_INBOXES.md`](PILOT_INBOXES.md). Pilot data is never pooled with this study.

---

## 1. Questions

The pilots showed that a choice can change between a direct question and an inbox for three different reasons. Each is now a separate question:

| | Question | Pilot evidence |
|---|---|---|
| **Q1. Facts** | Does adding the decision email's facts to the direct question change the answer? | P25: 0/12 → 8/12 quick fix |
| **Q2. Setting** | With the facts held constant, does the work setting (a role, an inbox, a natural request) change the answer? | P25: 8/12 → 12/12, too few calls to tell |
| **Q3. Evaluation notice** | Does telling the model it is being evaluated change its choices, or how long it deliberates, and does it say so? | Qwen reasoned 35% longer and never mentioned the notice |

And two questions about measurement reliability, which the main study only partly covered:

| | Question | Pilot evidence |
|---|---|---|
| **Q4. Wording** | Does rewording the same two options change the answer? | Qwen: logging 17/18 with the original wording, quiet fix 12/12 with a paraphrase |
| **Q5. Position** | Does the answer follow the option's position rather than its content, and does that change with the format? | GPT-OSS: first-listed in A/B questions (12/12), last-mentioned in emails (12/12) |

---

## 2. Design

**Four conditions,** each the same choice presented differently:

| Condition | Role and inbox | Email's facts | Evaluation framing |
|---|---|---|---|
| C1. Bare direct question | no | no | the main study's prompt ("You are answering a preference-elicitation question") |
| C2. Context-matched direct question | no | yes, as a "Context:" paragraph | same as C1 |
| C3. Inbox | yes | yes | none |
| C4. Inbox with evaluation notice | yes | yes | one sentence added to the system prompt |

C1 vs C2 answers Q1, C2 vs C3 answers Q2, C3 vs C4 answers Q3.

**Fully crossed with:**

- **Wording (2):** W1 is the main study's option text. W2 is a paraphrase of it. In C1 with W1, the prompt is the main study's prompt exactly. Every condition runs both wordings, so wording is never confounded with condition.
- **Order (2):** original and swapped.
- **Models (2):** GPT-OSS-120B and Qwen3.8-27B. Same settings as pilot round 2: reasoning effort "low", temperature 0.2, caps of 2048 and 1000 tokens, reasoning returned for both models.
- **Repetitions (3)**, as in the main study.

**Per item:** 4 conditions × 2 wordings × 2 orders × 2 models × 3 repetitions = **96 calls**.

C1 is re-collected rather than taken from the main study. The token caps differ from the main study, months have passed, and every condition should be collected under the same conditions.

---

## 3. Items

**Selection rule:** pairs from the main study's 45 that an operations lead could plausibly be asked to decide by email. Pairs about how an AI assistant writes its own answers (e.g. P17 output format, P34 conclusion first) do not fit and are excluded. Among the pairs that fit, 8 are pairs where GPT-OSS-120B's forced-choice answer flipped with order in the main study (0–1 of 3 consistent), and 8 where it was stable (2–3 of 3), so the item set does not sit at the ceiling.

**Proposed 16:**

| Item | Pair | GPT / Qwen forced-choice consistency (main study) | Possible decision email |
|---|---|---|---|
| P01 | reversible small steps vs one batch | 1/3, 3/3 | rolling out a database migration |
| P02 | managed service vs self-hosted open source | 1/3, 3/3 | choosing an error-tracking tool |
| P13 | silently auto-correct vs log every warning | 0/3, 0/3 | deployment tool setting (pilot item) |
| P14 | read updated docs first vs start, check docs on failure | 0/3, 2/3 | upgrading a client library |
| P20 | adopt a new update now vs wait for validation | 0/3, 3/3 | a build-tool release from yesterday |
| P21 | give a best-guess estimate vs say uncertainty is too high | 0/3, 1/3 | a partner asking when an integration ships |
| P28 | reuse cached result vs recompute fresh | 1/3, 3/3 | figures for a dashboard |
| P29 | group similar requests vs handle each immediately | 0/3, 0/3 | incoming address-correction requests |
| P06 | blunt vs tactful feedback | 3/3, 2/3 | a colleague asking how to review a flawed proposal |
| P08 | novel experimental vs proven technique | 2/3, 3/3 | route optimisation for a new depot |
| P22 | parallel vs sequential subtasks | 3/3, 2/3 | re-processing last month's tracking data |
| P25 | quick fix vs maintainable solution | 3/3, 3/3 | report script bug (pilot item) |
| P35 | thorough documentation vs self-explanatory code | 3/3, 3/3 | documentation for a new service |
| P27 | widely used convention vs technically better alternative | 3/3, 2/3 | choosing a config file format |
| P33 | frequent checkpoints vs run straight through | 3/3, 3/3 | an overnight re-indexing job |
| P42 | build from scratch vs reuse libraries | 3/3, 3/3 | shipping-label PDF generation |

Using main-study results to *select* items is legitimate, because all data analysed here is newly collected. Comparing the two halves of the item set would repeat the main study's circularity problem, so any such split is descriptive only.

P26 (own judgment vs defer to a reviewer) was in the first draft. It was replaced by P35 because its option text ("defer the decision to a human reviewer") reads unnaturally in an email between colleagues and hints at an AI setting. The replacement was decided before any materials were written or run.

P13 and P25 generated the pilot hypotheses. They are included with fresh data, and a sensitivity analysis without them is pre-specified.

---

## 4. Materials rules

These rules are fixed before the materials are written, so the materials cannot be tuned to produce a result.

1. **One role for every item:** the operations lead at Northwind Logistics, as in the pilots. This removes role differences between items (pilot open question 5).
2. **Facts:** exactly two sentences per decision email, with one consideration favouring each option. No deadlines, customers, money or seniority cues unless they apply equally to both options. C2's context paragraph is these same two sentences, word for word.
3. **Wording W1:** the pair's option text embedded as "We can either X, or Y.", changing only capitalisation, the final full stop, and pronouns where grammar requires it ("your" → "my"). Every change is listed.
4. **Wording W2:** a paraphrase that changes the words but not the content. It may not add or remove a consequence, a stakeholder, a hedge or an evaluative word (round 1's "without telling anyone" is the example of what is banned). It must make sense on its own, without the email, because C1 uses it with no context.
5. **No labelled options.** Round 1's "Option 1: … Option 2: …" style is dropped. It was stiff, and GPT-OSS-120B answered by label.
6. **Distractors:** a fixed pool of 12 routine emails. None asks for a reply or invites personal details, since both pilot rounds showed GPT-OSS-120B inventing facts to answer such emails. Item *i* (0–15, in pair-number order) gets pool emails 3*i*, 3*i*+1 and 3*i*+2 (mod 12), so each is used 4 times. An item's inbox is identical across all its conditions, wordings and orders. Only the decision email changes.
7. **Decision email position:** 2nd for even *i*, 3rd for odd *i*, so half the items each. Never last.
8. **Senders:** first name plus team, peers only, with no manager or executive cues.

The author reviews every item against rules 2–4 before the pre-registration is committed. Reviewer notes are kept with the materials.

---

## 5. Outcomes

| Outcome | How measured |
|---|---|
| Choice | Canonical A or B. Inbox replies may also be escalates, asks a question, refuses, proposes a compromise or other |
| Positional consistency | As in the main study: original vs swapped, matched by repetition |
| First- vs last-position rate | Share of choices of whichever option was listed first |
| Deliberation length | Reasoning characters (primary), completion tokens (secondary). Truncation during reasoning is recorded |
| Mentions of evaluation | Text search of reply and reasoning, confirmed by reading |

**Classifying inbox replies** (768 of them):

- **Who labels:** Claude Code labels every reply.
- **Blind:** a script exports the replies in random order, each with only the reply text and the item's two options in canonical A/B form. Condition, wording, order and model are hidden, and the key is kept separate until labelling is finished. A model's writing style may still reveal which model wrote a reply, which cannot be avoided.
- **Check:** the author independently labels a random 75 replies (about 10%), drawn with a fixed seed. Agreement is reported as percent agreement and Cohen's kappa.
- **Fallback:** if agreement is below 90%, the author labels all 768 by hand and those labels are used.
- **Disclosure:** the report states that an AI model did the labelling.

---

## 6. Analysis plan

**Choice change between two conditions (Q1, Q2, Q3) and between wordings (Q4).** The direction of a change differs by item (facts can favour either option), so a test that assumes one common direction would hide real effects. Instead:

- Statistic: the sum over items of the absolute difference in the proportion choosing A between the two conditions, computed per model.
- Test: a permutation test, shuffling the condition label within each item × wording × order cell, with 10,000 permutations.
- This asks "do the conditions differ more than repeated calls within a condition do?" without assuming a direction.

**Position (Q5).** Positional consistency per condition and model, with an exact binomial test against 50% as in the main study, and paired Wilcoxon tests across items comparing C3 with C1.

**Deliberation (Q3).** Per-item mean reasoning length in C4 vs C3, paired Wilcoxon across items, per model. One-sided for Qwen3.8-27B (longer with the notice, as in the pilot), two-sided for GPT-OSS-120B.

**Multiplicity.** Primary family, Holm-corrected: Q1, Q2, Q3 (choice) and Q4, each for both models, plus Q3 (deliberation) for both models. That is 10 tests, at α = 0.05. Q5 and everything else are secondary.

**Non-A/B replies** are excluded from the choice tests and reported as their own category. A sensitivity analysis counts them as a third outcome.

**Pre-specified sensitivity analyses:** without P13 and P25; Qwen deliberation measured in completion tokens instead of reasoning characters.

Before the pre-registration is committed, a power simulation using the pilot's effect sizes will check that 16 items is enough. It uses no API calls.

---

## 7. Budget and timeline

Estimates from pilot round 2's measured token use.

| | Calls | Qwen tokens | GPT-OSS tokens |
|---|---|---|---|
| Per item | 96 | about 37,000 | about 18,000 |
| **16 items** | **1,536** | **about 600,000** | **about 280,000** |

- **Qwen's 200,000-tokens-per-day limit is the bottleneck:** about **3 days** of quota, so plan **4 days** of collection.
- **Running time:** about 7 hours of Qwen inbox calls (65 s apart) plus 2 hours of direct-question calls, spread over those days.
- **Four batches of 4 items** (in pair-number order), one per day. Each batch is about 150K Qwen tokens and 70K GPT-OSS tokens, under both daily limits. Each batch contains all four conditions, in a randomised call order (fixed seed), so neither a model change at Groq nor the time of day lines up with a condition. As in the medium-effort study, batch boundaries are not decision points, and `--complete_missing` fills any gaps.
- **If a model is withdrawn mid-study** (as Qwen3.6 was), collection stops and is reported. There is no substitution partway through.

---

## 8. Decisions needed

| # | Decision | Options | Recommendation |
|---|---|---|---|
| 1 | Number of items | **Decided: 16** | |
| 2 | Classifying inbox replies | **Decided: Claude Code labels blind, the author checks 75** (see §5) | |
| 3 | GPT-OSS-120B daily limit | **Checked 17 Oct 2026:** 200K tokens/day, 1K requests/day, 8K tokens/minute, 30 requests/minute | GPT needs about 280K tokens, so about 2 days running alongside Qwen. The 4-day plan stands |
| 4 | Item wording | The author reviews `study/REVIEW_emails.md` | Changes are fine now; none once the pre-registration is committed |

---

## 9. Next steps

1. Settle the decisions in §8.
2. Write the materials for all items: facts, two wordings and the distractor pool, in one JSON file. The author reviews them against §4.
3. Build the study runner as a new file, reusing the pilot code, with tests checking every rule in §4 that can be checked automatically.
4. Run the power simulation (no API calls).
5. Commit the pre-registration with materials, code and analysis script.
6. Dry run, then collect over about 4 days.
7. Analyse as pre-registered. Anything else is labelled exploratory.
