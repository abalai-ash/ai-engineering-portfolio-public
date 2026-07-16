# Agent Reliability Evaluation

Passed: **10/10**

| Check | Result | Details |
|---|---|---|
| retry policy completes after recoverable failures | PASS | completed |
| all workflow steps complete | PASS | 5/5 |
| recovered failures are counted | PASS | 2 |
| fail-fast policy stops immediately | PASS | failed |
| fail-fast records one unrecovered failure | PASS | 1 |
| retry exhaustion stops safely | PASS | failed |
| checkpoint preserves completed steps | PASS | ['route_query', 'retrieve_notes'] |
| workflow resumes and completes | PASS | completed |
| resumed workflow does not repeat completed steps | PASS | {'route_query': 1, 'retrieve_notes': 1, 'summarize_evidence': 2, 'build_checklist': 1, 'draft_update': 1} |
| simulated reliability evaluation is deterministic | PASS | equal=True |

## Scope

This evaluation uses deterministic simulated tool failures. It demonstrates checkpointing, retries, safe stopping, resume behavior, and policy comparison without calling external services.
