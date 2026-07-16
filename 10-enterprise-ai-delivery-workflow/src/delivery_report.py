from __future__ import annotations

import json
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parents[1]
PLANS_PATH = BASE_DIR / "examples" / "solution_plans.json"
REPORT_PATH = BASE_DIR / "examples" / "delivery_report.md"


def load_solution_plans(
    path: Path = PLANS_PATH,
) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as file:
        plans = json.load(file)

    if not isinstance(plans, list):
        raise ValueError("Solution plan file must contain a list.")

    return plans


def format_label(value: str) -> str:
    return value.replace("_", " ").title()


def recommendation_summary(recommendation: str) -> str:
    summaries = {
        "pilot_ready": (
            "The proposal has enough defined safeguards and evaluation steps "
            "to move into a limited, monitored pilot."
        ),
        "needs_review": (
            "The proposal needs additional controls or decisions before a "
            "pilot should begin."
        ),
        "block": (
            "The proposal should not advance until its major gaps are resolved."
        ),
    }

    return summaries.get(
        recommendation,
        "The proposal requires additional technical review.",
    )


def build_report(plans: list[dict[str, Any]]) -> str:
    lines = [
        "# Enterprise AI Delivery Report",
        "",
        (
            "This report summarizes three synthetic technical discovery and "
            "solution-planning cases. The goal is to show how an unclear "
            "request can be translated into architecture, evaluation, risk, "
            "and launch decisions."
        ),
        "",
        "## Portfolio Scope",
        "",
        "- Enterprise knowledge retrieval and grounded AI responses",
        "- Robot localization and sensor reliability",
        "- Scientific algorithm benchmarking and reproducibility",
        "",
    ]

    for plan in plans:
        request_id = str(plan.get("request_id", "unknown"))
        domain = str(plan.get("domain", "unknown"))
        goal = str(plan.get("goal", ""))
        risk_level = str(plan.get("risk_level", "unknown"))
        recommendation = str(
            plan.get("launch_recommendation", "unknown")
        )

        architecture = plan.get("architecture", {})
        components = architecture.get("components", [])
        evaluation_checks = architecture.get("evaluation_checks", [])
        deployment_path = architecture.get("deployment_path", [])
        risks = plan.get("risk_register", [])
        next_actions = plan.get("next_actions", [])

        lines.extend(
            [
                f"## {format_label(request_id)}",
                "",
                f"**Domain:** {format_label(domain)}",
                "",
                f"**Goal:** {goal}",
                "",
                f"**Risk level:** {risk_level.title()}",
                "",
                (
                    f"**Recommendation:** "
                    f"{format_label(recommendation)}"
                ),
                "",
                recommendation_summary(recommendation),
                "",
                "### Proposed components",
                "",
            ]
        )

        for component in components:
            lines.append(f"- {component}")

        lines.extend(
            [
                "",
                "### Evaluation plan",
                "",
            ]
        )

        for check in evaluation_checks:
            lines.append(f"- {check}")

        lines.extend(
            [
                "",
                "### Delivery path",
                "",
            ]
        )

        for index, step in enumerate(deployment_path, start=1):
            lines.append(f"{index}. {step}")

        lines.extend(
            [
                "",
                "### Main risks and mitigations",
                "",
            ]
        )

        for item in risks:
            risk = item.get("risk", "Unspecified risk")
            mitigation = item.get(
                "mitigation",
                "Additional review required.",
            )
            lines.append(f"- **Risk:** {risk}")
            lines.append(f"  - **Mitigation:** {mitigation}")

        lines.extend(
            [
                "",
                "### Next actions",
                "",
            ]
        )

        for action in next_actions:
            lines.append(f"- {action}")

        lines.append("")

    lines.extend(
        [
            "## Limitations",
            "",
            (
                "This is a local portfolio demonstration using synthetic "
                "requests and transparent rule-based logic. It is not a "
                "production deployment, real customer engagement, operating "
                "robotics system, clinical system, financial system, or "
                "quantum hardware experiment."
            ),
            "",
        ]
    )

    return "\n".join(lines)


def main() -> None:
    plans = load_solution_plans()
    report = build_report(plans)

    REPORT_PATH.write_text(
        report,
        encoding="utf-8",
    )

    print(f"Generated report for {len(plans)} solution plans.")
    print(f"Wrote {REPORT_PATH}")


if __name__ == "__main__":
    main()
