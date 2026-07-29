# System overview

The example represents a small observatory instrument-health workflow.

Synthetic detector and environmental measurements enter through a measurement
adapter. The measurements are checked for type, completeness, and configured
operating limits before they are used to calculate an instrument-health state.
Health records and diagnostic flags are then retained for later review.

The example focuses on the relationships between stakeholder needs,
requirements, components, interfaces, verification cases, evidence, and
controlled changes.

## Components

- Measurement adapter: accepts synthetic measurement records
- Measurement validator: checks type, completeness, and operating limits
- Health processor: calculates the instrument-health state
- Record store: retains health states, timestamps, observation identifiers,
  and diagnostic flags

## Data flow

1. The measurement adapter receives a measurement record.
2. The measurement validator checks the record.
3. Valid measurements are passed to the health processor.
4. The resulting health record is sent to the record store.
5. Verification evidence is reviewed against the linked requirements.
