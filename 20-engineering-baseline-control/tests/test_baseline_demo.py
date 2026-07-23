from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = PROJECT_ROOT / "src" / "baseline_demo.py"

spec = importlib.util.spec_from_file_location("baseline_demo", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)


class BaselineDemoTests(unittest.TestCase):
    def test_missing_approval_blocks_release(self) -> None:
        summary = module.review_baseline(module.load_records())

        self.assertEqual(summary["changed_items"], ["sampling_interval_seconds"])
        self.assertEqual(summary["declared_affected_items"], ["sampling_interval_seconds"])
        self.assertEqual(summary["undeclared_changes"], [])
        self.assertEqual(summary["unnecessary_affected_items"], [])
        self.assertEqual(summary["missing_approvals"], ["verification_review"])
        self.assertTrue(summary["rollback_recorded"])
        self.assertFalse(summary["release_ready"])


if __name__ == "__main__":
    unittest.main()
