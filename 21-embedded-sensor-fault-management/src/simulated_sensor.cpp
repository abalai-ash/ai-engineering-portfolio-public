#include "simulated_sensor.hpp"

#include <utility>

SimulatedSensor::SimulatedSensor(
    std::vector<SensorMeasurement> measurements
) : measurements_(std::move(measurements)) {}

std::optional<SensorMeasurement> SimulatedSensor::next_measurement() {
    if (next_index_ >= measurements_.size()) {
        return std::nullopt;
    }

    return measurements_.at(next_index_++);
}

void SimulatedSensor::reset() {
    next_index_ = 0;
}

std::size_t SimulatedSensor::remaining() const {
    return measurements_.size() - next_index_;
}
