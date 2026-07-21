"""Run the curated public evaluation example."""

from __future__ import annotations

import json
from pathlib import Path

from evaluator import (
    adjudicated_score,
    needs_adjudication,
    reviewer_spread,
    score_case,
)

PROJECT_DIR = Path(__file__).resolve().parent

def main() -> None:
    """Evaluate the public synthetic examples."""

    data_path = (
        PROJECT_DIR
        / "data"
        / "sample_cases.json"
    )

    data = json.loads(
        data_path.read_text(
            encoding="utf-8",
        )
    )

    results = []

    for case in data["cases"]:
        result = score_case(case)
        result["expected_status"] = case[
            "expected_status"
        ]
        result["expected_check_passed"] = (
            result["status"]
            == case["expected_status"]
        )
        results.append(result)

    reviewer_scores = data[
        "reviewer_scores"
    ]

    report = {
        "case_count": len(results),
        "all_expected_checks_passed": all(
            result["expected_check_passed"]
            for result in results
        ),
        "results": results,
        "reviewer_consistency": {
            "scores": reviewer_scores,
            "spread": reviewer_spread(
                reviewer_scores
            ),
            "needs_adjudication": (
                needs_adjudication(
                    reviewer_scores
                )
            ),
            "adjudicated_score": (
                adjudicated_score(
                    reviewer_scores
                )
            ),
        },
        "scope": (
            "Synthetic portfolio-scale example."
        ),
    }

    output_dir = (
        PROJECT_DIR
        / "output"
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = (
        output_dir
        / "evaluation_results.json"
    )

    output_path.write_text(
        json.dumps(
            report,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    print(
        json.dumps(
            report,
            indent=2,
        )
    )

    if not report[
        "all_expected_checks_passed"
    ]:
        raise SystemExit(
            "One or more expected checks failed."
        )

if __name__ == "__main__":
    main()
