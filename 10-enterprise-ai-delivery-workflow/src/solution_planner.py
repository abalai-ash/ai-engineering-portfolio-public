from __future__ import annotations

import json
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parents[1]
DISCOVERY_PATH = BASE_DIR / "examples" / "discovery_reports.json"
OUTPUT_PATH = BASE_DIR / "examples" / "solution_plans.json"


DOMAIN_ARCHITECTURES = {
    "enterprise_ai": {
        "components": [
            "document ingestion",
            "structured data connector",
            "access-aware retrieval",
            "vector search",
            "grounded response service",
            "citation formatter",
            "human review queue",
            "monitoring and audit logs",
        ],
        "evaluation_checks": [
            "retrieval relevance",
            "answer grounding",
            "citation correctness",
            "permission enforcement",
            "abstention quality",
            "latency",
        ],
        "deployment_path": [
            "offline evaluation",
            "internal pilot",
            "limited user rollout",
            "monitored expansion",
        ],
    },
    "robotics": {
        "components": [
            "sensor ingestion",
            "timestamp synchronization",
            "calibration validator",
            "localization estimator",
            "uncertainty tracker",
            "map mismatch detector",
            "sensor health monitor",
            "fallback state estimator",
        ],
        "evaluation_checks": [
            "position error",
            "orientation error",
            "sensor dropout recovery",
            "calibration drift detection",
            "map mismatch detection",
            "latency",
        ],
        "deployment_path": [
            "synthetic replay tests",
            "recorded sensor runs",
            "controlled environment trial",
            "limited fleet pilot",
        ],
    },
    "scientific_computing": {
        "components": [
            "benchmark case loader",
            "baseline implementation",
            "candidate algorithm runner",
            "hardware timing collector",
            "noise and uncertainty analyzer",
            "result comparison",
            "versioned experiment outputs",
            "reproducibility report",
        ],
        "evaluation_checks": [
            "correctness against baseline",
            "runtime",
            "memory use",
            "repeatability",
            "noise sensitivity",
            "hardware tradeoffs",
        ],
        "deployment_path": [
            "small benchmark suite",
            "repeated local runs",
            "hardware comparison",
            "documented implementation decision",
        ],
    },
}


def load_discovery_reports(
    path: Path = DISCOVERY_PATH,
) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as file:
        reports = json.load(file)

    if not isinstance(reports, list):
        raise ValueError("Discovery report file must contain a list.")

    return reports


def estimate_risk_level(report: dict[str, Any]) -> str:
    missing_controls = report.get("missing_controls", [])
    sensitive_sources = report.get("data_summary", {}).get(
        "sensitive_sources",
        [],
    )

    score = 0

    if missing_controls:
        score += len(missing_controls)

    if sensitive_sources:
        score += 2

    if report.get("domain") == "robotics":
        score += 1

    if score >= 3:
        return "high"
    if score >= 1:
        return "medium"
    return "low"


def build_risk_register(report: dict[str, Any]) -> list[dict[str, str]]:
    risks = []

    for control in report.get("missing_controls", []):
        risks.append(
            {
                "risk": f"Missing required control: {control}",
                "mitigation": f"Define and test {control} before launch.",
            }
        )

    for source in report.get("data_summary", {}).get(
        "sensitive_sources",
        [],
    ):
        risks.append(
            {
                "risk": f"Sensitive source exposure: {source}",
                "mitigation": (
                    "Use access checks, restricted logs, and source-level "
                    "permission enforcement."
                ),
            }
        )

    domain = report.get("domain")

    if domain == "enterprise_ai":
        risks.extend(
            [
                {
                    "risk": "Unsupported or weakly grounded answer",
                    "mitigation": (
                        "Require retrieved evidence, citations, and abstention "
                        "when evidence is insufficient."
                    ),
                },
                {
                    "risk": "Incorrect access to restricted information",
                    "mitigation": (
                        "Apply user-level authorization before retrieval."
                    ),
                },
            ]
        )

    elif domain == "robotics":
        risks.extend(
            [
                {
                    "risk": "Localization failure during sensor dropout",
                    "mitigation": (
                        "Track uncertainty and use a tested fallback estimate."
                    ),
                },
                {
                    "risk": "Map or calibration drift",
                    "mitigation": (
                        "Monitor residuals and stop deployment when thresholds "
                        "are exceeded."
                    ),
                },
            ]
        )

    elif domain == "scientific_computing":
        risks.extend(
            [
                {
                    "risk": "Selecting a faster but inaccurate method",
                    "mitigation": (
                        "Compare all candidates against a trusted baseline."
                    ),
                },
                {
                    "risk": "Results depend on one run or one machine",
                    "mitigation": (
                        "Repeat runs and record hardware, software, and seed "
                        "information."
                    ),
                },
            ]
        )

    return risks


def choose_launch_recommendation(
    report: dict[str, Any],
    risk_level: str,
) -> str:
    if report.get("status") != "ready_for_solution_planning":
        return "block"

    sensitive_sources = report.get("data_summary", {}).get(
        "sensitive_sources",
        [],
    )

    if risk_level == "high":
        return "needs_review"

    if report.get("missing_controls"):
        return "needs_review"

    if sensitive_sources:
        return "needs_review"

    return "pilot_ready"


def build_solution_plan(report: dict[str, Any]) -> dict[str, Any]:
    domain = report.get("domain", "unknown")
    architecture = DOMAIN_ARCHITECTURES.get(
        domain,
        {
            "components": ["requirements review"],
            "evaluation_checks": ["manual validation"],
            "deployment_path": ["prototype"],
        },
    )

    risk_level = estimate_risk_level(report)
    risks = build_risk_register(report)
    recommendation = choose_launch_recommendation(
        report,
        risk_level,
    )

    return {
        "request_id": report.get("request_id", "unknown"),
        "domain": domain,
        "goal": report.get("goal", ""),
        "architecture": architecture,
        "risk_level": risk_level,
        "risk_register": risks,
        "launch_recommendation": recommendation,
        "next_actions": [
            "Resolve open discovery questions.",
            "Confirm measurable success thresholds.",
            "Build the smallest testable prototype.",
            "Run offline evaluation before any pilot.",
            "Document rollback or stopping conditions.",
        ],
    }


def main() -> None:
    reports = load_discovery_reports()
    plans = [build_solution_plan(report) for report in reports]

    OUTPUT_PATH.write_text(
        json.dumps(plans, indent=2),
        encoding="utf-8",
    )

    print("Solution plans")
    print("--------------")

    for plan in plans:
        print(
            f"{plan['request_id']}: "
            f"risk={plan['risk_level']} "
            f"recommendation={plan['launch_recommendation']}"
        )

    print(f"\nWrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
