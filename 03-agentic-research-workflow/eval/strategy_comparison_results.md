# Workflow Strategy Comparison

This benchmark runs five repeatable failure scenarios using two error-handling policies.

## Policy summary

| Policy | Completed | Completion rate | Average attempts |
|---|---:|---:|---:|
| fail_fast | 1/5 | 20% | 3.4 |
| retry_then_resume | 4/5 | 80% | 5.6 |

## Scenario results

| Scenario | Policy | Status | Steps | Attempts | Failure category |
|---|---|---|---:|---:|---|
| no_failure | fail_fast | completed | 5/5 | 5 | none |
| no_failure | retry_then_resume | completed | 5/5 | 5 | none |
| early_transient | fail_fast | failed | 1/5 | 2 | stopped_on_failure |
| early_transient | retry_then_resume | completed | 5/5 | 6 | recovered_transient |
| two_transient_failures | fail_fast | failed | 1/5 | 2 | stopped_on_failure |
| two_transient_failures | retry_then_resume | completed | 5/5 | 7 | recovered_transient |
| late_transient | fail_fast | failed | 4/5 | 5 | stopped_on_failure |
| late_transient | retry_then_resume | completed | 5/5 | 6 | recovered_transient |
| retry_exhausted | fail_fast | failed | 2/5 | 3 | stopped_on_failure |
| retry_exhausted | retry_then_resume | failed | 2/5 | 4 | retry_exhausted |

## Resume test

The first run completed 2 steps before stopping. The resumed run finished with status `completed` without running those completed steps again.

## Scope

All failures are repeatable simulations. This benchmark does not call an external model or estimate token cost.
