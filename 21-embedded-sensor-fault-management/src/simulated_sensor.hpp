#ifndef SIMULATED_SENSOR_HPP
#define SIMULATED_SENSOR_HPP

#include "sensor_interface.hpp"

#include <cstddef>
#include <optional>
#include <vector>

class SimulatedSensor : public SensorInterface {
public:
    explicit SimulatedSensor(std::vector<SensorMeasurement> measurements);

    std::optional<SensorMeasurement> next_measurement() override;
    void reset();
    std::size_t remaining() const;

private:
    std::vector<SensorMeasurement> measurements_;
    std::size_t next_index_{0};
};

#endif
