#include <cmath>
#include <iostream>
#include <string>
#include <vector>

struct Measurement {
    double value;
    bool available;
};

enum class ControllerState {
    Monitoring,
    Safe
};

class SensorFaultDemo {
public:
    SensorFaultDemo(double minimum, double maximum, double maximum_change)
        : minimum_(minimum),
          maximum_(maximum),
          maximum_change_(maximum_change) {}

    bool process(const Measurement& measurement) {
        if (state_ == ControllerState::Safe) {
            return false;
        }

        if (!measurement.available || !std::isfinite(measurement.value)) {
            state_ = ControllerState::Safe;
            message_ = "invalid or missing measurement";
            return false;
        }

        if (measurement.value < minimum_ || measurement.value > maximum_) {
            state_ = ControllerState::Safe;
            message_ = "measurement outside allowed range";
            return false;
        }

        if (
            has_previous_ &&
            std::abs(measurement.value - previous_value_) > maximum_change_
        ) {
            state_ = ControllerState::Safe;
            message_ = "measurement changed too quickly";
            return false;
        }

        previous_value_ = measurement.value;
        has_previous_ = true;
        message_ = "measurement accepted";
        return true;
    }

    bool recover(const Measurement& measurement) {
        if (state_ != ControllerState::Safe) {
            return false;
        }

        if (
            !measurement.available ||
            !std::isfinite(measurement.value) ||
            measurement.value < minimum_ ||
            measurement.value > maximum_
        ) {
            return false;
        }

        state_ = ControllerState::Monitoring;
        previous_value_ = measurement.value;
        has_previous_ = true;
        message_ = "recovery accepted";
        return true;
    }

    ControllerState state() const {
        return state_;
    }

    const std::string& message() const {
        return message_;
    }

private:
    double minimum_;
    double maximum_;
    double maximum_change_;
    double previous_value_{0.0};
    bool has_previous_{false};
    ControllerState state_{ControllerState::Monitoring};
    std::string message_{"ready"};
};

int main() {
    SensorFaultDemo controller(0.0, 100.0, 15.0);

    const std::vector<Measurement> sequence = {
        {30.0, true},
        {35.0, true},
        {70.0, true}
    };

    for (const Measurement& measurement : sequence) {
        controller.process(measurement);
        std::cout << controller.message() << "\n";
    }

    const bool recovered = controller.recover({40.0, true});
    std::cout << (recovered ? "recovered" : "recovery rejected") << "\n";

    return recovered ? 0 : 1;
}
