"""Run the synthetic monitoring evaluation."""

from __future__ import annotations

import json
import sys
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_DIR / "src"

sys.path.insert(0, str(SRC_DIR))

from monitoring import (
    build_incident_response,
    choose_action,
    compare_metrics,
    load_metrics,
)


def main() -> None:
    baseline = load_metrics(
        PROJECT_DIR / "data" / "baseline_metrics.json"
    )

    current = load_metrics(
        PROJECT_DIR / "data" / "current_metrics.json"
    )

    alerts = compare_metrics(baseline, current)
    decision = choose_action(alerts)
    incident_response = build_incident_response(
        alerts,
        decision,
        current["model_version"],
    )

    checks = {
        "critical_incident_detected": (
            incident_response["severity"] == "critical"
        ),
        "rollback_required": incident_response["rollback_required"],
        "response_owner_assigned": bool(incident_response["owner"]),
        "recovery_checks_defined": (
            len(incident_response["recovery_checks"]) >= 3
        ),
        "closure_blocked_until_recovery": (
            incident_response["closure_status"]
            == "blocked_pending_recovery"
        ),
    }

    results = {
        "baseline_version": baseline["model_version"],
        "current_version": current["model_version"],
        "alerts": alerts,
        "decision": decision,
        "incident_response": incident_response,
        "checks": checks,
        "scope": (
            "This local example uses synthetic metrics. "
            "It demonstrates monitoring rules and incident decisions. "
            "It is not a production monitoring service."
        ),
    }

    if not all(checks.values()):
        failed = [name for name, passed in checks.items() if not passed]
        raise AssertionError(f"Failed checks: {failed}")

    output_path = PROJECT_DIR / "eval" / "evaluation_results.json"

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(results, file, indent=2)
        file.write("\n")

    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
