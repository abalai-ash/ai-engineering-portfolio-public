from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from measurement_core import (
    MeasurementPlan,
    collect,
    evaluate,
)


class MeasurementValidationTests(
    unittest.TestCase
):
    def test_collection_is_repeatable(
        self,
    ) -> None:
        plan = MeasurementPlan(
            case_id="repeatable",
            target=10.0,
            warning_limit=0.5,
            failure_limit=1.0,
            sample_count=5,
            noise=0.1,
        )

        first = collect(plan, seed=4)
        second = collect(plan, seed=4)

        self.assertEqual(first, second)

    def test_stable_case_passes(
        self,
    ) -> None:
        plan = MeasurementPlan(
            case_id="stable",
            target=3.3,
            warning_limit=0.08,
            failure_limit=0.15,
            sample_count=6,
            noise=0.01,
        )

        result = evaluate(
            plan,
            seed=4,
        )

        self.assertEqual(
            result["status"],
            "pass",
        )

    def test_drift_requires_review(
        self,
    ) -> None:
        plan = MeasurementPlan(
            case_id="drift",
            target=20.0,
            warning_limit=0.5,
            failure_limit=2.0,
            sample_count=6,
            drift=0.12,
        )

        result = evaluate(
            plan,
            seed=4,
        )

        self.assertEqual(
            result["status"],
            "review",
        )

    def test_interruption_fails(
        self,
    ) -> None:
        plan = MeasurementPlan(
            case_id="interrupted",
            target=5.0,
            warning_limit=0.2,
            failure_limit=0.5,
            sample_count=6,
            interrupted_at=2,
        )

        result = evaluate(
            plan,
            seed=4,
        )

        self.assertEqual(
            result["status"],
            "fail",
        )

        self.assertEqual(
            result["collected_samples"],
            5,
        )


if __name__ == "__main__":
    unittest.main()
