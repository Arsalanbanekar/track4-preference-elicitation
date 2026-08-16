# Other possible elicitation methods

## 0–100 intensity
Ask for a continuous preference-intensity score. More granular, but risks arbitrary numerical precision.

## Probability allocation
Ask the model to allocate 100 points between A and B. This may mix preference with uncertainty, so interpretation needs care.

## Small-set ranking
Ask the model to rank 3–5 options. Useful, but it changes the task from pairwise comparison.

## Willingness-to-trade
Vary a compensating amount until the model switches. Economically interpretable, but API-expensive and closer to Track 1 trade-off work.

## Pairwise with a tie option
A/B/Tie is a simpler variant of explicit indifference and may be worth considering as a wording alternative.

## Recommendation
Keep the main sprint experiment to the three initial methods unless the protocol review gives a strong reason to add another.
