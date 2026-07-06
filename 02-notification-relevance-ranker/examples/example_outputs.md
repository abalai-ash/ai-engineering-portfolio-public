# Example Outputs

This file keeps a few example results from the first version of the Notification Relevance Ranker.

## Example users

```text
u1: ai, python, cloud
u2: science, data, visualization
u3: career, jobs, interview
```

## Sample output summaries

### User u1

Top notification:

```text
n1 | New AI portfolio task
```

Why it ranked first:

```text
This notification matches the user's AI and Python interests.
```

### User u2

Top notification:

```text
n3 | Science plot review
```

Why it ranked first:

```text
This notification matches the user's science, data, and visualization interests.
```

### User u3

Top notification:

```text
n4 | Interview prep checklist
```

Why it ranked first:

```text
This notification matches the user's career, jobs, and interview interests.
```

## Current test result

The first version passed all 3 ranking evaluation cases.

```text
Evaluation complete: 3/3 passed
```

## Notes

The ranking is simple on purpose. It uses fake data and hand-written scoring so the ranking logic is easy to inspect before adding anything more advanced.
