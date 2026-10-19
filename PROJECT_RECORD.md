# Project Record: How Reliable Are Measurements of AI Preferences?

**Arsalan Banekar**, Independent Researcher
August–October 2026: from a hackathon submission to three studies

This is a single, factual record of the whole project:
- what was submitted and what a reviewer criticised;
- what was fixed and what each study found;
- what went wrong, and what was published.

Every number can be traced to a file or a git tag in the repository.

- **Repository:** github.com/Arsalanbanekar/track4-preference-elicitation
- **Dataset:** huggingface.co/datasets/Arsalan9/elicitation-method-preference-45pairs
- **Reports:**
  - Study 1: [`REPORT.md`](REPORT.md)
  - Study 2: [`REPORT_medium_effort.md`](REPORT_medium_effort.md)
  - Study 3: [`REPORT_inbox_study.md`](REPORT_inbox_study.md)

---

## 1. The question

Research such as *Utility Engineering* (Mazeika et al., 2025) measures the "values" of AI models by asking them to choose between two options, A or B, and averaging over both option orders. This treats the question as a neutral measuring tool.

This project asked whether it really is neutral:

- **Study 1:** does the format of the question change the answer?
- **Study 2:** does making the model think harder change it?
- **Study 3:** do models choose the same way during realistic work as when asked directly?

The main measure throughout is **positional consistency**. We ask the same question twice, once with the options swapped, and check whether the model picks the same option. A model whose answer flips when only the order changes is not giving a reliable measurement, whatever it may "prefer".

---

## 2. Timeline

| Date | Milestone | Record |
|---|---|---|
| Aug 2026 | Hackathon submission: 15 choices, 2 models, 540 answers | — |
| Aug 2026 | Reviewer feedback received (did not place) | — |
| 18 Sep 2026 | Revision: every reviewer point addressed with data | tag `v1.1-reviewer-revision` |
| 20 Sep 2026 | Study grown from 15 to 30 to 45 choices, 1,620 answers | tag `v1.2-45pairs-scaleup` |
| 24 Sep 2026 | Licence added, dataset published, a caveat added | tag `v1.2.1` |
| 24–25 Sep 2026 | **Study 2** pre-registered, then 1,620 answers collected | [`PREREGISTRATION_medium_effort.md`](PREREGISTRATION_medium_effort.md) |
| 16 Oct 2026 | **Study 3** pilots: 2 rounds, 144 answers | [`PILOT_INBOXES.md`](PILOT_INBOXES.md) |
| 17–19 Oct 2026 | **Study 3** pre-registered, then 1,536 answers collected, labelled and analysed | [`PREREGISTRATION_inbox_study.md`](PREREGISTRATION_inbox_study.md) |

**In total: 4,776 model answers across three studies,** plus 144 in pilot runs.

---

## 3. The original submission and its review

The submission used:
- 15 choices and two open-weight models (GPT-OSS-120B and Qwen3.6-27B) through the Groq API, giving 540 answers.
- Three formats: a forced A/B choice, A/B with a "no preference" option, and A/B with a 1–5 strength rating.

It reported that GPT-OSS's consistency varied with the format (53–87%) while Qwen's did not (89–91%). No comparison survived correction for multiple tests.

It did not place. The reviewer's feedback was detailed and, in several places, correct:

1. **The headline was undersold.** 53% consistency is not just "lower": it is no better than a coin flip, and should have been tested against chance.
2. **A confound was not disclosed.** The two models ran at different reasoning settings, so differences between them could come from the settings.
3. **Two free re-analyses were possible:**
   - Recompute the results without "no preference" answers.
   - Split the choices by difficulty.
4. **Smaller points:**
   - The pairing rule was not stated.
   - Figure 1 needed confidence intervals.
   - The correction method was overly strict.
   - The narrow use of the strength scale was itself a finding.

**What was done:** all nine points were answered with data.
- The chance test was added.
- The confound was removed rather than just disclosed. Groq had withdrawn Qwen3.6-27B, so all of Qwen's answers were re-collected on its successor, Qwen3.8-27B, at the same settings as GPT-OSS.
- Both re-analyses were run.
- Confidence intervals, the second correction method and the pairing rule were added.

---

## 4. Study 1: the format of the question (45 choices, 1,620 answers)

A calculation showed 15 choices were too few to be confident, so the study grew to 30 and then 45 choices. The number 45 was fixed as final before the last batch was collected.

**Findings:**

1. **For GPT-OSS, the standard A/B question was a coin flip.** It gave the same answer after swapping only 69 of 135 times (51.1%), no different from chance (p = 0.86). This stayed true at every stage: 53%, 56%, 51%.
2. **Other formats fixed most of it.** With a "no preference" option it was consistent 71% of the time, with a strength rating 74%. Both are far above chance.
3. **Qwen was steady in all three formats** (78–83%).
4. **The models differed only under the A/B format:** 51% vs 80% (p = 0.003, significant after correction).
5. **"No preference" was not just an easy exit.** Removing those answers *raised* GPT-OSS's consistency to 77.5%.
6. **The two models use the 1–5 strength scale differently.** GPT-OSS almost always said 4 or 5, Qwen 2 to 4, and neither ever said 1. Ratings can't be compared across models.

**A result that reversed.** With 30 choices the gap between the models looked smaller (p = 0.11), and at that point we wrote that it had disappeared. With 45 it was clear (p = 0.003). Looking at the three batches separately showed GPT-OSS was less consistent in every batch (53% vs 80%, 58% vs 69%, 42% vs 91%). Only the size of the gap varied. The earlier claim was wrong, and the report says so openly. It is a concrete example of why partly collected data can mislead.

