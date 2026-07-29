from __future__ import annotations

from collections import defaultdict, deque
from typing import Any


Record = dict[str, Any]


def find_unallocated_functions(
    functions: list[Record],
    allocations: list[Record],
) -> list[str]:
    """Return functions without a logical-component allocation."""
    allocated = {
        str(record["function_id"])
        for record in allocations
    }

    return sorted(
        str(function["id"])
        for function in functions
        if str(function["id"]) not in allocated
    )


def find_duplicate_function_allocations(
    allocations: list[Record],
) -> dict[str, list[str]]:
    """Return functions assigned to more than one component."""
    assigned: dict[str, list[str]] = defaultdict(list)

    for record in allocations:
        assigned[str(record["function_id"])].append(
            str(record["component_id"])
        )

    return {
        function_id: sorted(component_ids)
        for function_id, component_ids in assigned.items()
        if len(component_ids) > 1
    }


def find_invalid_function_allocations(
    functions: list[Record],
    components: list[Record],
    allocations: list[Record],
) -> list[Record]:
    """Return allocations that reference unknown records."""
    function_ids = {
        str(function["id"])
        for function in functions
    }
    component_ids = {
        str(component["id"])
        for component in components
    }

    findings: list[Record] = []

    for record in allocations:
        function_id = str(record["function_id"])
        component_id = str(record["component_id"])

        if (
            function_id not in function_ids
            or component_id not in component_ids
        ):
            findings.append(
                {
                    "function_id": function_id,
                    "component_id": component_id,
                }
            )

    return findings


def review_interfaces(
    components: list[Record],
    interfaces: list[Record],
) -> list[Record]:
    """Return interface records needing review."""
    component_ids = {
        str(component["id"])
        for component in components
    }

    findings: list[Record] = []

    for interface in interfaces:
        issues: list[str] = []
        source = str(interface.get("source", ""))
        target = str(interface.get("target", ""))
        required_fields = interface.get(
            "required_fields",
            [],
        )

        if source not in component_ids:
            issues.append("unknown source component")

        if target not in component_ids:
            issues.append("unknown target component")

        if source == target:
            issues.append("source and target are identical")

        if not interface.get("data"):
            issues.append("data item is missing")

        if not required_fields:
            issues.append("required fields are missing")

        if len(required_fields) != len(set(required_fields)):
            issues.append("required fields contain duplicates")

        if issues:
            findings.append(
                {
                    "interface_id": str(interface["id"]),
                    "issues": issues,
                }
            )

    return findings


def find_resource_overloads(
    resources: list[Record],
    allocations: list[Record],
) -> list[Record]:
    """Return resources whose assigned demand exceeds capacity."""
    capacities = {
        str(resource["id"]): float(
            resource.get("capacity_units", 0)
        )
        for resource in resources
    }

    usage: dict[str, float] = defaultdict(float)

    for allocation in allocations:
        resource_id = str(allocation["resource_id"])
        usage[resource_id] += float(
            allocation.get("required_units", 0)
        )

    return sorted(
        [
            {
                "resource_id": resource_id,
                "capacity_units": capacities[resource_id],
                "assigned_units": assigned_units,
            }
            for resource_id, assigned_units in usage.items()
            if (
                resource_id in capacities
                and assigned_units > capacities[resource_id]
            )
        ],
        key=lambda record: record["resource_id"],
    )


def find_invalid_resource_allocations(
    components: list[Record],
    resources: list[Record],
    allocations: list[Record],
) -> list[Record]:
    """Return resource allocations with unknown references."""
    component_ids = {
        str(component["id"])
        for component in components
    }
    resource_ids = {
        str(resource["id"])
        for resource in resources
    }

    findings: list[Record] = []

    for record in allocations:
        component_id = str(record["component_id"])
        resource_id = str(record["resource_id"])

        if (
            component_id not in component_ids
            or resource_id not in resource_ids
        ):
            findings.append(
                {
                    "component_id": component_id,
                    "resource_id": resource_id,
                }
            )

    return findings


def find_dependency_cycles(
    functions: list[Record],
    dependencies: list[Record],
) -> list[str]:
    """Return function identifiers that remain in dependency cycles."""
    function_ids = {
        str(function["id"])
        for function in functions
    }

    adjacency: dict[str, list[str]] = defaultdict(list)
    indegree = {
        function_id: 0
        for function_id in function_ids
    }

    for dependency in dependencies:
        before = str(dependency["before"])
        after = str(dependency["after"])

        if before in function_ids and after in function_ids:
            adjacency[before].append(after)
            indegree[after] += 1

    queue = deque(
        sorted(
            function_id
            for function_id, degree in indegree.items()
            if degree == 0
        )
    )

    visited: set[str] = set()

    while queue:
        function_id = queue.popleft()
        visited.add(function_id)

        for dependent_id in adjacency.get(
            function_id,
            [],
        ):
            indegree[dependent_id] -= 1

            if indegree[dependent_id] == 0:
                queue.append(dependent_id)

    return sorted(function_ids - visited)


def review_dependencies(
    functions: list[Record],
    dependencies: list[Record],
) -> list[Record]:
    """Return dependencies that reference unknown functions."""
    function_ids = {
        str(function["id"])
        for function in functions
    }

    findings: list[Record] = []

    for dependency in dependencies:
        before = str(dependency["before"])
        after = str(dependency["after"])

        if before not in function_ids or after not in function_ids:
            findings.append(
                {
                    "before": before,
                    "after": after,
                }
            )

    return findings
