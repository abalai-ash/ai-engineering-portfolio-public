import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from architecture_review import (
    find_dependency_cycles,
    find_duplicate_function_allocations,
    find_invalid_function_allocations,
    find_invalid_resource_allocations,
    find_resource_overloads,
    find_unallocated_functions,
    review_dependencies,
    review_interfaces,
)
from trade_study import (
    rank_alternatives,
    sensitivity_review,
    validate_weights,
)


class ArchitectureReviewTests(unittest.TestCase):
    def setUp(self):
        self.functions = [
            {"id": "F-001"},
            {"id": "F-002"},
        ]

        self.components = [
            {"id": "request_manager"},
            {"id": "schedule_service"},
        ]

        self.resources = [
            {
                "id": "operations_node",
                "capacity_units": 3,
            }
        ]

        self.allocations = [
            {
                "function_id": "F-001",
                "component_id": "request_manager",
            },
            {
                "function_id": "F-002",
                "component_id": "schedule_service",
            },
        ]

    def test_all_functions_are_allocated(self):
        result = find_unallocated_functions(
            self.functions,
            self.allocations,
        )
        self.assertEqual(result, [])

    def test_unallocated_function_is_detected(self):
        result = find_unallocated_functions(
            self.functions,
            self.allocations[:1],
        )
        self.assertEqual(result, ["F-002"])

    def test_duplicate_allocation_is_detected(self):
        allocations = self.allocations + [
            {
                "function_id": "F-001",
                "component_id": "schedule_service",
            }
        ]

        result = find_duplicate_function_allocations(
            allocations
        )

        self.assertEqual(
            result,
            {
                "F-001": [
                    "request_manager",
                    "schedule_service",
                ]
            },
        )

    def test_invalid_function_allocation_is_detected(self):
        result = find_invalid_function_allocations(
            self.functions,
            self.components,
            [
                {
                    "function_id": "F-999",
                    "component_id": "request_manager",
                }
            ],
        )

        self.assertEqual(
            result,
            [
                {
                    "function_id": "F-999",
                    "component_id": "request_manager",
                }
            ],
        )

    def test_interface_with_unknown_target_is_detected(self):
        findings = review_interfaces(
            self.components,
            [
                {
                    "id": "IF-001",
                    "source": "request_manager",
                    "target": "missing_component",
                    "data": "validated_request",
                    "required_fields": ["request_id"],
                }
            ],
        )

        self.assertEqual(
            findings[0]["interface_id"],
            "IF-001",
        )
        self.assertIn(
            "unknown target component",
            findings[0]["issues"],
        )

    def test_resource_overload_is_detected(self):
        result = find_resource_overloads(
            self.resources,
            [
                {
                    "component_id": "request_manager",
                    "resource_id": "operations_node",
                    "required_units": 2,
                },
                {
                    "component_id": "schedule_service",
                    "resource_id": "operations_node",
                    "required_units": 2,
                },
            ],
        )

        self.assertEqual(
            result,
            [
                {
                    "resource_id": "operations_node",
                    "capacity_units": 3.0,
                    "assigned_units": 4.0,
                }
            ],
        )

    def test_invalid_resource_reference_is_detected(self):
        result = find_invalid_resource_allocations(
            self.components,
            self.resources,
            [
                {
                    "component_id": "request_manager",
                    "resource_id": "missing_resource",
                    "required_units": 1,
                }
            ],
        )

        self.assertEqual(
            result,
            [
                {
                    "component_id": "request_manager",
                    "resource_id": "missing_resource",
                }
            ],
        )

    def test_dependency_cycle_is_detected(self):
        result = find_dependency_cycles(
            self.functions,
            [
                {"before": "F-001", "after": "F-002"},
                {"before": "F-002", "after": "F-001"},
            ],
        )

        self.assertEqual(
            result,
            ["F-001", "F-002"],
        )

    def test_unknown_dependency_reference_is_detected(self):
        result = review_dependencies(
            self.functions,
            [
                {"before": "F-001", "after": "F-999"},
            ],
        )

        self.assertEqual(
            result,
            [
                {
                    "before": "F-001",
                    "after": "F-999",
                }
            ],
        )

    def test_valid_weights_are_accepted(self):
        self.assertTrue(
            validate_weights(
                {
                    "integration": 0.5,
                    "resilience": 0.5,
                }
            )
        )

    def test_rank_alternatives_orders_highest_first(self):
        alternatives = [
            {
                "id": "ALT-001",
                "name": "first",
                "scores": {
                    "integration": 3,
                    "resilience": 2,
                },
            },
            {
                "id": "ALT-002",
                "name": "second",
                "scores": {
                    "integration": 4,
                    "resilience": 4,
                },
            },
        ]

        ranking = rank_alternatives(
            alternatives,
            {
                "integration": 0.5,
                "resilience": 0.5,
            },
        )

        self.assertEqual(
            ranking[0]["id"],
            "ALT-002",
        )

    def test_sensitivity_review_returns_leaders(self):
        alternatives = [
            {
                "id": "ALT-001",
                "name": "integration focused",
                "scores": {
                    "integration": 5,
                    "resilience": 1,
                },
            },
            {
                "id": "ALT-002",
                "name": "resilience focused",
                "scores": {
                    "integration": 2,
                    "resilience": 5,
                },
            },
        ]

        result = sensitivity_review(
            alternatives,
            {
                "integration_case": {
                    "integration": 0.8,
                    "resilience": 0.2,
                },
                "resilience_case": {
                    "integration": 0.2,
                    "resilience": 0.8,
                },
            },
        )

        self.assertEqual(
            result,
            {
                "integration_case": "ALT-001",
                "resilience_case": "ALT-002",
            },
        )


if __name__ == "__main__":
    unittest.main()
