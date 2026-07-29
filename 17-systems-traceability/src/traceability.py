from __future__ import annotations

from collections import defaultdict
from typing import Any


Record = dict[str, Any]


def index_by_id(records: list[Record]) -> dict[str, Record]:
    """Return records indexed by their string identifiers."""
    return {
        str(record["id"]): record
        for record in records
    }


def build_child_links(
    requirements: list[Record],
) -> dict[str, list[str]]:
    """Map each parent record to its direct child requirements."""
    children: dict[str, list[str]] = defaultdict(list)

    for requirement in requirements:
        parent = requirement.get("parent")

        if parent:
            children[str(parent)].append(
                str(requirement["id"])
            )

    return {
        parent: sorted(child_ids)
        for parent, child_ids in children.items()
    }


def build_verification_links(
    verification_cases: list[Record],
) -> dict[str, list[str]]:
    """Map each requirement to its verification cases."""
    links: dict[str, list[str]] = defaultdict(list)

    for case in verification_cases:
        case_id = str(case["id"])

        for requirement_id in case.get(
            "requirement_ids",
            [],
        ):
            links[str(requirement_id)].append(case_id)

    return {
        requirement_id: sorted(case_ids)
        for requirement_id, case_ids in links.items()
    }


def find_orphan_requirements(
    stakeholder_needs: list[Record],
    requirements: list[Record],
) -> list[str]:
    """Find requirements whose parent record does not exist."""
    valid_parent_ids = {
        str(record["id"])
        for record in stakeholder_needs + requirements
    }

    return sorted(
        str(requirement["id"])
        for requirement in requirements
        if str(requirement.get("parent", ""))
        not in valid_parent_ids
    )


def find_unverified_requirements(
    requirements: list[Record],
    verification_cases: list[Record],
) -> list[str]:
    """Find requirements without a verification link."""
    links = build_verification_links(
        verification_cases
    )

    return sorted(
        str(requirement["id"])
        for requirement in requirements
        if str(requirement["id"]) not in links
    )


def find_unknown_requirement_links(
    requirements: list[Record],
    verification_cases: list[Record],
) -> list[dict[str, str]]:
    """Find case links that reference missing requirements."""
    known_ids = {
        str(requirement["id"])
        for requirement in requirements
    }

    unknown_links: list[dict[str, str]] = []

    for case in verification_cases:
        for requirement_id in case.get(
            "requirement_ids",
            [],
        ):
            requirement_id = str(requirement_id)

            if requirement_id not in known_ids:
                unknown_links.append(
                    {
                        "case_id": str(case["id"]),
                        "requirement_id": requirement_id,
                    }
                )

    return unknown_links


def trace_requirement(
    requirement_id: str,
    stakeholder_needs: list[Record],
    requirements: list[Record],
    verification_cases: list[Record],
) -> dict[str, Any]:
    """Return the immediate traceability record for one requirement."""
    requirement_index = index_by_id(requirements)
    need_index = index_by_id(stakeholder_needs)
    verification_links = build_verification_links(
        verification_cases
    )

    requirement = requirement_index[requirement_id]
    parent_id = str(requirement.get("parent", ""))

    parent_record = (
        requirement_index.get(parent_id)
        or need_index.get(parent_id)
    )

    return {
        "requirement_id": requirement_id,
        "parent_id": parent_id or None,
        "parent_exists": parent_record is not None,
        "component": requirement.get("component"),
        "verification_method": requirement.get(
            "verification_method"
        ),
        "verification_cases": verification_links.get(
            requirement_id,
            [],
        ),
    }
