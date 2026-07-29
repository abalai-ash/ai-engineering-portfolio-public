from __future__ import annotations

from collections import deque
from typing import Any

from traceability import (
    build_child_links,
    build_verification_links,
)


Record = dict[str, Any]


def analyze_change(
    changed_requirement_ids: list[str],
    requirements: list[Record],
    verification_cases: list[Record],
) -> dict[str, list[str]]:
    """Find downstream requirements, cases, and components."""
    child_links = build_child_links(requirements)
    verification_links = build_verification_links(
        verification_cases
    )

    impacted_requirements: set[str] = set()
    queue = deque(
        str(requirement_id)
        for requirement_id in changed_requirement_ids
    )

    while queue:
        requirement_id = queue.popleft()

        if requirement_id in impacted_requirements:
            continue

        impacted_requirements.add(requirement_id)

        for child_id in child_links.get(
            requirement_id,
            [],
        ):
            queue.append(child_id)

    impacted_cases = sorted(
        {
            case_id
            for requirement_id in impacted_requirements
            for case_id in verification_links.get(
                requirement_id,
                [],
            )
        }
    )

    impacted_components = sorted(
        {
            str(requirement["component"])
            for requirement in requirements
            if str(requirement["id"])
            in impacted_requirements
            and requirement.get("component")
        }
    )

    return {
        "requirements": sorted(impacted_requirements),
        "verification_cases": impacted_cases,
        "components": impacted_components,
    }
