# Evaluation Results

| Case | Expected | Actual | Result |
|---|---|---|---|
| `research_assistant_ready` | `approve` | `approve` | **PASS** |
| `clinical_summary_incomplete` | `block` | `block` | **PASS** |
| `financial_risk_high` | `block` | `block` | **PASS** |
| `agent_workflow_review` | `needs_review` | `needs_review` | **PASS** |
| `environmental_monitoring_review` | `needs_review` | `needs_review` | **PASS** |

Evaluation complete: **5/5 passed**.

These cases use synthetic proposals and transparent rule-based checks.
