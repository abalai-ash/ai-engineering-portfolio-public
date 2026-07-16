from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ReadinessThresholds:
    max_p95_latency_ms: float = 300.0
    max_error_rate: float = 0.05
    max_timeout_rate: float = 0.03
    max_dependency_failure_rate: float = 0.05


def percentile(values: list[float], percentile_value: float) -> float:
    if not values:
        return 0.0

    ordered = sorted(values)
    index = int(round((len(ordered) - 1) * percentile_value))
    return float(ordered[index])


def validate_thresholds(thresholds: ReadinessThresholds) -> list[str]:
    problems: list[str] = []

    if thresholds.max_p95_latency_ms <= 0:
        problems.append("max_p95_latency_ms must be greater than zero")

    rate_fields = {
        "max_error_rate": thresholds.max_error_rate,
        "max_timeout_rate": thresholds.max_timeout_rate,
        "max_dependency_failure_rate": thresholds.max_dependency_failure_rate,
    }

    for name, value in rate_fields.items():
        if not 0.0 <= value <= 1.0:
            problems.append(f"{name} must be between zero and one")

    return problems


def evaluate_operational_readiness(
    requests: list[dict[str, Any]],
    thresholds: ReadinessThresholds | None = None,
) -> dict[str, Any]:
    active_thresholds = thresholds or ReadinessThresholds()
    configuration_errors = validate_thresholds(active_thresholds)

    if configuration_errors:
        return {
            "status": "invalid_configuration",
            "liveness": False,
            "readiness": False,
            "recommendation": "block_deployment",
            "reasons": configuration_errors,
            "metrics": {},
        }

    if not requests:
        return {
            "status": "insufficient_data",
            "liveness": True,
            "readiness": False,
            "recommendation": "hold_deployment",
            "reasons": ["No request observations were provided."],
            "metrics": {
                "request_count": 0,
                "p95_latency_ms": 0.0,
                "error_rate": 0.0,
                "timeout_rate": 0.0,
                "dependency_failure_rate": 0.0,
            },
        }

    latencies = [float(item.get("latency_ms", 0.0)) for item in requests]
    request_count = len(requests)

    errors = sum(
        1
        for item in requests
        if int(item.get("status_code", 500)) >= 500
    )
    timeouts = sum(
        1
        for item in requests
        if bool(item.get("timed_out", False))
    )
    dependency_failures = sum(
        1
        for item in requests
        if not bool(item.get("dependency_ok", True))
    )

    metrics = {
        "request_count": request_count,
        "p95_latency_ms": round(percentile(latencies, 0.95), 2),
        "error_rate": round(errors / request_count, 4),
        "timeout_rate": round(timeouts / request_count, 4),
        "dependency_failure_rate": round(
            dependency_failures / request_count,
            4,
        ),
    }

    reasons: list[str] = []

    if metrics["p95_latency_ms"] > active_thresholds.max_p95_latency_ms:
        reasons.append("P95 latency exceeded the deployment threshold.")

    if metrics["error_rate"] > active_thresholds.max_error_rate:
        reasons.append("Service error rate exceeded the deployment threshold.")

    if metrics["timeout_rate"] > active_thresholds.max_timeout_rate:
        reasons.append("Timeout rate exceeded the deployment threshold.")

    if (
        metrics["dependency_failure_rate"]
        > active_thresholds.max_dependency_failure_rate
    ):
        reasons.append(
            "Dependency failure rate exceeded the deployment threshold."
        )

    readiness = not reasons
    severe_failure = (
        metrics["error_rate"] > active_thresholds.max_error_rate * 2
        or metrics["timeout_rate"] > active_thresholds.max_timeout_rate * 2
        or metrics["dependency_failure_rate"]
        > active_thresholds.max_dependency_failure_rate * 2
    )

    if readiness:
        recommendation = "continue_deployment"
        status = "ready"
    elif severe_failure:
        recommendation = "rollback"
        status = "unhealthy"
    else:
        recommendation = "hold_deployment"
        status = "degraded"

    return {
        "status": status,
        "liveness": True,
        "readiness": readiness,
        "recommendation": recommendation,
        "reasons": reasons,
        "metrics": metrics,
        "thresholds": {
            "max_p95_latency_ms": active_thresholds.max_p95_latency_ms,
            "max_error_rate": active_thresholds.max_error_rate,
            "max_timeout_rate": active_thresholds.max_timeout_rate,
            "max_dependency_failure_rate": (
                active_thresholds.max_dependency_failure_rate
            ),
        },
    }


def build_scenario(name: str) -> list[dict[str, Any]]:
    scenarios: dict[str, list[dict[str, Any]]] = {
        "healthy": [
            {
                "latency_ms": 85 + index * 3,
                "status_code": 200,
                "timed_out": False,
                "dependency_ok": True,
            }
            for index in range(20)
        ],
        "dependency_degradation": [
            {
                "latency_ms": 130 + index * 5,
                "status_code": 503 if index in {3, 7, 11, 15} else 200,
                "timed_out": False,
                "dependency_ok": index not in {3, 7, 11, 15},
            }
            for index in range(20)
        ],
        "timeout_spike": [
            {
                "latency_ms": 900 if index in {2, 5, 8, 11} else 120,
                "status_code": 504 if index in {2, 5, 8, 11} else 200,
                "timed_out": index in {2, 5, 8, 11},
                "dependency_ok": True,
            }
            for index in range(20)
        ],
        "moderate_latency": [
            {
                "latency_ms": 340 if index in {16, 17, 18, 19} else 170,
                "status_code": 200,
                "timed_out": False,
                "dependency_ok": True,
            }
            for index in range(20)
        ],
    }

    if name not in scenarios:
        raise ValueError(f"Unknown scenario: {name}")

    return scenarios[name]


def main() -> None:
    for scenario_name in (
        "healthy",
        "moderate_latency",
        "dependency_degradation",
        "timeout_spike",
    ):
        report = evaluate_operational_readiness(
            build_scenario(scenario_name)
        )
        print(
            f"{scenario_name}: "
            f"status={report['status']} "
            f"recommendation={report['recommendation']} "
            f"p95={report['metrics']['p95_latency_ms']}ms"
        )


if __name__ == "__main__":
    main()
