#!/usr/bin/env python3
"""Run controlled stress tests against the Version 1 readiness evaluator."""

from __future__ import annotations

import copy
import importlib.util
import json
from collections import Counter
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
EVALUATOR_PATH = PROJECT_ROOT / "src" / "readiness_evaluator.py"
DATA_PATH = PROJECT_ROOT / "data" / "system_proposals.json"
JSON_REPORT = PROJECT_ROOT / "examples" / "stress_test_v2_report.json"
MARKDOWN_REPORT = PROJECT_ROOT / "examples" / "stress_test_v2_report.md"

spec = importlib.util.spec_from_file_location(
    "readiness_evaluator",
    EVALUATOR_PATH,
)
if spec is None or spec.loader is None:
    raise RuntimeError("Could not load the Version 1 readiness evaluator.")

evaluator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(evaluator)


REQUIRED_FIELDS = {
    "id": str,
    "name": str,
    "domain": str,
    "description": str,
    "uses_sensitive_data": bool,
    "requires_human_review": bool,
    "has_source_citations": bool,
    "has_abstention": bool,
    "has_monitoring": bool,
    "has_rollback_plan": bool,
    "has_access_controls": bool,
    "logs_sensitive_content": bool,
    "has_prompt_injection_checks": bool,
    "has_latency_target": bool,
    "has_owner": bool,
    "evidence_quality": str,
}


def validate_proposal(proposal: Any) -> list[str]:
    """Return readable validation errors without calling the main evaluator."""
    if not isinstance(proposal, dict):
        return ["Proposal must be a JSON object."]

    errors: list[str] = []

    for field, expected_type in REQUIRED_FIELDS.items():
        if field not in proposal:
            errors.append(f"Missing required field: {field}")
            continue

        value = proposal[field]
        if not isinstance(value, expected_type):
            errors.append(
                f"Field {field} must be {expected_type.__name__}, "
                f"not {type(value).__name__}."
            )

    evidence_quality = proposal.get("evidence_quality")
    if evidence_quality not in {"weak", "medium", "strong"}:
        errors.append(
            "Field evidence_quality must be weak, medium, or strong."
        )

    return errors


def safe_evaluate(proposal: Any) -> dict[str, Any]:
    """Validate first so incomplete input produces a report instead of a crash."""
    validation_errors = validate_proposal(proposal)

    if validation_errors:
        proposal_id = (
            proposal.get("id", "unknown")
            if isinstance(proposal, dict)
            else "unknown"
        )
        return {
            "id": proposal_id,
            "recommendation": "invalid_input",
            "risk_score": None,
            "finding_count": len(validation_errors),
            "findings": [],
            "validation_errors": validation_errors,
        }

    result = evaluator.evaluate_system(proposal)
    result["validation_errors"] = []
    return result


def find_proposal(
    proposals: list[dict[str, Any]],
    proposal_id: str,
) -> dict[str, Any]:
    for proposal in proposals:
        if proposal.get("id") == proposal_id:
            return copy.deepcopy(proposal)

    raise KeyError(f"Proposal not found: {proposal_id}")


def compare_case(
    name: str,
    baseline: dict[str, Any],
    changed: dict[str, Any],
    change_summary: str,
) -> dict[str, Any]:
    before = safe_evaluate(baseline)
    after = safe_evaluate(changed)

    before_score = before.get("risk_score")
    after_score = after.get("risk_score")

    score_change = None
    if isinstance(before_score, int) and isinstance(after_score, int):
        score_change = after_score - before_score

    return {
        "name": name,
        "change": change_summary,
        "before": before,
        "after": after,
        "recommendation_changed": (
            before.get("recommendation") != after.get("recommendation")
        ),
        "score_change": score_change,
    }


