import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from closure_review import (
    closure_status,
    review_corrective_actions,
    unresolved_anomalies,
    unresolved_critical_anomalies,
)
from verification_review import (
    compare_value,
    evaluate_plan_outcomes,
    evaluate_readiness,
    find_unplanned_requirements,
    requirement_outcomes,
    review_evidence,
    review_plan,
)


class VerificationReviewTests(unittest.TestCase):
    def setUp(self):
        self.requirements = [
            {
                "id": "REQ-001",
                "verification_method": "analysis",
            },
            {
                "id": "REQ-002",
                "verification_method": "test",
            },
        ]

        self.plans = [
            {
                "id": "VP-001",
                "requirement_ids": ["REQ-001"],
                "objective": "Evaluate a measured condition.",
                "method": "analysis",
                "entry_conditions": [
                    "dataset available",
                    "configuration recorded",
                ],
                "acceptance_criteria": {
                    "metric": "measured_value",
                    "operator": "<=",
                    "threshold": 1.0,
                },
                "required_evidence_fields": [
                    "dataset_id",
                    "metric_value",
                    "reviewer",
                ],
            }
        ]

    def test_unplanned_requirement_is_detected(self):
        result = find_unplanned_requirements(
            self.requirements,
            self.plans,
        )

        self.assertEqual(result, ["REQ-002"])

    def test_complete_plan_has_no_findings(self):
        result = review_plan(self.plans[0])
        self.assertEqual(result, [])

    def test_missing_acceptance_metric_is_detected(self):
        plan = dict(self.plans[0])
        plan["acceptance_criteria"] = {
            "operator": "<=",
            "threshold": 1.0,
        }

        result = review_plan(plan)

        self.assertIn(
            "Acceptance metric is missing.",
            result,
        )

    def test_readiness_is_ready_when_conditions_pass(self):
        result = evaluate_readiness(
            self.plans,
            [
                {
                    "plan_id": "VP-001",
                    "condition_results": {
                        "dataset available": True,
                        "configuration recorded": True,
                    },
                }
            ],
        )

        self.assertEqual(
            result["VP-001"],
            "ready",
        )

    def test_missing_readiness_condition_is_incomplete(self):
        result = evaluate_readiness(
            self.plans,
            [
                {
                    "plan_id": "VP-001",
                    "condition_results": {
                        "dataset available": True,
                    },
                }
            ],
        )

        self.assertEqual(
            result["VP-001"],
            "incomplete",
        )

    def test_missing_evidence_field_is_detected(self):
        findings = review_evidence(
            self.plans,
            [
                {
                    "id": "EV-001",
                    "plan_id": "VP-001",
                    "dataset_id": "SYN-001",
                    "metric_value": 0.5,
                    "recorded_at": "2026-07-20T12:00:00Z",
                }
            ],
        )

        self.assertIn(
            "Required field is missing: reviewer.",
            findings["EV-001"],
        )

    def test_numeric_comparison(self):
        self.assertTrue(
            compare_value(0.8, "<=", 1.0)
        )
        self.assertFalse(
            compare_value(1.2, "<=", 1.0)
        )

    def test_passing_evidence_produces_pass(self):
        readiness = {"VP-001": "ready"}
        evidence = [
            {
                "id": "EV-001",
                "plan_id": "VP-001",
                "dataset_id": "SYN-001",
                "metric_value": 0.7,
                "reviewer": "technical review",
                "recorded_at": "2026-07-20T12:00:00Z",
            }
        ]

        findings = review_evidence(
            self.plans,
            evidence,
        )

        outcomes = evaluate_plan_outcomes(
            self.plans,
            readiness,
            evidence,
            findings,
        )

        self.assertEqual(
            outcomes["VP-001"],
            "pass",
        )

    def test_requirement_outcome_rollup(self):
        outcomes = requirement_outcomes(
            self.requirements,
            self.plans,
            {"VP-001": "pass"},
        )

        self.assertEqual(
            outcomes["REQ-001"],
            "pass",
        )
        self.assertEqual(
            outcomes["REQ-002"],
            "not_run",
        )

    def test_open_anomalies_are_reported(self):
        anomalies = [
            {
                "id": "ANOM-001",
                "severity": "minor",
                "status": "open",
            },
            {
                "id": "ANOM-002",
                "severity": "critical",
                "status": "resolved",
            },
        ]

        self.assertEqual(
            unresolved_anomalies(anomalies),
            ["ANOM-001"],
        )
        self.assertEqual(
            unresolved_critical_anomalies(anomalies),
            [],
        )

    def test_resolved_anomaly_requires_completed_retest(self):
        findings = review_corrective_actions(
            [
                {
                    "id": "ANOM-001",
                    "severity": "critical",
                    "status": "resolved",
                    "corrective_action_id": "CA-001",
                }
            ],
            [
                {
                    "id": "CA-001",
                    "status": "completed",
                    "retest_id": "RT-001",
                }
            ],
            [
                {
                    "id": "RT-001",
                    "status": "fail",
                }
            ],
        )

        self.assertIn(
            "Linked retest did not pass.",
            findings["ANOM-001"],
        )

    def test_closure_is_ready_after_passing_review(self):
        result = closure_status(
            [
                {
                    "requirement_id": "REQ-001",
                    "requested_status": "closed",
                }
            ],
            {
                "REQ-001": "pass",
            },
            [],
            {},
        )

        self.assertEqual(
            result["REQ-001"],
            "ready_to_close",
        )

    def test_critical_anomaly_blocks_closure(self):
        result = closure_status(
            [
                {
                    "requirement_id": "REQ-001",
                    "requested_status": "closed",
                }
            ],
            {
                "REQ-001": "pass",
            },
            [
                {
                    "id": "ANOM-001",
                    "severity": "critical",
                    "status": "open",
                }
            ],
            {},
        )

        self.assertEqual(
            result["REQ-001"],
            "blocked_by_critical_anomaly",
        )


if __name__ == "__main__":
    unittest.main()
