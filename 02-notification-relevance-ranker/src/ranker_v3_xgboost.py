from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Any

import numpy as np
from xgboost import XGBRanker


FEATURE_NAMES = [
    "interest_match",
    "urgency",
    "freshness",
    "channel_match",
]

BASELINE_WEIGHTS = {
    "interest_match": 3.0,
    "urgency": 2.0,
    "freshness": 1.0,
    "channel_match": 1.0,
}


@dataclass(frozen=True)
class RankingExample:
    query_id: str
    notification_id: str
    features: dict[str, float]
    relevance: int


def baseline_score(features: dict[str, float]) -> float:
    return sum(
        features[name] * BASELINE_WEIGHTS[name]
        for name in FEATURE_NAMES
    )


def generate_synthetic_examples(
    *,
    seed: int = 42,
    query_count: int = 180,
    candidates_per_query: int = 6,
) -> list[RankingExample]:
    rng = random.Random(seed)
    examples: list[RankingExample] = []

    for query_index in range(query_count):
        preferred_channel = rng.choice([0.0, 1.0])
        user_interest_strength = rng.uniform(0.35, 1.0)
        query_id = f"q{query_index:04d}"

        raw_candidates: list[tuple[str, dict[str, float], float]] = []

        for candidate_index in range(candidates_per_query):
            features = {
                "interest_match": round(
                    rng.uniform(0.0, 1.0) * user_interest_strength,
                    6,
                ),
                "urgency": round(rng.uniform(0.0, 1.0), 6),
                "freshness": round(rng.uniform(0.0, 1.0), 6),
                "channel_match": float(
                    rng.choice([0.0, 1.0]) == preferred_channel
                ),
            }

            hidden_score = (
                3.4 * features["interest_match"]
                + 1.8 * features["urgency"]
                + 1.2 * features["freshness"]
                + 0.9 * features["channel_match"]
                + 1.1
                * features["interest_match"]
                * features["urgency"]
                - 0.8
                * max(
                    0.0,
                    features["urgency"] - features["freshness"] - 0.35,
                )
                + rng.uniform(-0.12, 0.12)
            )

            raw_candidates.append(
                (
                    f"{query_id}_n{candidate_index}",
                    features,
                    hidden_score,
                )
            )

        ordered = sorted(
            raw_candidates,
            key=lambda item: item[2],
            reverse=True,
        )

        relevance_by_id: dict[str, int] = {}
        for position, item in enumerate(ordered):
            notification_id = item[0]

            if position == 0:
                relevance = 3
            elif position == 1:
                relevance = 2
            elif position == 2:
                relevance = 1
            else:
                relevance = 0

            relevance_by_id[notification_id] = relevance

        for notification_id, features, _ in raw_candidates:
            examples.append(
                RankingExample(
                    query_id=query_id,
                    notification_id=notification_id,
                    features=features,
                    relevance=relevance_by_id[notification_id],
                )
            )

    return examples


def split_examples_by_query(
    examples: list[RankingExample],
    *,
    seed: int = 42,
    train_fraction: float = 0.75,
) -> tuple[list[RankingExample], list[RankingExample]]:
    query_ids = sorted({example.query_id for example in examples})

    rng = random.Random(seed)
    rng.shuffle(query_ids)

    split_index = int(len(query_ids) * train_fraction)

    train_ids = set(query_ids[:split_index])
    test_ids = set(query_ids[split_index:])

    train_examples = [
        example for example in examples if example.query_id in train_ids
    ]
    test_examples = [
        example for example in examples if example.query_id in test_ids
    ]

    return train_examples, test_examples


def examples_to_arrays(
    examples: list[RankingExample],
) -> tuple[np.ndarray, np.ndarray, list[int]]:
    ordered = sorted(
        examples,
        key=lambda item: (item.query_id, item.notification_id),
    )

    features = np.asarray(
        [
            [example.features[name] for name in FEATURE_NAMES]
            for example in ordered
        ],
        dtype=float,
    )

    labels = np.asarray(
        [example.relevance for example in ordered],
        dtype=float,
    )

    group_sizes: list[int] = []
    current_query: str | None = None
    current_size = 0

    for example in ordered:
        if current_query is None:
            current_query = example.query_id

        if example.query_id != current_query:
            group_sizes.append(current_size)
            current_query = example.query_id
            current_size = 0

        current_size += 1

    if current_size:
        group_sizes.append(current_size)

    return features, labels, group_sizes