def main() -> int:
    proposals = json.loads(DATA_PATH.read_text(encoding="utf-8"))

    ready = find_proposal(proposals, "research_assistant_ready")
    clinical = find_proposal(proposals, "clinical_summary_incomplete")
    financial = find_proposal(proposals, "financial_risk_high")
    agent = find_proposal(proposals, "agent_workflow_review")

    no_monitoring = copy.deepcopy(ready)
    no_monitoring["id"] = "research_assistant_no_monitoring"
    no_monitoring["has_monitoring"] = False

    unsafe_logging = copy.deepcopy(ready)
    unsafe_logging["id"] = "research_assistant_sensitive_logging"
    unsafe_logging["logs_sensitive_content"] = True

    repaired_clinical = copy.deepcopy(clinical)
    repaired_clinical.update(
        {
            "id": "clinical_summary_repaired",
            "requires_human_review": True,
            "has_abstention": True,
            "has_monitoring": True,
            "has_rollback_plan": True,
            "has_prompt_injection_checks": True,
            "has_latency_target": True,
            "has_owner": True,
            "logs_sensitive_content": False,
            "evidence_quality": "strong",
        }
    )

    repaired_financial = copy.deepcopy(financial)
    repaired_financial.update(
        {
            "id": "financial_risk_repaired",
            "requires_human_review": True,
            "has_source_citations": True,
            "has_abstention": True,
            "has_monitoring": True,
            "has_rollback_plan": True,
            "has_access_controls": True,
            "logs_sensitive_content": False,
            "has_prompt_injection_checks": True,
            "has_latency_target": True,
            "has_owner": True,
            "evidence_quality": "strong",
        }
    )

    repaired_agent = copy.deepcopy(agent)
    repaired_agent.update(
        {
            "id": "agent_workflow_repaired",
            "has_rollback_plan": True,
            "has_latency_target": True,
            "evidence_quality": "strong",
        }
    )

    comparisons = [
        compare_case(
            "Remove monitoring from an approved system",
            ready,
            no_monitoring,
            "Changed has_monitoring from true to false.",
        ),
        compare_case(
            "Enable sensitive-content logging",
            ready,
            unsafe_logging,
            "Changed logs_sensitive_content from false to true.",
        ),
        compare_case(
            "Add safeguards to the clinical support proposal",
            clinical,
            repaired_clinical,
            "Added human review, abstention, monitoring, rollback, "
            "prompt-injection checks, ownership, latency target, "
            "and stronger evidence.",
        ),
        compare_case(
            "Add safeguards to the financial proposal",
            financial,
            repaired_financial,
            "Added human review, citations, abstention, monitoring, "
            "rollback, access controls, prompt-injection checks, "
            "ownership, latency target, and stronger evidence.",
        ),
        compare_case(
            "Complete the agent workflow safeguards",
            agent,
            repaired_agent,
            "Added rollback planning, a latency target, and stronger evidence.",
        ),
    ]

    malformed_cases = [
        {
            "name": "Missing required fields",
            "proposal": {
                "id": "missing_fields",
                "name": "Incomplete Proposal",
            },
        },
        {
            "name": "Incorrect field types",
            "proposal": {
                **ready,
                "id": "incorrect_types",
                "has_monitoring": "yes",
                "risk_score": "unknown",
            },
        },
        {
            "name": "Non-object input",
            "proposal": ["not", "a", "proposal"],
        },
    ]

    malformed_results = [
        {
            "name": case["name"],
            "result": safe_evaluate(case["proposal"]),
        }
        for case in malformed_cases
    ]

    first_run = safe_evaluate(ready)
    second_run = safe_evaluate(ready)
    deterministic = first_run == second_run

    evaluated_results = [
        comparison["before"]
        for comparison in comparisons
    ] + [
        comparison["after"]
        for comparison in comparisons
    ]

    recommendation_counts = Counter(
        result["recommendation"] for result in evaluated_results
    )

    severity_counts: Counter[str] = Counter()
    category_counts: Counter[str] = Counter()

    for result in evaluated_results:
        for finding in result.get("findings", []):
            severity_counts[finding["severity"]] += 1
            category_counts[finding["category"]] += 1

    report = {
        "version": "2",
        "purpose": (
            "Controlled readiness stress tests, malformed-input handling, "
            "determinism checks, and risk-summary metrics."
        ),
        "comparison_cases": comparisons,
        "malformed_input_cases": malformed_results,
        "deterministic_repeat_check": {
            "passed": deterministic,
            "first": first_run,
            "second": second_run,
        },
        "metrics": {
            "recommendation_counts": dict(
                sorted(recommendation_counts.items())
            ),
            "severity_counts": dict(sorted(severity_counts.items())),
            "risk_category_counts": dict(sorted(category_counts.items())),
        },
    }

    JSON_REPORT.write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8",
    )

    lines = [
        "# AI System Readiness Stress Test V2",
        "",
        "Controlled changes are applied to synthetic proposals to show how "
        "specific safeguards affect recommendations and risk scores.",
        "",
        "## Before-and-after comparisons",
        "",
        "| Case | Before | After | Score change |",
        "|---|---|---|---:|",
    ]

    for case in comparisons:
        score_change = case["score_change"]
        shown_change = "n/a" if score_change is None else str(score_change)
        lines.append(
            f"| {case['name']} | "
            f"{case['before']['recommendation']} | "
            f"{case['after']['recommendation']} | "
            f"{shown_change} |"
        )

    lines.extend(
        [
            "",
            "## Malformed-input handling",
            "",
        ]
    )

    for case in malformed_results:
        result = case["result"]
        lines.append(
            f"- **{case['name']}**: "
            f"{result['recommendation']} "
            f"({result['finding_count']} validation issue(s))"
        )

    lines.extend(
        [
            "",
            "## Determinism",
            "",
            f"- Repeat check passed: **{deterministic}**",
            "",
            "## Recommendation counts",
            "",
        ]
    )

    for label, count in sorted(recommendation_counts.items()):
        lines.append(f"- {label}: {count}")

    lines.extend(
        [
            "",
            "## Severity counts",
            "",
        ]
    )

    for label, count in sorted(severity_counts.items()):
        lines.append(f"- {label}: {count}")

    lines.extend(
        [
            "",
            "## Most common risk categories",
            "",
        ]
    )

    for label, count in category_counts.most_common():
        lines.append(f"- {label}: {count}")

    lines.extend(
        [
            "",
            "## Limitations",
            "",
            "These are local rule-based stress tests using synthetic "
            "configuration data. They are not production security, "
            "compliance, medical, or financial evaluations.",
            "",
        ]
    )

    MARKDOWN_REPORT.write_text(
        "\n".join(lines),
        encoding="utf-8",
    )

    print(f"Wrote {JSON_REPORT}")
    print(f"Wrote {MARKDOWN_REPORT}")
    print(f"Deterministic repeat check: {deterministic}")

    for case in comparisons:
        print(
            f"{case['before']['recommendation']:>12} -> "
            f"{case['after']['recommendation']:<12} "
            f"{case['name']}"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
