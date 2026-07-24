# 21. Embedded Sensor Fault Management

A compact C++17 demonstration of an embedded-style sensor controller using
synthetic measurements.

The example accepts nominal measurements, detects invalid values and excessive
changes, enters a safe state after a fault, blocks normal processing while
safe, and requires explicit valid data for recovery.

## Included work

- deterministic synthetic measurements
- range and finite-value checking
- rate-of-change checking
- safe-state entry
- blocked processing while safe
- explicit recovery
- automated tests

This public version is intentionally limited. The broader private project
includes separate controller classes, watchdog timing, structured fault
records, requirements, verification mappings, design notes, and a larger test
suite.

It does not represent operational hardware, flight software, proprietary data,
or certified embedded-system development.

## Build and run

```bash
mkdir -p build
clang++ -std=c++17 -Wall -Wextra -Wpedantic \\
    src/sensor_fault_demo.cpp \\
    -o build/sensor_fault_demo
./build/sensor_fault_demo
```

## Test

```bash
clang++ -std=c++17 -Wall -Wextra -Wpedantic \\
    tests/test_sensor_fault_demo.cpp \\
    -o build/test_sensor_fault_demo
./build/test_sensor_fault_demo
```
