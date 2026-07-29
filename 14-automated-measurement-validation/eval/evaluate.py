from __future__ import annotations

import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "measurement_cases.json"
)
JSON_OUTPUT = (
    PROJECT_ROOT
    / "eval"
    / "evaluation_results.json"
)
MARKDOWN_OUTPUT = (
    PROJECT_ROOT
    / "eval"
    / "evaluation_results.md"
)

sys.path.insert(0, str(SRC_DIR))

from measurement_system import evaluate_batch


def build_markdown(report: dict) -> str:
    lines = [
        "# Measurement Evaluation Results",
        "",
        f"Cases: {report['case_count']}",
        f"Passed: {report['pass_count']}",
        f"Warnings: {report['warning_count']}",
        f"Failed: {report['fail_count']}",
        (
            "Instrument errors: "
            + str(report["instrument_error_count"])
        ),
        "",
        (
            "| Case | Status | Samples | Errors | "
            "Drift | Summary |"
        ),
        "|---|---|---:|---:|---:|---|",
    ]

    for result in report["results"]:
        lines.append(
            "| "
            + result["case_id"]
            + " | "
            + result["status"]
            + " | "
            + str(result["collected_samples"])
            + "/"
            + str(result["requested_samples"])
            + " | "
            + str(len(result["errors"]))
            + " | "
            + str(result["drift"]["total_drift"])
            + " | "
            + result["summary"]
            + " |"
        )

    lines.extend(
        [
            "",
            (
                "Expected checks passed: "
                + str(
                    report[
                        "all_expected_checks_passed"
                    ]
                )
            ),
            "",
            report["scope"],
            "",
        ]
    )

    return "\n".join(lines)


def main() -> None:
    payload = json.loads(
        DATA_PATH.read_text(
            encoding="utf-8",
        )
    )

    report = evaluate_batch(
        payload["cases"],
        seed=int(payload["seed"]),
    )

    JSON_OUTPUT.write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8",
    )

    MARKDOWN_OUTPUT.write_text(
        build_markdown(report),
        encoding="utf-8",
    )

    print(json.dumps(report, indent=2))

    if not report["all_expected_checks_passed"]:
        raise SystemExit(
            "One or more expected outcomes failed."
        )


if __name__ == "__main__":
    main()
