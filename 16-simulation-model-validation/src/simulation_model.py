from __future__ import annotations

import math
from typing import Any


def validate_case(case: dict[str, Any]) -> None:
    required = {
        "case_id",
        "omega",
        "zeta",
        "initial_position",
        "initial_velocity",
        "duration",
        "time_step",
        "pass_tolerance",
        "review_tolerance",
    }

    missing = required - case.keys()

    if missing:
        raise ValueError(
            "Missing fields: " + ", ".join(sorted(missing))
        )

    if float(case["omega"]) <= 0:
        raise ValueError("omega must be positive.")

    if float(case["duration"]) <= 0:
        raise ValueError("duration must be positive.")

    if float(case["time_step"]) <= 0:
        raise ValueError("time_step must be positive.")

    if float(case["zeta"]) < 0 or float(case["zeta"]) >= 1:
        raise ValueError("This model requires 0 <= zeta < 1.")


def reference_position(
    time: float,
    omega: float,
    zeta: float,
    initial_position: float,
    initial_velocity: float,
) -> float:
    damped_frequency = omega * math.sqrt(1.0 - zeta**2)

    coefficient = (
        initial_velocity
        + zeta * omega * initial_position
    ) / damped_frequency

    return math.exp(-zeta * omega * time) * (
        initial_position * math.cos(damped_frequency * time)
        + coefficient * math.sin(damped_frequency * time)
    )


def simulate(case: dict[str, Any]) -> list[dict[str, float]]:
    validate_case(case)

    omega = float(case["omega"])
    zeta = float(case["zeta"])
    time_step = float(case["time_step"])
    duration = float(case["duration"])

    position = float(case["initial_position"])
    velocity = float(case["initial_velocity"])
    time = 0.0

    samples = []

    while time <= duration + 1e-12:
        samples.append(
            {
                "time": time,
                "position": position,
                "reference": reference_position(
                    time,
                    omega,
                    zeta,
                    float(case["initial_position"]),
                    float(case["initial_velocity"]),
                ),
            }
        )

        def derivatives(
            current_position: float,
            current_velocity: float,
        ) -> tuple[float, float]:
            acceleration = (
                -2.0 * zeta * omega * current_velocity
                - omega**2 * current_position
            )
            return current_velocity, acceleration

        k1_position, k1_velocity = derivatives(
            position,
            velocity,
        )
        k2_position, k2_velocity = derivatives(
            position + 0.5 * time_step * k1_position,
            velocity + 0.5 * time_step * k1_velocity,
        )
        k3_position, k3_velocity = derivatives(
            position + 0.5 * time_step * k2_position,
            velocity + 0.5 * time_step * k2_velocity,
        )
        k4_position, k4_velocity = derivatives(
            position + time_step * k3_position,
            velocity + time_step * k3_velocity,
        )

        position += time_step * (
            k1_position
            + 2.0 * k2_position
            + 2.0 * k3_position
            + k4_position
        ) / 6.0

        velocity += time_step * (
            k1_velocity
            + 2.0 * k2_velocity
            + 2.0 * k3_velocity
            + k4_velocity
        ) / 6.0

        time += time_step

        if not math.isfinite(position) or abs(position) > 1e6:
            break

    return samples


def evaluate_case(case: dict[str, Any]) -> dict[str, Any]:
    try:
        samples = simulate(case)
    except ValueError as error:
        return {
            "case_id": case.get("case_id", "unknown"),
            "status": "fail",
            "maximum_error": None,
            "sample_count": 0,
            "reason": str(error),
        }

    errors = [
        abs(sample["position"] - sample["reference"])
        for sample in samples
    ]

    maximum_error = max(errors)

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
        "sample_count": len(samples),
        "reason": "Compared numerical output with the reference solution.",
    }
