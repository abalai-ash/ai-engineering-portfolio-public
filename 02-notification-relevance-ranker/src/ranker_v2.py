from __future__ import annotations

from typing import Any

from ranker_v1 import split_tags


FEATURE_WEIGHTS = {
    "interest": 3.0,
    "urgency": 2.0,
    "freshness": 1.0,
    "channel": 1.0,
}


def feature_values(user: dict[str, str], notification: dict[str, str]) -> dict[str, float]:
    user_interests = split_tags(user.get("interests", ""))
    notification_tags = split_tags(notification.get("tags", ""))

    matching_tags = user_interests & notification_tags

    return {
        "interest": float(len(matching_tags)),
        "urgency": float(notification.get("urgency", 0)),
        "freshness": float(notification.get("freshness", 0)),
        "channel": float(
            user.get("preferred_channel") == notification.get("channel")
        ),
    }


def score_breakdown(
    user: dict[str, str],
    notification: dict[str, str],
    disabled_features: set[str] | None = None,
) -> dict[str, Any]:
    disabled = disabled_features or set()
    values = feature_values(user, notification)

    contributions = {
        name: 0.0 if name in disabled else values[name] * FEATURE_WEIGHTS[name]
        for name in FEATURE_WEIGHTS
    }

    matching_tags = sorted(
        split_tags(user.get("interests", ""))
        & split_tags(notification.get("tags", ""))
    )

    return {
        "notification_id": notification["notification_id"],
        "matching_tags": matching_tags,
        "feature_values": values,
        "contributions": contributions,
        "total_score": round(sum(contributions.values()), 4),
    }


def baseline_score(notification: dict[str, str]) -> float:
    urgency = float(notification.get("urgency", 0))
    freshness = float(notification.get("freshness", 0))
    return (2.0 * urgency) + freshness


def rank_notifications_v2(
    user: dict[str, str],
    notifications: list[dict[str, str]],
    disabled_features: set[str] | None = None,
) -> list[dict[str, Any]]:
    ranked: list[dict[str, Any]] = []

    for notification in notifications:
        breakdown = score_breakdown(user, notification, disabled_features)
        ranked.append(
            {
                **notification,
                **breakdown,
            }
        )

    ranked.sort(
        key=lambda item: (
            -float(item["total_score"]),
            item["notification_id"],
        )
    )
    return ranked


def rank_baseline(
    notifications: list[dict[str, str]],
) -> list[dict[str, Any]]:
    ranked = [
        {
            **notification,
            "total_score": baseline_score(notification),
        }
        for notification in notifications
    ]

    ranked.sort(
        key=lambda item: (
            -float(item["total_score"]),
            item["notification_id"],
        )
    )
    return ranked
