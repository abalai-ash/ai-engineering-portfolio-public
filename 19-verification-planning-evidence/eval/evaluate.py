from __future__ import annotations

import csv
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from closure_review import (
    closure_status,
    review_corrective_actions,
    unresolved_anomalies,
    unresolved_critical_anomalies,
)
from verification_review import (
    evaluate_plan_outcomes,
    evaluate_readiness,
    find_unplanned_requirements,
    requirement_outcomes,
    review_evidence,
    review_plans,
)


def load_json(filename: str):
    path = ROOT / "data" / filename
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    requirements = load_json("requirements.json")
    plans = load_json("verification_plans.json")
    readiness_records = load_json(
        "readiness_records.json"
    )
    evidence_records = load_json(
        "evidence_records.json"
    )
    anomalies = load_json("anomalies.json")
    corrective_actions = load_json(
        "corrective_actions.json"
    )
    retests = load_json("retests.json")
    closure_records = load_json(
        "closure_records.json"
    )

    reports_dir = ROOT / "reports"
    reports_dir.mkdir(exist_ok=True)

    plan_findings = review_plans(plans)
    unplanned = find_unplanned_requirements(
        requirements,
        plans,
    )
    readiness = evaluate_readiness(
        plans,
        readiness_records,
    )
    evidence_findings = review_evidence(
        plans,
        evidence_records,
    )
    plan_outcomes = evaluate_plan_outcomes(
        plans,
        readiness,
        evidence_records,
        evidence_findings,
    )
    requirement_results = requirement_outcomes(
        requirements,
        plans,
        plan_outcomes,
    )
    action_findings = review_corrective_actions(
        anomalies,
        corrective_actions,
        retests,
    )
    closure_results = closure_status(
        closure_records,
        requirement_results,
        anomalies,
        action_findings,
    )

    open_anomalies = unresolved_anomalies(
        anomalies
    )
    open_critical = unresolved_critical_anomalies(
        anomalies
    )

    summary = {
        "requirements": len(requirements),
        "verification_plans": len(plans),
        "evidence_records": len(evidence_records),
        "plan_findings": plan_findings,
        "unplanned_requirements": unplanned,
        "readiness": readiness,
        "evidence_findings": evidence_findings,
        "plan_outcomes": plan_outcomes,
        "requirement_outcomes": requirement_results,
        "open_anomalies": open_anomalies,
        "open_critical_anomalies": open_critical,
        "corrective_action_findings": action_findings,
        "closure_status": closure_results,
    }

    summary_path = (
        reports_dir / "verification_summary.json"
    )
    summary_path.write_text(
        json.dumps(summary, indent=2) + "\n",
        encoding="utf-8",
    )

    matrix_path = (
        reports_dir / "verification_matrix.csv"
    )

    plan_index = {
        plan["id"]: plan
        for plan in plans
    }

    with matrix_path.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.writer(file)
        writer.writerow(
            [
                "plan_id",
                "requirement_ids",
                "method",
                "readiness",
                "outcome",
                "evidence_count",
            ]
        )

        for plan_id in sorted(plan_index):
            plan = plan_index[plan_id]
            evidence_count = sum(
                1
                for record in evidence_records
                if record["plan_id"] == plan_id
            )

            writer.writerow(
                [
                    plan_id,
                    ",".join(
                        plan["requirement_ids"]
                    ),
                    plan["method"],
                    readiness[plan_id],
                    plan_outcomes[plan_id],
                    evidence_count,
                ]
            )

    report_lines = [
        "# Verification Planning and Evidence Report",
        "",
        f"Requirements: {len(requirements)}",
        f"Verification plans: {len(plans)}",
        f"Evidence records: {len(evidence_records)}",
        "",
        "## Plan outcomes",
        "",
    ]

    for plan_id, status in sorted(
        plan_outcomes.items()
    ):
        report_lines.append(
            f"- {plan_id}: {status}"
        )

    report_lines.extend(
        [
            "",
            "## Requirement outcomes",
            "",
        ]
    )

    for requirement_id, status in sorted(
        requirement_results.items()
    ):
        report_lines.append(
            f"- {requirement_id}: {status}"
        )

    report_lines.extend(
        [
            "",
            "## Closure review",
            "",
        ]
    )

    for requirement_id, status in sorted(
        closure_results.items()
    ):
        report_lines.append(
            f"- {requirement_id}: {status}"
        )

    report_lines.extend(
        [
            "",
            "## Open findings",
            "",
            (
                "- Unplanned requirements: "
                + (
                    ", ".join(unplanned)
                    or "none"
                )
            ),
            (
                "- Open anomalies: "
                + (
                    ", ".join(open_anomalies)
                    or "none"
                )
            ),
            (
                "- Open critical anomalies: "
                + (
                    ", ".join(open_critical)
                    or "none"
                )
            ),
            (
                "- Evidence records needing review: "
                + str(len(evidence_findings))
            ),
            (
                "- Corrective actions needing review: "
                + str(len(action_findings))
            ),
        ]
    )

    report_path = (
        reports_dir / "verification_report.md"
    )
    report_path.write_text(
        "\n".join(report_lines) + "\n",
        encoding="utf-8",
    )

    print(
        json.dumps(
            {
                "requirements": len(requirements),
                "verification_plans": len(plans),
                "evidence_records": len(
                    evidence_records
                ),
                "unplanned_requirements": len(
                    unplanned
                ),
                "open_anomalies": len(
                    open_anomalies
                ),
                "ready_to_close": sum(
                    status == "ready_to_close"
                    for status in closure_results.values()
                ),
                "reports": [
                    str(
                        summary_path.relative_to(ROOT)
                    ),
                    str(
                        matrix_path.relative_to(ROOT)
                    ),
                    str(
                        report_path.relative_to(ROOT)
                    ),
                ],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
