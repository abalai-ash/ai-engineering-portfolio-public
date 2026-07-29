from __future__ import annotations

from typing import Any


Record = dict[str, Any]
SUPPORTED_METHODS = {
    "analysis",
    "demonstration",
    "inspection",
    "test",
}
SUPPORTED_OPERATORS = {"<=", ">=", "==", "<", ">"}


def index_by_id(
    records: list[Record],
    field: str = "id",
) -> dict[str, Record]:
    return {
        str(record[field]): record
        for record in records
    }


def find_unplanned_requirements(
    requirements: list[Record],
    plans: list[Record],
) -> list[str]:
    planned_ids = {
        str(requirement_id)
        for plan in plans
        for requirement_id in plan.get(
            "requirement_ids",
            [],
        )
    }

    return sorted(
        str(requirement["id"])
        for requirement in requirements
        if str(requirement["id"]) not in planned_ids
    )


def review_plan(
    plan: Record,
) -> list[str]:
    findings: list[str] = []

    if not plan.get("requirement_ids"):
        findings.append(
            "No requirement is linked."
        )

    if plan.get("method") not in SUPPORTED_METHODS:
        findings.append(
            "Verification method is missing or unsupported."
        )

    if not plan.get("objective"):
        findings.append(
            "Verification objective is missing."
        )

    if not plan.get("entry_conditions"):
        findings.append(
            "Entry conditions are missing."
        )

    criteria = plan.get("acceptance_criteria", {})

    if not criteria.get("metric"):
        findings.append(
            "Acceptance metric is missing."
        )

    if criteria.get("operator") not in SUPPORTED_OPERATORS:
        findings.append(
            "Acceptance operator is missing or unsupported."
        )

    if "threshold" not in criteria:
        findings.append(
            "Acceptance threshold is missing."
        )

    if not plan.get("required_evidence_fields"):
        findings.append(
            "Required evidence fields are missing."
        )

    return findings


def review_plans(
    plans: list[Record],
) -> dict[str, list[str]]:
    findings: dict[str, list[str]] = {}

    for plan in plans:
        plan_findings = review_plan(plan)

        if plan_findings:
            findings[str(plan["id"])] = plan_findings

    return findings


def evaluate_readiness(
    plans: list[Record],
    readiness_records: list[Record],
) -> dict[str, str]:
    readiness_index = {
        str(record["plan_id"]): record
        for record in readiness_records
    }

    outcomes: dict[str, str] = {}

    for plan in plans:
        plan_id = str(plan["id"])
        record = readiness_index.get(plan_id)

        if record is None:
            outcomes[plan_id] = "not_recorded"
            continue

        required_conditions = set(
            str(condition)
            for condition in plan.get(
                "entry_conditions",
                [],
            )
        )
        condition_results = record.get(
            "condition_results",
            {},
        )

        missing = required_conditions - set(
            condition_results
        )

        if missing:
            outcomes[plan_id] = "incomplete"
        elif all(
            bool(condition_results[condition])
            for condition in required_conditions
        ):
            outcomes[plan_id] = "ready"
        else:
            outcomes[plan_id] = "not_ready"

    return outcomes


def review_evidence(
    plans: list[Record],
    evidence_records: list[Record],
) -> dict[str, list[str]]:
    plan_index = index_by_id(plans)
    findings: dict[str, list[str]] = {}

    for evidence in evidence_records:
        evidence_id = str(evidence["id"])
        plan_id = str(evidence.get("plan_id", ""))
        issues: list[str] = []

        plan = plan_index.get(plan_id)

        if plan is None:
            issues.append(
                "Evidence references an unknown plan."
            )
        else:
            for field in plan.get(
                "required_evidence_fields",
                [],
            ):
                if field not in evidence:
                    issues.append(
                        f"Required field is missing: {field}."
                    )

        if not evidence.get("recorded_at"):
            issues.append(
                "Evidence timestamp is missing."
            )

        if issues:
            findings[evidence_id] = issues

    return findings


def compare_value(
    value: float,
    operator: str,
    threshold: float,
) -> bool:
    if operator == "<=":
        return value <= threshold
    if operator == ">=":
        return value >= threshold
    if operator == "==":
        return value == threshold
    if operator == "<":
        return value < threshold
    if operator == ">":
        return value > threshold

    raise ValueError(
        f"Unsupported operator: {operator}"
    )


def evaluate_plan_outcomes(
    plans: list[Record],
    readiness_outcomes: dict[str, str],
    evidence_records: list[Record],
    evidence_findings: dict[str, list[str]],
) -> dict[str, str]:
    evidence_by_plan: dict[str, list[Record]] = {}

    for evidence in evidence_records:
        evidence_by_plan.setdefault(
            str(evidence["plan_id"]),
            [],
        ).append(evidence)

    outcomes: dict[str, str] = {}

    for plan in plans:
        plan_id = str(plan["id"])

        if readiness_outcomes.get(plan_id) != "ready":
            outcomes[plan_id] = "blocked"
            continue

        plan_evidence = evidence_by_plan.get(
            plan_id,
            [],
        )

        if not plan_evidence:
            outcomes[plan_id] = "not_run"
            continue

        if any(
            str(record["id"]) in evidence_findings
            for record in plan_evidence
        ):
            outcomes[plan_id] = "review"
            continue

        criteria = plan["acceptance_criteria"]
        latest = plan_evidence[-1]

        value = float(latest["metric_value"])
        threshold = float(criteria["threshold"])

        outcomes[plan_id] = (
            "pass"
            if compare_value(
                value,
                str(criteria["operator"]),
                threshold,
            )
            else "fail"
        )

    return outcomes


def requirement_outcomes(
    requirements: list[Record],
    plans: list[Record],
    plan_outcomes: dict[str, str],
) -> dict[str, str]:
    priority = {
        "pass": 0,
        "not_run": 1,
        "review": 2,
        "blocked": 3,
        "fail": 4,
    }

    outcomes = {
        str(requirement["id"]): "not_run"
        for requirement in requirements
    }

    for plan in plans:
        status = plan_outcomes[str(plan["id"])]

        for requirement_id in plan.get(
            "requirement_ids",
            [],
        ):
            requirement_id = str(requirement_id)
            current = outcomes.get(
                requirement_id,
                "not_run",
            )

            if priority[status] > priority[current]:
                outcomes[requirement_id] = status
            elif current == "not_run" and status == "pass":
                outcomes[requirement_id] = "pass"

    return outcomes
