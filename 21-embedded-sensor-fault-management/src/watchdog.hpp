#ifndef WATCHDOG_HPP
#define WATCHDOG_HPP

#include <cstdint>
#include <optional>

class Watchdog {
public:
    explicit Watchdog(std::uint64_t timeout_ms);

    void record_update(std::uint64_t update_time_ms);
    bool expired(std::uint64_t current_time_ms) const;
    void reset();
    bool has_update() const;

private:
    std::uint64_t timeout_ms_;
    std::optional<std::uint64_t> last_update_ms_;
};

#endif
