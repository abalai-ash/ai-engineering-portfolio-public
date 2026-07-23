from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "traceability_records.json"


def load_records(path: Path = DATA_FILE) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def review_traceability(records: dict) -> dict:
    requirements = records.get("requirements", [])
    verification_cases = records.get("verification_cases", [])

    requirement_ids = {
        str(requirement["id"])
        for requirement in requirements
        if requirement.get("id")
    }

    linked_ids = {
        str(requirement_id)
        for case in verification_cases
        for requirement_id in case.get("requirement_ids", [])
    }

    missing_verification = sorted(requirement_ids - linked_ids)
    unknown_links = sorted(linked_ids - requirement_ids)

    coverage = (
        (len(requirement_ids) - len(missing_verification))
        / len(requirement_ids)
        if requirement_ids
        else 0.0
    )

    return {
        "requirement_count": len(requirement_ids),
        "verification_case_count": len(verification_cases),
        "missing_verification": missing_verification,
        "unknown_links": unknown_links,
        "coverage_percent": round(coverage * 100, 1),
    }


def main() -> None:
    summary = review_traceability(load_records())

    print("Systems Traceability Review")
    print(f"Requirements: {summary['requirement_count']}")
    print(f"Verification cases: {summary['verification_case_count']}")
    print(f"Coverage: {summary['coverage_percent']}%")

    missing = summary["missing_verification"]
    unknown = summary["unknown_links"]

    print("Missing verification:", ", ".join(missing) if missing else "none")
    print("Unknown links:", ", ".join(unknown) if unknown else "none")


if __name__ == "__main__":
    main()
