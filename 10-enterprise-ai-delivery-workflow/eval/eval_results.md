# Evaluation Results

Passed: **10/10**

| Check | Result | Details |
|---|---|---|
| all requests reach solution planning | PASS | 4 reports checked |
| restricted enterprise sources are detected | PASS | ['support notes', 'account records'] |
| robotics plan includes failure recovery | PASS | pilot_ready |
| scientific case identifies missing rollback plan | PASS | ['rollback_plan'] |
| enterprise_knowledge_assistant recommendation | PASS | expected=needs_review actual=needs_review |
| robot_localization_support recommendation | PASS | expected=pilot_ready actual=pilot_ready |
| scientific_workload_benchmark recommendation | PASS | expected=needs_review actual=needs_review |
| environmental_monitoring_review recommendation | PASS | expected=needs_review actual=needs_review |
| incomplete request is rejected | PASS | invalid_request |
| solution planning is deterministic | PASS | equal=True |

## Scope

This evaluation uses synthetic requests and local, rule-based planning logic to test discovery coverage, risk decisions, recommendation behavior, invalid-input handling, and deterministic output.
