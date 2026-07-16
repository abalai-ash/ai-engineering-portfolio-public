# Cloud ML Operational Readiness Evaluation

Passed: 8/8

| Check | Result | Details |
|---|---|---|
| healthy service remains ready | PASS | status=ready recommendation=continue_deployment |
| moderate latency holds deployment | PASS | p95=340.0 recommendation=hold_deployment |
| dependency degradation recommends rollback | PASS | dependency_failure_rate=0.2 recommendation=rollback |
| timeout spike recommends rollback | PASS | timeout_rate=0.2 recommendation=rollback |
| missing observations hold deployment | PASS | status=insufficient_data recommendation=hold_deployment |
| invalid thresholds block deployment | PASS | status=invalid_configuration recommendation=block_deployment |
| evaluation is deterministic | PASS | equal=True |
| liveness and readiness remain distinct | PASS | liveness=True readiness=False |

## Scope

This is a deterministic local evaluation using synthetic service observations. It demonstrates latency, error, timeout, dependency-health, readiness, and rollback logic without calling a cloud provider or external service.
