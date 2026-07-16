from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from workflow_v4 import run_agent_v4


BASE_DIR = Path(__file__).resolve().parents[1]
CHECKPOINT_DIR = BASE_DIR / "runtime" / "checkpoints"
LOG_DIR = BASE_DIR / "runtime" / "logs"

STEPS = [
    "route_query",
    "retrieve_notes",
    "summarize_evidence",
    "build_checklist",
    "draft_update",
]


@dataclass
class WorkflowState:
    run_id: str
    query: str
    policy: str
    status: str = "pending"
    current_step: str | None = None
    completed_steps: list[str] = field(default_factory=list)
    attempts: dict[str, int] = field(default_factory=dict)
    outputs: dict[str, Any] = field(default_factory=dict)
    recovered_failures: int = 0
    unrecovered_failures: int = 0


def checkpoint_path(run_id: str) -> Path:
    return CHECKPOINT_DIR / f"{run_id}.json"


def log_path(run_id: str) -> Path:
    return LOG_DIR / f"{run_id}.jsonl"


def save_checkpoint(state: WorkflowState) -> None:
    CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)

    checkpoint_path(state.run_id).write_text(
        json.dumps(asdict(state), indent=2),
        encoding="utf-8",
    )


def load_checkpoint(run_id: str) -> WorkflowState | None:
    path = checkpoint_path(run_id)

    if not path.exists():
        return None

    data = json.loads(path.read_text(encoding="utf-8"))
    return WorkflowState(**data)


def write_event(
    run_id: str,
    event: str,
    step: str | None = None,
    details: dict[str, Any] | None = None,
) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    record = {
        "event": event,
        "step": step,
        "details": details or {},
    }

    with log_path(run_id).open("a", encoding="utf-8") as file:
        file.write(json.dumps(record) + "\n")


def should_fail(
    step: str,
    attempt: int,
    failure_plan: dict[str, list[int]],
) -> bool:
    return attempt in failure_plan.get(step, [])


def execute_step(
    step: str,
    state: WorkflowState,
) -> Any:
    query = state.query

    if step == "route_query":
        routed = run_agent_v4(query)

        return {
            "route": routed.get("route"),
            "confidence": routed.get("router_v4", {}).get(
                "confidence",
                routed.get("confidence"),
            ),
            "reason": routed.get("router_v4", {}).get(
                "reason",
                routed.get("reason"),
            ),
            "human_review_required": routed.get(
                "human_review_required",
                True,
            ),
        }

    if step == "retrieve_notes":
        routed = run_agent_v4(query)

        return {
            "source_snippets": routed.get("source_snippets", []),
            "private_risk": routed.get("private_risk", False),
        }

    if step == "summarize_evidence":
        routed = run_agent_v4(query)

        return {
            "summary": routed.get(
                "summary",
                routed.get("answer", ""),
            ),
            "grounded": bool(routed.get("source_snippets", [])),
        }

    if step == "build_checklist":
        routed = run_agent_v4(query)

        checklist = routed.get("checklist", [])

        if isinstance(checklist, str):
            checklist = [
                line.strip("- ").strip()
                for line in checklist.splitlines()
                if line.strip()
            ]

        return {
            "checklist": checklist,
            "human_review_required": routed.get(
                "human_review_required",
                True,
            ),
        }

    if step == "draft_update":
        routed = run_agent_v4(query)

        return {
            "draft_update": routed.get(
                "draft_update",
                routed.get("answer", ""),
            ),
            "route": routed.get("route"),
        }

    raise ValueError(f"Unknown workflow step: {step}")


