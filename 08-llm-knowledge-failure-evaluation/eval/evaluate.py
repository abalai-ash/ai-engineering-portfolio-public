from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"

sys.path.insert(0, str(SRC_DIR))

from evaluator import evaluate_all, load_cases


def main() -> None:
    cases = load_cases()
    results = evaluate_all()

    checks: list[tuple[str, bool]] = []

    for case, result in zip(cases, results):
        expected = case["expected"]

        checks.extend(
            [
                (
                    f"{case['case_id']}: grounded",
                    result.grounded == expected["grounded"],
                ),
                (
                    f"{case['case_id']}: unsupported claim",
                    result.has_unsupported_claim
                    == expected["has_unsupported_claim"],
                ),
                (
                    f"{case['case_id']}: instruction following",
                    result.follows_instruction
                    == expected["follows_instruction"],
                ),
                (
                    f"{case['case_id']}: uncertainty behavior",
                    result.expresses_uncertainty
                    == expected["expresses_uncertainty"],
                ),
            ]
        )

    passed = sum(result for _, result in checks)

    print("LLM Knowledge and Failure Evaluation")
    print("=" * 38)

    for name, result in checks:
        print(f"{'PASS' if result else 'FAIL'}: {name}")

    print()
    print(f"Evaluation complete: {passed}/{len(checks)} passed")

    if passed != len(checks):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
