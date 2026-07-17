from __future__ import annotations

import csv
import json
import math
import statistics
import sys
from pathlib import Path
from time import perf_counter

BASE_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = BASE_DIR / "src"
DATA_DIR = BASE_DIR / "data"
EVAL_DIR = BASE_DIR / "eval"

RESULTS_JSON = EVAL_DIR / "eval_results_v2.json"
RESULTS_MD = EVAL_DIR / "eval_results_v2.md"

sys.path.append(str(SRC_DIR))

from ranker_v1 import load_csv  # noqa: E402
from ranker_v2 import rank_baseline, rank_notifications_v2  # noqa: E402


def load_judgments(path: Path) -> dict[str, dict[str, int]]:
    judgments: dict[str, dict[str, int]] = {}

    with path.open(encoding="utf-8") as file:
        for row in csv.DictReader(file):
            judgments.setdefault(row["user_id"], {})[row["notification_id"]] = int(
                row["relevance"]
            )

    return judgments


def reciprocal_rank(
    ranked_ids: list[str],
    relevance: dict[str, int],
) -> float:
    for position, notification_id in enumerate(ranked_ids, start=1):
        if relevance.get(notification_id, 0) > 0:
            return 1.0 / position
    return 0.0


def dcg_at_k(
    ranked_ids: list[str],
    relevance: dict[str, int],
    k: int,
) -> float:
    score = 0.0

    for index, notification_id in enumerate(ranked_ids[:k]):
        grade = relevance.get(notification_id, 0)
        gain = (2**grade) - 1
        score += gain / math.log2(index + 2)

    return score


def ndcg_at_k(
    ranked_ids: list[str],
    relevance: dict[str, int],
    k: int,
) -> float:
    actual = dcg_at_k(ranked_ids, relevance, k)

    ideal_ids = [
        notification_id
        for notification_id, _ in sorted(
            relevance.items(),
            key=lambda item: (-item[1], item[0]),
        )
    ]
    ideal = dcg_at_k(ideal_ids, relevance, k)

    return actual / ideal if ideal else 0.0


def evaluate_ranker(
    users: list[dict[str, str]],
    notifications: list[dict[str, str]],
    judgments: dict[str, dict[str, int]],
    mode: str,
    disabled_features: set[str] | None = None,
) -> dict[str, object]:
    rows: list[dict[str, object]] = []

    for user in users:
        user_id = user["user_id"]
        relevance = judgments[user_id]

        if mode == "baseline":
            ranked = rank_baseline(notifications)
        else:
            ranked = rank_notifications_v2(
                user,
                notifications,
                disabled_features=disabled_features,
            )

        ranked_ids = [item["notification_id"] for item in ranked]
        expected_top = max(
            relevance,
            key=lambda notification_id: (
                relevance[notification_id],
                notification_id,
            ),
        )
        actual_top = ranked_ids[0]

        rows.append(
            {
                "user_id": user_id,
                "expected_top": expected_top,
                "actual_top": actual_top,
                "hit_at_1": int(actual_top == expected_top),
                "reciprocal_rank": reciprocal_rank(ranked_ids, relevance),
                "ndcg_at_3": ndcg_at_k(ranked_ids, relevance, 3),
                "ranked_ids": ranked_ids,
            }
        )

    return {
        "hit_at_1": sum(int(row["hit_at_1"]) for row in rows) / len(rows),
        "mrr": sum(float(row["reciprocal_rank"]) for row in rows) / len(rows),
        "ndcg_at_3": sum(float(row["ndcg_at_3"]) for row in rows) / len(rows),
        "rows": rows,
    }


def measure_latency(
    users: list[dict[str, str]],
    notifications: list[dict[str, str]],
    repetitions: int = 500,
) -> dict[str, float]:
    samples_ms: list[float] = []

    for _ in range(repetitions):
        start = perf_counter()

        for user in users:
            rank_notifications_v2(user, notifications)

        elapsed_ms = (perf_counter() - start) * 1000
        samples_ms.append(elapsed_ms)

    ordered = sorted(samples_ms)
    p95_index = min(len(ordered) - 1, math.ceil(0.95 * len(ordered)) - 1)

    return {
        "repetitions": repetitions,
        "median_ms": statistics.median(samples_ms),
        "p95_ms": ordered[p95_index],
    }


