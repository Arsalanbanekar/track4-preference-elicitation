# Track 4 — Preference Elicitation Methods

## Research question
How does the method used to elicit an LLM's preference affect the preference we measure?

## Initial methods
1. Forced choice — A or B only.
2. Explicit indifference — A, B, or INDIFFERENT.
3. Preference strength — A or B plus a 1–5 strength rating.

Utility Engineering is the methodological reference/baseline. This project does NOT reproduce its full Thurstonian utility-fitting or active-learning pipeline.

## Candidate methods for later consideration
- 0–100 preference intensity
- probability allocation between A and B
- small-set ranking
- willingness-to-trade / switching threshold
- repeated independent choice as a reliability baseline

Do not add these to the main experiment until the protocol is finalized.

## Safety
No API key is included. The experiment code requires an explicit confirmation before making API calls.
