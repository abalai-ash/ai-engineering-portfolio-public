#ifndef CONTROLLER_TYPES_HPP
#define CONTROLLER_TYPES_HPP

#include <cstddef>
#include <cstdint>
#include <optional>
#include <string>

enum class ControllerState {
    Initializing,
    Monitoring,
    Safe
};

enum class SourceStatus {
    Valid,
    Invalid,
    Missing
};

enum class FaultType {
    None,
    Range,
    RateOfChange,
    StaleData,
    InvalidSource,
    Watchdog
};

struct SensorMeasurement {
    double value;
    std::uint64_t timestamp_ms;
    std::uint32_t sequence_number;
    SourceStatus source_status;
};

struct ControllerConfig {
    double minimum_value;
    double maximum_value;
    double maximum_change;
    std::uint64_t stale_limit_ms;
    std::uint64_t watchdog_limit_ms;
};

struct ValidationResult {
    bool accepted;
    FaultType fault_type;
    std::string message;
};

struct FaultRecord {
    FaultType fault_type;
    std::uint64_t detection_time_ms;
    std::optional<std::uint32_t> sequence_number;
    std::string message;
    bool critical;
    bool active;
};


struct ControllerCycleResult {
    ControllerState state;
    bool measurement_available;
    bool measurement_accepted;
    FaultType fault_type;
    std::string message;
    std::size_t active_fault_count;
};

#endif
