from pathlib import Path
import csv
import sys


BASE_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = BASE_DIR / "src"
EVAL_FILE = BASE_DIR / "eval" / "eval_cases.csv"
RESULTS_FILE = BASE_DIR / "eval" / "eval_v2_results.md"

sys.path.append(str(SRC_DIR))

from search_v2 import search  # noqa: E402


results = []

with EVAL_FILE.open("r", encoding="utf-8") as file:
    reader = csv.DictReader(file)

    for row in reader:
        output = search(row["query"], top_k=3)
        top_item = output["results"][0]
        expected = row["expected_top_image"]

        top_passed = top_item["image_id"] == expected
        type_present = bool(top_item["object_type"])
        reason_present = bool(top_item["match_reason"])
        query_reason_present = len(output["query_reasons"]) > 0

        passed = top_passed and type_present and reason_present and query_reason_present

        results.append({
            "query": row["query"],
            "expected": expected,
            "top": top_item["image_id"],
            "object_type": top_item["object_type"],
            "similarity": top_item["similarity"],
            "reason": top_item["match_reason"],
            "passed": passed,
        })

passed_count = sum(1 for item in results if item["passed"])
total = len(results)

lines = [
    "# Scientific Image Search v2 Evaluation Results",
    "",
    f"Passed: {passed_count}/{total}",
    "",
    "| Query | Expected top | Actual top | Type | Similarity | Result |",
    "|---|---|---|---|---:|---|",
]

for item in results:
    result_text = "PASS" if item["passed"] else "FAIL"
    lines.append(
        f"| {item['query']} | {item['expected']} | {item['top']} | "
        f"{item['object_type']} | {item['similarity']:.3f} | {result_text} |"
    )

lines.extend([
    "",
    "## What this evaluation checks",
    "",
    "This checks the expected top image, object type availability, query interpretation, and match explanation.",
    "The project uses synthetic image features and does not include private research images.",
])

RESULTS_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")

print(f"Evaluation complete: {passed_count}/{total} passed")
print(f"Results written to: {RESULTS_FILE}")
