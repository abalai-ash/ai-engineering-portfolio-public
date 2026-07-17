# Notification Relevance Ranker

This project is a small ranking-system demo that chooses which notification is most useful for a user.

It uses fake users and fake notifications, then scores each notification based on interest match, urgency, freshness, and preferred channel. The goal is to practice the basic structure behind recommendation, notification, search, and product-ranking systems.

## Why this project matters

Many AI and product systems need to decide what to show first. This can apply to:

- notifications
- search results
- recommendations
- job matches
- user-facing reminders
- feed ranking

A good ranking system should not only return a result, but also make the decision inspectable. This project includes a score breakdown so each ranking decision can be reviewed.

## Project structure

```text
02-notification-relevance-ranker/
  README.md
  data/
    notifications.csv
    users.csv
  eval/
    eval_cases.csv
    eval_results.md
    evaluate.py
  examples/
    example_outputs.md
  src/
    ranker_v1.py
```

## Current features

- loads fake user and notification data
- scores notifications using multiple ranking signals
- uses interest match, urgency, freshness, and channel preference
- returns a ranked list from most relevant to least relevant
- prints matching tags and score breakdowns
- includes an evaluation script for expected top-ranked results

## Ranking signals

The current hand-written scoring uses:

- interest match
- urgency
- freshness
- preferred channel match

Each notification receives a total score. The ranker also prints the score breakdown so the ranking is easier to inspect.

## Run locally

```bash
python src/ranker_v1.py
```

Then choose a user:

```text
u1
```

To run the evaluation:

```bash
python eval/evaluate.py
```

## Current evaluation result

```text
Passed: 3/3
```

The evaluation checks whether the highest-ranked notification matches the expected top notification for each fake user. It also records the top score and matching tags.

## What this project demonstrates

- ranking logic
- feature-style scoring
- score breakdowns
- simple evaluation
- user-context matching
- product ML thinking

## Limitations

This is a small demo with fake data and hand-written weights. It does not train on real user behavior and does not claim to be a production notification system.

## Version 3: learned ranking evaluation

Version 3 compares the original hand-written ranking logic with a learned XGBoost ranker on deterministic synthetic judgments.

It demonstrates:

- grouped train and held-out evaluation data
- Top-1 accuracy, MRR, and NDCG@3
- comparison against a non-personalized baseline
- feature-importance and feature-ablation analysis
- deterministic repeated predictions
- local training and prediction latency measurements

In the current held-out evaluation, the learned ranker improves over the hand-written baseline across Top-1 accuracy, MRR, and NDCG@3.

The public project reports the experiment design and measured results without presenting it as a production ranking recipe or a model trained on real users.

Run the evaluation:

```bash
python3 eval/evaluate_v3.py
```

See `model_card_v3.md` and `eval/eval_results_v3.md` for scope, results, and limitations.
