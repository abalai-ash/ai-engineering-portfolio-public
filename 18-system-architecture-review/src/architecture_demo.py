from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "architecture_records.json"


def load_records(path: Path = DATA_FILE) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def review_architecture(records: dict) -> dict:
    functions = records.get("functions", [])
    components = records.get("components", [])
    interfaces = records.get("interfaces", [])

    component_ids = {
        str(component["id"])
        for component in components
        if component.get("id")
    }

    unallocated_functions = sorted(
        str(function["id"])
        for function in functions
        if not function.get("component")
    )

    unknown_allocations = sorted(
        str(function["id"])
        for function in functions
        if function.get("component")
        and str(function["component"]) not in component_ids
    )

    unknown_interface_components = sorted({
        str(endpoint)
        for interface in interfaces
        for endpoint in (interface.get("source"), interface.get("target"))
        if endpoint and str(endpoint) not in component_ids
    })

    allocated_count = (
        len(functions)
        - len(unallocated_functions)
        - len(unknown_allocations)
    )

    allocation_percent = (
        allocated_count / len(functions) * 100
        if functions
        else 0.0
    )

    return {
        "function_count": len(functions),
        "component_count": len(components),
        "interface_count": len(interfaces),
        "unallocated_functions": unallocated_functions,
        "unknown_allocations": unknown_allocations,
        "unknown_interface_components": unknown_interface_components,
        "allocation_percent": round(allocation_percent, 1),
    }


def main() -> None:
    summary = review_architecture(load_records())

    print("System Architecture Review")
    print(f"Functions: {summary['function_count']}")
    print(f"Components: {summary['component_count']}")
    print(f"Interfaces: {summary['interface_count']}")
    print(f"Function allocation: {summary['allocation_percent']}%")

    unallocated = summary["unallocated_functions"]
    unknown = summary["unknown_allocations"]
    interface_issues = summary["unknown_interface_components"]

    print("Unallocated functions:", ", ".join(unallocated) if unallocated else "none")
    print("Unknown allocations:", ", ".join(unknown) if unknown else "none")
    print("Unknown interface components:", ", ".join(interface_issues) if interface_issues else "none")


if __name__ == "__main__":
    main()
