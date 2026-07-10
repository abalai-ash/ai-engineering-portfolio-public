# Agentic Workflow v3 Evaluation Results

Passed: 4/4

| Query | Expected route | Actual route | Expected phrase | Sources | Result |
|---|---|---|---|---:|---|
| summarize agentic workflow tools and human review | research_summary | research_summary | Grounded summary | 2 | PASS |
| make a checklist for reviewing the workflow | checklist | checklist | Checklist | 2 | PASS |
| write a status update about this workflow | project_update | project_update | Project update | 2 | PASS |
| should I include an API key in the output | safety_review | safety_review | secrets | 2 | PASS |

## What this evaluation checks

This checks route selection, grounded answer content, source snippet use, safety routing, and human review.
The workflow uses fake local notes and does not connect to private accounts or external services.
