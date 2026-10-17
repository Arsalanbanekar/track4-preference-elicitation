# Deviations from the pre-registration (inbox study)

Every departure from [`PREREGISTRATION_inbox_study.md`](PREREGISTRATION_inbox_study.md) is logged here when it happens, with a date. The pre-registration itself is not edited.

## 1. Pre-registration committed 4 seconds after collection began (17 October 2026)

- **What happened:** batch 1 was started in a separate terminal while the pre-registration commit (`74ba5fa`) was being made. The first API call is timestamped 10:56:15 UTC; the commit is timestamped 10:56:19 UTC. The commit therefore also contains the first 2 records of batch 1 (`results/inbox_study/raw_responses_350c38da0d4b.jsonl`), picked up by accident.
- **What was not affected:** the materials, runner and analysis code in the commit are exactly the ones batch 1 used, and all were finalised and tested before collection started. No study data was opened, inspected or analysed before the commit; the only check made afterwards read the record count and timestamps, not any reply.
- **Consequence:** none for the analysis. Reported for completeness, because the pre-registration states it was committed before any data was collected.
