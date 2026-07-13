from __future__ import annotations

import csv
import sys
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = BASE_DIR / "src"
EVAL_FILE = BASE_DIR / "eval" / "eval_questions_v2.csv"
RESULTS_FILE = BASE_DIR / "eval" / "eval_results_v2.md"

sys.path.insert(0, str(SRC_DIR))

from rag_v2 import build_index, load_documents, retrieve, answer_question


def main() -> None:
    documents = load_documents()
    index = build_index(documents)

    rows: list[dict[str, str]] = []

    with EVAL_FILE.open("r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            question = row["question"]
            expected_source = row["expected_source"]
            expected_status = row["expected_status"]

            results = retrieve(question, index, top_k=3)
            answer = answer_question(question, results)

            top_source = (
                results[0]["source"]
                if results
                else "NONE"
            )

            source_passed = (
                top_source == expected_source
                if expected_source != "NONE"
                else answer["status"] == "abstained"
            )

            status_passed = answer["status"] == expected_status
            passed = source_passed and status_passed

            rows.append(
                {
                    "question": question,
                    "expected_source": expected_source,
                    "top_source": top_source,
                    "expected_status": expected_status,
                    "actual_status": answer["status"],
                    "score": (
                        f"{results[0]['score']:.4f}"
                        if results
                        else "0.0000"
                    ),
                    "result": "PASS" if passed else "FAIL",
                }
            )

    passed_count = sum(
        row["result"] == "PASS"
        for row in rows
    )

    lines = [
        "# RAG v2 Evaluation Results",
        "",
        f"Passed: {passed_count}/{len(rows)}",
        "",
        (
            "| Question | Expected source | Top source | "
            "Expected status | Actual status | Score | Result |"
        ),
        (
            "|---|---|---|---|---|---:|---|"
        ),
    ]

    for row in rows:
        lines.append(
            f"| {row['question']} "
            f"| {row['expected_source']} "
            f"| {row['top_source']} "
            f"| {row['expected_status']} "
            f"| {row['actual_status']} "
            f"| {row['score']} "
            f"| {row['result']} |"
        )

    lines.extend(
        [
            "",
            "## Notes",
            "",
            (
                "This evaluation checks source retrieval and whether the "
                "system abstains when the documents do not contain enough "
                "evidence."
            ),
            (
                "It does not claim that simple local retrieval solves every "
                "grounded-answer problem."
            ),
        ]
    )

    RESULTS_FILE.write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )

    print("RAG v2 Evaluation")
    print("=" * 20)

    for row in rows:
        print(
            f"{row['result']}: "
            f"{row['question']} "
            f"| source={row['top_source']} "
            f"| status={row['actual_status']} "
            f"| score={row['score']}"
        )

    print()
    print(
        f"Evaluation complete: "
        f"{passed_count}/{len(rows)} passed"
    )
    print(f"Wrote {RESULTS_FILE}")

    if passed_count != len(rows):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
