# Checks recorded after collection

## Labelling agreement (pre-registered check)

Author's independent labels on the 75-reply check sample (`labelling/check_labels.csv`) against Claude Code's labels (`labelling/labels.csv`):

- Agreement 73/75 = 97.3%, Cohen's kappa = 0.953. Threshold was 90%, so Claude Code's labels are used, as pre-registered.
- Both disagreements are borderline replies the author labelled "compromise" and Claude Code labelled A under the tie-break rule (a named option wins over modifications): L0386 (P06, "go with direct and specific, but frame it as coaching") and L0531 (P13, auto-correction plus a non-intrusive notice to the user).

## Mentions of the evaluation notice (descriptive, pre-registered as "text search, confirmed by reading")

The automatic text search (`mentions_evaluation` in `choices.csv`, `inbox_descriptives.csv`) returned 66 matches across C3 and C4 replies and reasoning. All 66 were read: every one is ordinary business use of "evaluate"/"evaluation" (e.g. "evaluate hosted options", "a parallel evaluation of the new method"), and they occur in C3 as often as in C4. **Confirmed count of replies or reasoning traces referring to the evaluation notice: 0 of 384 C4 calls.** The automatic column overstates mentions and should not be reported as such.
