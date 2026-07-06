from pathlib import Path
import csv
import sys


BASE_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = BASE_DIR / "src"
EVAL_FILE = BASE_DIR / "eval" / "eval_questions.csv"
RESULTS_FILE = BASE_DIR / "eval" / "eval_results.md"

sys.path.append(str(SRC_DIR))

from rag_v1 import DOCS_DIR, load_documents, build_index, retrieve


docs = load_documents(DOCS_DIR)
index = build_index(docs)

results = []

with EVAL_FILE.open("r", encoding="utf-8") as file:
    reader = csv.DictReader(file)

    for row in reader:
        question = row["question"]
        expected_source = row["expected_source"]

        matches = retrieve(question, index, top_k=3)

        if matches:
            top_source = matches[0]["source"]
            top_score = matches[0]["score"]
        else:
            top_source = "No result"
            top_score = 0

        passed = top_source == expected_source

        results.append({
            "question": question,
            "expected_source": expected_source,
            "top_source": top_source,
            "top_score": top_score,
            "passed": passed
        })

passed_count = sum(1 for item in results if item["passed"])
total = len(results)

lines = [
    "# RAG Evaluation Results",
    "",
    f"Passed: {passed_count}/{total}",
    "",
    "| Question | Expected source | Top source | Score | Result |",
    "|---|---|---|---:|---|"
]

for item in results:
    result_text = "PASS" if item["passed"] else "FAIL"

    lines.append(
        f"| {item['question']} | {item['expected_source']} | "
        f"{item['top_source']} | {item['top_score']} | {result_text} |"
    )

lines.extend([
    "",
    "## Notes",
    "",
    "This checks whether the top retrieved chunk came from the expected source file.",
    "It does not check the quality of the final answer yet."
])

RESULTS_FILE.write_text("\n".join(lines), encoding="utf-8")

print(f"Evaluation complete: {passed_count}/{total} passed")
print(f"Results written to: {RESULTS_FILE}")
