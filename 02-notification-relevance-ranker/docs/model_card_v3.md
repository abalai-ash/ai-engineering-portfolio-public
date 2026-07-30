# Notification Relevance Ranker Version 3

## Purpose

This experiment compares an interpretable hand-written ranking baseline with a small XGBoost learning-to-rank model.

The goal is to demonstrate:

- grouped ranking data
- held-out evaluation
- baseline comparison
- MRR, NDCG@3, and top-1 accuracy
- deterministic training
- feature importance
- feature ablation
- held-out ranking-error analysis
- candidate-level comparison of expected and predicted top results
- prediction latency measurement

## Data

The experiment uses deterministic synthetic users, notifications, and graded relevance judgments.

No real users, private data, account information, production logs, or company data are included.

## Model

The learned system uses `XGBRanker` with the `rank:pairwise` objective.

The public repository includes enough information to review and run the experiment, but it does not document an exhaustive tuning recipe.

## Error analysis

The held-out review records misranked queries, compares the expected and predicted top candidates, measures score margins, and checks whether the hand-written baseline succeeds on the same cases.

The current evaluation reports 7 misranked queries out of 45 held-out queries. Four of those cases were ranked correctly by the hand-written baseline.

## Limitations

This is a portfolio-scale offline experiment.

It does not demonstrate:

- production recommendation quality
- causal impact
- online A/B testing
- fairness across real populations
- model monitoring at production scale
- ranking trained from real engagement events
