# Evaluation Results

Passed: **9/9**

| Check | Result | Details |
|---|---|---|
| all requests reach solution planning | PASS | 3 reports checked |
| restricted enterprise sources are detected | PASS | ['support notes', 'account records'] |
| robotics plan includes failure recovery | PASS | pilot_ready |
| scientific case identifies missing rollback plan | PASS | ['rollback_plan'] |
| enterprise_knowledge_assistant recommendation | PASS | expected=needs_review actual=needs_review |
| robot_localization_support recommendation | PASS | expected=pilot_ready actual=pilot_ready |
| scientific_workload_benchmark recommendation | PASS | expected=needs_review actual=needs_review |
| incomplete request is rejected | PASS | invalid_request |
| solution planning is deterministic | PASS | equal=True |

## Scope

This evaluation uses synthetic requests and local, rule-based planning logic. It does not represent a production deployment, customer engagement, robotics system, or quantum hardware benchmark.
