from __future__ import annotations

from typing import Any


Record = dict[str, Any]
VALID_STATUSES = {"pass", "review", "fail", "not_run"}


def evaluate_cases(
    verification_cases: list[Record],
    verification_results: list[Record],
) -> list[Record]:
    """Combine planned verification cases with recorded results."""
    result_index = {
        str(result["case_id"]): result
        for result in verification_results
    }

    evaluated: list[Record] = []

    for case in verification_cases:
        case_id = str(case["id"])
        result = result_index.get(case_id)

        if result is None:
            status = "not_run"
            evidence = "No result was recorded."
        else:
            status = str(result.get("status", "not_run"))
            evidence = str(result.get("evidence", ""))

        if status not in VALID_STATUSES:
            status = "fail"
            evidence = "Unsupported verification status was recorded."

        evaluated.append(
            {
                "case_id": case_id,
                "requirement_ids": list(
                    case.get("requirement_ids", [])
                ),
                "method": case.get("method"),
                "status": status,
                "evidence": evidence,
            }
        )

    return evaluated


def requirement_outcomes(
    requirements: list[Record],
    evaluated_cases: list[Record],
) -> dict[str, str]:
    """Roll case results up to requirement-level outcomes."""
    priority = {
        "pass": 0,
        "not_run": 1,
        "review": 2,
        "fail": 3,
    }

    outcomes = {
        str(requirement["id"]): "not_run"
        for requirement in requirements
    }

    for case in evaluated_cases:
        case_status = str(case["status"])

        for requirement_id in case["requirement_ids"]:
            requirement_id = str(requirement_id)
            current = outcomes.get(
                requirement_id,
                "not_run",
            )

            if priority[case_status] > priority[current]:
                outcomes[requirement_id] = case_status
            elif current == "not_run" and case_status == "pass":
                outcomes[requirement_id] = "pass"

    return outcomes
