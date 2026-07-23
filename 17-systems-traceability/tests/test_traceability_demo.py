from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = PROJECT_ROOT / "src" / "traceability_demo.py"

spec = importlib.util.spec_from_file_location("traceability_demo", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)


class TraceabilityDemoTests(unittest.TestCase):
    def test_missing_verification_is_reported(self) -> None:
        records = module.load_records()
        summary = module.review_traceability(records)

        self.assertEqual(summary["requirement_count"], 3)
        self.assertEqual(summary["verification_case_count"], 1)
        self.assertEqual(summary["missing_verification"], ["SUB-002"])
        self.assertEqual(summary["unknown_links"], [])
        self.assertEqual(summary["coverage_percent"], 66.7)


if __name__ == "__main__":
    unittest.main()
