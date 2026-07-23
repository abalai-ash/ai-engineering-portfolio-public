import sys
import unittest
from pathlib import Path

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root))

from simulation_core import (
    evaluate_case,
    reference_position,
    simulate,
)


class SimulationCoreTests(unittest.TestCase):
    def setUp(self):
        self.case = {
            "case_id": "test-case",
            "frequency": 2.0,
            "damping": 0.15,
            "duration": 2.0,
            "time_step": 0.01,
            "pass_tolerance": 0.01,
            "review_tolerance": 0.05,
        }

    def test_reference_initial_value(self):
        value = reference_position(
            0.0,
            2.0,
            0.15,
        )
        self.assertAlmostEqual(value, 1.0)

    def test_fine_step_passes(self):
        result = evaluate_case(self.case)
        self.assertEqual(result["status"], "pass")

    def test_coarse_step_requires_review(self):
        coarse = dict(self.case)
        coarse["duration"] = 4.0
        coarse["time_step"] = 0.5
        coarse["review_tolerance"] = 0.08

        result = evaluate_case(coarse)
        self.assertEqual(result["status"], "review")

    def test_invalid_step_fails(self):
        invalid = dict(self.case)
        invalid["time_step"] = 0.0

        result = evaluate_case(invalid)
        self.assertEqual(result["status"], "fail")

    def test_simulation_is_repeatable(self):
        first = simulate(self.case)
        second = simulate(self.case)
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
