from __future__ import annotations

from typing import Any


Record = dict[str, Any]


def expected_manifest(
    baseline: Record,
) -> list[str]:
    return sorted(
        (
            f"{item['configuration_item_id']}"
            f"@{item['revision']}"
        )
        for item in baseline.get("items", [])
    )


def review_release(
    release: Record,
    baseline: Record,
    approved_change_ids: set[str],
) -> list[str]:
    findings: list[str] = []

    if str(release.get("baseline_id")) != str(
        baseline.get("id")
    ):
        findings.append(
            "Release references a different baseline."
        )

    if str(release.get("version")) != str(
        baseline.get("version")
    ):
        findings.append(
            "Release version does not match the baseline."
        )

    if sorted(release.get("manifest_items", [])) != (
        expected_manifest(baseline)
    ):
        findings.append(
            "Release manifest cannot reconstruct the baseline."
        )

    included_changes = {
        str(change_id)
        for change_id in release.get(
            "included_change_requests",
            [],
        )
    }

    unknown_or_unapproved = sorted(
        included_changes - approved_change_ids
    )

    if unknown_or_unapproved:
        findings.append(
            "Release includes unapproved change requests: "
            + ", ".join(unknown_or_unapproved)
            + "."
        )

    if (
        release.get("status") == "released"
        and not release.get("released_at")
    ):
        findings.append(
            "Released configuration lacks a release timestamp."
        )

    return findings


def review_rollback_records(
    rollback_records: list[Record],
    releases: list[Record],
) -> dict[str, list[str]]:
    release_ids = {
        str(release["id"])
        for release in releases
    }
    findings: dict[str, list[str]] = {}

    for record in rollback_records:
        release_id = str(record["release_id"])
        issues: list[str] = []

        if release_id not in release_ids:
            issues.append(
                "Rollback source release does not exist."
            )

        target_id = str(record.get("target_release_id", ""))

        if target_id not in release_ids:
            issues.append(
                "Rollback target release does not exist."
            )

        required = set(
            str(item)
            for item in record.get(
                "required_artifacts",
                [],
            )
        )
        available = set(
            str(item)
            for item in record.get(
                "available_artifacts",
                [],
            )
        )

        missing = sorted(required - available)

        if missing:
            issues.append(
                "Rollback artifacts are missing: "
                + ", ".join(missing)
                + "."
            )

        if (
            record.get("status") == "ready"
            and issues
        ):
            issues.append(
                "Rollback is marked ready despite open findings."
            )

        if issues:
            findings[release_id] = issues

    return findings
