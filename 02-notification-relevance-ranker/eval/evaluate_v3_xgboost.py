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
    model_scores_with_ablation,
    predict_scores,
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

    baseline_metrics = evaluate_rankings(
        test_examples,
        baseline_scores(test_examples),
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
