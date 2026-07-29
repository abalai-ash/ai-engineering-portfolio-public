from __future__ import annotations

import csv
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from architecture_review import (
    find_dependency_cycles,
    find_duplicate_function_allocations,
    find_invalid_function_allocations,
    find_invalid_resource_allocations,
    find_resource_overloads,
    find_unallocated_functions,
    review_dependencies,
    review_interfaces,
)
from trade_study import (
    rank_alternatives,
    sensitivity_review,
)


def load_json(filename: str):
    path = ROOT / "data" / filename
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    context = load_json("context.json")
    functions = load_json("functions.json")
    components = load_json("logical_components.json")
    resources = load_json("physical_resources.json")
    function_allocations = load_json(
        "function_allocations.json"
    )
    resource_allocations = load_json(
        "resource_allocations.json"
    )
    interfaces = load_json("interfaces.json")
    dependencies = load_json("dependencies.json")
    alternatives = load_json("design_alternatives.json")
    weights = load_json("review_weights.json")

    reports_dir = ROOT / "reports"
    reports_dir.mkdir(exist_ok=True)

    findings = {
        "unallocated_functions": find_unallocated_functions(
            functions,
            function_allocations,
        ),
        "duplicate_function_allocations": (
            find_duplicate_function_allocations(
                function_allocations
            )
        ),
        "invalid_function_allocations": (
            find_invalid_function_allocations(
                functions,
                components,
                function_allocations,
            )
        ),
        "interface_findings": review_interfaces(
            components,
            interfaces,
        ),
        "resource_overloads": find_resource_overloads(
            resources,
            resource_allocations,
        ),
        "invalid_resource_allocations": (
            find_invalid_resource_allocations(
                components,
                resources,
                resource_allocations,
            )
        ),
        "dependency_findings": review_dependencies(
            functions,
            dependencies,
        ),
        "dependency_cycles": find_dependency_cycles(
            functions,
            dependencies,
        ),
    }

    ranking = rank_alternatives(
        alternatives,
        weights,
    )

    sensitivity = sensitivity_review(
        alternatives,
        {
            "balanced": weights,
            "resilience_emphasis": {
                "integration": 0.20,
                "maintainability": 0.20,
                "resilience": 0.50,
                "resource_efficiency": 0.10,
            },
            "integration_emphasis": {
                "integration": 0.50,
                "maintainability": 0.20,
                "resilience": 0.20,
                "resource_efficiency": 0.10,
            },
        },
    )

    summary = {
        "system": context["system"],
        "functions": len(functions),
        "logical_components": len(components),
        "physical_resources": len(resources),
        "interfaces": len(interfaces),
        "findings": findings,
        "ranking": ranking,
        "sensitivity": sensitivity,
    }

    summary_path = reports_dir / "architecture_summary.json"
    summary_path.write_text(
        json.dumps(summary, indent=2) + "\n",
        encoding="utf-8",
    )

    allocation_path = reports_dir / "function_allocations.csv"

    with allocation_path.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.writer(file)
        writer.writerow(
            [
                "function_id",
                "function_name",
                "component_id",
            ]
        )

        function_index = {
            function["id"]: function
            for function in functions
        }

        for record in function_allocations:
            function = function_index[
                record["function_id"]
            ]

            writer.writerow(
                [
                    record["function_id"],
                    function["name"],
                    record["component_id"],
                ]
            )

    report_lines = [
        "# System Architecture Review",
        "",
        f"System: {context['system']}",
        f"Functions: {len(functions)}",
        f"Logical components: {len(components)}",
        f"Physical resources: {len(resources)}",
        f"Interfaces: {len(interfaces)}",
        "",
        "## Review findings",
        "",
    ]

    finding_count = 0

    for name, value in findings.items():
        count = len(value)
        finding_count += count
        report_lines.append(
            f"- {name.replace('_', ' ')}: {count}"
        )

    report_lines.extend(
        [
            "",
            "## Architecture alternatives",
            "",
        ]
    )

    for record in ranking:
        report_lines.append(
            f"- {record['id']} ({record['name']}): "
            f"{record['weighted_score']:.4f}"
        )

    report_lines.extend(
        [
            "",
            "## Sensitivity leaders",
            "",
        ]
    )

    for name, leader in sorted(sensitivity.items()):
        report_lines.append(
            f"- {name.replace('_', ' ')}: {leader}"
        )

    report_lines.extend(
        [
            "",
            f"Total review findings: {finding_count}",
        ]
    )

    report_path = reports_dir / "architecture_report.md"
    report_path.write_text(
        "\n".join(report_lines) + "\n",
        encoding="utf-8",
    )

    print(
        json.dumps(
            {
                "functions": len(functions),
                "components": len(components),
                "interfaces": len(interfaces),
                "review_findings": finding_count,
                "leading_alternative": ranking[0]["id"],
                "reports": [
                    str(summary_path.relative_to(ROOT)),
                    str(allocation_path.relative_to(ROOT)),
                    str(report_path.relative_to(ROOT)),
                ],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
