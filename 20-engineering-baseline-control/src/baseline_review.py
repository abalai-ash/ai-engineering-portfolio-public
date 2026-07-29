from __future__ import annotations

from typing import Any


Record = dict[str, Any]


def item_index(
    baseline: Record,
) -> dict[str, Record]:
    return {
        str(item["configuration_item_id"]): item
        for item in baseline.get("items", [])
    }


def review_configuration_items(
    definitions: list[Record],
    baseline: Record,
) -> dict[str, list[str]]:
    definition_index = {
        str(record["id"]): record
        for record in definitions
    }
    baseline_items = item_index(baseline)
    findings: dict[str, list[str]] = {}

    for item_id, definition in definition_index.items():
        issues: list[str] = []
        item = baseline_items.get(item_id)

        if item is None:
            issues.append("Configuration item is absent from the baseline.")
        else:
            if not item.get("revision"):
                issues.append("Revision is missing.")

            values = item.get("values", {})

            for field in definition.get("required_fields", []):
                if field not in values:
                    issues.append(
                        f"Required configuration field is missing: {field}."
                    )

        if issues:
            findings[item_id] = issues

    for item_id in sorted(
        set(baseline_items) - set(definition_index)
    ):
        findings[item_id] = [
            "Baseline references an undefined configuration item."
        ]

    return findings


def compare_baselines(
    previous: Record,
    current: Record,
) -> list[Record]:
    previous_items = item_index(previous)
    current_items = item_index(current)
    differences: list[Record] = []

    for item_id in sorted(
        set(previous_items) | set(current_items)
    ):
        old_item = previous_items.get(item_id)
        new_item = current_items.get(item_id)

        if old_item is None:
            differences.append(
                {
                    "configuration_item_id": item_id,
                    "change_type": "added",
                    "field": None,
                    "previous_value": None,
                    "current_value": new_item,
                }
            )
            continue

        if new_item is None:
            differences.append(
                {
                    "configuration_item_id": item_id,
                    "change_type": "removed",
                    "field": None,
                    "previous_value": old_item,
                    "current_value": None,
                }
            )
            continue

        if old_item.get("revision") != new_item.get("revision"):
            differences.append(
                {
                    "configuration_item_id": item_id,
                    "change_type": "revision",
                    "field": "revision",
                    "previous_value": old_item.get("revision"),
                    "current_value": new_item.get("revision"),
                }
            )

        old_values = old_item.get("values", {})
        new_values = new_item.get("values", {})

        for field in sorted(
            set(old_values) | set(new_values)
        ):
            old_value = old_values.get(field)
            new_value = new_values.get(field)

            if old_value != new_value:
                differences.append(
                    {
                        "configuration_item_id": item_id,
                        "change_type": "value",
                        "field": field,
                        "previous_value": old_value,
                        "current_value": new_value,
                    }
                )

    return differences


def expected_change_signatures(
    changes: list[Record],
) -> set[tuple[str, str, str, str]]:
    signatures: set[tuple[str, str, str, str]] = set()

    for change in changes:
        if change.get("status") != "approved":
            continue

        for proposal in change.get(
            "proposed_changes",
            [],
        ):
            signatures.add(
                (
                    str(proposal["configuration_item_id"]),
                    str(proposal["field"]),
                    repr(proposal.get("previous_value")),
                    repr(proposal.get("proposed_value")),
                )
            )

    return signatures


def undocumented_differences(
    differences: list[Record],
    changes: list[Record],
) -> list[Record]:
    expected = expected_change_signatures(changes)
    undocumented: list[Record] = []

    for difference in differences:
        if (
            difference.get("change_type") != "value"
            or difference.get("field") is None
        ):
            continue

        signature = (
            str(difference["configuration_item_id"]),
            str(difference["field"]),
            repr(difference.get("previous_value")),
            repr(difference.get("current_value")),
        )

        if signature not in expected:
            undocumented.append(difference)

    return undocumented
