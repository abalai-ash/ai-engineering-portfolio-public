from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"

sys.path.insert(0, str(SRC_DIR))

from compare_responses import compare_all


def main() -> None:
    results = compare_all()

    checks = [
        (
            item["comparison_id"],
            item["winner"] == item["expected_winner"],
        )
        for item in results
    ]

    passed = sum(result for _, result in checks)

    print("Response Comparison Evaluation")
    print("=" * 30)

    for name, result in checks:
        print(f"{'PASS' if result else 'FAIL'}: {name}")

    print()
    print(f"Evaluation complete: {passed}/{len(checks)} passed")

    if passed != len(checks):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
