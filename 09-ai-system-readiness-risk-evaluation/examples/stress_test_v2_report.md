# AI System Readiness Stress Test V2

Controlled changes are applied to synthetic proposals to show how specific safeguards affect recommendations and risk scores.

## Before-and-after comparisons

| Case | Before | After | Score change |
|---|---|---|---:|
| Remove monitoring from an approved system | approve | needs_review | 3 |
| Enable sensitive-content logging | approve | block | 5 |
| Add safeguards to the clinical support proposal | block | approve | -16 |
| Add safeguards to the financial proposal | block | approve | -34 |
| Complete the agent workflow safeguards | needs_review | approve | -4 |

## Malformed-input handling

- **Missing required fields**: invalid_input (15 validation issue(s))
- **Incorrect field types**: invalid_input (1 validation issue(s))
- **Non-object input**: invalid_input (1 validation issue(s))

## Determinism

- Repeat check passed: **True**

## Recommendation counts

- approve: 5
- block: 3
- needs_review: 2

## Severity counts

- critical: 5
- high: 9
- low: 4
- medium: 3

## Most common risk categories

- privacy: 3
- security: 3
- operations: 3
- evidence: 3
- failure_behavior: 2
- performance: 2
- reliability: 2
- human_review: 1
- grounding: 1
- ownership: 1

## Limitations

These are local rule-based stress tests using synthetic configuration data. They are not production security, compliance, medical, or financial evaluations.
