#!/usr/bin/env python3
"""Evaluate the Version 2 readiness stress-test behavior."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = PROJECT_ROOT / "src" / "stress_test_v2.py"
RESULTS_PATH = PROJECT_ROOT / "eval" / "eval_results_v2.md"

spec = importlib.util.spec_from_file_location(
    "stress_test_v2",
    SCRIPT_PATH,
)
if spec is None or spec.loader is None:
    raise RuntimeError("Could not load the Version 2 stress-test module.")

stress = importlib.util.module_from_spec(spec)
spec.loader.exec_module(stress)


def check(
    name: str,
    condition: bool,
    detail: str,
) -> dict[str, Any]:
    return {
        "name": name,
        "passed": bool(condition),
        "detail": detail,
    }


def main() -> int:
    proposals = json.loads(stress.DATA_PATH.read_text(encoding="utf-8"))

    ready = stress.find_proposal(proposals, "research_assistant_ready")
    clinical = stress.find_proposal(
        proposals,
        "clinical_summary_incomplete",
    )
    agent = stress.find_proposal(proposals, "agent_workflow_review")

    no_monitoring = dict(ready)
    no_monitoring["has_monitoring"] = False

    unsafe_logging = dict(ready)
    unsafe_logging["logs_sensitive_content"] = True

    repaired_clinical = dict(clinical)
    repaired_clinical.update(
        {
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

    repaired_agent = dict(agent)
    repaired_agent.update(
        {
            "has_rollback_plan": True,
            "has_latency_target": True,
            "evidence_quality": "strong",
        }
    )

    ready_result = stress.safe_evaluate(ready)
    no_monitoring_result = stress.safe_evaluate(no_monitoring)
    unsafe_logging_result = stress.safe_evaluate(unsafe_logging)
    clinical_result = stress.safe_evaluate(clinical)
    repaired_clinical_result = stress.safe_evaluate(repaired_clinical)
    agent_result = stress.safe_evaluate(agent)
    repaired_agent_result = stress.safe_evaluate(repaired_agent)

    incomplete_result = stress.safe_evaluate(
        {
            "id": "incomplete_case",
            "name": "Incomplete Case",
        }
    )

    wrong_type = dict(ready)
    wrong_type["has_monitoring"] = "yes"
    wrong_type_result = stress.safe_evaluate(wrong_type)

    repeated_a = stress.safe_evaluate(ready)
    repeated_b = stress.safe_evaluate(ready)

    tests = [
        check(
            "approved baseline remains approved",
            ready_result["recommendation"] == "approve",
            f"actual={ready_result['recommendation']}",
        ),
        check(
            "removing monitoring raises risk",
            no_monitoring_result["risk_score"]
            > ready_result["risk_score"],
            (
                f"before={ready_result['risk_score']} "
                f"after={no_monitoring_result['risk_score']}"
            ),
        ),
        check(
            "sensitive logging blocks launch",
            unsafe_logging_result["recommendation"] == "block",
            f"actual={unsafe_logging_result['recommendation']}",
        ),
        check(
            "clinical safeguards lower risk",
            repaired_clinical_result["risk_score"]
            < clinical_result["risk_score"],
            (
                f"before={clinical_result['risk_score']} "
                f"after={repaired_clinical_result['risk_score']}"
            ),
        ),
        check(
            "agent safeguards lower risk",
            repaired_agent_result["risk_score"]
            < agent_result["risk_score"],
            (
                f"before={agent_result['risk_score']} "
                f"after={repaired_agent_result['risk_score']}"
            ),
        ),
        check(
            "missing fields return invalid input",
            incomplete_result["recommendation"] == "invalid_input",
            f"actual={incomplete_result['recommendation']}",
        ),
        check(
            "incorrect types return invalid input",
            wrong_type_result["recommendation"] == "invalid_input",
            f"actual={wrong_type_result['recommendation']}",
        ),
        check(
            "repeated evaluation is deterministic",
            repeated_a == repeated_b,
            f"equal={repeated_a == repeated_b}",
        ),
    ]

    passed = sum(test["passed"] for test in tests)
    total = len(tests)

    lines = [
        "# Version 2 Stress-Test Evaluation",
        "",
        "| Test | Result | Detail |",
        "|---|---|---|",
    ]

    for test in tests:
        label = "PASS" if test["passed"] else "FAIL"
        lines.append(
            f"| {test['name']} | **{label}** | {test['detail']} |"
        )
        print(f"{label}: {test['name']} - {test['detail']}")

    lines.extend(
        [
            "",
            f"Evaluation complete: **{passed}/{total} passed**.",
            "",
            "The cases use synthetic proposals and local rule-based checks.",
            "",
        ]
    )

    RESULTS_PATH.write_text(
        "\n".join(lines),
        encoding="utf-8",
    )

    print(f"\nEvaluation complete: {passed}/{total} passed")
    print(f"Wrote {RESULTS_PATH}")

    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
