from pathlib import Path
import csv
import sys


BASE_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = BASE_DIR / "src"
EVAL_FILE = BASE_DIR / "eval" / "eval_cases.csv"
RESULTS_FILE = BASE_DIR / "eval" / "eval_results.md"

sys.path.append(str(SRC_DIR))

from workflow_v1 import run_workflow  # noqa: E402


results = []

with EVAL_FILE.open("r", encoding="utf-8") as file:
    reader = csv.DictReader(file)

    for row in reader:
        output = run_workflow(row["query"])
        draft = output["draft_update"]

        passed = row["expected_phrase"].lower() in draft.lower()

        results.append({
            "query": row["query"],
            "expected_phrase": row["expected_phrase"],
            "passed": passed
        })

passed_count = sum(1 for item in results if item["passed"])
total = len(results)

lines = [
    "# Agentic Workflow Evaluation Results",
    "",
    f"Passed: {passed_count}/{total}",
    "",
    "| Query | Expected phrase | Result |",
    "|---|---|---|"
]

for item in results:
    result_text = "PASS" if item["passed"] else "FAIL"
    lines.append(
        f"| {item['query']} | {item['expected_phrase']} | {result_text} |"
    )

lines.extend([
    "",
    "## Notes",
    "",
    "This checks whether the workflow returns a draft update containing the expected safety or task phrase.",
    "It uses fake notes and does not connect to private files or accounts."
])

RESULTS_FILE.write_text("\n".join(lines), encoding="utf-8")

print(f"Evaluation complete: {passed_count}/{total} passed")
print(f"Results written to: {RESULTS_FILE}")
