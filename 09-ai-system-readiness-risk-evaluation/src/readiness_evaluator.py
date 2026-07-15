#!/usr/bin/env python3
"""Evaluate synthetic AI system proposals for launch readiness and risk."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "system_proposals.json"
JSON_REPORT = ROOT / "examples" / "readiness_report.json"
MARKDOWN_REPORT = ROOT / "examples" / "example_report.md"


def add_finding(
    findings: list[dict[str, Any]],
    category: str,
    severity: str,
    message: str,
    action: str,
    points: int,
) -> None:
    findings.append(
        {
            "category": category,
            "severity": severity,
            "message": message,
            "recommended_action": action,
            "points": points,
        }
    )


def evaluate_system(proposal: dict[str, Any]) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []

    if proposal["uses_sensitive_data"] and not proposal["has_access_controls"]:
        add_finding(
            findings,
            "security",
            "critical",
            "Sensitive data is used without access controls.",
            "Add role-based access controls before launch.",
            5,
        )

    if proposal["logs_sensitive_content"]:
        add_finding(
            findings,
            "privacy",
            "critical",
            "Sensitive content may be written to logs.",
            "Redact or disable sensitive-content logging.",
            5,
        )

    if (
        proposal["domain"] in {"healthcare", "financial"}
        and not proposal["requires_human_review"]
    ):
        add_finding(
            findings,
            "human_review",
            "critical",
            "A high-impact workflow has no required human review.",
            "Require qualified human review for consequential decisions.",
            5,
        )

    checks = [
        (
            "has_source_citations",
            "grounding",
            "high",
            "Outputs are not tied to inspectable source evidence.",
            "Add source references or evidence traces.",
            3,
        ),
        (
            "has_abstention",
            "failure_behavior",
            "high",
            "The system has no clear abstention or uncertainty behavior.",
            "Add a safe fallback when evidence is weak or missing.",
            3,
        ),
        (
            "has_prompt_injection_checks",
            "security",
            "high",
            "Prompt-injection or instruction-conflict checks are missing.",
            "Add input screening and instruction-boundary tests.",
            3,
        ),
        (
            "has_monitoring",
            "operations",
            "high",
            "Post-launch monitoring is not defined.",
            "Add quality, failure, latency, and drift monitoring.",
            3,
        ),
        (
            "has_rollback_plan",
            "reliability",
            "medium",
            "No rollback plan is documented.",
            "Define rollback triggers and a recovery procedure.",
            2,
        ),
        (
            "has_owner",
            "ownership",
            "medium",
            "No accountable system owner is listed.",
            "Assign an owner for incidents, reviews, and updates.",
            2,
        ),
        (
            "has_latency_target",
            "performance",
            "low",
            "No latency target is defined.",
            "Set and measure an acceptable response-time target.",
            1,
        ),
    ]

    for key, category, severity, message, action, points in checks:
        if not proposal[key]:
            add_finding(
                findings,
                category,
                severity,
                message,
                action,
                points,
            )

    if proposal["evidence_quality"] == "weak":
        add_finding(
            findings,
            "evidence",
            "high",
            "Evidence quality is too weak for the proposed use.",
            "Collect stronger evaluation evidence before launch.",
            3,
        )
    elif proposal["evidence_quality"] == "medium":
        add_finding(
            findings,
            "evidence",
            "low",
            "Evidence is usable but still limited.",
            "Expand evaluation coverage and document remaining gaps.",
            1,
        )

    score = sum(item["points"] for item in findings)
    critical_count = sum(
        item["severity"] == "critical" for item in findings
    )
    high_count = sum(
        item["severity"] == "high" for item in findings
    )

    if critical_count >= 1 or score >= 12:
        recommendation = "block"
    elif high_count >= 1 or score >= 4:
        recommendation = "needs_review"
    else:
        recommendation = "approve"

    return {
        "id": proposal["id"],
        "name": proposal["name"],
        "domain": proposal["domain"],
        "risk_score": score,
        "recommendation": recommendation,
        "finding_count": len(findings),
        "findings": findings,
    }


def build_markdown(results: list[dict[str, Any]]) -> str:
    lines = [
        "# AI System Readiness Report",
        "",
        "Generated from synthetic proposals using transparent rule-based checks.",
        "",
    ]

    for result in results:
        lines.extend(
            [
                f"## {result['name']}",
                "",
                f"- Domain: `{result['domain']}`",
                f"- Recommendation: **{result['recommendation']}**",
                f"- Risk score: **{result['risk_score']}**",
                f"- Findings: **{result['finding_count']}**",
                "",
            ]
        )

        if not result["findings"]:
            lines.extend(
                [
                    "No launch-blocking gaps were found by the current checks.",
                    "",
                ]
            )
            continue

        for finding in result["findings"]:
            lines.append(
                f"- **{finding['severity']} / {finding['category']}**: "
                f"{finding['message']} "
                f"Action: {finding['recommended_action']}"
            )

        lines.append("")

    lines.extend(
        [
            "## Limitations",
            "",
            "This is a local portfolio prototype. It is not a production "
            "security, compliance, clinical, or financial review system.",
            "",
        ]
    )

    return "\n".join(lines)


def main() -> int:
    proposals = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    results = [evaluate_system(item) for item in proposals]

    JSON_REPORT.write_text(
        json.dumps(results, indent=2) + "\n",
        encoding="utf-8",
    )
    MARKDOWN_REPORT.write_text(
        build_markdown(results),
        encoding="utf-8",
    )

    for result in results:
        print(
            f"{result['recommendation'].upper():12} "
            f"score={result['risk_score']:2d} "
            f"{result['name']}"
        )

    print(f"\nWrote {JSON_REPORT}")
    print(f"Wrote {MARKDOWN_REPORT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
