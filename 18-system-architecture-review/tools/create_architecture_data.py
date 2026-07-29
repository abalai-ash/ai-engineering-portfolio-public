from pathlib import Path
import json


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"


def write_json(filename: str, contents: object) -> None:
    path = DATA_DIR / filename
    path.write_text(
        json.dumps(contents, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {path.relative_to(ROOT)}")


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    context = {
        "system": "environmental_monitoring_system",
        "purpose": (
            "Coordinate a synthetic environmental monitoring request from "
            "planning through measurement collection, validation, and "
            "technical-review transfer."
        ),
        "external_actors": [
            {
                "id": "technical_reviewer",
                "interaction": "submits monitoring and investigation requests",
            },
            {
                "id": "condition_service",
                "interaction": "provides environmental-condition data",
            },
            {
                "id": "evidence_repository",
                "interaction": "accepts validated monitoring products",
            },
        ],
    }

    functions = [
        {
            "id": "F-001",
            "name": "validate monitoring request",
            "parent": None,
            "required_inputs": ["monitoring_request"],
            "produced_outputs": ["validated_request"],
        },
        {
            "id": "F-002",
            "name": "create monitoring plan",
            "parent": None,
            "required_inputs": [
                "validated_request",
                "condition_forecast",
            ],
            "produced_outputs": ["monitoring_plan"],
        },
        {
            "id": "F-003",
            "name": "configure instrument",
            "parent": None,
            "required_inputs": ["monitoring_plan"],
            "produced_outputs": ["instrument_configuration"],
        },
        {
            "id": "F-004",
            "name": "collect monitoring measurements",
            "parent": None,
            "required_inputs": [
                "instrument_configuration",
                "monitoring_plan",
            ],
            "produced_outputs": ["raw_measurements"],
        },
        {
            "id": "F-005",
            "name": "apply calibration",
            "parent": None,
            "required_inputs": [
                "raw_measurements",
                "calibration_reference",
            ],
            "produced_outputs": ["validated_measurement_product"],
        },
        {
            "id": "F-006",
            "name": "transfer monitoring product",
            "parent": None,
            "required_inputs": ["validated_measurement_product"],
            "produced_outputs": ["repository_receipt"],
        },
    ]

    logical_components = [
        {
            "id": "request_manager",
            "responsibility": "Validate and track monitoring requests",
        },
        {
            "id": "schedule_service",
            "responsibility": (
                "Create monitoring plans using requests and conditions"
            ),
        },
        {
            "id": "instrument_controller",
            "responsibility": (
                "Configure the synthetic sensor and collection state"
            ),
        },
        {
            "id": "acquisition_service",
            "responsibility": "Collect environmental measurement records",
        },
        {
            "id": "calibration_service",
            "responsibility": "Apply calibration and validation references",
        },
        {
            "id": "archive_adapter",
            "responsibility": (
                "Transfer validated products to an evidence repository"
            ),
        },
    ]

    physical_resources = [
        {
            "id": "operations_node",
            "type": "compute",
            "capacity_units": 8,
        },
        {
            "id": "instrument_node",
            "type": "instrument-control",
            "capacity_units": 4,
        },
        {
            "id": "processing_node",
            "type": "compute",
            "capacity_units": 12,
        },
        {
            "id": "local_storage",
            "type": "storage",
            "capacity_units": 20,
        },
    ]

    function_allocations = [
        {
            "function_id": "F-001",
            "component_id": "request_manager",
        },
        {
            "function_id": "F-002",
            "component_id": "schedule_service",
        },
        {
            "function_id": "F-003",
            "component_id": "instrument_controller",
        },
        {
            "function_id": "F-004",
            "component_id": "acquisition_service",
        },
        {
            "function_id": "F-005",
            "component_id": "calibration_service",
        },
        {
            "function_id": "F-006",
            "component_id": "archive_adapter",
        },
    ]

    resource_allocations = [
        {
            "component_id": "request_manager",
            "resource_id": "operations_node",
            "required_units": 1,
        },
        {
            "component_id": "schedule_service",
            "resource_id": "operations_node",
            "required_units": 2,
        },
        {
            "component_id": "instrument_controller",
            "resource_id": "instrument_node",
            "required_units": 2,
        },
        {
            "component_id": "acquisition_service",
            "resource_id": "instrument_node",
            "required_units": 2,
        },
        {
            "component_id": "calibration_service",
            "resource_id": "processing_node",
            "required_units": 5,
        },
        {
            "component_id": "archive_adapter",
            "resource_id": "processing_node",
            "required_units": 1,
        },
    ]

    interfaces = [
        {
            "id": "IF-001",
            "source": "request_manager",
            "target": "schedule_service",
            "data": "validated_request",
            "required_fields": [
                "request_id",
                "monitoring_area",
                "sampling_interval",
                "priority",
            ],
        },
        {
            "id": "IF-002",
            "source": "schedule_service",
            "target": "instrument_controller",
            "data": "monitoring_plan",
            "required_fields": [
                "request_id",
                "collection_window",
                "configuration_id",
            ],
        },
        {
            "id": "IF-003",
            "source": "instrument_controller",
            "target": "acquisition_service",
            "data": "instrument_configuration",
            "required_fields": [
                "configuration_id",
                "sensor_mode",
                "sampling_interval",
            ],
        },
        {
            "id": "IF-004",
            "source": "acquisition_service",
            "target": "calibration_service",
            "data": "raw_measurements",
            "required_fields": [
                "request_id",
                "measurement_ids",
                "timestamps",
            ],
        },
        {
            "id": "IF-005",
            "source": "calibration_service",
            "target": "archive_adapter",
            "data": "validated_measurement_product",
            "required_fields": [
                "request_id",
                "product_id",
                "validation_version",
            ],
        },
    ]

    dependencies = [
        {
            "before": "F-001",
            "after": "F-002",
        },
        {
            "before": "F-002",
            "after": "F-003",
        },
        {
            "before": "F-003",
            "after": "F-004",
        },
        {
            "before": "F-004",
            "after": "F-005",
        },
        {
            "before": "F-005",
            "after": "F-006",
        },
    ]

    design_alternatives = [
        {
            "id": "ALT-001",
            "name": "central processing",
            "scores": {
                "integration": 5,
                "maintainability": 4,
                "resilience": 2,
                "resource_efficiency": 4,
            },
        },
        {
            "id": "ALT-002",
            "name": "separated acquisition and processing",
            "scores": {
                "integration": 4,
                "maintainability": 4,
                "resilience": 4,
                "resource_efficiency": 3,
            },
        },
        {
            "id": "ALT-003",
            "name": "distributed services",
            "scores": {
                "integration": 3,
                "maintainability": 3,
                "resilience": 5,
                "resource_efficiency": 2,
            },
        },
    ]

    review_weights = {
        "integration": 0.30,
        "maintainability": 0.25,
        "resilience": 0.30,
        "resource_efficiency": 0.15,
    }

    records = {
        "context.json": context,
        "functions.json": functions,
        "logical_components.json": logical_components,
        "physical_resources.json": physical_resources,
        "function_allocations.json": function_allocations,
        "resource_allocations.json": resource_allocations,
        "interfaces.json": interfaces,
        "dependencies.json": dependencies,
        "design_alternatives.json": design_alternatives,
        "review_weights.json": review_weights,
    }

    for filename, contents in records.items():
        write_json(filename, contents)


if __name__ == "__main__":
    main()
