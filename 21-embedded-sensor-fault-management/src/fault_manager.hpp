#ifndef FAULT_MANAGER_HPP
#define FAULT_MANAGER_HPP

#include "controller_types.hpp"

#include <cstddef>
#include <vector>

class FaultManager {
public:
    void record_fault(const FaultRecord& fault);
    bool has_active_faults() const;
    bool has_active_critical_fault() const;
    std::size_t active_fault_count() const;
    const std::vector<FaultRecord>& faults() const;
    bool clear_faults(bool recovery_allowed);

private:
    std::vector<FaultRecord> faults_;
};

#endif
