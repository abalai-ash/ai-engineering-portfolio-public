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

    requirements = [
        {
            "id": "REQ-001",
            "text": (
                "The monitoring workflow shall calculate measurement-model "
                "difference within 0.8 percent."
            ),
            "verification_method": "analysis",
        },
        {
            "id": "REQ-002",
            "text": (
                "The monitoring record set shall contain "
                "no missing measurement identifiers."
            ),
            "verification_method": "test",
        },
        {
            "id": "REQ-003",
            "text": (
                "The validation record shall preserve the source "
                "version, timestamp, and review configuration."
            ),
            "verification_method": "inspection",
        },
        {
            "id": "REQ-004",
            "text": (
                "The review-readiness display shall identify "
                "whether monitoring evidence is current."
            ),
            "verification_method": "demonstration",
        },
        {
            "id": "REQ-005",
            "text": (
                "The workflow shall prevent closure while a critical "
                "monitoring anomaly remains unresolved."
            ),
            "verification_method": "test",
        },
    ]

    verification_plans = [
        {
            "id": "VP-001",
            "requirement_ids": ["REQ-001"],
            "objective": "Assess measurement-model agreement.",
            "method": "analysis",
            "entry_conditions": [
                "monitoring dataset available",
                "review configuration recorded",
                "analysis script version recorded",
            ],
            "acceptance_criteria": {
                "metric": "maximum_measurement_model_difference_percent",
                "operator": "<=",
                "threshold": 0.8,
            },
            "required_evidence_fields": [
                "dataset_id",
                "script_version",
                "metric_value",
                "reviewer",
            ],
        },
        {
            "id": "VP-002",
            "requirement_ids": ["REQ-002"],
            "objective": "Verify monitoring-record completeness.",
            "method": "test",
            "entry_conditions": [
                "monitoring records available",
                "review configuration approved",
            ],
            "acceptance_criteria": {
                "metric": "missing_measurement_id_count",
                "operator": "==",
                "threshold": 0,
            },
            "required_evidence_fields": [
                "run_id",
                "configuration_id",
                "metric_value",
                "reviewer",
            ],
        },
        {
            "id": "VP-003",
            "requirement_ids": ["REQ-003"],
            "objective": "Inspect validation-record contents.",
            "method": "inspection",
            "entry_conditions": [
                "validation record generated",
            ],
            "acceptance_criteria": {
                "metric": "required_field_count",
                "operator": ">=",
                "threshold": 3,
            },
            "required_evidence_fields": [
                "record_id",
                "inspected_fields",
                "metric_value",
                "reviewer",
            ],
        },
        {
            "id": "VP-004",
            "requirement_ids": ["REQ-004"],
            "objective": "Demonstrate readiness-state reporting.",
            "method": "demonstration",
            "entry_conditions": [
                "current monitoring evidence available",
                "expired monitoring evidence available",
            ],
            "acceptance_criteria": {
                "metric": "correct_state_count",
                "operator": "==",
                "threshold": 2,
            },
            "required_evidence_fields": [
                "demonstration_id",
                "observed_states",
                "metric_value",
                "reviewer",
            ],
        },
        {
            "id": "VP-005",
            "requirement_ids": ["REQ-005"],
            "objective": "Verify anomaly-based closure blocking.",
            "method": "test",
            "entry_conditions": [
                "critical anomaly record available",
                "closure workflow available",
            ],
            "acceptance_criteria": {
                "metric": "blocked_closure_attempts",
                "operator": "==",
                "threshold": 1,
            },
            "required_evidence_fields": [
                "run_id",
                "anomaly_id",
                "metric_value",
                "reviewer",
            ],
        },
    ]

    readiness_records = [
        {
            "plan_id": "VP-001",
            "condition_results": {
                "monitoring dataset available": True,
                "review configuration recorded": True,
                "analysis script version recorded": True,
            },
        },
        {
            "plan_id": "VP-002",
            "condition_results": {
                "monitoring records available": True,
                "review configuration approved": True,
            },
        },
        {
            "plan_id": "VP-003",
            "condition_results": {
                "validation record generated": True,
            },
        },
        {
            "plan_id": "VP-004",
            "condition_results": {
                "current monitoring evidence available": True,
                "expired monitoring evidence available": True,
            },
        },
        {
            "plan_id": "VP-005",
            "condition_results": {
                "critical anomaly record available": True,
                "closure workflow available": True,
            },
        },
    ]

    evidence_records = [
        {
            "id": "EV-001",
            "plan_id": "VP-001",
            "dataset_id": "SYN-MON-014",
            "script_version": "2.1",
            "metric_value": 0.62,
            "reviewer": "technical review",
            "recorded_at": "2026-07-18T14:00:00Z",
        },
        {
            "id": "EV-002",
            "plan_id": "VP-002",
            "run_id": "SYN-REC-008",
            "configuration_id": "CFG-REV-03",
            "metric_value": 0,
            "reviewer": "test review",
            "recorded_at": "2026-07-18T15:00:00Z",
        },
        {
            "id": "EV-003",
            "plan_id": "VP-003",
            "record_id": "VAL-REC-021",
            "inspected_fields": [
                "source_version",
                "timestamp",
                "review_configuration",
            ],
            "metric_value": 3,
            "reviewer": "record review",
            "recorded_at": "2026-07-18T16:00:00Z",
        },
        {
            "id": "EV-004",
            "plan_id": "VP-004",
            "demonstration_id": "DEMO-006",
            "observed_states": [
                "current",
                "expired",
            ],
            "metric_value": 2,
            "reviewer": "demonstration review",
            "recorded_at": "2026-07-18T17:00:00Z",
        },
        {
            "id": "EV-005",
            "plan_id": "VP-005",
            "run_id": "SYN-CLOSE-004",
            "anomaly_id": "ANOM-001",
            "metric_value": 1,
            "reviewer": "test review",
            "recorded_at": "2026-07-19T11:00:00Z",
        },
    ]

    anomalies = [
        {
            "id": "ANOM-001",
            "plan_id": "VP-005",
            "severity": "critical",
            "status": "resolved",
            "description": (
                "An early workflow revision allowed a closure request "
                "to proceed before anomaly review completed."
            ),
            "corrective_action_id": "CA-001",
        },
        {
            "id": "ANOM-002",
            "plan_id": "VP-002",
            "severity": "minor",
            "status": "open",
            "description": (
                "One diagnostic message used an abbreviated review "
                "configuration label."
            ),
            "corrective_action_id": "CA-002",
        },
    ]

    corrective_actions = [
        {
            "id": "CA-001",
            "anomaly_id": "ANOM-001",
            "action": (
                "Require anomaly-state validation before closure."
            ),
            "status": "completed",
            "retest_id": "RT-001",
        },
        {
            "id": "CA-002",
            "anomaly_id": "ANOM-002",
            "action": (
                "Replace the abbreviated configuration label."
            ),
            "status": "planned",
            "retest_id": None,
        },
    ]

    retests = [
        {
            "id": "RT-001",
            "anomaly_id": "ANOM-001",
            "plan_id": "VP-005",
            "status": "pass",
            "evidence_id": "EV-005",
            "notes": (
                "Closure remained blocked until the critical anomaly "
                "was marked resolved."
            ),
        }
    ]

    closure_records = [
        {
            "requirement_id": "REQ-001",
            "requested_status": "closed",
        },
        {
            "requirement_id": "REQ-002",
            "requested_status": "closed",
        },
        {
            "requirement_id": "REQ-003",
            "requested_status": "closed",
        },
        {
            "requirement_id": "REQ-004",
            "requested_status": "closed",
        },
        {
            "requirement_id": "REQ-005",
            "requested_status": "closed",
        },
    ]

    records = {
        "requirements.json": requirements,
        "verification_plans.json": verification_plans,
        "readiness_records.json": readiness_records,
        "evidence_records.json": evidence_records,
        "anomalies.json": anomalies,
        "corrective_actions.json": corrective_actions,
        "retests.json": retests,
        "closure_records.json": closure_records,
    }

    for filename, contents in records.items():
        write_json(filename, contents)


if __name__ == "__main__":
    main()
