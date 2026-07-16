from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = BASE_DIR / "src"
RESULTS_JSON = BASE_DIR / "eval" / "operational_readiness_results.json"
RESULTS_MD = BASE_DIR / "eval" / "operational_readiness_results.md"

sys.path.append(str(SRC_DIR))

from operational_readiness import (  # noqa: E402
    ReadinessThresholds,
    build_scenario,
    evaluate_operational_readiness,
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


def main() -> None:
    results: list[dict[str, Any]] = []

    healthy = evaluate_operational_readiness(build_scenario("healthy"))
    record(
        results,
        "healthy service remains ready",
        healthy["readiness"] is True
        and healthy["recommendation"] == "continue_deployment",
        (
            f"status={healthy['status']} "
            f"recommendation={healthy['recommendation']}"
        ),
    )

    moderate = evaluate_operational_readiness(
        build_scenario("moderate_latency")
    )
    record(
        results,
        "moderate latency holds deployment",
        moderate["readiness"] is False
        and moderate["recommendation"] == "hold_deployment",
        (
            f"p95={moderate['metrics']['p95_latency_ms']} "
            f"recommendation={moderate['recommendation']}"
        ),
    )

    dependency = evaluate_operational_readiness(
        build_scenario("dependency_degradation")
    )
    record(
        results,
        "dependency degradation recommends rollback",
        dependency["recommendation"] == "rollback",
        (
            "dependency_failure_rate="
            f"{dependency['metrics']['dependency_failure_rate']} "
            f"recommendation={dependency['recommendation']}"
        ),
    )

    timeout = evaluate_operational_readiness(
        build_scenario("timeout_spike")
    )
    record(
        results,
        "timeout spike recommends rollback",
        timeout["recommendation"] == "rollback",
        (
            f"timeout_rate={timeout['metrics']['timeout_rate']} "
            f"recommendation={timeout['recommendation']}"
        ),
    )

    no_data = evaluate_operational_readiness([])
    record(
        results,
        "missing observations hold deployment",
        no_data["status"] == "insufficient_data"
        and no_data["recommendation"] == "hold_deployment",
        (
            f"status={no_data['status']} "
            f"recommendation={no_data['recommendation']}"
        ),
    )

    invalid = evaluate_operational_readiness(
        build_scenario("healthy"),
        ReadinessThresholds(max_error_rate=1.5),
    )
    record(
        results,
        "invalid thresholds block deployment",
        invalid["status"] == "invalid_configuration"
        and invalid["recommendation"] == "block_deployment",
        (
            f"status={invalid['status']} "
            f"recommendation={invalid['recommendation']}"
        ),
    )

    repeated_first = evaluate_operational_readiness(
        build_scenario("healthy")
    )
    repeated_second = evaluate_operational_readiness(
        build_scenario("healthy")
    )
    record(
        results,
        "evaluation is deterministic",
        repeated_first == repeated_second,
        f"equal={repeated_first == repeated_second}",
    )

    record(
        results,
        "liveness and readiness remain distinct",
        dependency["liveness"] is True
        and dependency["readiness"] is False,
        (
            f"liveness={dependency['liveness']} "
            f"readiness={dependency['readiness']}"
        ),
    )

    passed_count = sum(1 for item in results if item["passed"])
    total = len(results)

    RESULTS_JSON.write_text(
        json.dumps(
            {
                "passed": passed_count,
                "total": total,
                "results": results,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    lines = [
        "# Cloud ML Operational Readiness Evaluation",
        "",
        f"Passed: {passed_count}/{total}",
        "",
        "| Check | Result | Details |",
        "|---|---|---|",
    ]

    for item in results:
        result_label = "PASS" if item["passed"] else "FAIL"
        lines.append(
            f"| {item['check']} | {result_label} | {item['details']} |"
        )

    lines.extend(
        [
            "",
            "## Scope",
            "",
            (
                "This is a deterministic local evaluation using synthetic "
                "service observations. It demonstrates latency, error, "
                "timeout, dependency-health, readiness, and rollback logic "
                "without calling a cloud provider or external service."
            ),
            "",
        ]
    )

    RESULTS_MD.write_text(
        "\n".join(lines),
        encoding="utf-8",
    )

    for item in results:
        label = "PASS" if item["passed"] else "FAIL"
        print(f"{label}: {item['check']} - {item['details']}")

    print()
    print(f"Evaluation complete: {passed_count}/{total} passed")
    print(f"Wrote {RESULTS_JSON}")
    print(f"Wrote {RESULTS_MD}")

    if passed_count != total:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
