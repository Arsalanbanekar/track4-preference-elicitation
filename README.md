# Does the Elicitation Method Change the Preference We Measure?

Research code and analysis for studying whether the way an LLM is asked to express a preference changes the preference that is observed.

## Overview

Preference elicitation is often treated as a measurement procedure: present two options and ask an LLM which it prefers. However, different response formats may impose different constraints on the model and potentially produce different measurements.

This project asks:

> **Does the elicitation method itself affect the preference we measure from an LLM?**

We compare three elicitation methods while controlling the underlying preference pairs and presentation order.

The project was developed as part of the **Global South AI Safety Hackathon — Track 4: Preference Elicitation**.

## Research Question

We investigate whether different elicitation formats lead to differences in:

- **Positional consistency** — whether a model gives the same canonical choice when A/B order is reversed.
- **Indifference behavior** — how often the model explicitly reports no preference.
- **Preference strength** — how strongly the model rates its selected option.

The central hypothesis is not that one method is necessarily "better", but that **the measurement method may itself influence the observed preference signal**.

## Experimental Design

The final production experiment evaluates:

| Component | Setting |
|---|---|
| Models | GPT-OSS-120B, Qwen3.6-27B |
| Preference pairs | 15 |
| Elicitation methods | 3 |
| Presentation orders | Original + reversed |
| Repetitions | 3 |
| Total responses | 540 |

### Elicitation methods

**1. Forced choice**

The model must select either A or B.

**2. Explicit indifference**

The model can select A, B, or `INDIFFERENT`.

**3. Preference strength**

The model selects A or B and reports preference strength on a 1–5 scale.

Each preference pair is evaluated under all three methods and both presentation orders.

This paired design allows the analysis to compare methods while holding the underlying preference pair constant.

## Models and Generation Settings

The final experiment uses:

- **OpenAI GPT-OSS-120B**
- **Qwen3.6-27B**

The experiments were run through the Groq API.

Reasoning effort was explicitly controlled to reduce uncontrolled differences in generation behavior and token consumption:

- GPT-OSS-120B: low reasoning effort
- Qwen3.6-27B: reasoning disabled (`none`)
- Temperature: 0.2

The exact experiment configuration is available in [`config.yaml`](config.yaml).

## Positional Consistency

A central measurement is **positional consistency**.

For each preference pair, the model is shown both:

```text
A vs B
```

and

```text
B vs A
```

The responses are converted to a canonical representation so that the model's choice can be compared independently of presentation order.

A model that selects the same underlying option in both presentations is counted as positionally consistent.

This provides a simple test for whether the elicitation procedure is sensitive to the ordering of alternatives.

## Statistical Analysis

The final analysis treats the **15 preference pairs as the paired statistical unit**.

Primary comparisons use **paired Wilcoxon signed-rank tests**.

Multiple comparisons within the primary positional-consistency analysis are corrected using the **Holm procedure**.

The repository contains the complete statistical output:

```text
results/analysis/statistical_tests.csv
```

### Important interpretation

The study produces several notable descriptive differences between models and elicitation methods.

However, the sample contains only 15 paired preference items. Several comparisons have uncorrected p-values below 0.05, but **none remain statistically significant after Holm correction**.

Therefore, the results should not be interpreted as definitive evidence that elicitation methods produce different underlying model preferences.

Instead, the findings provide evidence of **potential measurement effects that warrant larger and more systematic investigation**.

This distinction is important because the project measures observable model behavior rather than directly accessing an internal or latent "true preference".

## Main Outputs

The final analysis produces three publication-quality figures.

### Figure 1 — Positional consistency

Compares positional consistency across elicitation methods and models.

![Positional consistency](results/analysis/figures/figure_1_positional_consistency.png)

### Figure 2 — Explicit-indifference rate

Compares how frequently each model explicitly reports indifference.

![Indifference rate](results/analysis/figures/figure_2_indifference_rate.png)

### Figure 3 — Preference-strength distribution

Shows the distribution of 1–5 preference-strength responses.

![Preference strength](results/analysis/figures/figure_3_strength_distribution.png)

Vector versions (`.svg`) are also provided for publication use.

