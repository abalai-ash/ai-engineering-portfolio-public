import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from baseline import compare_baselines
from change_impact import analyze_change
from requirement_review import review_requirement
from traceability import (
    build_verification_links,
    find_orphan_requirements,
    find_unknown_requirement_links,
    find_unverified_requirements,
)
from verification import evaluate_cases, requirement_outcomes


class SystemsTraceabilityTests(unittest.TestCase):
    def setUp(self):
        self.needs = [
            {
                "id": "NEED-001",
                "text": "Observers need valid instrument data.",
            }
        ]

        self.requirements = [
            {
                "id": "SYS-001",
                "parent": "NEED-001",
                "text": "The system shall record each valid measurement.",
                "component": "record_store",
                "verification_method": "test",
            },
            {
                "id": "SUB-001",
                "parent": "SYS-001",
                "text": "The record store shall preserve each timestamp.",
                "component": "record_store",
                "verification_method": "inspection",
            },
        ]

        self.cases = [
            {
                "id": "TEST-001",
                "requirement_ids": ["SYS-001"],
                "method": "test",
            }
        ]

    def test_well_formed_requirement_has_no_findings(self):
        findings = review_requirement(self.requirements[0])
        self.assertEqual(findings, [])

    def test_vague_wording_is_detected(self):
        requirement = dict(self.requirements[0])
        requirement["text"] = (
            "The system should provide useful information."
        )

        findings = review_requirement(requirement)

        self.assertTrue(
            any("shall" in finding for finding in findings)
        )
        self.assertTrue(
            any("vague" in finding for finding in findings)
        )

    def test_orphan_requirement_is_detected(self):
        requirements = [
            {
                **self.requirements[0],
                "parent": "MISSING-001",
            }
        ]

        result = find_orphan_requirements(
            self.needs,
            requirements,
        )

        self.assertEqual(result, ["SYS-001"])

    def test_unverified_requirement_is_detected(self):
        result = find_unverified_requirements(
            self.requirements,
            self.cases,
        )

        self.assertEqual(result, ["SUB-001"])

    def test_unknown_verification_link_is_detected(self):
        cases = [
            {
                "id": "TEST-002",
                "requirement_ids": ["MISSING-001"],
            }
        ]

        result = find_unknown_requirement_links(
            self.requirements,
            cases,
        )

        self.assertEqual(
            result,
            [
                {
                    "case_id": "TEST-002",
                    "requirement_id": "MISSING-001",
                }
            ],
        )

    def test_verification_links_are_created(self):
        links = build_verification_links(self.cases)
        self.assertEqual(links["SYS-001"], ["TEST-001"])

    def test_missing_result_is_not_run(self):
        evaluated = evaluate_cases(self.cases, [])
        self.assertEqual(evaluated[0]["status"], "not_run")

    def test_review_result_rolls_up_to_requirement(self):
        evaluated = evaluate_cases(
            self.cases,
            [
                {
                    "case_id": "TEST-001",
                    "status": "review",
                    "evidence": "Additional review required.",
                }
            ],
        )

        outcomes = requirement_outcomes(
            self.requirements,
            evaluated,
        )

        self.assertEqual(outcomes["SYS-001"], "review")

    def test_modified_baseline_record_is_detected(self):
        previous = [
            {
                "id": "SYS-001",
                "text": "Previous wording",
            }
        ]
        current = [
            {
                "id": "SYS-001",
                "text": "Current wording",
            }
        ]

        result = compare_baselines(previous, current)

        self.assertEqual(result["modified"], ["SYS-001"])
        self.assertEqual(result["added"], [])
        self.assertEqual(result["removed"], [])

    def test_change_impact_includes_child_and_test(self):
        result = analyze_change(
            ["SYS-001"],
            self.requirements,
            self.cases,
        )

        self.assertEqual(
            result["requirements"],
            ["SUB-001", "SYS-001"],
        )
        self.assertEqual(
            result["verification_cases"],
            ["TEST-001"],
        )
        self.assertEqual(
            result["components"],
            ["record_store"],
        )


if __name__ == "__main__":
    unittest.main()
