#include "sensor_controller.hpp"
#include "simulated_sensor.hpp"

#include <cstdint>
#include <iostream>
#include <string>
#include <vector>

std::string state_name(ControllerState state) {
    switch (state) {
        case ControllerState::Initializing:
            return "initializing";
        case ControllerState::Monitoring:
            return "monitoring";
        case ControllerState::Safe:
            return "safe";
    }

    return "unknown";
}

int main() {
    const ControllerConfig config{
        0.0,
        100.0,
        15.0,
        250,
        500
    };

    std::vector<SensorMeasurement> measurements{
        {42.0, 1000, 1, SourceStatus::Valid},
        {46.0, 1100, 2, SourceStatus::Valid},
        {85.0, 1200, 3, SourceStatus::Valid},
        {48.0, 1300, 4, SourceStatus::Valid}
    };

    SimulatedSensor sensor(measurements);
    SensorController controller(sensor, config);

    const ControllerCycleResult first = controller.run_cycle(1000);
    const ControllerCycleResult second = controller.run_cycle(1100);
    const ControllerCycleResult third = controller.run_cycle(1200);

    std::cout << "cycle 1: " << state_name(first.state)
              << ", " << first.message << "\n";
    std::cout << "cycle 2: " << state_name(second.state)
              << ", " << second.message << "\n";
    std::cout << "cycle 3: " << state_name(third.state)
              << ", " << third.message << "\n";

    const bool recovered = controller.request_recovery(1300);

    std::cout << "recovery: "
              << (recovered ? "accepted" : "rejected")
              << "\n";
    std::cout << "final state: "
              << state_name(controller.state())
              << "\n";

    return recovered ? 0 : 1;
}
