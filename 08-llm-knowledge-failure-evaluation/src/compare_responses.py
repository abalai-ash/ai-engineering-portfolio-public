from __future__ import annotations

import json
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
COMPARISON_CASES = PROJECT_ROOT / "data" / "comparison_cases.json"

sys.path.insert(0, str(SRC_DIR))

from evaluator import evaluate_case


def load_comparisons() -> list[dict[str, Any]]:
    return json.loads(COMPARISON_CASES.read_text(encoding="utf-8"))


def evaluate_response(
    comparison: dict[str, Any],
    label: str,
) -> dict[str, Any]:
    response_key = f"response_{label.lower()}"

    case = {
        "case_id": f"{comparison['comparison_id']}_{label}",
        "prompt": comparison["prompt"],
        "source": comparison["source"],
        "response": comparison[response_key],
        "expected": {
            "grounded": True,
            "has_unsupported_claim": False,
            "follows_instruction": True,
            "expresses_uncertainty": False,
        },
    }

    result = evaluate_case(case)

    return {
        "label": label,
        "response": comparison[response_key],
        "evaluation": asdict(result),
    }


def choose_winner(
    result_a: dict[str, Any],
    result_b: dict[str, Any],
) -> str:
    score_a = result_a["evaluation"]["score"]
    score_b = result_b["evaluation"]["score"]

    if score_a > score_b:
        return "A"

    if score_b > score_a:
        return "B"

    grounded_a = result_a["evaluation"]["grounded"]
    grounded_b = result_b["evaluation"]["grounded"]

    if grounded_a and not grounded_b:
        return "A"

    if grounded_b and not grounded_a:
        return "B"

    unsupported_a = result_a["evaluation"]["has_unsupported_claim"]
    unsupported_b = result_b["evaluation"]["has_unsupported_claim"]

    if not unsupported_a and unsupported_b:
        return "A"

    if not unsupported_b and unsupported_a:
        return "B"

    return "TIE"


def compare_all() -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []

    for comparison in load_comparisons():
        result_a = evaluate_response(comparison, "A")
        result_b = evaluate_response(comparison, "B")
        winner = choose_winner(result_a, result_b)

        output.append(
            {
                "comparison_id": comparison["comparison_id"],
                "prompt": comparison["prompt"],
                "source": comparison["source"],
                "response_a": result_a,
                "response_b": result_b,
                "winner": winner,
                "expected_winner": comparison["expected_winner"],
                "passed": winner == comparison["expected_winner"],
            }
        )

    return output


def write_report(results: list[dict[str, Any]]) -> Path:
    output_path = PROJECT_ROOT / "results" / "comparison_report.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "# Response Comparison Report",
        "",
    ]

    for item in results:
        lines.extend(
            [
                f"## {item['comparison_id']}",
                "",
                f"**Prompt:** {item['prompt']}",
                "",
                f"**Source:** {item['source']}",
                "",
                f"**Response A:** {item['response_a']['response']}",
                "",
                f"**Response B:** {item['response_b']['response']}",
                "",
                f"**Chosen response:** {item['winner']}",
                "",
                f"**Expected response:** {item['expected_winner']}",
                "",
                f"**Result:** {'PASS' if item['passed'] else 'FAIL'}",
                "",
                "### Reasoning",
                "",
                f"- Response A score: {item['response_a']['evaluation']['score']}/4",
                f"- Response B score: {item['response_b']['evaluation']['score']}/4",
                f"- Response A grounded: {item['response_a']['evaluation']['grounded']}",
                f"- Response B grounded: {item['response_b']['evaluation']['grounded']}",
                f"- Response A unsupported claim: {item['response_a']['evaluation']['has_unsupported_claim']}",
                f"- Response B unsupported claim: {item['response_b']['evaluation']['has_unsupported_claim']}",
                "",
            ]
        )

    output_path.write_text("\n".join(lines), encoding="utf-8")
    return output_path


def main() -> None:
    results = compare_all()
    report_path = write_report(results)

    passed = sum(item["passed"] for item in results)

    for item in results:
        print(
            f"{item['comparison_id']}: "
            f"winner={item['winner']} "
            f"expected={item['expected_winner']} "
            f"{'PASS' if item['passed'] else 'FAIL'}"
        )

    print()
    print(f"Comparison evaluation: {passed}/{len(results)} passed")
    print(f"Wrote {report_path}")

    if passed != len(results):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
