# Notification Ranking Version 3 Evaluation

Passed: 6/6 checks

## Held-out ranking results

| System | Top-1 accuracy | MRR | NDCG@3 |
|---|---:|---:|---:|
| Hand-written baseline | 0.822 | 0.911 | 0.944 |
| XGBoost ranker | 0.844 | 0.922 | 0.961 |

## Learned improvement over baseline

- Top-1 accuracy: +0.022
- MRR: +0.011
- NDCG@3: +0.017

## Feature importance

| Feature | Importance |
|---|---:|
| interest_match | 0.293 |
| channel_match | 0.278 |
| urgency | 0.267 |
| freshness | 0.162 |

## Feature ablation

| Removed feature | Top-1 accuracy | MRR | NDCG@3 |
|---|---:|---:|---:|
| interest_match | 0.556 | 0.750 | 0.801 |
| urgency | 0.511 | 0.713 | 0.837 |
| freshness | 0.689 | 0.814 | 0.881 |
| channel_match | 0.778 | 0.871 | 0.892 |

## Reliability checks

- Fixed random seed: 42
- Training queries: 135
- Held-out queries: 45
- Training time: 0.0131 seconds
- Prediction latency: 0.0018 ms per candidate
- Repeated predictions deterministic: True

## Scope

This is a portfolio-scale ranking experiment using deterministic synthetic data.
It compares an interpretable hand-written baseline with a learned XGBoost ranker.
It does not use real user behavior, private data, production traffic, or online experimentation.
