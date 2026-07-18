# Performance and Rollout Evaluation

## Result

- Rollout decision: `continue_rollout`
- Reason: All configured checks passed.

## Baseline

- Requests: 1000
- Mean latency: 0.000214 ms
- p95 latency: 0.000250 ms
- p99 latency: 0.000333 ms
- Throughput: 3765896.755 requests/second
- Error rate: 0.000000

## Candidate

- Requests: 1000
- Mean latency: 0.000815 ms
- p95 latency: 0.001000 ms
- p99 latency: 0.001042 ms
- Throughput: 1155234.658 requests/second
- Error rate: 0.000000

## Canary Routing

- Baseline requests: 76
- Candidate requests: 24
- Repeated routing is deterministic: True

## Scope

This local exercise uses synthetic requests and a hand-written classifier. It is intended to demonstrate basic benchmarking, service objectives, canary routing, and rollback logic rather than production-scale performance.
