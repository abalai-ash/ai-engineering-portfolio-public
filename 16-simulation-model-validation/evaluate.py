import json
from pathlib import Path

from simulation_core import evaluate_case

root = Path(__file__).resolve().parent

payload = json.loads(
    (root / "data" / "sample_cases.json").read_text(
        encoding="utf-8"
    )
)

results = [
    evaluate_case(case)
    for case in payload["cases"]
]

report = {
    "case_count": len(results),
    "pass_count": sum(
        result["status"] == "pass"
        for result in results
    ),
    "review_count": sum(
        result["status"] == "review"
        for result in results
    ),
    "fail_count": sum(
        result["status"] == "fail"
        for result in results
    ),
    "all_expected_checks_passed": all(
        result["status"] == case["expected_status"]
        for result, case in zip(results, payload["cases"])
    ),
    "results": results,
    "scope": "Limited synthetic public simulation example.",
}

(root / "evaluation_results.json").write_text(
    json.dumps(report, indent=2) + "\n",
    encoding="utf-8",
)

print(json.dumps(report, indent=2))

expected_summary = {
    "case_count": 3,
    "pass_count": 1,
    "review_count": 1,
    "fail_count": 1,
    "all_expected_checks_passed": True,
}

for key, expected_value in expected_summary.items():
    actual_value = report.get(key)

    if actual_value != expected_value:
        raise SystemExit(
            f"Unexpected {key}: "
            f"expected {expected_value}, got {actual_value}"
        )
