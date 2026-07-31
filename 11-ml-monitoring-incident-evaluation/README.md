# ML Monitoring and Incident Evaluation

This project compares current model metrics with a saved baseline. It creates
alerts when model quality, latency, error rate, or prediction behavior changes
beyond a set of simple limits.

## What this project covers

- Model-quality monitoring
- Latency and error-rate checks
- Prediction-rate changes
- Alert severity
- Rollback and review decisions
- Deterministic evaluation output

## Run

From this project directory, run:

    python3 eval/evaluate.py

## Included example

The synthetic candidate has lower accuracy, precision, and recall than the
baseline. It also has higher latency, a higher error rate, and a changed
positive-prediction rate.

The monitoring rules use these changes to recommend an action.

## Limits

This is a local demonstration using synthetic metrics. It does not connect to
a live model, production traffic, an alerting system, or a monitoring service.
The included limits were selected for the example and are not production
service objectives.

## Incident response workflow

When monitoring limits are exceeded, the project now creates a structured
incident-response record containing:

- Incident severity
- Assigned operational owner
- Affected metrics
- Immediate response steps
- Whether rollback is required
- Recovery verification checks
- Incident closure status

For the included candidate, multiple high-severity quality and reliability
alerts produce a critical incident. Candidate promotion is stopped, rollback
to the approved baseline is required, and the incident remains open until the
recovery checks pass.

The evaluator also verifies that critical incidents receive an owner, require
rollback, include recovery checks, and cannot be closed before recovery.