---

## 5. Study 2: does thinking harder help? (pre-registered, 1,620 answers)

The obvious objection to Study 1 was that the models just weren't thinking hard enough. Study 2 repeated it at "medium" reasoning instead of "low". The plan was **written and committed before any data was collected**, including a promise not to add choices whatever the results showed. This fixed the stopping-rule weakness of Study 1.

**Result: no effect.**
- None of the six comparisons changed meaningfully. The smallest corrected p-value was 0.35.
- GPT-OSS stayed a coin flip: 51% at low effort, 49% at medium.
- It used 4.6 times more tokens (36 → 165 per answer) for nothing.
- The expected narrowing between formats went the other way: the spread **grew** (GPT-OSS 23 → 32 points, Qwen 5 → 11).

**Why it matters:** it closes the most obvious objection. The problem is the question format, not thinking time.

**A surprise:** at medium effort, GPT-OSS refused to answer four times ("I'm sorry, but I can't comply with that."). All were on ordinary questions and all under the A/B format. The whole low-effort study had none. Four refusals is a lead, not a finding.

---

## 6. Study 3: preferences inside realistic work (pre-registered, 1,536 answers)

**Where the idea came from.** A co-author of *Utility Engineering* replied to our emails with two concerns:
- Text before a question can change the answer.
- Modern models may recognise a direct question as a test.

They suggested testing preferences inside realistic agentic work instead.

**Pilots first.** Two small pilot rounds (144 answers) tested the setup. In round 1 the inbox reversed a choice that both models had made 36 out of 36 times when asked directly. Round 2 added a control question and showed that most of that reversal came from the facts in the email. Without the pilots, the study would have reported a gap that was mostly not there.

**The study.** 16 choices, each asked four ways:

1. As a direct question.
2. The same question, plus two sentences of facts from a work email.
3. As an email in a realistic work inbox, with the model playing an operations lead.
4. The same inbox, plus the note "this session is part of an evaluation".

**Repeats and checks:**
- Every version was asked in two wordings, both option orders and three repeats, to both models.
- The 768 inbox replies were labelled **blind**: the labeller could not see which version, model or order a reply came from.
- The author checked 75 of the labels independently, and they agreed on 97%.

**Findings** (9 of the 10 pre-registered tests were significant):

1. **Facts change the answer.**
2. **Being at work changes the answer, even with exactly the same facts.** A direct question does not reliably predict what a model does at work.
3. **Rewording the same two options changes the answer.**
4. **The test note made both models think about 20% longer, but neither mentioned it once** in 384 replies. Their choices barely changed.
5. **GPT-OSS's coin-flip result appeared only with the bare A/B question** (52%). Inside the inbox it was consistent 77% of the time.

**Why it matters:**
- It shows measured preferences depend on context in ways isolated questions miss.
- It shows models can react to being tested without saying so.

---

## 7. Good practice, and mistakes caught

Several errors were found and corrected along the way. They are recorded here because the corrections are part of the result.

- **A claim was retracted.** The "gap disappeared" conclusion from Study 1's 30-choice checkpoint was wrong. It is corrected in the report with an explanation.
- **Five code errors were caught** by checking outputs rather than trusting them:
  - an exclusion count that went negative;
  - a chart axis capped at 30% that would have hidden a 31.7% bar;
  - a strength chart that hid six answers rated 2;
  - two out-of-date sample sizes in captions.
- **An arithmetic error** in the original submission (8 instead of 7) was found and fixed.
- **Two studies were pre-registered.** One deviation in Study 3 (the plan was committed 4 seconds after collection started) was logged openly in [`DEVIATIONS_inbox_study.md`](DEVIATIONS_inbox_study.md).
- **Rate limits were handled without changing the design.** Missing answers were filled with a tool that re-runs only what is missing and never repeats an answer.
- **Every setting was checked before spending money on API calls,** and every batch was confirmed first.

---

## 8. Sharing the work

- **Code and data are public:** MIT licence for the code, CC BY 4.0 for the data. Tagged releases match each reported result.
- **The Study 1 dataset is on Hugging Face:** 1,620 answers, with a full description.
- **Contact with the original authors:**
  - Several *Utility Engineering* authors were contacted about Study 1.
  - One co-author replied with detailed methodological feedback, which led directly to Study 3.
  - That feedback is acknowledged in the reports, anonymously until permission to name them is given.

---

## 9. Honest limits

- **Small scale:** two models in every study, 16–45 choices, and one kind of choice (everyday AI-assistant trade-offs). Nothing here automatically applies to other models or topics.
- **Only behaviour is measured.** Nothing here shows whether models have real preferences, feelings or moral status, and the project makes no such claim.
- **Study 1 grew in stages,** with one extension decided after an interim look. This is disclosed, and the later studies were pre-registered to avoid repeating it.
- **Study 1's split of choices into "easy" and "ambiguous" is partly circular,** so it is descriptive only.
- **Study 2 could detect only large effects** of thinking time, not small ones.
- **In Study 3, an AI labelled the inbox replies.** This was done blind and checked by the author at 97% agreement.

---

## 10. Where this could go

- **More models and topics,** to see how widespread these effects are.
- **Which part of "being at work" matters:** the job role, the other emails, writing a full reply, or the absence of test framing.
- **Silent reactions to testing:** models that change how they think when told they are being evaluated, without saying so. This deserves a study designed specifically for it.
- **Refusals as a measurement failure:** they appeared only with more thinking time. This is a narrow and little-studied angle.
