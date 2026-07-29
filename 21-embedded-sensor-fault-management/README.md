# Embedded Sensor Fault Management

A host-simulated sensor controller is used to examine measurement validation,
operating-state transitions, timing faults, and safe-state behavior.

The implementation represents the controller as a set of C++ classes with
defined responsibilities for sensor acquisition, measurement review, state
management, fault recording, watchdog checks, and output reporting.

## Included work

- synthetic sensor and timing records
- object-oriented C++ design
- sensor interfaces and simulated implementations
- measurement range and rate-of-change checks
- operating-state transitions
- stale-data and timeout detection
- watchdog and safe-state behavior
- fault latching and recovery rules
- requirements and acceptance criteria
- unit and integration tests
- JSON and Markdown verification records
- Agile backlog and retrospective notes

## Scope

The project uses synthetic measurements, deterministic timing records,
validation limits, fault states, watchdog behavior, and recovery scenarios to
demonstrate embedded-style sensor fault management in a host simulation.

## Environmental and subsurface transfer

The controller structure can support synthetic environmental-monitoring cases
such as conductivity, moisture, temperature, or other measurement streams by
changing the configured limits and simulated inputs while retaining validation,
fault latching, watchdog, safe-state, and recovery behavior.

## Verified local build and run

The project was compiled locally with Apple Clang 17 in C++17 mode.

    mkdir -p build

    clang++ -std=c++17 -Wall -Wextra -Wpedantic -Isrc \
        src/fault_manager.cpp \
        src/measurement_validator.cpp \
        src/sensor_controller.cpp \
        src/simulated_sensor.cpp \
        src/watchdog.cpp \
        src/main.cpp \
        -o build/sensor_controller_demo

    ./build/sensor_controller_demo

## Verified automated tests

    clang++ -std=c++17 -Wall -Wextra -Wpedantic -Isrc \
        src/fault_manager.cpp \
        src/measurement_validator.cpp \
        src/sensor_controller.cpp \
        src/simulated_sensor.cpp \
        src/watchdog.cpp \
        tests/test_controller.cpp \
        -o build/controller_tests

    ./build/controller_tests

The current suite contains 36 passing checks. Requirement mappings are stored
in `data/verification_cases.json`, and the private verification summary is
stored in `reports/verification_summary.md`.

A CMake build definition is included for portability, but CMake was not
available in the local shell used for this verification.

## Goals

- Model a small embedded-style controller with clear C++ interfaces and
  deterministic state transitions.
- Detect invalid, stale, rapidly changing, and missing measurements before they
  affect downstream behavior.
- Connect controller requirements to repeatable automated verification evidence.
- Demonstrate fault latching, safe-state entry, and controlled recovery using
  deterministic synthetic measurements.

## Lessons

- Separating sensor input, validation, fault storage, watchdog timing, and
  controller coordination made the behavior easier to test and explain.
- Rejected measurements should not update the previous-value baseline used for
  rate-of-change checks.
- Safe-state recovery is stronger when it requires both an explicit request and
  valid current data.
- Deterministic synthetic inputs make fault reproduction and verification more
  reliable.
- Tooling assumptions should be checked early; direct Apple Clang compilation
  provided a practical fallback when CMake was unavailable.

## Accomplishments

- Implemented a C++17 sensor interface and deterministic simulated sensor.
- Added range, source-status, stale-data, future-timestamp, and rate-of-change
  validation behavior.
- Implemented fault recording, active-fault queries, critical-fault latching,
  and controlled clearing.
- Added watchdog monitoring for missing accepted updates.
- Built controller logic for initialization, monitoring, safe-state entry, and
  explicit recovery.
- Compiled the project successfully with Apple Clang using `-Wall`, `-Wextra`,
  and `-Wpedantic`.
- Added a deterministic demonstration that enters monitoring, detects a fault,
  transitions to safe, and successfully recovers.
- Added 36 passing automated checks covering sensor behavior, validation,
  controller state changes, watchdog handling, fault latching, safe-state
  cycle blocking, valid recovery, and failed-recovery preservation.
- Created requirement-to-test mappings and a private verification summary for
  REQ-001 through REQ-010.
- Completed an Agile backlog and retrospective based on the implemented work.
