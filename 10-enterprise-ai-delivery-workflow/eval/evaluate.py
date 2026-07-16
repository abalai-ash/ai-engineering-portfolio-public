from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


PROJECT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_DIR / "src"
sys.path.insert(0, str(SRC_DIR))

from discovery_engine import build_discovery_report, load_requests
from solution_planner import build_solution_plan


RESULTS_JSON = PROJECT_DIR / "eval" / "eval_results.json"
RESULTS_MD = PROJECT_DIR / "eval" / "eval_results.md"


def record(
    results: list[dict[str, Any]],
    name: str,
    passed: bool,
    details: str,
) -> None:
    results.append(
        {
            "name": name,
            "passed": passed,
            "details": details,
        }
    )

    label = "PASS" if passed else "FAIL"
    print(f"{label}: {name} - {details}")


def main() -> None:
    requests = load_requests()
    reports = [build_discovery_report(item) for item in requests]
    plans = [build_solution_plan(report) for report in reports]

    report_by_id = {
        report["request_id"]: report
        for report in reports
    }

    plan_by_id = {
        plan["request_id"]: plan
        for plan in plans
    }

    results: list[dict[str, Any]] = []

    record(
        results,
        "all requests reach solution planning",
        all(
            report["status"] == "ready_for_solution_planning"
            for report in reports
        ),
        f"{len(reports)} reports checked",
    )

    enterprise = report_by_id["enterprise_knowledge_assistant"]
    record(
        results,
        "restricted enterprise sources are detected",
        set(enterprise["data_summary"]["sensitive_sources"])
        == {"support notes", "account records"},
        str(enterprise["data_summary"]["sensitive_sources"]),
    )

    robotics = plan_by_id["robot_localization_support"]
    record(
        results,
        "robotics plan includes failure recovery",
        "fallback state estimator"
        in robotics["architecture"]["components"],
        robotics["launch_recommendation"],
    )

    scientific = report_by_id["scientific_workload_benchmark"]
    record(
        results,
        "scientific case identifies missing rollback plan",
        "rollback_plan" in scientific["missing_controls"],
        str(scientific["missing_controls"]),
    )

    expected_recommendations = {
        "enterprise_knowledge_assistant": "needs_review",
        "robot_localization_support": "pilot_ready",
        "scientific_workload_benchmark": "needs_review",
    }

    for request_id, expected in expected_recommendations.items():
        actual = plan_by_id[request_id]["launch_recommendation"]

        record(
            results,
            f"{request_id} recommendation",
            actual == expected,
            f"expected={expected} actual={actual}",
        )

    invalid_report = build_discovery_report(
        {
            "request_id": "invalid_example",
            "domain": "enterprise_ai",
        }
    )

    record(
        results,
        "incomplete request is rejected",
        invalid_report["status"] == "invalid_request",
        invalid_report["status"],
    )

    first_plan = build_solution_plan(reports[0])
    repeated_plan = build_solution_plan(reports[0])

    record(
        results,
        "solution planning is deterministic",
        first_plan == repeated_plan,
        f"equal={first_plan == repeated_plan}",
    )

    total = len(results)
    passed = sum(1 for result in results if result["passed"])

    summary = {
        "passed": passed,
        "total": total,
        "all_passed": passed == total,
        "results": results,
    }

    RESULTS_JSON.write_text(
        json.dumps(summary, indent=2),
        encoding="utf-8",
    )

    markdown_lines = [
        "# Evaluation Results",
        "",
        f"Passed: **{passed}/{total}**",
        "",
        "| Check | Result | Details |",
        "|---|---|---|",
    ]

    for result in results:
        label = "PASS" if result["passed"] else "FAIL"
        details = str(result["details"]).replace("|", "/")

        markdown_lines.append(
            f"| {result['name']} | {label} | {details} |"
        )

    markdown_lines.extend(
        [
            "",
            "## Scope",
            "",
            (
                "This evaluation uses synthetic requests and local, "
                "rule-based planning logic. It does not represent a "
                "production deployment, customer engagement, robotics "
                "system, or quantum hardware benchmark."
            ),
            "",
        ]
    )

    RESULTS_MD.write_text(
        "\n".join(markdown_lines),
        encoding="utf-8",
    )

    print()
    print(f"Evaluation complete: {passed}/{total} passed")
    print(f"Wrote {RESULTS_JSON}")
    print(f"Wrote {RESULTS_MD}")

    if passed != total:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
