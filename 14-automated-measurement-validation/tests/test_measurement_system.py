from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from measurement_system import (
    InstrumentConnectionError,
    InstrumentError,
    MeasurementCase,
    SimulatedInstrument,
    classify_reading,
    build_case,
    collect_measurements,
    detect_drift,
    detect_outliers,
    evaluate_case,
    simulate_measurements,
)


class MeasurementSystemTests(unittest.TestCase):
    def make_case(
        self,
        **overrides,
    ) -> MeasurementCase:
        values = {
            "case_id": "test-case",
            "instrument": "test-instrument",
            "target": 5.0,
            "warning_tolerance": 0.3,
            "failure_tolerance": 0.8,
            "noise": 0.0,
            "drift_per_sample": 0.0,
            "sample_count": 5,
            "expected_status": "pass",
            "outlier_index": None,
            "outlier_offset": 0.0,
            "connection_failure": False,
            "timeout_index": None,
            "invalid_sample_index": None,
        }

        values.update(overrides)
        return MeasurementCase(**values)

    def test_instrument_requires_connection(self) -> None:
        instrument = SimulatedInstrument(
            self.make_case(),
            seed=1,
        )

        with self.assertRaises(
            InstrumentConnectionError
        ):
            instrument.read(0)

    def test_simulation_is_repeatable(self) -> None:
        case = self.make_case(noise=0.1)

        first = simulate_measurements(
            case,
            seed=5,
        )

        second = simulate_measurements(
            case,
            seed=5,
        )

        self.assertEqual(first, second)

    def test_nominal_reading_passes(self) -> None:
        self.assertEqual(
            classify_reading(
                3.31,
                target=3.3,
                warning_tolerance=0.08,
                failure_tolerance=0.15,
            ),
            "pass",
        )

    def test_warning_reading_is_detected(self) -> None:
        self.assertEqual(
            classify_reading(
                3.40,
                target=3.3,
                warning_tolerance=0.08,
                failure_tolerance=0.15,
            ),
            "warning",
        )

    def test_failed_reading_is_detected(self) -> None:
        self.assertEqual(
            classify_reading(
                3.50,
                target=3.3,
                warning_tolerance=0.08,
                failure_tolerance=0.15,
            ),
            "fail",
        )

    def test_drift_is_detected(self) -> None:
        result = detect_drift(
            [10.0, 10.2, 10.4],
            warning_tolerance=0.25,
        )

        self.assertTrue(
            result["drift_detected"]
        )

    def test_outlier_index_is_recorded(self) -> None:
        indices = detect_outliers(
            [1.0, 1.1, 1.8, 1.0],
            target=1.0,
            failure_tolerance=0.5,
        )

        self.assertEqual(indices, [2])

    def test_connection_failure_is_recorded(self) -> None:
        case = self.make_case(
            connection_failure=True,
            expected_status="fail",
        )

        result = evaluate_case(
            case,
            seed=2,
        )

        self.assertEqual(
            result["status"],
            "fail",
        )

        self.assertFalse(
            result["connected"]
        )

        self.assertEqual(
            result["errors"][0]["error_type"],
            "connection",
        )

    def test_timeout_is_recorded(self) -> None:
        case = self.make_case(
            timeout_index=2,
            expected_status="fail",
        )

        result = evaluate_case(
            case,
            seed=2,
        )

        self.assertEqual(
            result["status"],
            "fail",
        )

        self.assertEqual(
            result["missing_samples"],
            1,
        )

        self.assertEqual(
            result["errors"][0]["error_type"],
            "timeout",
        )

    def test_invalid_sample_is_recorded(self) -> None:
        case = self.make_case(
            invalid_sample_index=3,
            expected_status="fail",
        )

        result = evaluate_case(
            case,
            seed=2,
        )

        self.assertEqual(
            result["status"],
            "fail",
        )

        self.assertEqual(
            result["errors"][0]["error_type"],
            "invalid-sample",
        )

    def test_strict_simulation_raises_on_error(
        self,
    ) -> None:
        case = self.make_case(
            timeout_index=1,
        )

        with self.assertRaises(
            InstrumentError
        ):
            simulate_measurements(
                case,
                seed=2,
            )

    def test_pass_case(self) -> None:
        result = evaluate_case(
            self.make_case(
                noise=0.03,
                expected_status="pass",
            ),
            seed=2,
        )

        self.assertEqual(
            result["status"],
            "pass",
        )

    def test_warning_case(self) -> None:
        result = evaluate_case(
            self.make_case(
                warning_tolerance=0.3,
                failure_tolerance=1.0,
                drift_per_sample=0.1,
                expected_status="warning",
            ),
            seed=2,
        )

        self.assertEqual(
            result["status"],
            "warning",
        )

    def test_failure_case(self) -> None:
        result = evaluate_case(
            self.make_case(
                expected_status="fail",
                outlier_index=3,
                outlier_offset=1.2,
            ),
            seed=2,
        )

        self.assertEqual(
            result["status"],
            "fail",
        )

        self.assertEqual(
            result["outlier_indices"],
            [3],
        )

    def test_environmental_measurement_cases(self) -> None:
        data_path = (
            PROJECT_ROOT
            / "data"
            / "measurement_cases.json"
        )

        payload = json.loads(
            data_path.read_text(encoding="utf-8")
        )

        expected = {
            "conductivity-drift-warning": "warning",
            "moisture-timeout-failure": "fail",
            "temperature-outlier-failure": "fail",
        }

        selected = {
            item["case_id"]: item
            for item in payload["cases"]
            if item["case_id"] in expected
        }

        self.assertEqual(
            set(selected),
            set(expected),
        )

        for offset, case_id in enumerate(expected):
            case = build_case(selected[case_id])
            result = evaluate_case(
                case,
                seed=int(payload["seed"]) + offset,
            )

            self.assertEqual(
                result["status"],
                expected[case_id],
            )


    def test_collection_disconnects_after_reading(
        self,
    ) -> None:
        collection = collect_measurements(
            self.make_case(),
            seed=2,
        )

        self.assertTrue(
            collection["connected"]
        )

        self.assertEqual(
            len(collection["readings"]),
            5,
        )


if __name__ == "__main__":
    unittest.main()
