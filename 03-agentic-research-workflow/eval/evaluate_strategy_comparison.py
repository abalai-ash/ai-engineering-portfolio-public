from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = BASE_DIR / "src"
RESULTS_JSON = BASE_DIR / "eval" / "strategy_comparison_results.json"
RESULTS_MD = BASE_DIR / "eval" / "strategy_comparison_results.md"

sys.path.insert(0, str(SRC_DIR))

from reliable_workflow import STEPS, run_reliable_workflow


SCENARIOS = [
    {"name": "no_failure", "failure_plan": {}},
    {"name": "early_transient", "failure_plan": {"retrieve_notes": [1]}},
    {
        "name": "two_transient_failures",
        "failure_plan": {"retrieve_notes": [1], "build_checklist": [1]},
    },
    {"name": "late_transient", "failure_plan": {"draft_update": [1]}},
    {
        "name": "retry_exhausted",
        "failure_plan": {"summarize_evidence": [1, 2]},
    },
]


def classify_failure(result: dict[str, Any]) -> str:
    if result["status"] == "completed" and result["recovered_failures"] == 0:
        return "none"
    if result["status"] == "completed":
        return "recovered_transient"
    if result["policy"] == "fail_fast":
        return "stopped_on_failure"
    return "retry_exhausted"


def main() -> None:
    query = "Summarize agentic workflow tools and human review."
    rows: list[dict[str, Any]] = []

    for scenario in SCENARIOS:
        for policy in ["fail_fast", "retry_then_resume"]:
            result = run_reliable_workflow(
                query=query,
                run_id=f"benchmark_{scenario["name"]}_{policy}",
                policy=policy,
                max_retries=1,
                failure_plan=scenario["failure_plan"],
            )

            rows.append(
                {
                    "scenario": scenario["name"],
                    "policy": policy,
                    "status": result["status"],
                    "completed_steps": len(result["completed_steps"]),
                    "completion_rate": round(
                        len(result["completed_steps"]) / len(STEPS), 3
                    ),
                    "total_attempts": result["total_attempts"],
                    "recovered_failures": result["recovered_failures"],
                    "unrecovered_failures": result["unrecovered_failures"],
                    "failure_category": classify_failure(result),
                }
            )

    first_run = run_reliable_workflow(
        query=query,
        run_id="benchmark_checkpoint_resume",
        policy="retry_then_resume",
        max_retries=0,
        failure_plan={"summarize_evidence": [1]},
    )

    resumed_run = run_reliable_workflow(
        query=query,
        run_id="benchmark_checkpoint_resume",
        policy="retry_then_resume",
        max_retries=1,
        failure_plan={},
        resume=True,
    )

    work_avoided = len(first_run["completed_steps"])

    policy_summary = {}
    for policy in ["fail_fast", "retry_then_resume"]:
        policy_rows = [row for row in rows if row["policy"] == policy]
        completed = sum(row["status"] == "completed" for row in policy_rows)
        policy_summary[policy] = {
            "completed": completed,
            "total": len(policy_rows),
            "completion_rate": round(completed / len(policy_rows), 3),
            "average_attempts": round(
                sum(row["total_attempts"] for row in policy_rows)
                / len(policy_rows),
                2,
            ),
        }

    summary = {
        "scenario_count": len(SCENARIOS),
        "workflow_steps": len(STEPS),
        "policy_summary": policy_summary,
        "checkpoint_resume": {
            "initial_completed_steps": first_run["completed_steps"],
            "resumed_status": resumed_run["status"],
            "steps_not_repeated": work_avoided,
        },
        "results": rows,
    }

    RESULTS_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    lines = [
        "# Workflow Strategy Comparison",
        "",
        "This benchmark runs five repeatable failure scenarios using two error-handling policies.",
        "",
        "## Policy summary",
        "",
        "| Policy | Completed | Completion rate | Average attempts |",
        "|---|---:|---:|---:|",
    ]

    for policy, values in policy_summary.items():
        lines.append(
            f"| {policy} | {values["completed"]}/{values["total"]} | "
            f"{values["completion_rate"]:.0%} | {values["average_attempts"]} |"
        )

    lines.extend(
        [
            "",
            "## Scenario results",
            "",
            "| Scenario | Policy | Status | Steps | Attempts | Failure category |",
            "|---|---|---|---:|---:|---|",
        ]
    )

    for row in rows:
        lines.append(
            f"| {row["scenario"]} | {row["policy"]} | {row["status"]} | "
            f"{row["completed_steps"]}/{len(STEPS)} | {row["total_attempts"]} | "
            f"{row["failure_category"]} |"
        )

    lines.extend(
        [
            "",
            "## Resume test",
            "",
            f"The first run completed {work_avoided} steps before stopping. "
            f"The resumed run finished with status `{resumed_run["status"]}` without running those completed steps again.",
            "",
            "## Scope",
            "",
            "All failures are repeatable simulations. This benchmark does not call an external model or estimate token cost.",
            "",
        ]
    )

    RESULTS_MD.write_text("\n".join(lines), encoding="utf-8")

    expected_fail_fast = 1
    expected_retry = 4

    passed = (
        policy_summary["fail_fast"]["completed"] == expected_fail_fast
        and policy_summary["retry_then_resume"]["completed"] == expected_retry
        and resumed_run["status"] == "completed"
        and work_avoided == 2
    )

    print(
        "fail_fast completion: "
        f"{policy_summary["fail_fast"]["completed"]}/{len(SCENARIOS)}"
    )
    print(
        "retry_then_resume completion: "
        f"{policy_summary["retry_then_resume"]["completed"]}/{len(SCENARIOS)}"
    )
    print(f"checkpointed steps not repeated: {work_avoided}")
    print(f"Wrote {RESULTS_JSON}")
    print(f"Wrote {RESULTS_MD}")

    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
