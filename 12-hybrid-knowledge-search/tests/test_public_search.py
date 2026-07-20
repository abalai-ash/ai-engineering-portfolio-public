"""Selected public checks for the search example."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_DIR / "src"

sys.path.insert(0, str(SRC_DIR))

from answering import answer_question
from search import hybrid_search, validate_records


class PublicSearchChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.records = json.loads(
            (
                PROJECT_DIR
                / "data"
                / "records.json"
            ).read_text(encoding="utf-8")
        )

    def test_records_are_valid(self) -> None:
        validate_records(self.records)

    def test_related_incidents_are_retrieved(self) -> None:
        results = hybrid_search(
            (
                "Why can payment requests time out "
                "when identity validation is slow?"
            ),
            self.records,
            limit=4,
        )

        returned = {
            result["record"]["id"]
            for result in results
        }

        self.assertIn(
            "incident-payment-timeouts",
            returned,
        )

        self.assertIn(
            "incident-identity-slowdown",
            returned,
        )

    def test_missing_detail_is_not_answered(self) -> None:
        response = answer_question(
            (
                "What was the payroll system's "
                "database password?"
            ),
            self.records,
        )

        self.assertEqual(
            response["status"],
            "insufficient_evidence",
        )

        self.assertEqual(
            response["citations"],
            [],
        )


if __name__ == "__main__":
    unittest.main()
