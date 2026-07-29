#ifndef SENSOR_CONTROLLER_HPP
#define SENSOR_CONTROLLER_HPP

#include "controller_types.hpp"
#include "fault_manager.hpp"
#include "measurement_validator.hpp"
#include "sensor_interface.hpp"
#include "watchdog.hpp"

#include <cstdint>

class SensorController {
public:
    SensorController(
        SensorInterface& sensor,
        ControllerConfig config
    );

    ControllerCycleResult run_cycle(std::uint64_t current_time_ms);
    bool request_recovery(std::uint64_t current_time_ms);

    ControllerState state() const;
    const FaultManager& fault_manager() const;

private:
    void record_fault(
        FaultType fault_type,
        std::uint64_t detection_time_ms,
        const std::string& message,
        bool critical,
        const std::optional<std::uint32_t>& sequence_number
    );

    SensorInterface& sensor_;
    MeasurementValidator validator_;
    FaultManager fault_manager_;
    Watchdog watchdog_;
    ControllerState state_{ControllerState::Initializing};
};

#endif
