from __future__ import annotations

from typing import Any


Record = dict[str, Any]


def validate_weights(
    weights: dict[str, float],
    tolerance: float = 1e-9,
) -> bool:
    """Return whether weights are nonnegative and sum to one."""
    if not weights:
        return False

    if any(float(value) < 0 for value in weights.values()):
        return False

    return abs(
        sum(float(value) for value in weights.values()) - 1.0
    ) <= tolerance


def score_alternative(
    alternative: Record,
    weights: dict[str, float],
) -> float:
    """Return the weighted score for one architecture alternative."""
    scores = alternative.get("scores", {})

    return sum(
        float(scores.get(criterion, 0))
        * float(weight)
        for criterion, weight in weights.items()
    )


def rank_alternatives(
    alternatives: list[Record],
    weights: dict[str, float],
) -> list[Record]:
    """Return alternatives ordered from highest to lowest score."""
    if not validate_weights(weights):
        raise ValueError(
            "Review weights must be nonnegative and sum to one."
        )

    ranked = [
        {
            "id": str(alternative["id"]),
            "name": str(alternative["name"]),
            "weighted_score": round(
                score_alternative(
                    alternative,
                    weights,
                ),
                4,
            ),
        }
        for alternative in alternatives
    ]

    return sorted(
        ranked,
        key=lambda record: (
            -record["weighted_score"],
            record["id"],
        ),
    )


def sensitivity_review(
    alternatives: list[Record],
    weight_sets: dict[str, dict[str, float]],
) -> dict[str, str]:
    """Return the leading alternative for each weight set."""
    leaders: dict[str, str] = {}

    for name, weights in weight_sets.items():
        ranking = rank_alternatives(
            alternatives,
            weights,
        )
        leaders[name] = ranking[0]["id"]

    return leaders
