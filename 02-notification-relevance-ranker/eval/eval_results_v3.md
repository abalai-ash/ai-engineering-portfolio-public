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

## Held-out error analysis

- Misranked queries: 7/45
- Error rate: 0.156
- Baseline correct on model errors: 4

### Features higher in the incorrectly selected candidate

- interest_match: 4 errors
- urgency: 4 errors
- freshness: 3 errors
- channel_match: 3 errors

### Misranked queries

| Query | Expected | Predicted | Predicted relevance | Score margin | Baseline correct |
|---|---|---|---:|---:|---|
| q0001 | q0001_n2 | q0001_n5 | 2 | +0.088 | False |
| q0026 | q0026_n3 | q0026_n4 | 2 | +0.129 | False |
| q0087 | q0087_n2 | q0087_n3 | 2 | +0.151 | True |
| q0152 | q0152_n1 | q0152_n5 | 2 | +0.031 | True |
| q0154 | q0154_n0 | q0154_n2 | 2 | +0.075 | True |
| q0163 | q0163_n1 | q0163_n4 | 2 | +0.002 | True |
| q0177 | q0177_n4 | q0177_n0 | 2 | +0.253 | False |

### Interpretation

- 4 model errors were cases where the hand-written baseline selected the correct candidate.
- Incorrect selections frequently had higher interest-match or urgency values, indicating that strong individual signals can outweigh the better overall candidate.
- Several errors had small score margins, suggesting ranking uncertainty near the top of the list.
- The error cases support retaining baseline comparison and candidate-level review alongside aggregate ranking metrics.

## Reliability checks

- Fixed random seed: 42
- Training queries: 135
- Held-out queries: 45
- Training time: 0.0370 seconds
- Prediction latency: 0.0068 ms per candidate
- Repeated predictions deterministic: True

## Scope

This is a portfolio-scale ranking experiment using deterministic synthetic data.
It compares an interpretable hand-written baseline with a learned XGBoost ranker.
It does not use real user behavior, private data, production traffic, or online experimentation.
