import sys
import unittest
from pathlib import Path

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root))

from verification_core import classify


class VerificationCoreTests(unittest.TestCase):
    def setUp(self):
        self.requirement = {
            "id": "REQ-1",
            "parameter": "value",
            "unit": "V",
            "minimum": 4.0,
            "maximum": 6.0,
            "configuration": "baseline",
        }

    def test_pass(self):
        result = classify(
            self.requirement,
            {
                "id": "TEST-1",
                "parameter": "value",
                "unit": "V",
                "configuration": "baseline",
                "value": 5.0,
            },
        )
        self.assertEqual(result["status"], "pass")

    def test_review(self):
        result = classify(
            self.requirement,
            {
                "id": "TEST-1",
                "parameter": "value",
                "unit": "V",
                "configuration": "baseline",
                "value": 5.8,
                "review_margin": 0.3,
            },
        )
        self.assertEqual(result["status"], "review")

    def test_mismatch_fails(self):
        result = classify(
            self.requirement,
            {
                "id": "TEST-1",
                "parameter": "value",
                "unit": "mV",
                "configuration": "baseline",
                "value": 5.0,
            },
        )
        self.assertEqual(result["status"], "fail")

    def test_missing_test_requires_review(self):
        result = classify(self.requirement, None)
        self.assertEqual(result["status"], "review")


if __name__ == "__main__":
    unittest.main()
