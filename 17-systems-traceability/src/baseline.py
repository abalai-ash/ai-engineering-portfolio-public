from __future__ import annotations

from typing import Any


Record = dict[str, Any]


def compare_baselines(
    previous: list[Record],
    current: list[Record],
) -> dict[str, list[str]]:
    """Report added, removed, and modified records."""
    previous_index = {
        str(record["id"]): record
        for record in previous
    }
    current_index = {
        str(record["id"]): record
        for record in current
    }

    previous_ids = set(previous_index)
    current_ids = set(current_index)

    added = sorted(current_ids - previous_ids)
    removed = sorted(previous_ids - current_ids)

    modified = sorted(
        record_id
        for record_id in previous_ids & current_ids
        if previous_index[record_id] != current_index[record_id]
    )

    return {
        "added": added,
        "removed": removed,
        "modified": modified,
    }
