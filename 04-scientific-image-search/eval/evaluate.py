from pathlib import Path
import csv
import sys


BASE_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = BASE_DIR / "src"
EVAL_FILE = BASE_DIR / "eval" / "eval_cases.csv"
RESULTS_FILE = BASE_DIR / "eval" / "eval_results.md"

sys.path.append(str(SRC_DIR))

from search_v1 import search  # noqa: E402


results = []

with EVAL_FILE.open("r", encoding="utf-8") as file:
    reader = csv.DictReader(file)

    for row in reader:
        output = search(row["query"])
        top_image = output["results"][0]["image_id"]
        expected = row["expected_top_image"]
        passed = top_image == expected

        results.append({
            "query": row["query"],
            "expected": expected,
            "top": top_image,
            "passed": passed
        })

passed_count = sum(1 for item in results if item["passed"])
total = len(results)

lines = [
    "# Scientific Image Search Evaluation Results",
    "",
    f"Passed: {passed_count}/{total}",
    "",
    "| Query | Expected top image | Actual top image | Result |",
    "|---|---|---|---|"
]

for item in results:
    result_text = "PASS" if item["passed"] else "FAIL"

    lines.append(
        f"| {item['query']} | {item['expected']} | {item['top']} | {result_text} |"
    )

lines.extend([
    "",
    "## Notes",
    "",
    "This checks whether the closest image match is the expected fake image example.",
    "The project uses small synthetic feature values, not private research images."
])

RESULTS_FILE.write_text("\n".join(lines), encoding="utf-8")

print(f"Evaluation complete: {passed_count}/{total} passed")
print(f"Results written to: {RESULTS_FILE}")
