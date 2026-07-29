import json
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / "src"))

from simulation_model import evaluate_case

payload = json.loads(
    (root / "data" / "simulation_cases.json").read_text(
        encoding="utf-8"
    )
)

results = [evaluate_case(case) for case in payload["cases"]]

report = {
    "case_count": len(results),
    "pass_count": sum(item["status"] == "pass" for item in results),
    "review_count": sum(item["status"] == "review" for item in results),
    "fail_count": sum(item["status"] == "fail" for item in results),
    "all_expected_checks_passed": all(
        result["status"] == case["expected_status"]
        for result, case in zip(results, payload["cases"])
    ),
    "results": results,
    "scope": "Synthetic damped-oscillator validation workflow."
}

(root / "eval" / "evaluation_results.json").write_text(
    json.dumps(report, indent=2) + "\n",
    encoding="utf-8"
)

print(json.dumps(report, indent=2))
