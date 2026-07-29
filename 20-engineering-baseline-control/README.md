# Engineering Baseline Control

A synthetic environmental-monitoring configuration is followed through baseline
creation, proposed changes, technical review, approval, release comparison,
and rollback preparation.

The implementation checks whether configuration records are complete, whether
proposed changes identify their rationale and affected items, whether required
reviews are recorded, and whether a release can be reconstructed from its
approved baseline.

## Included work

- versioned configuration items
- approved baseline records
- proposed engineering changes
- affected-item and dependency review
- technical and approval records
- baseline comparison
- release reconstruction checks
- rollback readiness
- JSON, CSV, and Markdown reports
- automated tests

## Scope

The project uses synthetic monitoring configurations, model references,
processing thresholds, change requests, approvals, releases, and rollback
records to demonstrate controlled engineering baseline management.

## Run

    python3 eval/evaluate.py
    python3 -m unittest discover -s tests -v

Generated reports are written locally to reports/.

## Goals

- Keep technical configurations reproducible as controlled changes are reviewed.
- Identify incomplete approvals, affected records, and rollback limitations.

## Lessons

- A version number alone is not a sufficient engineering baseline.
- Change review is stronger when rationale, dependencies, evidence, and approval
  remain connected.

## Accomplishments

- Structured baseline creation, change review, release comparison, and rollback
  preparation for a synthetic environmental-monitoring configuration.
- Defined automated checks for configuration completeness, approvals, impact,
  reconstruction, and recovery readiness.