def run_reliable_workflow(
    query: str,
    run_id: str,
    policy: str = "retry_then_resume",
    max_retries: int = 2,
    failure_plan: dict[str, list[int]] | None = None,
    resume: bool = False,
) -> dict[str, Any]:
    if policy not in {"fail_fast", "retry_then_resume"}:
        raise ValueError(
            "policy must be 'fail_fast' or 'retry_then_resume'"
        )

    failure_plan = failure_plan or {}

    existing = load_checkpoint(run_id) if resume else None

    if existing is not None:
        state = existing
        write_event(
            run_id,
            "workflow_resumed",
            details={
                "completed_steps": state.completed_steps,
            },
        )
    else:
        state = WorkflowState(
            run_id=run_id,
            query=query,
            policy=policy,
        )

        checkpoint_path(run_id).unlink(missing_ok=True)
        log_path(run_id).unlink(missing_ok=True)

        write_event(
            run_id,
            "workflow_started",
            details={
                "policy": policy,
                "max_retries": max_retries,
            },
        )

    state.status = "running"
    save_checkpoint(state)

    for step in STEPS:
        if step in state.completed_steps:
            write_event(
                run_id,
                "step_skipped_from_checkpoint",
                step=step,
            )
            continue

        state.current_step = step
        save_checkpoint(state)

        allowed_attempts = (
            1 if policy == "fail_fast" else max_retries + 1
        )

        step_completed = False

        for _ in range(allowed_attempts):
            attempt = state.attempts.get(step, 0) + 1
            state.attempts[step] = attempt
            save_checkpoint(state)

            write_event(
                run_id,
                "step_started",
                step=step,
                details={"attempt": attempt},
            )

            if should_fail(step, attempt, failure_plan):
                write_event(
                    run_id,
                    "step_failed",
                    step=step,
                    details={
                        "attempt": attempt,
                        "reason": "simulated tool failure",
                    },
                )

                if attempt < allowed_attempts:
                    state.recovered_failures += 1
                    write_event(
                        run_id,
                        "retry_scheduled",
                        step=step,
                        details={
                            "next_attempt": attempt + 1,
                        },
                    )
                    continue

                state.unrecovered_failures += 1
                state.status = "failed"
                save_checkpoint(state)

                write_event(
                    run_id,
                    "workflow_stopped",
                    step=step,
                    details={
                        "reason": "retry limit reached",
                    },
                )

                return build_result(state)

            output = execute_step(step, state)
            state.outputs[step] = output
            state.completed_steps.append(step)
            step_completed = True
            save_checkpoint(state)

            write_event(
                run_id,
                "step_completed",
                step=step,
                details={"attempt": attempt},
            )
            break

        if not step_completed:
            return build_result(state)

    state.current_step = None
    state.status = "completed"
    save_checkpoint(state)

    write_event(
        run_id,
        "workflow_completed",
        details={
            "completed_steps": len(state.completed_steps),
        },
    )

    return build_result(state)


def build_result(state: WorkflowState) -> dict[str, Any]:
    total_attempts = sum(state.attempts.values())

    return {
        "run_id": state.run_id,
        "query": state.query,
        "policy": state.policy,
        "status": state.status,
        "completed_steps": state.completed_steps,
        "attempts": state.attempts,
        "total_attempts": total_attempts,
        "recovered_failures": state.recovered_failures,
        "unrecovered_failures": state.unrecovered_failures,
        "outputs": state.outputs,
        "checkpoint": str(checkpoint_path(state.run_id)),
        "event_log": str(log_path(state.run_id)),
    }


def main() -> None:
    result = run_reliable_workflow(
        query="Summarize agentic workflow tools and human review.",
        run_id="demo_retry_resume",
        policy="retry_then_resume",
        max_retries=2,
        failure_plan={
            "retrieve_notes": [1],
            "build_checklist": [1],
        },
    )

    print("Reliable Agentic Research Workflow")
    print("----------------------------------")
    print(f"Status: {result['status']}")
    print(f"Policy: {result['policy']}")
    print(
        "Completed steps: "
        f"{len(result['completed_steps'])}/{len(STEPS)}"
    )
    print(f"Total attempts: {result['total_attempts']}")
    print(
        "Recovered failures: "
        f"{result['recovered_failures']}"
    )
    print(
        "Unrecovered failures: "
        f"{result['unrecovered_failures']}"
    )
    print(f"Checkpoint: {result['checkpoint']}")
    print(f"Event log: {result['event_log']}")


if __name__ == "__main__":
    main()
