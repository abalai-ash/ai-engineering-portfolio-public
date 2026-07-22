from __future__ import annotations

from dataclasses import dataclass
from statistics import mean
from typing import Any
import random


@dataclass(frozen=True)
class MeasurementPlan:
    case_id: str
    target: float
    warning_limit: float
    failure_limit: float
    sample_count: int
    noise: float = 0.0
    drift: float = 0.0
    interrupted_at: int | None = None


def collect(
    plan: MeasurementPlan,
    *,
    seed: int,
) -> dict[str, Any]:
    rng = random.Random(seed)
    readings: list[float] = []
    errors: list[str] = []

    for index in range(plan.sample_count):
        if plan.interrupted_at == index:
            errors.append(
                f"Measurement interrupted at sample {index}"
            )
            continue

        value = (
            plan.target
            + plan.drift * index
            + rng.gauss(0.0, plan.noise)
        )

        readings.append(round(value, 6))

    return {
        "readings": readings,
        "errors": errors,
        "requested_samples": plan.sample_count,
        "collected_samples": len(readings),
    }


def classify(
    value: float,
    *,
    target: float,
    warning_limit: float,
    failure_limit: float,
) -> str:
    deviation = abs(value - target)

    if deviation > failure_limit:
        return "fail"

    if deviation > warning_limit:
        return "warning"

    return "pass"


def evaluate(
    plan: MeasurementPlan,
    *,
    seed: int,
) -> dict[str, Any]:
    collection = collect(
        plan,
        seed=seed,
    )

    readings = collection["readings"]
    errors = collection["errors"]

    statuses = [
        classify(
            value,
            target=plan.target,
            warning_limit=plan.warning_limit,
            failure_limit=plan.failure_limit,
        )
        for value in readings
    ]

    drift_value = (
        round(readings[-1] - readings[0], 6)
        if len(readings) >= 2
        else 0.0
    )

    drift_detected = (
        abs(drift_value) > plan.warning_limit
    )

    if errors or "fail" in statuses:
        status = "fail"
    elif "warning" in statuses or drift_detected:
        status = "review"
    else:
        status = "pass"

    if errors:
        reason = "The measurement did not complete cleanly."
    elif status == "fail":
        reason = "A reading exceeded the failure limit."
    elif status == "review":
        reason = "The readings showed drift or crossed a warning limit."
    else:
        reason = "All readings remained within the accepted range."

    return {
        "case_id": plan.case_id,
        "status": status,
        "reason": reason,
        "requested_samples": collection["requested_samples"],
        "collected_samples": collection["collected_samples"],
        "error_count": len(errors),
        "mean": (
            round(mean(readings), 6)
            if readings
            else None
        ),
        "drift": drift_value,
        "drift_detected": drift_detected,
    }
