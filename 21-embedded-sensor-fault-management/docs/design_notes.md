# Design Notes

## Design approach

The controller is divided into small classes so sensor input, measurement
validation, fault handling, and state transitions can be tested separately.

The implementation uses composition rather than a deep inheritance hierarchy.
A sensor interface separates controller behavior from the simulated data
source.

## Main data structures

### SensorMeasurement

Represents one sensor measurement.

Fields:

- measured value;
- timestamp in milliseconds;
- sequence number;
- source status.

### ControllerConfig

Stores the controller limits used during each deterministic run.

Fields:

- minimum accepted value;
- maximum accepted value;
- maximum change between valid measurements;
- stale-data interval;
- watchdog interval.

### FaultRecord

Stores one detected fault.

Fields:

- fault type;
- detection timestamp;
- triggering sequence number;
- descriptive message;
- critical or noncritical classification;
- active or cleared status.

## Main classes

### SensorInterface

Defines how the controller obtains a measurement.

Primary responsibility:

- provide the next available sensor measurement.

### SimulatedSensor

Provides an ordered host-based measurement sequence.

Primary responsibilities:

- return measurements in a fixed order;
- represent missing updates;
- represent invalid source conditions;
- support repeatable tests.

### MeasurementValidator

Reviews each measurement before it is accepted.

Primary responsibilities:

- range checking;
- rate-of-change checking;
- stale-data checking;
- source-status checking;
- return a structured validation result.

### FaultManager

Stores and manages controller faults.

Primary responsibilities:

- record detected faults;
- latch critical faults;
- report active faults;
- clear faults only when recovery conditions are satisfied.

### Watchdog

Tracks elapsed time since the most recent accepted update.

Primary responsibilities:

- record accepted update times;
- detect missing updates;
- reset only after a valid update.

### SensorController

Coordinates one controller cycle.

Primary responsibilities:

- request a measurement;
- invoke validation;
- update the watchdog;
- record faults;
- manage controller states;
- enforce safe-state and recovery rules;
- expose deterministic results for testing.

## Controller states

    initializing
        |
        | valid current measurement
        v
    monitoring
        |
        | critical fault
        v
    safe
        |
        | explicit reset and valid recovery measurement
        v
    monitoring

A reset request without valid recovery evidence leaves the controller in the
safe state.

## Object-oriented design choices

- Encapsulation keeps state changes within the classes responsible for them.
- Composition lets SensorController coordinate the validator, watchdog, and
  fault manager without inheriting their behavior.
- The sensor interface separates control logic from the measurement source.
- Structured result objects make outcomes explicit and easier to test.
- Constructors will reject invalid configuration values before execution.

## Planned file structure

    src/
      controller_types.hpp
      sensor_interface.hpp
      simulated_sensor.hpp
      simulated_sensor.cpp
      measurement_validator.hpp
      measurement_validator.cpp
      fault_manager.hpp
      fault_manager.cpp
      watchdog.hpp
      watchdog.cpp
      sensor_controller.hpp
      sensor_controller.cpp
      main.cpp

## Verification strategy

Unit tests will examine each class independently. Integration tests will pass
ordered measurement sequences through the complete controller and compare the
observed states and faults with expected outcomes.

The host simulation focuses on deterministic measurement handling,
validation, watchdog timing, fault management, state transitions, and recovery
behavior.
