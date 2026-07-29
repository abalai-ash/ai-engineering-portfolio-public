import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from baseline_review import (
    compare_baselines,
    review_configuration_items,
    undocumented_differences,
)
from change_review import (
    affected_item_summary,
    review_approval_coverage,
    review_change_request,
)
from release_review import (
    expected_manifest,
    review_release,
    review_rollback_records,
)


class BaselineControlTests(unittest.TestCase):
    def setUp(self):
        self.configuration_items = [
            {
                "id": "CI-001",
                "required_fields": [
                    "mode",
                    "threshold",
                ],
            }
        ]

        self.previous = {
            "id": "BL-001",
            "version": "1.0",
            "items": [
                {
                    "configuration_item_id": "CI-001",
                    "revision": "1",
                    "values": {
                        "mode": "standard",
                        "threshold": 0.90,
                    },
                }
            ],
        }

        self.current = {
            "id": "BL-002",
            "version": "1.1",
            "items": [
                {
                    "configuration_item_id": "CI-001",
                    "revision": "2",
                    "values": {
                        "mode": "standard",
                        "threshold": 0.93,
                    },
                }
            ],
        }

    def test_complete_baseline_has_no_findings(self):
        findings = review_configuration_items(
            self.configuration_items,
            self.current,
        )

        self.assertEqual(findings, {})

    def test_missing_configuration_field_is_detected(self):
        baseline = {
            "items": [
                {
                    "configuration_item_id": "CI-001",
                    "revision": "2",
                    "values": {
                        "mode": "standard",
                    },
                }
            ]
        }

        findings = review_configuration_items(
            self.configuration_items,
            baseline,
        )

        self.assertIn(
            "Required configuration field is missing: threshold.",
            findings["CI-001"],
        )

    def test_baseline_difference_is_detected(self):
        differences = compare_baselines(
            self.previous,
            self.current,
        )

        value_changes = [
            difference
            for difference in differences
            if difference.get("change_type") == "value"
        ]

        self.assertEqual(len(value_changes), 1)
        self.assertEqual(
            value_changes[0]["field"],
            "threshold",
        )

    def test_approved_change_documents_difference(self):
        differences = compare_baselines(
            self.previous,
            self.current,
        )

        changes = [
            {
                "id": "CR-001",
                "status": "approved",
                "proposed_changes": [
                    {
                        "configuration_item_id": "CI-001",
                        "field": "threshold",
                        "previous_value": 0.90,
                        "proposed_value": 0.93,
                    }
                ],
            }
        ]

        self.assertEqual(
            undocumented_differences(
                differences,
                changes,
            ),
            [],
        )

    def test_undocumented_difference_is_detected(self):
        differences = compare_baselines(
            self.previous,
            self.current,
        )

        self.assertEqual(
            len(
                undocumented_differences(
                    differences,
                    [],
                )
            ),
            1,
        )

    def test_change_request_requires_rationale(self):
        change = {
            "id": "CR-001",
            "title": "Update threshold",
            "status": "proposed",
            "affected_items": ["CI-001"],
            "proposed_changes": [
                {
                    "configuration_item_id": "CI-001",
                    "field": "threshold",
                    "previous_value": 0.90,
                    "proposed_value": 0.93,
                }
            ],
        }

        findings = review_change_request(
            change,
            {"CI-001"},
        )

        self.assertIn(
            "Change rationale is missing.",
            findings,
        )

    def test_approved_change_requires_evidence(self):
        change = {
            "id": "CR-001",
            "title": "Update threshold",
            "status": "approved",
            "rationale": "Improve record quality.",
            "affected_items": ["CI-001"],
            "proposed_changes": [
                {
                    "configuration_item_id": "CI-001",
                    "field": "threshold",
                    "previous_value": 0.90,
                    "proposed_value": 0.93,
                }
            ],
            "verification_evidence": [],
        }

        findings = review_change_request(
            change,
            {"CI-001"},
        )

        self.assertIn(
            "Approved change does not identify verification evidence.",
            findings,
        )

    def test_approval_coverage_passes(self):
        findings = review_approval_coverage(
            [
                {
                    "id": "CR-001",
                    "status": "approved",
                }
            ],
            [
                {
                    "change_request_id": "CR-001",
                    "review_type": "technical",
                    "status": "complete",
                    "decision": "recommend approval",
                },
                {
                    "change_request_id": "CR-001",
                    "review_type": "configuration",
                    "status": "complete",
                    "decision": "approve",
                },
            ],
            [
                {
                    "change_request_id": "CR-001",
                    "status": "approved",
                    "approved_at": "2026-07-20T10:00:00Z",
                }
            ],
        )

        self.assertEqual(findings, {})

    def test_affected_item_summary(self):
        summary = affected_item_summary(
            [
                {
                    "id": "CR-001",
                    "affected_items": [
                        "CI-001",
                        "CI-002",
                    ],
                },
                {
                    "id": "CR-002",
                    "affected_items": [
                        "CI-001",
                    ],
                },
            ]
        )

        self.assertEqual(
            summary["CI-001"],
            ["CR-001", "CR-002"],
        )

    def test_manifest_reconstructs_baseline(self):
        manifest = expected_manifest(self.current)

        self.assertEqual(
            manifest,
            ["CI-001@2"],
        )

    def test_valid_release_has_no_findings(self):
        release = {
            "id": "REL-001",
            "baseline_id": "BL-002",
            "version": "1.1",
            "status": "released",
            "released_at": "2026-07-21T10:00:00Z",
            "included_change_requests": ["CR-001"],
            "manifest_items": ["CI-001@2"],
        }

        findings = review_release(
            release,
            self.current,
            {"CR-001"},
        )

        self.assertEqual(findings, [])

    def test_unapproved_release_change_is_detected(self):
        release = {
            "id": "REL-001",
            "baseline_id": "BL-002",
            "version": "1.1",
            "status": "released",
            "released_at": "2026-07-21T10:00:00Z",
            "included_change_requests": ["CR-999"],
            "manifest_items": ["CI-001@2"],
        }

        findings = review_release(
            release,
            self.current,
            set(),
        )

        self.assertTrue(
            any(
                "unapproved change requests"
                in finding
                for finding in findings
            )
        )

    def test_complete_rollback_record_has_no_findings(self):
        findings = review_rollback_records(
            [
                {
                    "release_id": "REL-002",
                    "target_release_id": "REL-001",
                    "status": "ready",
                    "required_artifacts": [
                        "manifest",
                        "baseline",
                    ],
                    "available_artifacts": [
                        "manifest",
                        "baseline",
                    ],
                }
            ],
            [
                {"id": "REL-001"},
                {"id": "REL-002"},
            ],
        )

        self.assertEqual(findings, {})

    def test_missing_rollback_artifact_is_detected(self):
        findings = review_rollback_records(
            [
                {
                    "release_id": "REL-002",
                    "target_release_id": "REL-001",
                    "status": "ready",
                    "required_artifacts": [
                        "manifest",
                        "baseline",
                    ],
                    "available_artifacts": [
                        "manifest",
                    ],
                }
            ],
            [
                {"id": "REL-001"},
                {"id": "REL-002"},
            ],
        )

        self.assertTrue(
            any(
                "Rollback artifacts are missing"
                in finding
                for finding in findings["REL-002"]
            )
        )


if __name__ == "__main__":
    unittest.main()
