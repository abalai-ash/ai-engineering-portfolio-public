from __future__ import annotations

import csv
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from baseline import compare_baselines
from change_impact import analyze_change
from requirement_review import review_requirements
from traceability import (
    find_orphan_requirements,
    find_unknown_requirement_links,
    find_unverified_requirements,
)
from verification import evaluate_cases, requirement_outcomes


def load_json(filename: str):
    path = ROOT / "data" / filename
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    needs = load_json("stakeholder_needs.json")
    requirements = load_json("requirements.json")
    architecture = load_json("architecture.json")
    interfaces = load_json("interfaces.json")
    cases = load_json("verification_cases.json")
    results = load_json("verification_results.json")
    previous = load_json("baseline_previous.json")
    changes = load_json("change_requests.json")

    reports_dir = ROOT / "reports"
    reports_dir.mkdir(exist_ok=True)

    quality_findings = review_requirements(requirements)
    orphan_requirements = find_orphan_requirements(
        needs,
        requirements,
    )
    unverified_requirements = find_unverified_requirements(
        requirements,
        cases,
    )
    unknown_links = find_unknown_requirement_links(
        requirements,
        cases,
    )

    evaluated_cases = evaluate_cases(cases, results)
    outcomes = requirement_outcomes(
        requirements,
        evaluated_cases,
    )

    current_system_requirements = [
        {
            "id": requirement["id"],
            "text": requirement["text"],
            "status": requirement["status"],
        }
        for requirement in requirements
        if requirement["level"] == "system"
    ]

    baseline_results = compare_baselines(
        previous,
        current_system_requirements,
    )

    change_results = {
        change["id"]: analyze_change(
            change["changed_requirements"],
            requirements,
            cases,
        )
        for change in changes
    }

    summary = {
        "stakeholder_needs": len(needs),
        "requirements": len(requirements),
        "components": len(architecture["components"]),
        "interfaces": len(interfaces),
        "verification_cases": len(cases),
        "quality_findings": quality_findings,
        "orphan_requirements": orphan_requirements,
        "unverified_requirements": unverified_requirements,
        "unknown_verification_links": unknown_links,
        "requirement_outcomes": outcomes,
        "baseline_changes": baseline_results,
        "change_impact": change_results,
    }

    summary_path = reports_dir / "traceability_summary.json"
    summary_path.write_text(
        json.dumps(summary, indent=2) + "\n",
        encoding="utf-8",
    )

    matrix_path = reports_dir / "traceability_matrix.csv"

    with matrix_path.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.writer(file)
        writer.writerow(
            [
                "requirement_id",
                "level",
                "parent",
                "component",
                "verification_method",
                "outcome",
            ]
        )

        for requirement in requirements:
            writer.writerow(
                [
                    requirement["id"],
                    requirement["level"],
                    requirement["parent"],
                    requirement["component"],
                    requirement["verification_method"],
                    outcomes[requirement["id"]],
                ]
            )

    report_lines = [
        "# Systems Traceability Report",
        "",
        f"Stakeholder needs: {len(needs)}",
        f"Requirements: {len(requirements)}",
        f"Components: {len(architecture['components'])}",
        f"Interfaces: {len(interfaces)}",
        f"Verification cases: {len(cases)}",
        "",
        "## Requirement outcomes",
        "",
    ]

    for requirement_id, status in sorted(outcomes.items()):
        report_lines.append(
            f"- {requirement_id}: {status}"
        )

    report_lines.extend(
        [
            "",
            "## Baseline comparison",
            "",
            (
                "- Added: "
                + (
                    ", ".join(baseline_results["added"])
                    or "none"
                )
            ),
            (
                "- Removed: "
                + (
                    ", ".join(baseline_results["removed"])
                    or "none"
                )
            ),
            (
                "- Modified: "
                + (
                    ", ".join(baseline_results["modified"])
                    or "none"
                )
            ),
            "",
            "## Review findings",
            "",
        ]
    )

    if quality_findings:
        for requirement_id, findings in sorted(
            quality_findings.items()
        ):
            report_lines.append(
                f"- {requirement_id}: "
                + "; ".join(findings)
            )
    else:
        report_lines.append("- No wording findings.")

    report_path = reports_dir / "traceability_report.md"
    report_path.write_text(
        "\n".join(report_lines) + "\n",
        encoding="utf-8",
    )

    print(
        json.dumps(
            {
                "requirements": len(requirements),
                "verification_cases": len(cases),
                "quality_findings": len(quality_findings),
                "orphan_requirements": len(
                    orphan_requirements
                ),
                "unverified_requirements": len(
                    unverified_requirements
                ),
                "reports": [
                    str(summary_path.relative_to(ROOT)),
                    str(matrix_path.relative_to(ROOT)),
                    str(report_path.relative_to(ROOT)),
                ],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
