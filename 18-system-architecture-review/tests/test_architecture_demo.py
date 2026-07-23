from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = PROJECT_ROOT / "src" / "architecture_demo.py"

spec = importlib.util.spec_from_file_location("architecture_demo", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)


class ArchitectureDemoTests(unittest.TestCase):
    def test_unallocated_function_is_reported(self) -> None:
        summary = module.review_architecture(module.load_records())

        self.assertEqual(summary["function_count"], 3)
        self.assertEqual(summary["component_count"], 2)
        self.assertEqual(summary["interface_count"], 1)
        self.assertEqual(summary["unallocated_functions"], ["FUN-003"])
        self.assertEqual(summary["unknown_allocations"], [])
        self.assertEqual(summary["unknown_interface_components"], [])
        self.assertEqual(summary["allocation_percent"], 66.7)


if __name__ == "__main__":
    unittest.main()
