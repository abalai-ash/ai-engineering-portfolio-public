from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
RESULTS_JSON = PROJECT_ROOT / "eval" / "performance_rollout_eval_results_v4.json"
RESULTS_MD = PROJECT_ROOT / "eval" / "performance_rollout_eval_results_v4.md"

sys.path.insert(0, str(SRC_DIR))

from performance_rollout_v4 import (  # noqa: E402
    BenchmarkResult,
    ServiceObjectives,
    baseline_predict,
    build_messages,
    candidate_predict,
    demonstrate_routing,
    evaluate_rollout,
    select_model,
)


def record(
    results: list[dict[str, Any]],
    name: str,
    passed: bool,
    details: str,
) -> None:
    results.append(
        {
            "check": name,
            "passed": passed,
            "details": details,
        }
    )


def sample_result(
    *,
    p95_latency_ms: float,
    throughput_rps: float,
    error_rate: float,
) -> BenchmarkResult:
    return BenchmarkResult(
        request_count=1000,
        warmup_count=20,
        mean_latency_ms=p95_latency_ms / 2,
        median_latency_ms=p95_latency_ms / 2,
        p95_latency_ms=p95_latency_ms,
        p99_latency_ms=p95_latency_ms * 1.1,
        throughput_rps=throughput_rps,
        error_rate=error_rate,
    )


def main() -> None:
    results: list[dict[str, Any]] = []

    messages = build_messages(25)
    predictions = [baseline_predict(message) for message in messages]
    valid_labels = all(
        prediction.get("label") in {"low", "medium", "high"}
        for prediction in predictions
    )
    record(
        results,
        "baseline predictions use valid labels",
        valid_labels,
        f"labels={sorted({item['label'] for item in predictions})}",
    )

    candidate_predictions = [
        candidate_predict(message)
        for message in messages
    ]
    candidate_valid = all(
        prediction.get("label") in {"low", "medium", "high"}
        for prediction in candidate_predictions
    )
    record(
        results,
        "candidate predictions use valid labels",
        candidate_valid,
        f"labels={sorted({item['label'] for item in candidate_predictions})}",
    )

    first_routing = demonstrate_routing(
        request_count=100,
        candidate_percentage=20,
    )
    second_routing = demonstrate_routing(
        request_count=100,
        candidate_percentage=20,
    )
    record(
        results,
        "canary routing is deterministic",
        first_routing == second_routing,
        f"first={first_routing} second={second_routing}",
    )

    disabled_routes = {
        select_model(
            request_id=f"request-{index}",
            candidate_percentage=100,
            feature_enabled=False,
        )
        for index in range(20)
    }
    record(
        results,
        "disabled feature flag routes to baseline",
        disabled_routes == {"baseline"},
        f"routes={sorted(disabled_routes)}",
    )

    baseline = sample_result(
        p95_latency_ms=1.0,
        throughput_rps=1000.0,
        error_rate=0.0,
    )
    healthy_candidate = sample_result(
        p95_latency_ms=1.1,
        throughput_rps=950.0,
        error_rate=0.0,
    )

    healthy_decision = evaluate_rollout(
        baseline=baseline,
        candidate=healthy_candidate,
        objectives=ServiceObjectives(),
    )
    record(
        results,
        "healthy candidate continues rollout",
        healthy_decision.decision == "continue_rollout",
        f"decision={healthy_decision.decision}",
    )

    slow_candidate = sample_result(
        p95_latency_ms=8.0,
        throughput_rps=450.0,
        error_rate=0.0,
    )
    slow_decision = evaluate_rollout(
        baseline=baseline,
        candidate=slow_candidate,
        objectives=ServiceObjectives(),
    )
    record(
        results,
        "latency or throughput regression holds rollout",
        slow_decision.decision == "hold",
        (
            f"decision={slow_decision.decision} "
            f"reasons={slow_decision.reasons}"
        ),
    )

    failing_candidate = sample_result(
        p95_latency_ms=1.1,
        throughput_rps=950.0,
        error_rate=0.08,
    )
    failing_decision = evaluate_rollout(
        baseline=baseline,
        candidate=failing_candidate,
        objectives=ServiceObjectives(),
    )
    record(
        results,
        "high error rate triggers rollback",
        failing_decision.decision == "rollback",
        (
            f"decision={failing_decision.decision} "
            f"reasons={failing_decision.reasons}"
        ),
    )

    invalid_percentage_rejected = False
    try:
        select_model(
            request_id="request-invalid",
            candidate_percentage=101,
        )
    except ValueError:
        invalid_percentage_rejected = True

    record(
        results,
        "invalid rollout percentage is rejected",
        invalid_percentage_rejected,
        f"rejected={invalid_percentage_rejected}",
    )

    passed_count = sum(1 for result in results if result["passed"])
    total_count = len(results)

    payload = {
        "passed": passed_count,
        "total": total_count,
        "results": results,
        "scope": (
            "This deterministic local evaluation uses synthetic metrics and "
            "requests. It checks routing, feature flags, service objectives, "
            "and rollout decisions rather than production-scale performance."
        ),
    }

    RESULTS_JSON.write_text(
        json.dumps(payload, indent=2) + "\n",
        encoding="utf-8",
    )

    report_lines = [
        "# Performance and Rollout Evaluation Results",
        "",
        f"Passed: **{passed_count}/{total_count}**",
        "",
        "| Check | Result | Details |",
        "|---|---|---|",
    ]

    for result in results:
        label = "PASS" if result["passed"] else "FAIL"
        report_lines.append(
            f"| {result['check']} | {label} | {result['details']} |"
        )

    report_lines.extend(
        [
            "",
            "## Scope",
            "",
            (
                "This is a deterministic local evaluation using synthetic "
                "requests and metrics. It demonstrates basic performance "
                "checks, feature-flag routing, canary rollout decisions, and "
                "rollback behavior. It is not a production load test."
            ),
            "",
        ]
    )

    RESULTS_MD.write_text(
        "\n".join(report_lines),
        encoding="utf-8",
    )

    for result in results:
        label = "PASS" if result["passed"] else "FAIL"
        print(f"{label}: {result['check']} - {result['details']}")

    print()
    print(f"Evaluation complete: {passed_count}/{total_count} passed")
    print(f"Wrote {RESULTS_JSON}")
    print(f"Wrote {RESULTS_MD}")

    if passed_count != total_count:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
