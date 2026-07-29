#ifndef SENSOR_INTERFACE_HPP
#define SENSOR_INTERFACE_HPP

#include "controller_types.hpp"

#include <optional>

class SensorInterface {
public:
    virtual ~SensorInterface() = default;

    virtual std::optional<SensorMeasurement> next_measurement() = 0;
};

#endif
