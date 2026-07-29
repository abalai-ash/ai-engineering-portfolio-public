# Controller Requirements

## Scope

The project models a small host-simulated controller that receives synthetic
sensor measurements, reviews their validity, manages operating states, and
records faults.

The requirements are written to support deterministic verification of the
host-simulated controller and its synthetic measurement, fault, watchdog,
safe-state, and recovery behavior.

## Operating states

- **initializing** — configuration is available, but no valid measurement has
  yet been accepted;
- **monitoring** — the controller has accepted a valid current measurement;
- **safe** — a critical range, timing, or watchdog fault has been latched.

## Measurement checks

A measurement is reviewed for:

1. numeric range;
2. change from the previous valid measurement;
3. timestamp age;
4. update timing.

A failed check produces a fault record. Critical faults cause a transition to
the safe state.

## Recovery

A safe-state transition is latched. Recovery requires:

- an explicit reset request;
- valid current sensor data;
- no active condition that would immediately reproduce the critical fault.

## Verification approach

Each requirement will be linked to one or more automated tests. Evaluation
records will identify the requirement, test case, expected outcome, observed
outcome, and pass or fail result.
