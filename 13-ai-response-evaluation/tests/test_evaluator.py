"""Tests for the curated response evaluator."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[1]

sys.path.insert(
    0,
    str(PROJECT_DIR),
)

from evaluator import (
    adjudicated_score,
    needs_adjudication,
    review_claim,
    reviewer_spread,
    score_case,
)

class EvaluatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        data_path = (
            PROJECT_DIR
            / "data"
            / "sample_cases.json"
        )

        data = json.loads(
            data_path.read_text(
                encoding="utf-8",
            )
        )

        cls.cases = {
            case["case_id"]: case
            for case in data["cases"]
        }

    def test_supported_answer_passes(self) -> None:
        result = score_case(
            self.cases["supported-answer"]
        )

        self.assertEqual(
            result["status"],
            "pass",
        )

    def test_invalid_citation_requires_review(self) -> None:
        result = score_case(
            self.cases["invalid-citation"]
        )

        self.assertEqual(
            result["status"],
            "review",
        )

    def test_contradiction_fails(self) -> None:
        result = score_case(
            self.cases["contradicted-answer"]
        )

        self.assertEqual(
            result["status"],
            "fail",
        )

    def test_missing_citation_is_recorded(self) -> None:
        review = review_claim(
            {
                "text": (
                    "Payment requests timed out while waiting "
                    "for identity validation."
                ),
                "evidence_ids": [
                    "missing-record",
                ],
            },
            {
                "incident-202": (
                    "Payment requests timed out while waiting "
                    "for identity validation."
                ),
            },
        )

        self.assertTrue(
            review["content_supported"]
        )

        self.assertFalse(
            review["citation_valid"]
        )

        self.assertEqual(
            review["invalid_evidence_ids"],
            ["missing-record"],
        )

    def test_reviewer_disagreement(self) -> None:
        scores = [
            8,
            5,
            7,
        ]

        self.assertEqual(
            reviewer_spread(scores),
            3,
        )

        self.assertTrue(
            needs_adjudication(scores)
        )

        self.assertEqual(
            adjudicated_score(scores),
            7.0,
        )

if __name__ == "__main__":
    unittest.main()
