"""Compare current model metrics with a saved baseline."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


DEFAULT_LIMITS = {
    "accuracy_drop": 0.05,
    "precision_drop": 0.06,
    "recall_drop": 0.08,
    "latency_increase_ratio": 0.40,
    "max_error_rate": 0.02,
    "prediction_rate_change": 0.12,
}


def load_metrics(path: Path) -> dict[str, Any]:
    """Load one metrics file and check required fields."""

    with path.open("r", encoding="utf-8") as file:
        metrics = json.load(file)

    required = {
        "model_version",
        "accuracy",
        "precision",
        "recall",
        "p95_latency_ms",
        "error_rate",
        "positive_prediction_rate",
    }

    missing = required.difference(metrics)

    if missing:
        missing_text = ", ".join(sorted(missing))
        raise ValueError(f"Missing required metrics: {missing_text}")

    return metrics


def compare_metrics(
    baseline: dict[str, Any],
    current: dict[str, Any],
    limits: dict[str, float] | None = None,
) -> list[dict[str, Any]]:
    """Return alerts for changes beyond the monitoring limits."""

    thresholds = DEFAULT_LIMITS if limits is None else limits
    alerts: list[dict[str, Any]] = []

    quality_checks = [
        ("accuracy", thresholds["accuracy_drop"]),
        ("precision", thresholds["precision_drop"]),
        ("recall", thresholds["recall_drop"]),
    ]

    for metric_name, allowed_drop in quality_checks:
        actual_drop = baseline[metric_name] - current[metric_name]

        if actual_drop > allowed_drop:
            alerts.append(
                {
                    "metric": metric_name,
                    "level": "high",
                    "message": (
                        f"{metric_name} dropped by {actual_drop:.3f}; "
                        f"allowed drop is {allowed_drop:.3f}"
                    ),
                }
            )

    baseline_latency = baseline["p95_latency_ms"]

    if baseline_latency <= 0:
        raise ValueError("Baseline latency must be greater than zero")

    latency_change = (
        current["p95_latency_ms"] - baseline_latency
    ) / baseline_latency

    if latency_change > thresholds["latency_increase_ratio"]:
        alerts.append(
            {
                "metric": "p95_latency_ms",
                "level": "medium",
                "message": (
                    f"p95 latency increased by {latency_change:.1%}"
                ),
            }
        )

    if current["error_rate"] > thresholds["max_error_rate"]:
        alerts.append(
            {
                "metric": "error_rate",
                "level": "high",
                "message": (
                    f"error rate is {current['error_rate']:.3f}; "
                    f"limit is {thresholds['max_error_rate']:.3f}"
                ),
            }
        )

    prediction_change = abs(
        current["positive_prediction_rate"]
        - baseline["positive_prediction_rate"]
    )

    if prediction_change > thresholds["prediction_rate_change"]:
        alerts.append(
            {
                "metric": "positive_prediction_rate",
                "level": "medium",
                "message": (
                    "positive prediction rate changed by "
                    f"{prediction_change:.3f}"
                ),
            }
        )

    return alerts


def choose_action(alerts: list[dict[str, Any]]) -> dict[str, Any]:
    """Turn monitoring alerts into a simple incident decision."""

    high_count = sum(
        alert["level"] == "high"
        for alert in alerts
    )

    medium_count = sum(
        alert["level"] == "medium"
        for alert in alerts
    )

    if high_count >= 2:
        action = "rollback"
    elif high_count == 1 or medium_count >= 2:
        action = "hold_and_review"
    elif alerts:
        action = "continue_with_monitoring"
    else:
        action = "continue"

    return {
        "action": action,
        "high_alerts": high_count,
        "medium_alerts": medium_count,
        "alert_count": len(alerts),
    }
