from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "baseline_records.json"


def load_records(path: Path = DATA_FILE) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def review_baseline(records: dict) -> dict:
    approved = records.get("approved_baseline", {})
    proposed = records.get("proposed_release", {})

    approved_items = approved.get("items", {})
    proposed_items = proposed.get("items", {})

    changed_items = sorted(
        key
        for key in set(approved_items) | set(proposed_items)
        if approved_items.get(key) != proposed_items.get(key)
    )

    declared_affected = sorted(
        str(item)
        for item in proposed.get("affected_items", [])
    )

    undeclared_changes = sorted(set(changed_items) - set(declared_affected))
    unnecessary_affected = sorted(set(declared_affected) - set(changed_items))

    approvals = {
        str(item)
        for item in proposed.get("approvals", [])
    }
    required_approvals = {
        str(item)
        for item in proposed.get("required_approvals", [])
    }

    missing_approvals = sorted(required_approvals - approvals)
    rollback_recorded = bool(proposed.get("rollback_recorded"))

    release_ready = (
        not missing_approvals
        and not undeclared_changes
        and rollback_recorded
    )

    return {
        "baseline_id": approved.get("id"),
        "baseline_version": approved.get("version"),
        "release_id": proposed.get("id"),
        "release_version": proposed.get("version"),
        "changed_items": changed_items,
        "declared_affected_items": declared_affected,
        "undeclared_changes": undeclared_changes,
        "unnecessary_affected_items": unnecessary_affected,
        "missing_approvals": missing_approvals,
        "rollback_recorded": rollback_recorded,
        "release_ready": release_ready,
    }


def main() -> None:
    summary = review_baseline(load_records())

    print("Engineering Baseline Control Review")
    print(f"Approved baseline: {summary['baseline_id']} v{summary['baseline_version']}")
    print(f"Proposed release: {summary['release_id']} v{summary['release_version']}")
    print("Changed items:", ", ".join(summary["changed_items"]) or "none")
    print("Missing approvals:", ", ".join(summary["missing_approvals"]) or "none")
    print("Undeclared changes:", ", ".join(summary["undeclared_changes"]) or "none")
    print("Rollback recorded:", "yes" if summary["rollback_recorded"] else "no")
    print("Release ready:", "yes" if summary["release_ready"] else "no")


if __name__ == "__main__":
    main()
