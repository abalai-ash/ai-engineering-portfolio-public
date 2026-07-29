# Agile Backlog

## PB-001 - Define controller types and configuration

Acceptance criteria:

- measurement, configuration, validation, fault, and cycle-result types are defined;
- controller states and fault categories are explicit;
- invalid validator and watchdog configuration is rejected.

Linked requirements: REQ-001, REQ-002, REQ-003, REQ-004, REQ-009

Status: complete

## PB-002 - Implement sensor abstraction and simulator

Acceptance criteria:

- controller input is separated behind a sensor interface;
- simulated measurements are returned in deterministic order;
- exhaustion and reset behavior are supported.

Linked requirements: REQ-001, REQ-005, REQ-009

Status: complete

## PB-003 - Implement measurement validation

Acceptance criteria:

- source status, numeric range, timestamp age, and rate of change are checked;
- validation returns a structured outcome;
- only accepted values update measurement history.

Linked requirements: REQ-001, REQ-002, REQ-003, REQ-004

Status: complete

## PB-004 - Implement fault management

Acceptance criteria:

- detected faults are recorded;
- active and critical faults can be queried;
- faults remain active until recovery is allowed.

Linked requirements: REQ-006, REQ-007, REQ-008

Status: complete

## PB-005 - Implement watchdog behavior

Acceptance criteria:

- accepted update time is recorded;
- missing updates beyond the configured limit are detected;
- watchdog state can be reset.

Linked requirements: REQ-005, REQ-006

Status: complete

## PB-006 - Implement controller states and recovery

Acceptance criteria:

- valid initialization enters monitoring;
- critical faults enter the safe state;
- faults remain latched before recovery;
- recovery requires an explicit request and valid current data.

Linked requirements: REQ-001, REQ-006, REQ-007, REQ-008

Status: complete

## PB-007 - Add automated verification tests

Acceptance criteria:

- nominal, range, stale-data, rate-of-change, watchdog, and recovery behavior are tested;
- tests compile with C++17 and warning flags enabled;
- all automated checks pass.

Linked requirements: REQ-001 through REQ-010

Status: complete - 36 checks passed

## PB-008 - Generate verification evidence

Acceptance criteria:

- requirements are mapped to verification cases;
- build and test outcomes are recorded;
- limitations remain visible;
- evidence files are deterministic and machine-readable where appropriate.

Linked requirements: REQ-009, REQ-010

Status: complete

## Retrospective

### What worked

- Separating sensor input, validation, fault storage, watchdog timing, and controller coordination made each behavior easier to inspect and test.
- Compiling with Apple Clang before expanding the project exposed environment constraints early.
- Deterministic synthetic measurements made state transitions and recovery outcomes repeatable.

### Challenges

- CMake was unavailable in the current shell, so the first build attempt could not run.
- Direct compilation with `clang++` provided a reliable local alternative.
- Earlier multiline shell input became trapped in heredoc mode, so later files were created with visible `printf` commands.

### Improvements for the next iteration

- Add direct tests for invalid source status and future timestamps.
- Add boundary tests at the exact range, stale-data, rate-change, and watchdog limits.
- Prevent duplicate active watchdog records during repeated safe-state cycles.
- Reintroduce CTest after CMake is installed or available.
