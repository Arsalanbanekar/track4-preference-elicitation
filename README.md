# How Reliable Are Measurements of AI Preferences?

Three studies testing whether the way we ask an AI model about its preferences changes the answer we get.

Researchers often measure what an AI model "prefers" by asking it to pick between two options, A or B. This project checks whether that measurement can be trusted. It uses two open-weight models, GPT-OSS-120B and Qwen3.8-27B, run through the Groq API.

**Author:** Arsalan Banekar, Independent Researcher.
**Started as:** a submission to the Global South AI Safety Hackathon, Track 4: Preference Elicitation, August 2026.

---

## The three studies at a glance

| Study | Question | Main finding | Report |
|---|---|---|---|
| **1. Question format** (45 choices, 1,620 answers) | Does the format of the question change the answer? | Under a plain A/B question, GPT-OSS's answers flip at coin-flip level when the options are swapped (51%). Letting it say "no preference" or rate its strength raises this to 71–74%. Qwen is steady in every format. | [REPORT.md](REPORT.md) |
| **2. Thinking harder** (pre-registered, 1,620 answers) | Does more reasoning effort make answers more reliable? | No. GPT-OSS is still a coin flip (49%) and uses 4.6 times more tokens. A new problem appeared: it refused to answer four times. | [REPORT_medium_effort.md](REPORT_medium_effort.md) |
| **3. Choices at work** (pre-registered, 1,536 answers) | Do models choose the same way inside a realistic work inbox as when asked directly? | No. The work setting changes their choices even with the same facts. Rewording changes them too. A "this is a test" note made both models think about 20% longer, but they never mentioned it. | [REPORT_inbox_study.md](REPORT_inbox_study.md) ([PDF](REPORT_inbox_study.pdf)) |

**Want the whole story in one place?** [PROJECT_RECORD.md](PROJECT_RECORD.md) covers the whole project: the original submission, the reviewer's feedback, all three studies, and the mistakes caught along the way.

---

## The key idea: positional consistency

Each question is asked twice, once as "A vs B" and once as "B vs A". If the model really prefers one option, it should pick it both times. If it picks whatever comes first (or last), its answer flips.

**Positional consistency** is how often the answer stays the same. 50% is what pure chance gives.

---

## What is in this repository

**Reports**

| File | What it is |
|---|---|
| `REPORT.md` | Study 1: question format |
| `REPORT_medium_effort.md` | Study 2: reasoning effort |
| `REPORT_inbox_study.md` / `.pdf` | Study 3: choices at work |
| `PROJECT_RECORD.md` | The whole project in one document |
| `PILOT_INBOXES.md` | The two pilot rounds that shaped Study 3 |

**Plans and records** (left unchanged on purpose: they prove what was decided before data existed)

| File | What it is |
|---|---|
| `PREREGISTRATION_medium_effort.md` | Study 2's plan, written before data collection |
| `PREREGISTRATION_inbox_study.md` | Study 3's plan, written before analysis |
| `STUDY_DESIGN_inbox.md` | Why Study 3 was designed the way it was |
| `DEVIATIONS_inbox_study.md` | The one place Study 3 departed from its plan |

**Code and data**

```text
data/preference_pairs.json         the 45 choices (Studies 1 and 2)
prompts/                           the three question formats
study/inbox_items.json             Study 3's 16 decisions and emails
pilot/                             the pilot emails, as run
config.yaml, config_medium.yaml    settings for Studies 1 and 2
src/                               all code (collection, analysis, figures, PDF)
tests/                             automatic checks (run with: pytest)
results/analysis/                  Study 1 dataset, statistics, figures
results/analysis_medium/           Study 2 dataset and statistics
results/runs_medium/               Study 2 raw answers
results/inbox_study/               Study 3 raw answers, labels, analysis, figures
results/pilot_inbox*/              pilot answers
hf_dataset/                        Hugging Face dataset card (Study 1)
```

---

## Reproducing the results

None of these commands calls the API:

```bash
python -m src.statistical_analysis       # Study 1: statistics and figures
python -m src.inbox_analysis --analyse   # Study 3: pre-registered analysis
python -m src.inbox_figures              # Study 3: figures
python -m src.inbox_power                # Study 3: power simulation
pytest                                   # automatic checks
```

The Study 1 answers are also on Hugging Face: [Arsalan9/elicitation-method-preference-45pairs](https://huggingface.co/datasets/Arsalan9/elicitation-method-preference-45pairs).

## Running new experiments

1. **Install:**

   ```bash
   git clone https://github.com/Arsalanbanekar/track4-preference-elicitation.git
   cd track4-preference-elicitation
   python -m venv .venv
   .venv\Scripts\Activate.ps1        # Windows (macOS/Linux: source .venv/bin/activate)
   pip install -r requirements.txt
   ```

2. **Add your Groq key:** copy `.env.example` to `.env` and add `GROQ_API_KEY=...`. **Never commit API keys.**

3. **Run.** Every script shows the exact number of API calls and waits for you to type a confirmation before making any. For example:
   - `python -m src.experiment --config config_medium.yaml --pair_range 1-15` (Study 2 style)
   - `python -m src.inbox_study --batch 1` (Study 3)

---

## Limits

- **Two models,** and one kind of choice: everyday AI-assistant trade-offs. The results may not hold for other models or topics.
- **Study 1 grew in stages** (15 → 30 → 45 choices), and one result reversed along the way. This is disclosed in full. Studies 2 and 3 were pre-registered to avoid repeating it.
- **These are measurements of behaviour.** Nothing here shows whether models have real preferences, feelings or moral status.

## Relationship to prior work

This project builds on the A/B question format of *Utility Engineering* (Mazeika et al., 2025). It reuses only that format and its order-swapping step, not the paper's full statistical model. It is independent and not affiliated with that paper's authors.

## License

Code: [MIT License](LICENSE). Data on Hugging Face: CC BY 4.0.

## Repository

https://github.com/Arsalanbanekar/track4-preference-elicitation
