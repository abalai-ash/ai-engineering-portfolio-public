#ifndef MEASUREMENT_VALIDATOR_HPP
#define MEASUREMENT_VALIDATOR_HPP

#include "controller_types.hpp"

#include <cstdint>
#include <optional>

class MeasurementValidator {
public:
    explicit MeasurementValidator(ControllerConfig config);

    ValidationResult validate(
        const SensorMeasurement& measurement,
        std::uint64_t current_time_ms
    ) const;

    void record_accepted(const SensorMeasurement& measurement);
    void reset_history();

private:
    ControllerConfig config_;
    std::optional<double> previous_value_;
};

#endif
