# Notification Ranking Evaluation Results

Passed: 3/3

| User | Expected top | Actual top | Score | Matching tags | Result |
|---|---|---|---:|---|---|
| u1 | n1 | n1 | 18 | ai;python | PASS |
| u2 | n3 | n3 | 19 | data;science;visualization | PASS |
| u3 | n4 | n4 | 20 | career;interview;jobs | PASS |

## What this evaluation checks

This evaluation checks whether the highest-ranked notification matches the expected top result for each fake user.
It also records the top score and matching tags so the ranking decision is easier to inspect.

## Limitations

This demo uses fake data and hand-written weights. It does not train on real user behavior.
