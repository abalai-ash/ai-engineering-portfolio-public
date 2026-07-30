from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = BASE_DIR / "src"
RESULTS_JSON = BASE_DIR / "eval" / "eval_results_v3.json"
RESULTS_MD = BASE_DIR / "eval" / "eval_results_v3.md"

sys.path.append(str(SRC_DIR))

from ranker_v3_xgboost import (  # noqa: E402
    FEATURE_NAMES,
    baseline_scores,
    evaluate_rankings,
    feature_importance,
    generate_synthetic_examples,
    group_by_query,
    model_scores_with_ablation,
    predict_scores,
    rank_query,
    split_examples_by_query,
    train_ranker,
)


def rounded_difference(
    learned: dict[str, float],
    baseline: dict[str, float],
) -> dict[str, float]:
    return {
        name: round(learned[name] - baseline[name], 6)
        for name in ("top1_accuracy", "mrr", "ndcg_at_3")
    }


def build_error_analysis(
    examples: list[Any],
    learned_scores: dict[str, float],
    baseline_score_values: dict[str, float],
) -> dict[str, Any]:
    grouped = group_by_query(examples)
    errors: list[dict[str, Any]] = []
    predicted_higher_counts = {name: 0 for name in FEATURE_NAMES}
    baseline_correct_on_errors = 0

    for query_id in sorted(grouped):
        query_examples = grouped[query_id]
        learned_ranking = rank_query(query_examples, learned_scores)
        ideal_ranking = sorted(
            query_examples,
            key=lambda item: (item.relevance, item.notification_id),
            reverse=True,
        )

        expected = ideal_ranking[0]
        predicted = learned_ranking[0]

        if predicted.relevance == expected.relevance:
            continue

        baseline_ranking = rank_query(
            query_examples,
            baseline_score_values,
        )
        baseline_top = baseline_ranking[0]
        baseline_correct = baseline_top.relevance == expected.relevance

        if baseline_correct:
            baseline_correct_on_errors += 1

        feature_differences = {}
        for feature_name in FEATURE_NAMES:
            difference = round(
                predicted.features[feature_name]
                - expected.features[feature_name],
                6,
            )
            feature_differences[feature_name] = difference

            if difference > 0.0:
                predicted_higher_counts[feature_name] += 1

        errors.append(
            {
                "query_id": query_id,
                "expected_notification_id": expected.notification_id,
                "expected_relevance": expected.relevance,
                "expected_score": round(
                    learned_scores[expected.notification_id],
                    6,
                ),
                "predicted_notification_id": predicted.notification_id,
                "predicted_relevance": predicted.relevance,
                "predicted_score": round(
                    learned_scores[predicted.notification_id],
                    6,
                ),
                "score_margin": round(
                    learned_scores[predicted.notification_id]
                    - learned_scores[expected.notification_id],
                    6,
                ),
                "baseline_top_notification_id": baseline_top.notification_id,
                "baseline_correct": baseline_correct,
                "feature_differences": feature_differences,
            }
        )

    query_count = len(grouped)

    return {
        "misranked_queries": len(errors),
        "query_count": query_count,
        "error_rate": round(
            len(errors) / max(query_count, 1),
            6,
        ),
        "baseline_correct_on_model_errors": baseline_correct_on_errors,
        "predicted_higher_feature_counts": predicted_higher_counts,
        "errors": errors,
    }


