from pathlib import Path
import json


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"


def write_json(filename: str, contents: object) -> None:
    path = DATA_DIR / filename
    path.write_text(
        json.dumps(contents, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {path.relative_to(ROOT)}")


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    stakeholder_needs = [
        {
            "id": "NEED-001",
            "text": (
                "Observers need timely instrument-health information "
                "during data collection."
            ),
            "source": "observation operations",
            "priority": "high",
        },
        {
            "id": "NEED-002",
            "text": (
                "Invalid detector measurements must be identified "
                "before they affect recorded data."
            ),
            "source": "data quality",
            "priority": "high",
        },
        {
            "id": "NEED-003",
            "text": (
                "Observation and diagnostic records must support "
                "later technical review."
            ),
            "source": "instrument engineering",
            "priority": "medium",
        },
    ]

    requirements = [
        {
            "id": "SYS-001",
            "level": "system",
            "parent": "NEED-001",
            "text": (
                "The system shall publish an instrument-health state "
                "at least once every 5 seconds."
            ),
            "component": "health_processor",
            "verification_method": "test",
            "status": "approved",
        },
        {
            "id": "SYS-002",
            "level": "system",
            "parent": "NEED-002",
            "text": (
                "The system shall flag detector measurements outside "
                "configured operating limits."
            ),
            "component": "measurement_validator",
            "verification_method": "test",
            "status": "approved",
        },
        {
            "id": "SYS-003",
            "level": "system",
            "parent": "NEED-003",
            "text": (
                "The system shall retain observation and diagnostic "
                "records for at least 30 days."
            ),
            "component": "record_store",
            "verification_method": "inspection",
            "status": "approved",
        },
        {
            "id": "SUB-001",
            "level": "subsystem",
            "parent": "SYS-001",
            "text": (
                "The health processor shall calculate each health "
                "state within 4 seconds."
            ),
            "component": "health_processor",
            "verification_method": "test",
            "status": "approved",
        },
        {
            "id": "SUB-002",
            "level": "subsystem",
            "parent": "SYS-002",
            "text": (
                "The measurement validator shall reject nonnumeric "
                "detector measurements before processing."
            ),
            "component": "measurement_validator",
            "verification_method": "test",
            "status": "approved",
        },
        {
            "id": "SUB-003",
            "level": "subsystem",
            "parent": "SYS-003",
            "text": (
                "The record store shall preserve timestamps, "
                "observation identifiers, health states, and "
                "diagnostic flags."
            ),
            "component": "record_store",
            "verification_method": "inspection",
            "status": "approved",
        },
    ]

    architecture = {
        "system": "observatory_instrument_monitor",
        "components": [
            {
                "id": "measurement_adapter",
                "responsibility": (
                    "Accept synthetic detector and environmental "
                    "measurements"
                ),
            },
            {
                "id": "measurement_validator",
                "responsibility": (
                    "Check measurement type, range, and completeness"
                ),
            },
            {
                "id": "health_processor",
                "responsibility": (
                    "Calculate instrument-health states"
                ),
            },
            {
                "id": "record_store",
                "responsibility": (
                    "Retain observation and diagnostic records"
                ),
            },
        ],
    }

    interfaces = [
        {
            "id": "IF-001",
            "source": "measurement_adapter",
            "target": "measurement_validator",
            "data": "raw_measurement",
            "required_fields": [
                "timestamp",
                "observation_id",
                "channel",
                "value",
            ],
        },
        {
            "id": "IF-002",
            "source": "measurement_validator",
            "target": "health_processor",
            "data": "validated_measurement",
            "required_fields": [
                "timestamp",
                "observation_id",
                "channel",
                "value",
                "range_state",
            ],
        },
        {
            "id": "IF-003",
            "source": "health_processor",
            "target": "record_store",
            "data": "instrument_health_record",
            "required_fields": [
                "timestamp",
                "observation_id",
                "health_state",
                "diagnostic_flags",
            ],
        },
    ]

    verification_cases = [
        {
            "id": "TEST-001",
            "requirement_ids": ["SYS-001", "SUB-001"],
            "method": "test",
            "description": (
                "Measure processing and reporting time for a sequence "
                "of valid measurements."
            ),
            "success_criteria": (
                "Every health calculation completes within 4 seconds "
                "and a state is published within 5 seconds."
            ),
        },
        {
            "id": "TEST-002",
            "requirement_ids": ["SYS-002"],
            "method": "test",
            "description": (
                "Submit measurements below, within, and above "
                "configured operating limits."
            ),
            "success_criteria": (
                "Every out-of-range measurement is flagged and every "
                "in-range measurement remains unflagged."
            ),
        },
        {
            "id": "TEST-003",
            "requirement_ids": ["SUB-002"],
            "method": "test",
            "description": (
                "Submit missing and nonnumeric detector measurements."
            ),
            "success_criteria": (
                "Invalid measurements are rejected before "
                "health-state calculation."
            ),
        },
        {
            "id": "INSP-001",
            "requirement_ids": ["SYS-003", "SUB-003"],
            "method": "inspection",
            "description": (
                "Inspect stored records and retention configuration."
            ),
            "success_criteria": (
                "Required fields are present and the configured "
                "retention period is at least 30 days."
            ),
        },
    ]

    verification_results = [
        {
            "case_id": "TEST-001",
            "status": "pass",
            "evidence": (
                "Maximum observed processing time was 3.4 seconds."
            ),
        },
        {
            "case_id": "TEST-002",
            "status": "pass",
            "evidence": (
                "All boundary and out-of-range samples produced "
                "the expected state."
            ),
        },
        {
            "case_id": "TEST-003",
            "status": "review",
            "evidence": (
                "Invalid values were rejected, but one diagnostic "
                "message omitted the detector channel."
            ),
        },
        {
            "case_id": "INSP-001",
            "status": "pass",
            "evidence": (
                "Required record fields and 30-day retention "
                "configuration were present."
            ),
        },
    ]

    previous_baseline = [
        {
            "id": "SYS-001",
            "text": (
                "The system shall publish an instrument-health state "
                "at least once every 8 seconds."
            ),
            "status": "approved",
        },
        {
            "id": "SYS-002",
            "text": (
                "The system shall flag detector measurements outside "
                "configured operating limits."
            ),
            "status": "approved",
        },
        {
            "id": "SYS-003",
            "text": (
                "The system shall retain observation and diagnostic "
                "records for at least 30 days."
            ),
            "status": "approved",
        },
    ]

    change_requests = [
        {
            "id": "CR-001",
            "title": "Shorter health-reporting interval",
            "description": (
                "Reduce the maximum reporting interval from "
                "5 seconds to 3 seconds."
            ),
            "changed_requirements": ["SYS-001"],
            "reason": (
                "Support faster recognition of changing "
                "instrument conditions."
            ),
        },
    ]

    records = {
        "stakeholder_needs.json": stakeholder_needs,
        "requirements.json": requirements,
        "architecture.json": architecture,
        "interfaces.json": interfaces,
        "verification_cases.json": verification_cases,
        "verification_results.json": verification_results,
        "baseline_previous.json": previous_baseline,
        "change_requests.json": change_requests,
    }

    for filename, contents in records.items():
        write_json(filename, contents)


if __name__ == "__main__":
    main()
