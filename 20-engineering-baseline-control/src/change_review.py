from __future__ import annotations

from typing import Any


Record = dict[str, Any]


def review_change_request(
    change: Record,
    configuration_item_ids: set[str],
) -> list[str]:
    findings: list[str] = []

    if not change.get("title"):
        findings.append("Change title is missing.")

    if not change.get("rationale"):
        findings.append("Change rationale is missing.")

    affected_items = {
        str(item_id)
        for item_id in change.get("affected_items", [])
    }

    if not affected_items:
        findings.append("Affected configuration items are missing.")

    unknown_items = sorted(
        affected_items - configuration_item_ids
    )

    if unknown_items:
        findings.append(
            "Unknown affected configuration items: "
            + ", ".join(unknown_items)
            + "."
        )

    proposals = change.get("proposed_changes", [])

    if not proposals:
        findings.append("Proposed configuration changes are missing.")

    for proposal in proposals:
        item_id = str(
            proposal.get("configuration_item_id", "")
        )

        if item_id not in affected_items:
            findings.append(
                f"Proposed change for {item_id} is not listed as affected."
            )

        if not proposal.get("field"):
            findings.append(
                f"Proposed change for {item_id} does not identify a field."
            )

        if "proposed_value" not in proposal:
            findings.append(
                f"Proposed change for {item_id} lacks a proposed value."
            )

    if change.get("status") == "approved":
        if not change.get("verification_evidence"):
            findings.append(
                "Approved change does not identify verification evidence."
            )

    return findings


def review_change_requests(
    changes: list[Record],
    configuration_items: list[Record],
) -> dict[str, list[str]]:
    valid_ids = {
        str(record["id"])
        for record in configuration_items
    }
    findings: dict[str, list[str]] = {}

    for change in changes:
        issues = review_change_request(
            change,
            valid_ids,
        )

        if issues:
            findings[str(change["id"])] = issues

    return findings


def review_approval_coverage(
    changes: list[Record],
    reviews: list[Record],
    approvals: list[Record],
) -> dict[str, list[str]]:
    reviews_by_change: dict[str, list[Record]] = {}

    for review in reviews:
        reviews_by_change.setdefault(
            str(review["change_request_id"]),
            [],
        ).append(review)

    approval_by_change = {
        str(record["change_request_id"]): record
        for record in approvals
    }

    findings: dict[str, list[str]] = {}

    for change in changes:
        if change.get("status") != "approved":
            continue

        change_id = str(change["id"])
        issues: list[str] = []
        change_reviews = reviews_by_change.get(
            change_id,
            [],
        )

        completed_types = {
            str(review["review_type"])
            for review in change_reviews
            if (
                review.get("status") == "complete"
                and review.get("decision")
            )
        }

        for required_type in {
            "technical",
            "configuration",
        }:
            if required_type not in completed_types:
                issues.append(
                    f"Completed {required_type} review is missing."
                )

        approval = approval_by_change.get(change_id)

        if approval is None:
            issues.append("Approval record is missing.")
        elif approval.get("status") != "approved":
            issues.append("Approval record is not approved.")
        elif not approval.get("approved_at"):
            issues.append("Approval timestamp is missing.")

        if issues:
            findings[change_id] = issues

    return findings


def affected_item_summary(
    changes: list[Record],
) -> dict[str, list[str]]:
    summary: dict[str, list[str]] = {}

    for change in changes:
        for item_id in change.get(
            "affected_items",
            [],
        ):
            summary.setdefault(
                str(item_id),
                [],
            ).append(str(change["id"]))

    return {
        item_id: sorted(change_ids)
        for item_id, change_ids in sorted(
            summary.items()
        )
    }