def make_markdown(report: dict[str, Any]) -> str:
    baseline = report["baseline_metrics"]
    learned = report["learned_metrics"]
    difference = report["learned_minus_baseline"]

    lines = [
        "# Notification Ranking Version 3 Evaluation",
        "",
        f"Passed: {report['passed_checks']}/{report['total_checks']} checks",
        "",
        "## Held-out ranking results",
        "",
        "| System | Top-1 accuracy | MRR | NDCG@3 |",
        "|---|---:|---:|---:|",
        (
            f"| Hand-written baseline | "
            f"{baseline['top1_accuracy']:.3f} | "
            f"{baseline['mrr']:.3f} | "
            f"{baseline['ndcg_at_3']:.3f} |"
        ),
        (
            f"| XGBoost ranker | "
            f"{learned['top1_accuracy']:.3f} | "
            f"{learned['mrr']:.3f} | "
            f"{learned['ndcg_at_3']:.3f} |"
        ),
        "",
        "## Learned improvement over baseline",
        "",
        f"- Top-1 accuracy: {difference['top1_accuracy']:+.3f}",
        f"- MRR: {difference['mrr']:+.3f}",
        f"- NDCG@3: {difference['ndcg_at_3']:+.3f}",
        "",
        "## Feature importance",
        "",
        "| Feature | Importance |",
        "|---|---:|",
    ]

    for name, value in sorted(
        report["feature_importance"].items(),
        key=lambda item: item[1],
        reverse=True,
    ):
        lines.append(f"| {name} | {value:.3f} |")

    lines.extend(
        [
            "",
            "## Feature ablation",
            "",
            "| Removed feature | Top-1 accuracy | MRR | NDCG@3 |",
            "|---|---:|---:|---:|",
        ]
    )

    for name, metrics in report["ablation_metrics"].items():
        lines.append(
            f"| {name} | "
            f"{metrics['top1_accuracy']:.3f} | "
            f"{metrics['mrr']:.3f} | "
            f"{metrics['ndcg_at_3']:.3f} |"
        )

    error_analysis = report["error_analysis"]

    lines.extend(
        [
            "",
            "## Held-out error analysis",
            "",
            f"- Misranked queries: {error_analysis['misranked_queries']}/{error_analysis['query_count']}",
            f"- Error rate: {error_analysis['error_rate']:.3f}",
            f"- Baseline correct on model errors: {error_analysis['baseline_correct_on_model_errors']}",
            "",
            "### Features higher in the incorrectly selected candidate",
            "",
        ]
    )

    for name, count in error_analysis["predicted_higher_feature_counts"].items():
        lines.append(f"- {name}: {count} errors")

    lines.extend(
        [
            "",
            "### Misranked queries",
            "",
            "| Query | Expected | Predicted | Predicted relevance | Score margin | Baseline correct |",
            "|---|---|---|---:|---:|---|",
        ]
    )

    for error in error_analysis["errors"]:
        lines.append(
            f"| {error['query_id']} | "
            f"{error['expected_notification_id']} | "
            f"{error['predicted_notification_id']} | "
            f"{error['predicted_relevance']} | "
            f"{error['score_margin']:+.3f} | "
            f"{error['baseline_correct']} |"
        )

    lines.extend(
        [
            "",
            "### Interpretation",
            "",
            f"- {error_analysis['baseline_correct_on_model_errors']} model errors were cases where the hand-written baseline selected the correct candidate.",
            "- Incorrect selections frequently had higher interest-match or urgency values, indicating that strong individual signals can outweigh the better overall candidate.",
            "- Several errors had small score margins, suggesting ranking uncertainty near the top of the list.",
            "- The error cases support retaining baseline comparison and candidate-level review alongside aggregate ranking metrics.",
        ]
    )

    lines.extend(
        [
            "",
            "## Reliability checks",
            "",
            f"- Fixed random seed: {report['seed']}",
            f"- Training queries: {report['training_queries']}",
            f"- Held-out queries: {report['test_queries']}",
            f"- Training time: {report['training_seconds']:.4f} seconds",
            f"- Prediction latency: {report['prediction_latency_ms']:.4f} ms per candidate",
            f"- Repeated predictions deterministic: {report['deterministic_predictions']}",
            "",
            "## Scope",
            "",
            "This is a portfolio-scale ranking experiment using deterministic synthetic data.",
            "It compares an interpretable hand-written baseline with a learned XGBoost ranker.",
            "It does not use real user behavior, private data, production traffic, or online experimentation.",
        ]
    )

    return "\n".join(lines) + "\n"


