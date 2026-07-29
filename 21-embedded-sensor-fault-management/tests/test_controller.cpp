#include "measurement_validator.hpp"
#include "sensor_controller.hpp"
#include "simulated_sensor.hpp"
#include "watchdog.hpp"

#include <cmath>
#include <iostream>
#include <limits>
#include <string>
#include <vector>

namespace {

int failures = 0;

void expect(bool condition, const std::string& test_name) {
    if (condition) {
        std::cout << "PASS: " << test_name << "\n";
    } else {
        std::cout << "FAIL: " << test_name << "\n";
        ++failures;
    }
}

ControllerConfig test_config() {
    return {0.0, 100.0, 15.0, 250, 500};
}

void test_simulated_sensor() {
    SimulatedSensor sensor({
        {10.0, 100, 1, SourceStatus::Valid},
        {20.0, 200, 2, SourceStatus::Valid}
    });

    expect(sensor.remaining() == 2, "sensor starts with two measurements");
    expect(sensor.next_measurement()->sequence_number == 1,
           "sensor returns measurements in order");
    expect(sensor.remaining() == 1, "sensor tracks remaining measurements");

    sensor.reset();
    expect(sensor.next_measurement()->sequence_number == 1,
           "sensor reset restores the first measurement");
}

void test_measurement_validator() {
    MeasurementValidator validator(test_config());

    const ValidationResult nominal = validator.validate(
        {40.0, 1000, 1, SourceStatus::Valid},
        1000
    );
    expect(nominal.accepted, "validator accepts a nominal measurement");

    const ValidationResult range = validator.validate(
        {120.0, 1100, 2, SourceStatus::Valid},
        1100
    );
    expect(!range.accepted && range.fault_type == FaultType::Range,
           "validator rejects an out-of-range measurement");

    const ValidationResult stale = validator.validate(
        {40.0, 1000, 3, SourceStatus::Valid},
        1300
    );
    expect(!stale.accepted && stale.fault_type == FaultType::StaleData,
           "validator rejects stale data");
}


void test_validation_boundaries() {
    MeasurementValidator validator(test_config());

    const ValidationResult minimum = validator.validate(
        {0.0, 1000, 1, SourceStatus::Valid},
        1000
    );
    expect(minimum.accepted,
           "validator accepts the exact minimum value");

    const ValidationResult maximum = validator.validate(
        {100.0, 1000, 2, SourceStatus::Valid},
        1000
    );
    expect(maximum.accepted,
           "validator accepts the exact maximum value");

    const ValidationResult nan_value = validator.validate(
        {
            std::numeric_limits<double>::quiet_NaN(),
            1000,
            3,
            SourceStatus::Valid
        },
        1000
    );
    expect(
        !nan_value.accepted &&
        nan_value.fault_type == FaultType::Range,
        "validator rejects a NaN measurement"
    );

    const ValidationResult infinite_value = validator.validate(
        {
            std::numeric_limits<double>::infinity(),
            1000,
            4,
            SourceStatus::Valid
        },
        1000
    );
    expect(
        !infinite_value.accepted &&
        infinite_value.fault_type == FaultType::Range,
        "validator rejects an infinite measurement"
    );

    const ValidationResult invalid_source = validator.validate(
        {40.0, 1000, 3, SourceStatus::Invalid},
        1000
    );
    expect(
        !invalid_source.accepted &&
        invalid_source.fault_type == FaultType::InvalidSource,
        "validator rejects invalid source status"
    );

    const ValidationResult future_timestamp = validator.validate(
        {40.0, 1100, 4, SourceStatus::Valid},
        1000
    );
    expect(
        !future_timestamp.accepted &&
        future_timestamp.fault_type == FaultType::StaleData,
        "validator rejects a future timestamp"
    );

    const ValidationResult stale_boundary = validator.validate(
        {40.0, 1000, 5, SourceStatus::Valid},
        1250
    );
    expect(stale_boundary.accepted,
           "validator accepts data at the exact stale-data limit");

    validator.record_accepted(
        {40.0, 1250, 6, SourceStatus::Valid}
    );

    const ValidationResult change_boundary = validator.validate(
        {55.0, 1300, 7, SourceStatus::Valid},
        1300
    );
    expect(change_boundary.accepted,
           "validator accepts change at the exact rate limit");

    Watchdog watchdog(500);
    watchdog.record_update(1000);

    expect(!watchdog.expired(1500),
           "watchdog remains valid at the exact timeout limit");
    expect(watchdog.expired(1501),
           "watchdog expires after the timeout limit");
}

void test_controller_fault_and_recovery() {
    SimulatedSensor sensor({
        {42.0, 1000, 1, SourceStatus::Valid},
        {80.0, 1100, 2, SourceStatus::Valid},
        {45.0, 1200, 3, SourceStatus::Valid}
    });

    SensorController controller(sensor, test_config());

    const ControllerCycleResult first = controller.run_cycle(1000);
    expect(first.measurement_accepted,
           "controller accepts the initial valid measurement");
    expect(controller.state() == ControllerState::Monitoring,
           "controller enters monitoring after valid initialization");

    const ControllerCycleResult fault = controller.run_cycle(1100);
    expect(fault.fault_type == FaultType::RateOfChange,
           "controller detects excessive measurement change");
    expect(controller.state() == ControllerState::Safe,
           "controller enters the safe state after a critical fault");
    expect(controller.fault_manager().has_active_critical_fault(),
           "critical fault remains active before recovery");

    expect(controller.request_recovery(1200),
           "controller accepts explicit recovery with valid data");
    expect(controller.state() == ControllerState::Monitoring,
           "controller returns to monitoring after recovery");
    expect(!controller.fault_manager().has_active_faults(),
           "recovery clears active faults");
}



void test_safe_state_blocks_normal_cycles() {
    SimulatedSensor sensor({
        {40.0, 1000, 1, SourceStatus::Valid},
        {80.0, 1100, 2, SourceStatus::Valid},
        {50.0, 1200, 3, SourceStatus::Valid}
    });

    SensorController controller(sensor, test_config());

    controller.run_cycle(1000);
    controller.run_cycle(1100);

    expect(controller.state() == ControllerState::Safe,
           "controller enters safe before blocked normal cycle");

    expect(sensor.remaining() == 1,
           "recovery measurement remains available before blocked cycle");

    const ControllerCycleResult blocked = controller.run_cycle(1150);

    expect(
        blocked.state == ControllerState::Safe &&
        !blocked.measurement_available &&
        !blocked.measurement_accepted,
        "normal cycle is blocked while the controller is safe"
    );

    expect(sensor.remaining() == 1,
           "blocked safe-state cycle does not consume sensor data");

    expect(controller.request_recovery(1200),
           "explicit recovery consumes the preserved recovery measurement");
}

void test_recovery_respects_rate_limit() {
    SimulatedSensor sensor({
        {40.0, 1000, 1, SourceStatus::Valid},
        {80.0, 1100, 2, SourceStatus::Valid},
        {90.0, 1200, 3, SourceStatus::Valid}
    });

    SensorController controller(sensor, test_config());

    controller.run_cycle(1000);
    controller.run_cycle(1100);

    expect(controller.state() == ControllerState::Safe,
           "controller is safe before invalid recovery");

    expect(!controller.request_recovery(1200),
           "recovery rejects excessive change from the last accepted value");

    expect(controller.state() == ControllerState::Safe,
           "failed recovery leaves the controller in the safe state");

    expect(controller.fault_manager().has_active_critical_fault(),
           "failed recovery preserves the active critical fault");
}

void test_watchdog_fault() {
    SimulatedSensor sensor({
        {30.0, 1000, 1, SourceStatus::Valid}
    });

    SensorController controller(sensor, test_config());
    controller.run_cycle(1000);

    const ControllerCycleResult result = controller.run_cycle(1601);

    expect(result.fault_type == FaultType::Watchdog,
           "controller records a watchdog fault after a missing update");
    expect(controller.state() == ControllerState::Safe,
           "watchdog expiration places the controller in the safe state");
}

}

int main() {
    test_simulated_sensor();
    test_measurement_validator();
    test_validation_boundaries();
    test_controller_fault_and_recovery();
    test_safe_state_blocks_normal_cycles();
    test_recovery_respects_rate_limit();
    test_watchdog_fault();

    if (failures == 0) {
        std::cout << "\nAll controller tests passed.\n";
        return 0;
    }

    std::cout << "\n" << failures << " test checks failed.\n";
    return 1;
}
