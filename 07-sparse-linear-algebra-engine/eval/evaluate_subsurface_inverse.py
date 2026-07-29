from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(
    0,
    str(PROJECT_ROOT / "src"),
)

from synthetic_subsurface_inverse import (
    build_problem,
    solve,
)


def main() -> int:
    problem = build_problem()

    first_result = solve(problem)
    second_result = solve(problem)

    stored_entries = len(
        problem.sensitivity.entries
    )

    possible_entries = (
        problem.sensitivity.rows
        * problem.sensitivity.cols
    )

    checks = [
        {
            "name": "matrix is sparse",
            "passed": stored_entries < possible_entries,
            "detail": (
                f"{stored_entries} stored entries "
                f"out of {possible_entries}"
            ),
        },
        {
            "name": "strongest cell is identified",
            "passed": (
                first_result["strongest_cell"] == 2
            ),
            "detail": (
                "strongest cell = "
                f"{first_result['strongest_cell']}"
            ),
        },
        {
            "name": "residual remains small",
            "passed": (
                first_result["residual_norm"] < 0.12
            ),
            "detail": (
                "residual norm = "
                f"{first_result['residual_norm']:.6f}"
            ),
        },
        {
            "name": "objective decreases",
            "passed": (
                first_result["objective_decreased"]
            ),
            "detail": (
                "start = "
                f"{first_result['history'][0]:.6f}, "
                "end = "
                f"{first_result['history'][-1]:.6f}"
            ),
        },
        {
            "name": "result is repeatable",
            "passed": first_result == second_result,
            "detail": (
                "two runs returned the same result"
            ),
        },
    ]

    passed = sum(
        check["passed"]
        for check in checks
    )

    total = len(checks)

    lines = [
        "# Subsurface Inverse Evaluation",
        "",
        f"Passed {passed}/{total} checks.",
        "",
        "| Check | Result | Detail |",
        "|---|---|---|",
    ]

    for check in checks:
        label = (
            "PASS"
            if check["passed"]
            else "FAIL"
        )

        lines.append(
            f"| {check['name']} | "
            f"{label} | "
            f"{check['detail']} |"
        )

    estimated_values = [
        round(value, 4)
        for value in first_result["estimate"]
    ]

    lines.extend(
        [
            "",
            "## Result",
            "",
            (
                "- Estimated cell values: "
                f"{estimated_values}"
            ),
            (
                "- Strongest estimated cell: "
                f"cell_{first_result['strongest_cell']}"
            ),
            (
                "- Residual norm: "
                f"{first_result['residual_norm']:.6f}"
            ),
            "",
            "## Scope",
            "",
            (
                "This is a small synthetic linear inverse "
                "problem. It is not an Electrical Resistivity "
                "Tomography model, a field survey, or a "
                "professional geophysical inversion workflow."
            ),
            "",
        ]
    )

    output_path = (
        PROJECT_ROOT
        / "eval"
        / "subsurface_inverse_results.md"
    )

    output_path.write_text(
        "\n".join(lines),
        encoding="utf-8",
    )

    print(
        "Evaluation complete: "
        f"{passed}/{total} checks passed"
    )
    print(f"Wrote {output_path}")

    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
