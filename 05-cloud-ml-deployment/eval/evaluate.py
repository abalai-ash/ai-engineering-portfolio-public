from pathlib import Path
import csv
import sys


BASE_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = BASE_DIR / "src"
EVAL_FILE = BASE_DIR / "eval" / "eval_cases.csv"
RESULTS_FILE = BASE_DIR / "eval" / "eval_results.md"

sys.path.append(str(SRC_DIR))

from app_v1 import make_response  # noqa: E402


results = []

with EVAL_FILE.open("r", encoding="utf-8") as file:
    reader = csv.DictReader(file)

    for row in reader:
        response = make_response(row["message"])
        label = response["prediction"]["label"]
        expected = row["expected_label"]
        passed = label == expected

        results.append({
            "message": row["message"],
            "expected": expected,
            "label": label,
            "passed": passed
        })

passed_count = sum(1 for item in results if item["passed"])
total = len(results)

lines = [
    "# Cloud ML Deployment Evaluation Results",
    "",
    f"Passed: {passed_count}/{total}",
    "",
    "| Message | Expected label | Actual label | Result |",
    "|---|---|---|---|"
]

for item in results:
    result_text = "PASS" if item["passed"] else "FAIL"

    lines.append(
        f"| {item['message']} | {item['expected']} | {item['label']} | {result_text} |"
    )

lines.extend([
    "",
    "## Notes",
    "",
    "This checks whether the demo classifier returns the expected priority label.",
    "The app uses fake messages and simple hand-written scoring. It does not use private data or external services."
])

RESULTS_FILE.write_text("\n".join(lines), encoding="utf-8")

print(f"Evaluation complete: {passed_count}/{total} passed")
print(f"Results written to: {RESULTS_FILE}")
