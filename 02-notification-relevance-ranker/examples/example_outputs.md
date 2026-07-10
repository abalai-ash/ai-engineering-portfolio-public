# Example Outputs

## Evaluation run

```text
Evaluation complete: 3/3 passed
Results written to: 02-notification-relevance-ranker/eval/eval_results.md
```

## Evaluation summary

```text
Passed: 3/3
```

| User | Expected top | Actual top | Score | Matching tags | Result |
|---|---|---|---:|---|---|
| u1 | n1 | n1 | 18 | ai;python | PASS |
| u2 | n3 | n3 | 19 | data;science;visualization | PASS |
| u3 | n4 | n4 | 20 | career;interview;jobs | PASS |

## Example user run

```text
Notification Relevance Ranker v2
Available users: u1, u2, u3

Choose a user id:
User: u1
Interests: ai;python;cloud
Preferred channel: email

Ranked notifications:

n1 | score 18 | New AI portfolio task
tags: ai;python;portfolio
matching tags: ai;python
breakdown: interest=2, urgency=3, freshness=5, channel=1

n2 | score 12 | Cloud deployment reminder
tags: cloud;backend;deployment
matching tags: cloud
breakdown: interest=1, urgency=2, freshness=4, channel=1
```

## Interpretation

The top notification for user u1 is n1 because it matches two user interests, has high urgency, is fresh, and uses the user's preferred channel.

This makes the ranking decision easier to inspect instead of only showing a final score.
