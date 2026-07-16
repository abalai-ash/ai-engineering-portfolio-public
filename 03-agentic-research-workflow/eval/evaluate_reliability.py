from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = BASE_DIR / "src"
RESULTS_JSON = BASE_DIR / "eval" / "reliability_results.json"
RESULTS_MD = BASE_DIR / "eval" / "reliability_results.md"

sys.path.insert(0, str(SRC_DIR))

from reliable_workflow import STEPS, run_reliable_workflow


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
    results: list[dict[str, Any]] = []

    query = "Summarize agentic workflow tools and human review."

    retry_result = run_reliable_workflow(
        query=query,
        run_id="eval_retry_resume",
        policy="retry_then_resume",
        max_retries=2,
        failure_plan={
            "retrieve_notes": [1],
            "build_checklist": [1],
        },
    )

    record(
        results,
        "retry policy completes after recoverable failures",
        retry_result["status"] == "completed",
        retry_result["status"],
    )

    record(
        results,
        "all workflow steps complete",
        retry_result["completed_steps"] == STEPS,
        (
            f"{len(retry_result['completed_steps'])}/"
            f"{len(STEPS)}"
        ),
    )

    record(
        results,
        "recovered failures are counted",
        retry_result["recovered_failures"] == 2,
        str(retry_result["recovered_failures"]),
    )

    fail_fast_result = run_reliable_workflow(
        query=query,
        run_id="eval_fail_fast",
        policy="fail_fast",
        max_retries=2,
        failure_plan={
            "retrieve_notes": [1],
        },
    )

    record(
        results,
        "fail-fast policy stops immediately",
        fail_fast_result["status"] == "failed",
        fail_fast_result["status"],
    )

    record(
        results,
        "fail-fast records one unrecovered failure",
        fail_fast_result["unrecovered_failures"] == 1,
        str(fail_fast_result["unrecovered_failures"]),
    )

    exhaustion_result = run_reliable_workflow(
        query=query,
        run_id="eval_retry_exhausted",
        policy="retry_then_resume",
        max_retries=1,
        failure_plan={
            "summarize_evidence": [1, 2],
        },
    )

    record(
        results,
        "retry exhaustion stops safely",
        exhaustion_result["status"] == "failed",
        exhaustion_result["status"],
    )

    first_run = run_reliable_workflow(
        query=query,
        run_id="eval_resume_case",
        policy="retry_then_resume",
        max_retries=0,
        failure_plan={
            "summarize_evidence": [1],
        },
    )

    resumed_run = run_reliable_workflow(
        query=query,
        run_id="eval_resume_case",
        policy="retry_then_resume",
        max_retries=2,
        failure_plan={},
        resume=True,
    )

    record(
        results,
        "checkpoint preserves completed steps",
        len(first_run["completed_steps"]) == 2,
        str(first_run["completed_steps"]),
    )

    record(
        results,
        "workflow resumes and completes",
        resumed_run["status"] == "completed",
        resumed_run["status"],
    )

    record(
        results,
        "resumed workflow does not repeat completed steps",
        resumed_run["attempts"].get("route_query") == 1
        and resumed_run["attempts"].get("retrieve_notes") == 1,
        str(resumed_run["attempts"]),
    )

    deterministic_a = run_reliable_workflow(
        query=query,
        run_id="eval_deterministic_a",
        policy="retry_then_resume",
        max_retries=1,
        failure_plan={"retrieve_notes": [1]},
    )

    deterministic_b = run_reliable_workflow(
        query=query,
        run_id="eval_deterministic_b",
        policy="retry_then_resume",
        max_retries=1,
        failure_plan={"retrieve_notes": [1]},
    )

    comparable_a = {
        key: deterministic_a[key]
        for key in [
            "status",
            "completed_steps",
            "attempts",
            "recovered_failures",
            "unrecovered_failures",
            "outputs",
        ]
    }

    comparable_b = {
        key: deterministic_b[key]
        for key in [
            "status",
            "completed_steps",
            "attempts",
            "recovered_failures",
            "unrecovered_failures",
            "outputs",
        ]
    }

    record(
        results,
        "simulated reliability evaluation is deterministic",
        comparable_a == comparable_b,
        f"equal={comparable_a == comparable_b}",
    )

    passed = sum(1 for item in results if item["passed"])
    total = len(results)

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

    lines = [
        "# Agent Reliability Evaluation",
        "",
        f"Passed: **{passed}/{total}**",
        "",
        "| Check | Result | Details |",
        "|---|---|---|",
    ]

    for item in results:
        label = "PASS" if item["passed"] else "FAIL"
        details = item["details"].replace("|", "/")
        lines.append(
            f"| {item['name']} | {label} | {details} |"
        )

    lines.extend(
        [
            "",
            "## Scope",
            "",
            (
                "This evaluation uses deterministic simulated tool failures. "
                "It demonstrates checkpointing, retries, safe stopping, "
                "resume behavior, and policy comparison without calling "
                "external services."
            ),
            "",
        ]
    )

    RESULTS_MD.write_text(
        "\n".join(lines),
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
