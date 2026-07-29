#include "fault_manager.hpp"

#include <algorithm>

void FaultManager::record_fault(const FaultRecord& fault) {
    faults_.push_back(fault);
}

bool FaultManager::has_active_faults() const {
    return std::any_of(
        faults_.begin(),
        faults_.end(),
        [](const FaultRecord& fault) {
            return fault.active;
        }
    );
}

bool FaultManager::has_active_critical_fault() const {
    return std::any_of(
        faults_.begin(),
        faults_.end(),
        [](const FaultRecord& fault) {
            return fault.active && fault.critical;
        }
    );
}

std::size_t FaultManager::active_fault_count() const {
    return static_cast<std::size_t>(std::count_if(
        faults_.begin(),
        faults_.end(),
        [](const FaultRecord& fault) {
            return fault.active;
        }
    ));
}

const std::vector<FaultRecord>& FaultManager::faults() const {
    return faults_;
}

bool FaultManager::clear_faults(bool recovery_allowed) {
    if (!recovery_allowed) {
        return false;
    }

    for (FaultRecord& fault : faults_) {
        fault.active = false;
    }

    return true;
}
