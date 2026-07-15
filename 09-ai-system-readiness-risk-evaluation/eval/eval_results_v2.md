# Version 2 Stress-Test Evaluation

| Test | Result | Detail |
|---|---|---|
| approved baseline remains approved | **PASS** | actual=approve |
| removing monitoring raises risk | **PASS** | before=0 after=3 |
| sensitive logging blocks launch | **PASS** | actual=block |
| clinical safeguards lower risk | **PASS** | before=16 after=0 |
| agent safeguards lower risk | **PASS** | before=4 after=0 |
| missing fields return invalid input | **PASS** | actual=invalid_input |
| incorrect types return invalid input | **PASS** | actual=invalid_input |
| repeated evaluation is deterministic | **PASS** | equal=True |

Evaluation complete: **8/8 passed**.

The cases use synthetic proposals and local rule-based checks.
