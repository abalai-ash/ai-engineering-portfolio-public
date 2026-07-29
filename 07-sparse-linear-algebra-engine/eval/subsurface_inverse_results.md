# Subsurface Inverse Evaluation

Passed 5/5 checks.

| Check | Result | Detail |
|---|---|---|
| matrix is sparse | PASS | 12 stored entries out of 20 |
| strongest cell is identified | PASS | strongest cell = 2 |
| residual remains small | PASS | residual norm = 0.075264 |
| objective decreases | PASS | start = 0.269574, end = 0.038136 |
| result is repeatable | PASS | two runs returned the same result |

## Result

- Estimated cell values: [0.0, 0.1782, 0.915, 0.1165]
- Strongest estimated cell: cell_2
- Residual norm: 0.075264

## Scope

This evaluation uses a small synthetic linear inverse problem with fixed inputs and repeatable checks.
