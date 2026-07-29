# Verification Planning and Evidence

A synthetic environmental-monitoring workflow is used to organize verification
objectives, methods, readiness conditions, acceptance criteria, evidence,
anomalies, retesting, and closure.

The implementation checks whether planned verification is executable, whether
recorded evidence is sufficient, whether acceptance criteria were satisfied,
and whether unresolved findings prevent closure.

## Included work

- verification objectives and linked requirements
- test, analysis, demonstration, and inspection methods
- entry and readiness conditions
- measurable acceptance criteria
- evidence records and provenance fields
- anomaly classification
- corrective-action and retest records
- requirement-level outcome rollups
- closure-readiness review
- JSON, CSV, and Markdown reports
- automated tests

## Scope

The project uses synthetic monitoring records, model-comparison results,
readiness checks, evidence fields, anomalies, corrective actions, and retest
records to demonstrate verification planning and closure review.

## Environmental and subsurface transfer

The workflow verifies measurement-model agreement, monitoring-record
completeness, validation-record contents, evidence currency, and anomaly-based
closure controls.

The same structure can support synthetic subsurface investigations by changing
the measured quantity, model output, acceptance thresholds, and required
evidence while retaining the planning, readiness, provenance, anomaly, retest,
and closure checks.

## Run

    python3 eval/evaluate.py
    python3 -m unittest discover -s tests -v

Generated reports are written locally to reports/.

## Goals

- Connect verification plans to measurable evidence and technical outcomes.
- Identify incomplete evidence, unresolved anomalies, and blocked closure.
- Preserve traceability from requirements through retest and closure decisions.

## Lessons

- Acceptance criteria must be measurable before evidence can support closure.
- A passing metric is insufficient when readiness, provenance, or anomaly
  records are incomplete.
- Resolved anomalies still require completed corrective-action and retest
  evidence.

## Accomplishments

- Structured verification planning, execution evidence, anomaly review, and
  retesting for a synthetic environmental-monitoring workflow.
- Added automated checks for readiness, evidence sufficiency, outcomes,
  corrective actions, retesting, and closure status.
