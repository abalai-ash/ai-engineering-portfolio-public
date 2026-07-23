from __future__ import annotations

import math
from typing import Any


def reference_position(
    time: float,
    frequency: float,
    damping: float,
) -> float:
    damped_frequency = frequency * math.sqrt(1.0 - damping**2)

    coefficient = damping * frequency / damped_frequency

    return math.exp(-damping * frequency * time) * (
        math.cos(damped_frequency * time)
        + coefficient * math.sin(damped_frequency * time)
    )


def validate_case(case: dict[str, Any]) -> None:
    if float(case["frequency"]) <= 0:
        raise ValueError("frequency must be positive.")

    if not 0 <= float(case["damping"]) < 1:
        raise ValueError("damping must be between zero and one.")

    if float(case["duration"]) <= 0:
        raise ValueError("duration must be positive.")

    if float(case["time_step"]) <= 0:
        raise ValueError("time_step must be positive.")


def simulate(case: dict[str, Any]) -> list[dict[str, float]]:
    validate_case(case)

    frequency = float(case["frequency"])
    damping = float(case["damping"])
    duration = float(case["duration"])
    step = float(case["time_step"])

    position = 1.0
    velocity = 0.0
    time = 0.0
    samples = []

    def derivatives(
        current_position: float,
        current_velocity: float,
    ) -> tuple[float, float]:
        acceleration = (
            -2.0 * damping * frequency * current_velocity
            - frequency**2 * current_position
        )
        return current_velocity, acceleration

    while time <= duration + 1e-12:
        samples.append(
            {
                "time": time,
                "position": position,
                "reference": reference_position(
                    time,
                    frequency,
                    damping,
                ),
            }
        )

        k1_x, k1_v = derivatives(position, velocity)
        k2_x, k2_v = derivatives(
            position + 0.5 * step * k1_x,
            velocity + 0.5 * step * k1_v,
        )
        k3_x, k3_v = derivatives(
            position + 0.5 * step * k2_x,
            velocity + 0.5 * step * k2_v,
        )
        k4_x, k4_v = derivatives(
            position + step * k3_x,
            velocity + step * k3_v,
        )

        position += step * (
            k1_x + 2.0 * k2_x + 2.0 * k3_x + k4_x
        ) / 6.0

        velocity += step * (
            k1_v + 2.0 * k2_v + 2.0 * k3_v + k4_v
        ) / 6.0

        time += step

    return samples


def evaluate_case(case: dict[str, Any]) -> dict[str, Any]:
    try:
        samples = simulate(case)
    except (KeyError, TypeError, ValueError) as error:
        return {
            "case_id": case.get("case_id", "unknown"),
            "status": "fail",
            "maximum_error": None,
            "reason": str(error),
        }

    maximum_error = max(
        abs(sample["position"] - sample["reference"])
        for sample in samples
    )

    if maximum_error <= float(case["pass_tolerance"]):
        status = "pass"
    elif maximum_error <= float(case["review_tolerance"]):
        status = "review"
    else:
        status = "fail"

    return {
        "case_id": case["case_id"],
        "status": status,
        "maximum_error": maximum_error,
        "reason": "Compared simulation output with a reference solution.",
    }
