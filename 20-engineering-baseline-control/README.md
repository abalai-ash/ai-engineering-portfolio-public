# 20. Engineering Baseline Control

A compact configuration-baseline demonstration for a synthetic scientific instrument.

The example compares a proposed configuration with an approved baseline, records affected items, checks approvals and rollback readiness, and summarizes release status.

## Included work

- approved baseline records
- proposed configuration changes
- affected-item tracking
- approval checks
- release comparison
- rollback readiness
- synthetic records only

## Run

```bash
python3 src/baseline_demo.py
```

## Test

```bash
python3 -m unittest discover -s tests -v
```

This public version demonstrates the main baseline-control behavior while the broader review process remains private.
