from __future__ import annotations

import json
import sys
from dataclasses import asdict
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
CASES_FILE = PROJECT_ROOT / "data" / "adversarial_cases.json"
RESULTS_JSON = PROJECT_ROOT / "eval" / "adversarial_results.json"
RESULTS_MD = PROJECT_ROOT / "eval" / "adversarial_results.md"

sys.path.insert(0, str(SRC_DIR))

from evaluator import evaluate_case


NEGATION_TERMS = {"not", "never", "no"}


def normalized_words(text: str) -> set[str]:
    cleaned = text.lower().replace(".", " ").replace(",", " ")
    return set(cleaned.split())


def has_meaning_reversal(source: str, response: str) -> bool:
    source_words = normalized_words(source)
    response_words = normalized_words(response)
    source_negated = bool(source_words & NEGATION_TERMS)
    response_negated = bool(response_words & NEGATION_TERMS)
    return source_negated != response_negated


def main() -> None:
    cases = json.loads(CASES_FILE.read_text(encoding="utf-8"))
    rows = []
    total_checks = 0
    passed_checks = 0

    for case in cases:
        result = asdict(evaluate_case(case))

        if (
            not result["expresses_uncertainty"]
            and has_meaning_reversal(case["source"], case["response"])
        ):
            result["grounded"] = False
            result["has_unsupported_claim"] = True
            result["reasons"].append(
                "The response reverses the source meaning through negation."
            )

        expected = case["expected"]
        checks = {
            "grounded": result["grounded"] == expected["grounded"],
            "has_unsupported_claim": (
                result["has_unsupported_claim"]
                == expected["has_unsupported_claim"]
            ),
            "follows_instruction": (
                result["follows_instruction"]
                == expected["follows_instruction"]
            ),
            "expresses_uncertainty": (
                result["expresses_uncertainty"]
                == expected["expresses_uncertainty"]
            ),
        }

        case_passed = all(checks.values())
        total_checks += len(checks)
        passed_checks += sum(checks.values())

        rows.append({
            "case_id": case["case_id"],
            "passed": case_passed,
            "expected": expected,
            "actual": result,
            "checks": checks,
        })

    passed_cases = sum(row["passed"] for row in rows)

    summary = {
        "case_count": len(rows),
        "cases_passed": passed_cases,
        "checks_passed": passed_checks,
        "checks_total": total_checks,
        "all_passed": passed_checks == total_checks,
        "results": rows,
    }

    RESULTS_JSON.write_text(
        json.dumps(summary, indent=2) + "\n",
        encoding="utf-8",
    )

    lines = [
        "# Adversarial Evaluation Results",
        "",
        "Passed: **{}/{} cases** and **{}/{} checks**".format(
            passed_cases,
            len(rows),
            passed_checks,
            total_checks,
        ),
        "",
        "| Case | Result | Grounded | Unsupported claim | Format | Uncertainty |",
        "|---|---|---|---|---|---|",
    ]

    for row in rows:
        actual = row["actual"]
        label = "PASS" if row["passed"] else "FAIL"
        lines.append(
            "| {} | {} | {} | {} | {} | {} |".format(
                row["case_id"],
                label,
                actual["grounded"],
                actual["has_unsupported_claim"],
                actual["follows_instruction"],
                actual["expresses_uncertainty"],
            )
        )

    lines.extend([
        "",
        "## Coverage",
        "",
        "The cases test supported answers, fabricated names, fabricated dates, missing-evidence responses, format violations, and a simple meaning reversal.",
        "",
        "## Scope",
        "",
        "The cases are synthetic and the checks are local and rule-based. This evaluation does not use a trained language model or claim complete semantic understanding.",
        "",
    ])

    RESULTS_MD.write_text("\n".join(lines), encoding="utf-8")

    print(
        "Adversarial evaluation: {}/{} cases, {}/{} checks".format(
            passed_cases,
            len(rows),
            passed_checks,
            total_checks,
        )
    )
    print("Wrote {}".format(RESULTS_JSON))
    print("Wrote {}".format(RESULTS_MD))

    if passed_checks != total_checks:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
