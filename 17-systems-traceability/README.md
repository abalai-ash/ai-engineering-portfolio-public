# Systems Traceability

This project follows a synthetic monitoring system from stakeholder needs
through requirements, component allocation, interfaces, verification cases,
recorded evidence, baselines, and controlled changes.

The implementation checks requirement wording, parent-child relationships,
verification coverage, baseline differences, and the effects of proposed
requirement changes.

## Included work

- stakeholder, system, and subsystem requirement records
- requirement decomposition and parent-child links
- component and interface allocation
- verification methods and acceptance criteria
- recorded verification evidence
- requirement-level outcome rollups
- missing-link and orphan detection
- baseline comparison
- change-impact analysis
- CSV, JSON, and Markdown reports
- automated tests

## Scope

The project uses synthetic stakeholder, requirement, architecture, interface,
verification, baseline, and change-request records to demonstrate systems
traceability and technical review workflows.

## Environmental and subsurface transfer

The same traceability structure can support synthetic environmental and
subsurface monitoring workflows. Stakeholder needs can be connected to sensor
coverage, sampling requirements, model assumptions, data-quality checks,
interfaces, acceptance criteria, and technical-review evidence.

A proposed change to a monitoring interval, sensor tolerance, modeled
quantity, or investigation threshold can then be traced to affected
requirements, components, interfaces, verification cases, and reports before
the change is accepted.

## Run

```text
python3 eval/evaluate.py
python3 -m unittest discover -s tests -v
```

## Goals

- Connect stakeholder needs to requirements, components, interfaces, and verification evidence.
- Identify incomplete links and affected work before technical review.
- Preserve traceability between monitoring decisions, validation evidence, and controlled changes.

## Lessons

- Clear requirement wording makes verification and change review more reliable.
- Traceability is most useful when technical decisions remain connected to evidence.
- Change-impact analysis shows which verification work must be repeated after a requirement update.

## Accomplishments

- Built a tested requirements and verification workflow for a synthetic monitoring system.
- Documented how the traceability structure transfers to environmental and subsurface monitoring decisions.
- Added coverage checks, outcome rollups, baseline comparison, and change-impact reporting.
