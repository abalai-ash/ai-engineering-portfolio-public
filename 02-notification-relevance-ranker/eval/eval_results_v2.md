# Notification Ranking Version 2 Evaluation

Passed: 5/5 checks

## Main metrics

| System | Hit@1 | MRR | NDCG@3 |
|---|---:|---:|---:|
| Version 2 ranker | 1.000 | 1.000 | 0.972 |
| Non-personalized baseline | 0.333 | 0.611 | 0.669 |

## Feature ablation

| Removed feature | Hit@1 | MRR | NDCG@3 |
|---|---:|---:|---:|
| interest | 0.333 | 0.667 | 0.709 |
| urgency | 1.000 | 1.000 | 0.994 |
| freshness | 1.000 | 1.000 | 0.972 |
| channel | 1.000 | 1.000 | 0.972 |

## Reliability checks

- Deterministic output: `True`
- Median local evaluation latency: `0.0476 ms`
- P95 local evaluation latency: `0.0518 ms`

## Error analysis

- No top-rank errors occurred in the small synthetic evaluation set.

## Scope

This is a small deterministic portfolio evaluation using synthetic data.
It demonstrates ranking metrics, baseline comparison, feature ablation,
latency measurement, explainable signals, and reproducible evaluation.
It is not a production notification system or a model trained on real users.
