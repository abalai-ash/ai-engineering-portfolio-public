from __future__ import annotations

import csv
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from baseline_review import (
    compare_baselines,
    review_configuration_items,
    undocumented_differences,
)
from change_review import (
    affected_item_summary,
    review_approval_coverage,
    review_change_requests,
)
from release_review import (
    review_release,
    review_rollback_records,
)


def load_json(filename: str):
    path = ROOT / "data" / filename
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    configuration_items = load_json(
        "configuration_items.json"
    )
    previous_baseline = load_json(
        "baseline_previous.json"
    )
    current_baseline = load_json(
        "baseline_current.json"
    )
    change_requests = load_json(
        "change_requests.json"
    )
    reviews = load_json("reviews.json")
    approvals = load_json("approvals.json")
    releases = load_json("releases.json")
    rollback_records = load_json(
        "rollback_records.json"
    )

    reports_dir = ROOT / "reports"
    reports_dir.mkdir(exist_ok=True)

    baseline_findings = review_configuration_items(
        configuration_items,
        current_baseline,
    )

    differences = compare_baselines(
        previous_baseline,
        current_baseline,
    )

    undocumented = undocumented_differences(
        differences,
        change_requests,
    )

    change_findings = review_change_requests(
        change_requests,
        configuration_items,
    )

    approval_findings = review_approval_coverage(
        change_requests,
        reviews,
        approvals,
    )

    affected_items = affected_item_summary(
        change_requests
    )

    approved_change_ids = {
        str(record["change_request_id"])
        for record in approvals
        if record.get("status") == "approved"
    }

    current_release = next(
        release
        for release in releases
        if (
            release.get("baseline_id")
            == current_baseline.get("id")
        )
    )

    release_findings = review_release(
        current_release,
        current_baseline,
        approved_change_ids,
    )

    rollback_findings = review_rollback_records(
        rollback_records,
        releases,
    )

    approved_changes = [
        change
        for change in change_requests
        if change.get("status") == "approved"
    ]

    pending_changes = [
        change
        for change in change_requests
        if change.get("status") != "approved"
    ]

    summary = {
        "configuration_items": len(
            configuration_items
        ),
        "previous_baseline": previous_baseline["id"],
        "current_baseline": current_baseline["id"],
        "baseline_findings": baseline_findings,
        "recorded_differences": differences,
        "undocumented_differences": undocumented,
        "approved_changes": [
            change["id"]
            for change in approved_changes
        ],
        "pending_changes": [
            change["id"]
            for change in pending_changes
        ],
        "change_findings": change_findings,
        "approval_findings": approval_findings,
        "affected_items": affected_items,
        "release_findings": release_findings,
        "rollback_findings": rollback_findings,
    }

    summary_path = (
        reports_dir / "baseline_summary.json"
    )
    summary_path.write_text(
        json.dumps(summary, indent=2) + "\n",
        encoding="utf-8",
    )

    comparison_path = (
        reports_dir / "baseline_comparison.csv"
    )

    with comparison_path.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.writer(file)
        writer.writerow(
            [
                "configuration_item_id",
                "change_type",
                "field",
                "previous_value",
                "current_value",
            ]
        )

        for difference in differences:
            writer.writerow(
                [
                    difference[
                        "configuration_item_id"
                    ],
                    difference["change_type"],
                    difference.get("field"),
                    json.dumps(
                        difference.get(
                            "previous_value"
                        )
                    ),
                    json.dumps(
                        difference.get(
                            "current_value"
                        )
                    ),
                ]
            )

    report_lines = [
        "# Engineering Baseline Control Report",
        "",
        (
            "Previous baseline: "
            + str(previous_baseline["id"])
            + " / "
            + str(previous_baseline["version"])
        ),
        (
            "Current baseline: "
            + str(current_baseline["id"])
            + " / "
            + str(current_baseline["version"])
        ),
        "",
        "## Baseline review",
        "",
        (
            "- Configuration findings: "
            + str(len(baseline_findings))
        ),
        (
            "- Recorded differences: "
            + str(len(differences))
        ),
        (
            "- Undocumented value differences: "
            + str(len(undocumented))
        ),
        "",
        "## Change review",
        "",
        (
            "- Approved changes: "
            + (
                ", ".join(
                    change["id"]
                    for change in approved_changes
                )
                or "none"
            )
        ),
        (
            "- Pending changes: "
            + (
                ", ".join(
                    change["id"]
                    for change in pending_changes
                )
                or "none"
            )
        ),
        (
            "- Change records with findings: "
            + str(len(change_findings))
        ),
        (
            "- Approved changes with review findings: "
            + str(len(approval_findings))
        ),
        "",
        "## Release and recovery",
        "",
        (
            "- Release findings: "
            + str(len(release_findings))
        ),
        (
            "- Rollback records with findings: "
            + str(len(rollback_findings))
        ),
        "",
        "## Affected configuration items",
        "",
    ]

    for item_id, change_ids in affected_items.items():
        report_lines.append(
            f"- {item_id}: {', '.join(change_ids)}"
        )

    report_path = (
        reports_dir / "baseline_report.md"
    )
    report_path.write_text(
        "\n".join(report_lines) + "\n",
        encoding="utf-8",
    )

    print(
        json.dumps(
            {
                "configuration_items": len(
                    configuration_items
                ),
                "recorded_differences": len(
                    differences
                ),
                "undocumented_differences": len(
                    undocumented
                ),
                "approved_changes": len(
                    approved_changes
                ),
                "pending_changes": len(
                    pending_changes
                ),
                "release_findings": len(
                    release_findings
                ),
                "rollback_findings": len(
                    rollback_findings
                ),
                "reports": [
                    str(
                        summary_path.relative_to(ROOT)
                    ),
                    str(
                        comparison_path.relative_to(
                            ROOT
                        )
                    ),
                    str(
                        report_path.relative_to(ROOT)
                    ),
                ],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