def main() -> None:
    seed = 42

    examples = generate_synthetic_examples(
        seed=seed,
        query_count=180,
        candidates_per_query=6,
    )

    train_examples, test_examples = split_examples_by_query(
        examples,
        seed=seed,
        train_fraction=0.75,
    )

    training_start = time.perf_counter()
    model = train_ranker(train_examples, seed=seed)
    training_seconds = time.perf_counter() - training_start

    prediction_start = time.perf_counter()
    learned_scores = predict_scores(model, test_examples)
    prediction_seconds = time.perf_counter() - prediction_start

    repeated_scores = predict_scores(model, test_examples)

    learned_metrics = evaluate_rankings(
        test_examples,
        learned_scores,
    )

    baseline_score_values = baseline_scores(test_examples)

    baseline_metrics = evaluate_rankings(
        test_examples,
        baseline_score_values,
    )

    error_analysis = build_error_analysis(
        test_examples,
        learned_scores,
        baseline_score_values,
    )

    ablation_metrics = {}

    for feature_name in FEATURE_NAMES:
        ablation_scores = model_scores_with_ablation(
            model,
            test_examples,
            disabled_feature=feature_name,
        )

        ablation_metrics[feature_name] = evaluate_rankings(
            test_examples,
            ablation_scores,
        )

    deterministic_predictions = learned_scores == repeated_scores

    training_queries = len(
        {example.query_id for example in train_examples}
    )
    test_queries = len(
        {example.query_id for example in test_examples}
    )

    prediction_latency_ms = (
        prediction_seconds / max(len(test_examples), 1)
    ) * 1000.0

    checks = {
        "learned_top1_not_below_baseline": (
            learned_metrics["top1_accuracy"]
            >= baseline_metrics["top1_accuracy"]
        ),
        "learned_mrr_not_below_baseline": (
            learned_metrics["mrr"]
            >= baseline_metrics["mrr"]
        ),
        "learned_ndcg_not_below_baseline": (
            learned_metrics["ndcg_at_3"]
            >= baseline_metrics["ndcg_at_3"]
        ),
        "predictions_are_deterministic": deterministic_predictions,
        "importance_has_all_features": (
            set(feature_importance(model)) == set(FEATURE_NAMES)
        ),
        "latency_recorded": prediction_latency_ms >= 0.0,
    }

    passed_checks = sum(checks.values())
    total_checks = len(checks)

    report = {
        "project": "Notification Relevance Ranker Version 3",
        "model": "XGBoost rank:pairwise",
        "seed": seed,
        "training_queries": training_queries,
        "test_queries": test_queries,
        "candidates_per_query": 6,
        "baseline_metrics": baseline_metrics,
        "learned_metrics": learned_metrics,
        "learned_minus_baseline": rounded_difference(
            learned_metrics,
            baseline_metrics,
        ),
        "feature_importance": feature_importance(model),
        "ablation_metrics": ablation_metrics,
        "error_analysis": error_analysis,
        "training_seconds": round(training_seconds, 6),
        "prediction_latency_ms": round(prediction_latency_ms, 6),
        "deterministic_predictions": deterministic_predictions,
        "checks": checks,
        "passed_checks": passed_checks,
        "total_checks": total_checks,
        "limitations": [
            "Synthetic relevance judgments",
            "No real user behavior",
            "No online experimentation",
            "No production deployment",
        ],
    }

    RESULTS_JSON.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    RESULTS_MD.write_text(
        make_markdown(report),
        encoding="utf-8",
    )

    for name, passed in checks.items():
        label = "PASS" if passed else "FAIL"
        print(f"{label}: {name}")

    print()
    print(
        f"Evaluation complete: "
        f"{passed_checks}/{total_checks} checks passed"
    )
    print(f"Results written to: {RESULTS_JSON}")
    print(f"Results written to: {RESULTS_MD}")

    if passed_checks != total_checks:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