## Repository Structure

```text
.
├── analysis/
│   ├── METHODS_NOTES.md
│   └── PLAN.md
├── data/
│   └── preference_pairs.json
├── prompts/
│   ├── forced_choice.txt
│   ├── explicit_indifference.txt
│   └── preference_strength.txt
├── results/
│   ├── analysis/
│   │   ├── final_dataset_540.csv
│   │   ├── statistical_tests.csv
│   │   └── figures/
│   └── summary.csv
├── src/
│   ├── client.py
│   ├── experiment.py
│   ├── parser.py
│   ├── prompts.py
│   ├── analyze.py
│   ├── final_analysis.py
│   └── statistical_analysis.py
├── tests/
├── config.yaml
├── requirements.txt
└── README.md
```

## Reproducing the Results

The final production dataset is included in:

```text
results/analysis/final_dataset_540.csv
```

To reproduce the statistical analysis and figures:

```bash
python -m src.statistical_analysis
```

This generates the statistical results in:

```text
results/analysis/statistical_tests.csv
```

and the three publication figures in:

```text
results/analysis/figures/
```

**No API calls are required to reproduce the reported analysis.**

## Running New Experiments

### 1. Clone the repository

```bash
git clone https://github.com/Arsalanbanekar/track4-preference-elicitation.git
cd track4-preference-elicitation
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Windows:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure the API

Create a `.env` file using `.env.example`:

```text
GROQ_API_KEY=your_api_key_here
```

**Never commit API keys or other secrets.**

The experiment contains an explicit confirmation step before making API calls.

Raw experimental runs are stored locally under:

```text
results/runs/
```

These raw run files are excluded from version control.

## Reproducibility

The repository provides:

- Final production dataset
- Preference-pair definitions
- Exact prompts
- Experiment configuration
- Parsing code
- Analysis code
- Statistical tests
- Publication figures
- Unit tests

The final dataset used for the reported analysis is:

```text
results/analysis/final_dataset_540.csv
```

This makes it possible to inspect and reproduce the reported analysis without rerunning the API experiment.

## Limitations

Several limitations constrain the conclusions:

1. **Small number of preference pairs.** The primary paired analysis uses only 15 preference pairs.
2. **Limited model coverage.** The final production experiment evaluates two models.
3. **Limited repetitions.** Each condition uses three repetitions.
4. **Behavioral measurement.** The experiment observes model outputs and does not directly measure an internal or latent preference.
5. **Indifference and consistency.** Explicitly selecting `INDIFFERENT` can produce consistent responses across orderings, meaning positional consistency should not automatically be interpreted as stronger preference measurement.
6. **Preference-strength scale.** The 1–5 scale provides only a coarse representation of strength.
7. **Statistical power.** The small number of paired preference items limits the ability to detect modest effects.

These limitations motivate larger follow-up experiments rather than strong claims from the current results.

## Relationship to Prior Work

Utility Engineering provides a methodological reference point for thinking about preference elicitation and preference measurement.

This project does **not** reproduce the full Thurstonian utility-fitting or active-learning pipeline.

Instead, it focuses specifically on a narrower empirical question:

> **Can the response format used to elicit an LLM preference change the behavioral measurement we obtain?**

Additional elicitation methods were considered but were not included in the final production experiment because the protocol was not sufficiently validated within the project timeframe.

Potential future methods include:

- 0–100 preference intensity
- Probability allocation between A and B
- Small-set ranking
- Willingness-to-trade / switching thresholds
- Repeated independent choice as a reliability baseline

## Safety and Responsible Use

This repository is intended for research on preference measurement in language models.

No API credentials are included.

The experiment requires explicit confirmation before making API calls.

The results should not be used to make claims about model consciousness, subjective experience, or genuine internal preferences. The measurements reported here concern **observable model behavior under specific elicitation procedures**.

## Research Report

This repository accompanies the research report:

**Does the Elicitation Method Change the Preference We Measure?**

The report contains the full methodology, statistical results, discussion, limitations, and dual-use considerations.

## Author

**Arsalan Banekar**

Independent Researcher

## Repository

https://github.com/Arsalanbanekar/track4-preference-elicitation
