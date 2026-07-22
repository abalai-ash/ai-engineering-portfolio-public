from __future__ import annotations

import json
from pathlib import Path

from measurement_core import MeasurementPlan, evaluate


ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "data" / "sample_cases.json"
OUTPUT_PATH = ROOT / "evaluation_results.json"


def main() -> None:
    payload = json.loads(
        DATA_PATH.read_text(
            encoding="utf-8",
        )
    )

    results = []

    for index, raw in enumerate(
        payload["cases"]
    ):
        plan = MeasurementPlan(
            case_id=raw["case_id"],
            target=float(raw["target"]),
            warning_limit=float(
                raw["warning_limit"]
            ),
            failure_limit=float(
                raw["failure_limit"]
            ),
            sample_count=int(
                raw["sample_count"]
            ),
            noise=float(
                raw.get("noise", 0.0)
            ),
            drift=float(
                raw.get("drift", 0.0)
            ),
            interrupted_at=raw.get(
                "interrupted_at"
            ),
        )

        result = evaluate(
            plan,
            seed=int(payload["seed"]) + index,
        )

        result["expected_status"] = raw[
            "expected_status"
        ]

        result["expected_check_passed"] = (
            result["status"]
            == raw["expected_status"]
        )

        results.append(result)

    report = {
        "case_count": len(results),
        "all_expected_checks_passed": all(
            result["expected_check_passed"]
            for result in results
        ),
        "results": results,
        "scope": (
            "Synthetic public portfolio example "
            "with a limited implementation."
        ),
    }

    OUTPUT_PATH.write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8",
    )

    print(json.dumps(report, indent=2))

    if not report["all_expected_checks_passed"]:
        raise SystemExit(
            "An expected outcome did not pass."
        )


if __name__ == "__main__":
    main()