def main() -> None:
    users = load_csv(DATA_DIR / "users.csv")
    notifications = load_csv(DATA_DIR / "notifications.csv")
    judgments = load_judgments(EVAL_DIR / "judgments_v2.csv")

    full = evaluate_ranker(
        users,
        notifications,
        judgments,
        mode="full",
    )
    baseline = evaluate_ranker(
        users,
        notifications,
        judgments,
        mode="baseline",
    )

    ablations: dict[str, dict[str, object]] = {}
    for feature in ("interest", "urgency", "freshness", "channel"):
        ablations[feature] = evaluate_ranker(
            users,
            notifications,
            judgments,
            mode="full",
            disabled_features={feature},
        )

    first_run = [
        item["notification_id"]
        for item in rank_notifications_v2(users[0], notifications)
    ]
    second_run = [
        item["notification_id"]
        for item in rank_notifications_v2(users[0], notifications)
    ]
    deterministic = first_run == second_run

    latency = measure_latency(users, notifications)

    passed_checks = {
        "full_hit_at_1": float(full["hit_at_1"]) == 1.0,
        "full_beats_baseline": float(full["hit_at_1"])
        > float(baseline["hit_at_1"]),
        "full_mrr": float(full["mrr"]) == 1.0,
        "deterministic": deterministic,
        "latency_recorded": float(latency["p95_ms"]) >= 0.0,
    }

    report = {
        "full_model": full,
        "baseline": baseline,
        "ablations": ablations,
        "latency": latency,
        "checks": passed_checks,
        "scope": (
            "Synthetic deterministic ranking evaluation. "
            "This does not use real user behavior or production traffic."
        ),
    }

    RESULTS_JSON.write_text(
        json.dumps(report, indent=2),
        encoding="utf-8",
    )

    lines = [
        "# Notification Ranking Version 2 Evaluation",
        "",
        f"Passed: {sum(passed_checks.values())}/{len(passed_checks)} checks",
        "",
        "## Main metrics",
        "",
        "| System | Hit@1 | MRR | NDCG@3 |",
        "|---|---:|---:|---:|",
        (
            f"| Version 2 ranker | {float(full['hit_at_1']):.3f} | "
            f"{float(full['mrr']):.3f} | {float(full['ndcg_at_3']):.3f} |"
        ),
        (
            f"| Non-personalized baseline | {float(baseline['hit_at_1']):.3f} | "
            f"{float(baseline['mrr']):.3f} | "
            f"{float(baseline['ndcg_at_3']):.3f} |"
        ),
        "",
        "## Feature ablation",
        "",
        "| Removed feature | Hit@1 | MRR | NDCG@3 |",
        "|---|---:|---:|---:|",
    ]

    for feature, result in ablations.items():
        lines.append(
            f"| {feature} | {float(result['hit_at_1']):.3f} | "
            f"{float(result['mrr']):.3f} | "
            f"{float(result['ndcg_at_3']):.3f} |"
        )

    lines.extend(
        [
            "",
            "## Reliability checks",
            "",
            f"- Deterministic output: `{deterministic}`",
            f"- Median local evaluation latency: `{latency['median_ms']:.4f} ms`",
            f"- P95 local evaluation latency: `{latency['p95_ms']:.4f} ms`",
            "",
            "## Error analysis",
            "",
        ]
    )

    errors = [
        row
        for row in full["rows"]
        if not bool(row["hit_at_1"])
    ]

    if errors:
        for row in errors:
            lines.append(
                f"- `{row['user_id']}` expected `{row['expected_top']}` "
                f"but ranked `{row['actual_top']}` first."
            )
    else:
        lines.append(
            "- No top-rank errors occurred in the small synthetic evaluation set."
        )

    lines.extend(
        [
            "",
            "## Scope",
            "",
            "This is a small deterministic portfolio evaluation using synthetic data.",
            "It demonstrates ranking metrics, baseline comparison, feature ablation,",
            "latency measurement, explainable signals, and reproducible evaluation.",
            "It is not a production notification system or a model trained on real users.",
            "",
        ]
    )

    RESULTS_MD.write_text("\n".join(lines), encoding="utf-8")

    for name, passed in passed_checks.items():
        print(f"{'PASS' if passed else 'FAIL'}: {name}")

    print()
    print(f"Full Hit@1: {float(full['hit_at_1']):.3f}")
    print(f"Baseline Hit@1: {float(baseline['hit_at_1']):.3f}")
    print(f"Full MRR: {float(full['mrr']):.3f}")
    print(f"Full NDCG@3: {float(full['ndcg_at_3']):.3f}")
    print(f"P95 latency: {latency['p95_ms']:.4f} ms")
    print(f"Wrote {RESULTS_JSON}")
    print(f"Wrote {RESULTS_MD}")

    if not all(passed_checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
