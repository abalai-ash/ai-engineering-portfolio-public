# Notification Relevance Ranker

Goal: Build a small ranking demo that chooses which notification is most useful for a user.

This project practices a simple version of recommendation and relevance ranking. The first version uses fake users and fake notifications, then scores each notification based on interest match, urgency, freshness, and preferred channel.

## Why this project matters

Many AI and product systems need to choose what to show first. This can apply to notifications, search results, recommendations, job matches, or user-facing reminders.

## Project structure

```text
02-notification-relevance-ranker/
├── README.md
├── data/
│   ├── notifications.csv
│   └── users.csv
├── eval/
│   ├── eval_cases.csv
│   ├── eval_results.md
│   └── evaluate.py
├── examples/
└── src/
    └── ranker_v1.py
```

## Current features

- Loads fake user and notification data
- Scores notifications using simple ranking signals
- Uses interest match, urgency, freshness, and channel preference
- Sorts notifications from most relevant to least relevant
- Includes a small evaluation script

## How to run locally

From this folder, run:

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

## What I am learning

- How ranking systems use simple signals
- How different weights affect the final order
- How to test whether the top result matches an expected result
- How product ML connects to user-facing relevance

## Current limitations

- This version uses fake data.
- The scoring weights are simple and hand-written.
- It does not learn from real user behavior.
- It only checks the top result, not the full ranked list.

## Status

Version 1 in progress.
