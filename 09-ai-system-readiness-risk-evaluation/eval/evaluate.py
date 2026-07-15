#!/usr/bin/env python3
"""Check expected recommendations for the synthetic readiness cases."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "src" / "readiness_evaluator.py"
DATA_PATH = ROOT / "data" / "system_proposals.json"
RESULTS_PATH = ROOT / "eval" / "eval_results.md"

spec = importlib.util.spec_from_file_location(
    "readiness_evaluator",
    MODULE_PATH,
)
if spec is None or spec.loader is None:
    raise RuntimeError("Could not load readiness evaluator.")

module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

EXPECTED = {
    "research_assistant_ready": "approve",
    "clinical_summary_incomplete": "block",
    "financial_risk_high": "block",
    "agent_workflow_review": "needs_review",
}


def main() -> int:
    proposals = json.loads(DATA_PATH.read_text(encoding="utf-8"))

    lines = [
        "# Evaluation Results",
        "",
        "| Case | Expected | Actual | Result |",
        "|---|---|---|---|",
    ]

    passed = 0

    for proposal in proposals:
        result = module.evaluate_system(proposal)
        expected = EXPECTED[proposal["id"]]
        actual = result["recommendation"]
        ok = actual == expected

        if ok:
            passed += 1

        label = "PASS" if ok else "FAIL"
        print(
            f"{label}: {proposal['id']} "
            f"expected={expected} actual={actual}"
        )

        lines.append(
            f"| `{proposal['id']}` | `{expected}` | "
            f"`{actual}` | **{label}** |"
        )

    total = len(proposals)

    lines.extend(
        [
            "",
            f"Evaluation complete: **{passed}/{total} passed**.",
            "",
            "These cases use synthetic proposals and transparent "
            "rule-based checks.",
            "",
        ]
    )

    RESULTS_PATH.write_text(
        "\n".join(lines),
        encoding="utf-8",
    )

    print(f"\nEvaluation complete: {passed}/{total} passed")
    print(f"Wrote {RESULTS_PATH}")

    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
