import json
from pathlib import Path

from verification_core import evaluate

root = Path(__file__).resolve().parent
payload = json.loads(
    (root / "data" / "sample_cases.json").read_text(encoding="utf-8")
)

report = evaluate(
    payload["requirements"],
    payload["tests"],
)

(root / "evaluation_results.json").write_text(
    json.dumps(report, indent=2) + "\n",
    encoding="utf-8",
)

print(json.dumps(report, indent=2))

expected = {
    "requirement_count": 3,
    "test_count": 2,
    "pass_count": 1,
    "review_count": 2,
    "fail_count": 0,
    "all_expected_checks_passed": True,
}

for key, value in expected.items():
    if report.get(key) != value:
        print(f"Unexpected {key}: {report.get(key)}")
