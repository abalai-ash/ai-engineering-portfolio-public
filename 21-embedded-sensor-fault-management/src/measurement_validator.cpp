#include "measurement_validator.hpp"

#include <cmath>
#include <stdexcept>
#include <utility>

MeasurementValidator::MeasurementValidator(ControllerConfig config)
    : config_(std::move(config)) {
    if (config_.minimum_value > config_.maximum_value) {
        throw std::invalid_argument("minimum_value exceeds maximum_value");
    }

    if (config_.maximum_change < 0.0) {
        throw std::invalid_argument("maximum_change must be nonnegative");
    }
}

ValidationResult MeasurementValidator::validate(
    const SensorMeasurement& measurement,
    std::uint64_t current_time_ms
) const {
    if (measurement.source_status != SourceStatus::Valid) {
        return {
            false,
            FaultType::InvalidSource,
            "sensor source status is not valid"
        };
    }

    if (!std::isfinite(measurement.value)) {
        return {
            false,
            FaultType::Range,
            "measurement value is not finite"
        };
    }

    if (
        measurement.value < config_.minimum_value ||
        measurement.value > config_.maximum_value
    ) {
        return {
            false,
            FaultType::Range,
            "measurement is outside the configured range"
        };
    }

    if (current_time_ms < measurement.timestamp_ms) {
        return {
            false,
            FaultType::StaleData,
            "measurement timestamp is later than controller time"
        };
    }

    if (
        current_time_ms - measurement.timestamp_ms >
        config_.stale_limit_ms
    ) {
        return {
            false,
            FaultType::StaleData,
            "measurement exceeds the stale-data limit"
        };
    }

    if (
        previous_value_.has_value() &&
        std::abs(measurement.value - previous_value_.value()) >
        config_.maximum_change
    ) {
        return {
            false,
            FaultType::RateOfChange,
            "measurement change exceeds the configured limit"
        };
    }

    return {true, FaultType::None, "measurement accepted"};
}

void MeasurementValidator::record_accepted(
    const SensorMeasurement& measurement
) {
    previous_value_ = measurement.value;
}

void MeasurementValidator::reset_history() {
    previous_value_.reset();
}
