import sys
import unittest
from pathlib import Path

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / "src"))

from simulation_model import (
    evaluate_case,
    reference_position,
    simulate,
    validate_case,
)


class SimulationModelTests(unittest.TestCase):
    def setUp(self):
        self.case = {
            "case_id": "test-case",
            "omega": 2.0,
            "zeta": 0.15,
            "initial_position": 1.0,
            "initial_velocity": 0.0,
            "duration": 2.0,
            "time_step": 0.01,
            "pass_tolerance": 0.01,
            "review_tolerance": 0.03,
        }

    def test_reference_starts_at_initial_position(self):
        value = reference_position(
            0.0,
            2.0,
            0.15,
            1.0,
            0.0,
        )
        self.assertAlmostEqual(value, 1.0)

    def test_small_step_passes(self):
        result = evaluate_case(self.case)
        self.assertEqual(result["status"], "pass")

    def test_invalid_time_step_fails(self):
        invalid = dict(self.case)
        invalid["time_step"] = 0.0
        result = evaluate_case(invalid)
        self.assertEqual(result["status"], "fail")

    def test_negative_damping_is_rejected(self):
        invalid = dict(self.case)
        invalid["zeta"] = -0.1

        with self.assertRaises(ValueError):
            validate_case(invalid)

    def test_nonpositive_frequency_is_rejected(self):
        invalid = dict(self.case)
        invalid["omega"] = 0.0

        with self.assertRaises(ValueError):
            validate_case(invalid)

    def test_simulation_is_deterministic(self):
        first = simulate(self.case)
        second = simulate(self.case)
        self.assertEqual(first, second)

    def test_simulation_produces_multiple_samples(self):
        samples = simulate(self.case)
        self.assertGreater(len(samples), 2)

    def test_initial_sample_matches_inputs(self):
        samples = simulate(self.case)
        self.assertAlmostEqual(samples[0]["time"], 0.0)
        self.assertAlmostEqual(samples[0]["position"], 1.0)

    def test_coarse_case_requires_review(self):
        coarse = dict(self.case)
        coarse["duration"] = 8.0
        coarse["time_step"] = 0.5
        coarse["review_tolerance"] = 0.08

        result = evaluate_case(coarse)
        self.assertEqual(result["status"], "review")


if __name__ == "__main__":
    unittest.main()
