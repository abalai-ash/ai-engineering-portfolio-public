#include "watchdog.hpp"

#include <stdexcept>

Watchdog::Watchdog(std::uint64_t timeout_ms)
    : timeout_ms_(timeout_ms) {
    if (timeout_ms_ == 0) {
        throw std::invalid_argument("watchdog timeout must be greater than zero");
    }
}

void Watchdog::record_update(std::uint64_t update_time_ms) {
    last_update_ms_ = update_time_ms;
}

bool Watchdog::expired(std::uint64_t current_time_ms) const {
    if (!last_update_ms_.has_value()) {
        return false;
    }

    if (current_time_ms < last_update_ms_.value()) {
        return false;
    }

    return current_time_ms - last_update_ms_.value() > timeout_ms_;
}

void Watchdog::reset() {
    last_update_ms_.reset();
}

bool Watchdog::has_update() const {
    return last_update_ms_.has_value();
}
