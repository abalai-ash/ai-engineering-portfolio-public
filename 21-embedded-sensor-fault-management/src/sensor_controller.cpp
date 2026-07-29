#include "sensor_controller.hpp"

#include <optional>
#include <utility>

SensorController::SensorController(
    SensorInterface& sensor,
    ControllerConfig config
) :
    sensor_(sensor),
    validator_(config),
    watchdog_(config.watchdog_limit_ms) {}

ControllerCycleResult SensorController::run_cycle(
    std::uint64_t current_time_ms
) {
    if (state_ == ControllerState::Safe) {
        return {
            state_,
            false,
            false,
            FaultType::None,
            "controller is latched in the safe state",
            fault_manager_.active_fault_count()
        };
    }

    const std::optional<SensorMeasurement> measurement =
        sensor_.next_measurement();

    if (!measurement.has_value()) {
        if (watchdog_.expired(current_time_ms)) {
            record_fault(
                FaultType::Watchdog,
                current_time_ms,
                "watchdog limit exceeded without an accepted update",
                true,
                std::nullopt
            );
            state_ = ControllerState::Safe;

            return {
                state_,
                false,
                false,
                FaultType::Watchdog,
                "watchdog fault recorded",
                fault_manager_.active_fault_count()
            };
        }

        return {
            state_,
            false,
            false,
            FaultType::None,
            "no measurement available",
            fault_manager_.active_fault_count()
        };
    }

    const ValidationResult validation =
        validator_.validate(measurement.value(), current_time_ms);

    if (!validation.accepted) {
        record_fault(
            validation.fault_type,
            current_time_ms,
            validation.message,
            true,
            measurement->sequence_number
        );
        state_ = ControllerState::Safe;

        return {
            state_,
            true,
            false,
            validation.fault_type,
            validation.message,
            fault_manager_.active_fault_count()
        };
    }

    validator_.record_accepted(measurement.value());
    watchdog_.record_update(current_time_ms);

    if (state_ == ControllerState::Initializing) {
        state_ = ControllerState::Monitoring;
    }

    return {
        state_,
        true,
        true,
        FaultType::None,
        "measurement accepted",
        fault_manager_.active_fault_count()
    };
}

bool SensorController::request_recovery(
    std::uint64_t current_time_ms
) {
    if (state_ != ControllerState::Safe) {
        return false;
    }

    const std::optional<SensorMeasurement> measurement =
        sensor_.next_measurement();

    if (!measurement.has_value()) {
        return false;
    }

    const ValidationResult validation =
        validator_.validate(measurement.value(), current_time_ms);

    if (!validation.accepted) {
        return false;
    }

    if (!fault_manager_.clear_faults(true)) {
        return false;
    }

    validator_.record_accepted(measurement.value());
    watchdog_.record_update(current_time_ms);
    state_ = ControllerState::Monitoring;
    return true;
}

ControllerState SensorController::state() const {
    return state_;
}

const FaultManager& SensorController::fault_manager() const {
    return fault_manager_;
}

void SensorController::record_fault(
    FaultType fault_type,
    std::uint64_t detection_time_ms,
    const std::string& message,
    bool critical,
    const std::optional<std::uint32_t>& sequence_number
) {
    fault_manager_.record_fault({
        fault_type,
        detection_time_ms,
        sequence_number,
        message,
        critical,
        true
    });
}
