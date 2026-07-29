from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sparse_linear_algebra_v1 import SparseMatrixCOO


@dataclass(frozen=True)
class InverseProblem:
    sensitivity: SparseMatrixCOO
    measurements: list[float]
    regularization: float
    step_size: float
    iterations: int


def transpose_matvec(
    matrix: SparseMatrixCOO,
    vector: list[float],
) -> list[float]:
    if len(vector) != matrix.rows:
        raise ValueError(
            "Vector length must match the matrix row count."
        )

    result = [0.0 for _ in range(matrix.cols)]

    for row, column, value in matrix.entries:
        result[column] += value * vector[row]

    return result


def build_problem() -> InverseProblem:
    sensitivity = SparseMatrixCOO(
        rows=5,
        cols=4,
        entries=[
            (0, 0, 1.00),
            (0, 1, 0.25),
            (1, 0, 0.35),
            (1, 1, 0.85),
            (1, 2, 0.20),
            (2, 1, 0.30),
            (2, 2, 1.00),
            (2, 3, 0.20),
            (3, 2, 0.25),
            (3, 3, 0.95),
            (4, 0, 0.15),
            (4, 3, 0.80),
        ],
    )

    known_values = [0.0, 0.15, 1.0, 0.10]
    measurements = sensitivity.matvec(known_values)

    return InverseProblem(
        sensitivity=sensitivity,
        measurements=measurements,
        regularization=0.08,
        step_size=0.24,
        iterations=180,
    )


def objective(
    problem: InverseProblem,
    estimate: list[float],
) -> float:
    predicted = problem.sensitivity.matvec(estimate)

    residuals = [
        predicted_value - measured_value
        for predicted_value, measured_value in zip(
            predicted,
            problem.measurements,
        )
    ]

    residual_term = 0.5 * sum(
        value * value for value in residuals
    )

    regularization_term = (
        0.5
        * problem.regularization
        * sum(value * value for value in estimate)
    )

    return residual_term + regularization_term


def solve(problem: InverseProblem) -> dict[str, Any]:
    estimate = [
        0.0 for _ in range(problem.sensitivity.cols)
    ]

    history: list[float] = []

    for _ in range(problem.iterations):
        predicted = problem.sensitivity.matvec(estimate)

        residuals = [
            predicted_value - measured_value
            for predicted_value, measured_value in zip(
                predicted,
                problem.measurements,
            )
        ]

        gradient = transpose_matvec(
            problem.sensitivity,
            residuals,
        )

        gradient = [
            value
            + problem.regularization * estimate[index]
            for index, value in enumerate(gradient)
        ]

        estimate = [
            max(
                0.0,
                value
                - problem.step_size * gradient[index],
            )
            for index, value in enumerate(estimate)
        ]

        history.append(
            objective(problem, estimate)
        )

    predicted = problem.sensitivity.matvec(estimate)

    residuals = [
        predicted_value - measured_value
        for predicted_value, measured_value in zip(
            predicted,
            problem.measurements,
        )
    ]

    residual_norm = sum(
        value * value for value in residuals
    ) ** 0.5

    strongest_cell = max(
        range(len(estimate)),
        key=lambda index: estimate[index],
    )

    return {
        "estimate": estimate,
        "predicted": predicted,
        "measurements": problem.measurements,
        "residual_norm": residual_norm,
        "strongest_cell": strongest_cell,
        "history": history,
        "objective_decreased": history[-1] < history[0],
    }


def main() -> None:
    problem = build_problem()
    result = solve(problem)

    values = [
        round(value, 4)
        for value in result["estimate"]
    ]

    print("Synthetic Subsurface Inverse Problem")
    print("------------------------------------")
    print(
        f"Matrix shape: "
        f"{problem.sensitivity.rows} x "
        f"{problem.sensitivity.cols}"
    )
    print(
        f"Stored entries: "
        f"{len(problem.sensitivity.entries)}"
    )
    print(f"Estimated cell values: {values}")
    print(
        f"Strongest estimated cell: "
        f"cell_{result['strongest_cell']}"
    )
    print(
        f"Residual norm: "
        f"{result['residual_norm']:.6f}"
    )
    print(
        f"Objective decreased: "
        f"{result['objective_decreased']}"
    )


if __name__ == "__main__":
    main()