def train_ranker(
    train_examples: list[RankingExample],
    *,
    seed: int = 42,
) -> XGBRanker:
    features, labels, groups = examples_to_arrays(train_examples)

    model = XGBRanker(
        objective="rank:pairwise",
        eval_metric="ndcg@3",
        n_estimators=90,
        max_depth=3,
        learning_rate=0.06,
        subsample=0.85,
        colsample_bytree=0.9,
        reg_lambda=1.0,
        random_state=seed,
        n_jobs=1,
    )

    model.fit(
        features,
        labels,
        group=groups,
        verbose=False,
    )

    return model


def predict_scores(
    model: XGBRanker,
    examples: list[RankingExample],
) -> dict[str, float]:
    ordered = sorted(
        examples,
        key=lambda item: (item.query_id, item.notification_id),
    )

    features = np.asarray(
        [
            [example.features[name] for name in FEATURE_NAMES]
            for example in ordered
        ],
        dtype=float,
    )

    predictions = model.predict(features)

    return {
        example.notification_id: float(score)
        for example, score in zip(ordered, predictions, strict=True)
    }


def feature_importance(model: XGBRanker) -> dict[str, float]:
    values = model.feature_importances_

    return {
        name: round(float(value), 6)
        for name, value in zip(FEATURE_NAMES, values, strict=True)
    }


def group_by_query(
    examples: list[RankingExample],
) -> dict[str, list[RankingExample]]:
    grouped: dict[str, list[RankingExample]] = {}

    for example in examples:
        grouped.setdefault(example.query_id, []).append(example)

    return grouped


def rank_query(
    examples: list[RankingExample],
    scores: dict[str, float],
) -> list[RankingExample]:
    return sorted(
        examples,
        key=lambda item: (
            scores[item.notification_id],
            item.notification_id,
        ),
        reverse=True,
    )


def evaluate_rankings(
    examples: list[RankingExample],
    scores: dict[str, float],
) -> dict[str, float]:
    grouped = group_by_query(examples)

    reciprocal_ranks: list[float] = []
    ndcg_values: list[float] = []
    top_one_values: list[float] = []

    for query_examples in grouped.values():
        ranked = rank_query(query_examples, scores)

        ideal = sorted(
            query_examples,
            key=lambda item: item.relevance,
            reverse=True,
        )

        best_relevance = ideal[0].relevance
        top_one_values.append(
            float(ranked[0].relevance == best_relevance)
        )

        reciprocal_rank = 0.0
        for position, example in enumerate(ranked, start=1):
            if example.relevance == best_relevance:
                reciprocal_rank = 1.0 / position
                break

        reciprocal_ranks.append(reciprocal_rank)

        def dcg(items: list[RankingExample], limit: int = 3) -> float:
            total = 0.0

            for index, example in enumerate(items[:limit], start=1):
                gain = (2.0 ** example.relevance) - 1.0
                discount = np.log2(index + 1.0)
                total += gain / discount

            return total

        ideal_dcg = dcg(ideal)
        actual_dcg = dcg(ranked)

        ndcg_values.append(
            actual_dcg / ideal_dcg if ideal_dcg else 0.0
        )

    return {
        "top1_accuracy": round(float(np.mean(top_one_values)), 6),
        "mrr": round(float(np.mean(reciprocal_ranks)), 6),
        "ndcg_at_3": round(float(np.mean(ndcg_values)), 6),
    }


def baseline_scores(
    examples: list[RankingExample],
    *,
    disabled_feature: str | None = None,
) -> dict[str, float]:
    scores: dict[str, float] = {}

    for example in examples:
        features = dict(example.features)

        if disabled_feature is not None:
            features[disabled_feature] = 0.0

        scores[example.notification_id] = baseline_score(features)

    return scores


def model_scores_with_ablation(
    model: XGBRanker,
    examples: list[RankingExample],
    *,
    disabled_feature: str,
) -> dict[str, float]:
    changed_examples: list[RankingExample] = []

    for example in examples:
        features = dict(example.features)
        features[disabled_feature] = 0.0

        changed_examples.append(
            RankingExample(
                query_id=example.query_id,
                notification_id=example.notification_id,
                features=features,
                relevance=example.relevance,
            )
        )

    return predict_scores(model, changed_examples)
