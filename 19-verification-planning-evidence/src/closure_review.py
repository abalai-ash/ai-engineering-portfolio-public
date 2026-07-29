from __future__ import annotations

from typing import Any


Record = dict[str, Any]


def unresolved_anomalies(
    anomalies: list[Record],
) -> list[str]:
    return sorted(
        str(anomaly["id"])
        for anomaly in anomalies
        if anomaly.get("status") != "resolved"
    )


def unresolved_critical_anomalies(
    anomalies: list[Record],
) -> list[str]:
    return sorted(
        str(anomaly["id"])
        for anomaly in anomalies
        if (
            anomaly.get("severity") == "critical"
            and anomaly.get("status") != "resolved"
        )
    )


def review_corrective_actions(
    anomalies: list[Record],
    corrective_actions: list[Record],
    retests: list[Record],
) -> dict[str, list[str]]:
    action_index = {
        str(action["id"]): action
        for action in corrective_actions
    }
    retest_index = {
        str(retest["id"]): retest
        for retest in retests
    }

    findings: dict[str, list[str]] = {}

    for anomaly in anomalies:
        anomaly_id = str(anomaly["id"])
        issues: list[str] = []
        action_id = anomaly.get(
            "corrective_action_id"
        )

        if not action_id:
            issues.append(
                "Corrective action is not linked."
            )
        else:
            action = action_index.get(str(action_id))

            if action is None:
                issues.append(
                    "Linked corrective action does not exist."
                )
            elif anomaly.get("status") == "resolved":
                if action.get("status") != "completed":
                    issues.append(
                        "Resolved anomaly has an incomplete corrective action."
                    )

                retest_id = action.get("retest_id")

                if not retest_id:
                    issues.append(
                        "Resolved anomaly does not identify a retest."
                    )
                else:
                    retest = retest_index.get(
                        str(retest_id)
                    )

                    if retest is None:
                        issues.append(
                            "Linked retest does not exist."
                        )
                    elif retest.get("status") != "pass":
                        issues.append(
                            "Linked retest did not pass."
                        )

        if issues:
            findings[anomaly_id] = issues

    return findings


def closure_status(
    closure_records: list[Record],
    requirement_outcomes: dict[str, str],
    anomalies: list[Record],
    corrective_action_findings: dict[str, list[str]],
) -> dict[str, str]:
    critical_open = bool(
        unresolved_critical_anomalies(anomalies)
    )
    outcomes: dict[str, str] = {}

    for record in closure_records:
        requirement_id = str(
            record["requirement_id"]
        )
        verification_status = requirement_outcomes.get(
            requirement_id,
            "not_run",
        )

        if verification_status != "pass":
            outcomes[requirement_id] = (
                "blocked_by_verification"
            )
        elif critical_open:
            outcomes[requirement_id] = (
                "blocked_by_critical_anomaly"
            )
        elif corrective_action_findings:
            outcomes[requirement_id] = (
                "review_corrective_actions"
            )
        else:
            outcomes[requirement_id] = "ready_to_close"

    return outcomes
