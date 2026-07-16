from __future__ import annotations

import json
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parents[1]
REQUESTS_PATH = BASE_DIR / "data" / "customer_requests.json"


DOMAIN_QUESTIONS = {
    "enterprise_ai": [
        "Which sources are allowed to support an answer?",
        "Which users may access each source?",
        "When should the system abstain instead of answering?",
        "Who reviews high-impact or uncertain responses?",
        "How will retrieval quality and answer grounding be measured?",
    ],
    "robotics": [
        "Which coordinate frames and map conventions are used?",
        "How is each sensor calibrated and time-synchronized?",
        "What localization error is acceptable?",
        "How should the system respond to sensor dropout?",
        "How will map mismatch or environmental change be detected?",
    ],
    "scientific_computing": [
        "Which baseline should each method be compared against?",
        "Which hardware and runtime limits matter?",
        "How many repeated runs are needed?",
        "How will uncertainty and numerical error be reported?",
        "What evidence is required before selecting a method?",
    ],
}


COMMON_QUESTIONS = [
    "Who owns the system after launch?",
    "Which metric determines whether the project is successful?",
    "What failure would require stopping or rolling back the system?",
    "Which logs and outputs must be retained?",
    "Which assumptions still need to be validated?",
]


def load_requests(path: Path = REQUESTS_PATH) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, list):
        raise ValueError("Request file must contain a list.")

    return data


def validate_request(request: dict[str, Any]) -> list[str]:
    missing = []

    required_fields = [
        "request_id",
        "domain",
        "goal",
        "users",
        "data_sources",
        "requirements",
        "success_metrics",
    ]

    for field in required_fields:
        if field not in request:
            missing.append(field)

    if "users" in request and not isinstance(request["users"], list):
        missing.append("users must be a list")

    if "data_sources" in request and not isinstance(request["data_sources"], list):
        missing.append("data_sources must be a list")

    if "requirements" in request and not isinstance(request["requirements"], dict):
        missing.append("requirements must be an object")

    if "success_metrics" in request and not isinstance(
        request["success_metrics"], list
    ):
        missing.append("success_metrics must be a list")

    return missing


def summarize_data_sources(
    data_sources: list[dict[str, Any]],
) -> dict[str, Any]:
    type_counts: dict[str, int] = {}
    sensitive_sources = []

    for source in data_sources:
        source_type = str(source.get("type", "unknown"))
        sensitivity = str(source.get("sensitivity", "unknown"))
        name = str(source.get("name", "unnamed source"))

        type_counts[source_type] = type_counts.get(source_type, 0) + 1

        if sensitivity in {"restricted", "confidential", "sensitive"}:
            sensitive_sources.append(name)

    return {
        "source_count": len(data_sources),
        "source_types": type_counts,
        "sensitive_sources": sensitive_sources,
    }


def build_discovery_report(request: dict[str, Any]) -> dict[str, Any]:
    validation_errors = validate_request(request)

    if validation_errors:
        return {
            "request_id": request.get("request_id", "unknown"),
            "status": "invalid_request",
            "errors": validation_errors,
        }

    domain = request["domain"]
    domain_questions = DOMAIN_QUESTIONS.get(
        domain,
        ["Which technical constraints are specific to this domain?"],
    )

    data_summary = summarize_data_sources(request["data_sources"])

    open_questions = domain_questions + COMMON_QUESTIONS

    if data_summary["sensitive_sources"]:
        open_questions.append(
            "How will sensitive sources be protected in storage, retrieval, and logs?"
        )

    requirements = request["requirements"]

    missing_controls = []
    for control in ["monitoring", "rollback_plan"]:
        if not requirements.get(control, False):
            missing_controls.append(control)

    return {
        "request_id": request["request_id"],
        "domain": domain,
        "goal": request["goal"],
        "users": request["users"],
        "data_summary": data_summary,
        "success_metrics": request["success_metrics"],
        "open_questions": open_questions,
        "missing_controls": missing_controls,
        "status": "ready_for_solution_planning",
    }


def main() -> None:
    requests = load_requests()

    reports = [build_discovery_report(request) for request in requests]

    output_path = BASE_DIR / "examples" / "discovery_reports.json"
    output_path.write_text(
        json.dumps(reports, indent=2),
        encoding="utf-8",
    )

    print("Discovery reports")
    print("-----------------")

    for report in reports:
        print(
            f"{report['request_id']}: "
            f"{report['status']} "
            f"({len(report.get('open_questions', []))} questions)"
        )

    print(f"\nWrote {output_path}")


if __name__ == "__main__":
    main()
