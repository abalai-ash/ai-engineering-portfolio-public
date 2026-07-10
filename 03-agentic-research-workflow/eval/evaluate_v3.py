from pathlib import Path
import sys


BASE_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = BASE_DIR / "src"
RESULTS_FILE = BASE_DIR / "eval" / "eval_v3_results.md"

sys.path.append(str(SRC_DIR))

from workflow_v3 import run_grounded_agent  # noqa: E402


cases = [
    {
        "query": "summarize agentic workflow tools and human review",
        "expected_route": "research_summary",
        "expected_phrase": "Grounded summary",
    },
    {
        "query": "make a checklist for reviewing the workflow",
        "expected_route": "checklist",
        "expected_phrase": "Checklist",
    },
    {
        "query": "write a status update about this workflow",
        "expected_route": "project_update",
        "expected_phrase": "Project update",
    },
    {
        "query": "should I include an API key in the output",
        "expected_route": "safety_review",
        "expected_phrase": "secrets",
    },
]

results = []

for case in cases:
    output = run_grounded_agent(case["query"])

    route_passed = output["route"] == case["expected_route"]
    phrase_passed = case["expected_phrase"].lower() in output["answer"].lower()
    source_passed = output["route"] == "safety_review" or len(output["source_snippets"]) > 0
    review_passed = output["human_review_required"] is True

    passed = route_passed and phrase_passed and source_passed and review_passed

    results.append({
        "query": case["query"],
        "expected_route": case["expected_route"],
        "actual_route": output["route"],
        "expected_phrase": case["expected_phrase"],
        "source_count": len(output["source_snippets"]),
        "passed": passed,
    })

passed_count = sum(1 for item in results if item["passed"])
total = len(results)

lines = [
    "# Agentic Workflow v3 Evaluation Results",
    "",
    f"Passed: {passed_count}/{total}",
    "",
    "| Query | Expected route | Actual route | Expected phrase | Sources | Result |",
    "|---|---|---|---|---:|---|",
]

for item in results:
    result_text = "PASS" if item["passed"] else "FAIL"

    lines.append(
        f"| {item['query']} | {item['expected_route']} | {item['actual_route']} | "
        f"{item['expected_phrase']} | {item['source_count']} | {result_text} |"
    )

lines.extend([
    "",
    "## What this evaluation checks",
    "",
    "This checks route selection, grounded answer content, source snippet use, safety routing, and human review.",
    "The workflow uses fake local notes and does not connect to private accounts or external services.",
])

RESULTS_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")

print(f"Evaluation complete: {passed_count}/{total} passed")
print(f"Results written to: {RESULTS_FILE}")
