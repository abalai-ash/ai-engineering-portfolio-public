#include <cmath>
#include <iostream>
#include <string>

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
            return false;
        }

        if (measurement.value < minimum_ || measurement.value > maximum_) {
            state_ = ControllerState::Safe;
            return false;
        }

        if (
            has_previous_ &&
            std::abs(measurement.value - previous_value_) > maximum_change_
        ) {
            state_ = ControllerState::Safe;
            return false;
        }

        previous_value_ = measurement.value;
        has_previous_ = true;
        return true;
    }

    bool recover(const Measurement& measurement) {
        if (
            state_ != ControllerState::Safe ||
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
        return true;
    }

    ControllerState state() const {
        return state_;
    }

private:
    double minimum_;
    double maximum_;
    double maximum_change_;
    double previous_value_{0.0};
    bool has_previous_{false};
    ControllerState state_{ControllerState::Monitoring};
};

int failures = 0;

void expect(bool condition, const std::string& name) {
    if (condition) {
        std::cout << "PASS: " << name << "\n";
    } else {
        std::cout << "FAIL: " << name << "\n";
        ++failures;
    }
}

int main() {
    SensorFaultDemo controller(0.0, 100.0, 15.0);

    expect(controller.process({30.0, true}), "accept nominal value");
    expect(controller.process({40.0, true}), "accept allowed change");
    expect(!controller.process({70.0, true}), "reject excessive change");
    expect(
        controller.state() == ControllerState::Safe,
        "enter safe state after fault"
    );
    expect(!controller.process({42.0, true}), "block normal processing in safe state");
    expect(controller.recover({42.0, true}), "accept explicit valid recovery");
    expect(
        controller.state() == ControllerState::Monitoring,
        "return to monitoring after recovery"
    );

    return failures == 0 ? 0 : 1;
}
