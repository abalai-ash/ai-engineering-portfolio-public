from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = PROJECT_ROOT / "src" / "rl_infrastructure_v2.py"
RUNS_DIR = PROJECT_ROOT / "runs"


def newest_run() -> Path:
    candidates = sorted(
        RUNS_DIR.glob("rl_agent_reliability_v2-*"),
        key=lambda path: path.stat().st_mtime,
    )
    if not candidates:
        raise RuntimeError("No v2 experiment run was created.")
    return candidates[-1]


def main() -> None:
    subprocess.run(
        [sys.executable, str(SCRIPT)],
        cwd=PROJECT_ROOT,
        check=True,
    )

    run_dir = newest_run()
    summary = json.loads(
        (run_dir / "summary.json").read_text(encoding="utf-8")
    )
    records = json.loads(
        (run_dir / "episode_records.json").read_text(encoding="utf-8")
    )

    checks = [
        (
            "all scenarios completed",
            summary["episodes_completed"] == summary["episodes_total"],
        ),
        (
            "all expected decisions passed",
            summary["episodes_passed"] == summary["episodes_total"],
        ),
        (
            "transient failure was retried",
            summary["retried_episodes"] >= 1,
        ),
        (
            "structured records were written",
            len(records) == summary["episodes_total"],
        ),
        (
            "timing metrics were recorded",
            all(record["duration_ms"] >= 0 for record in records),
        ),
        (
            "checkpoint was written",
            (run_dir / "checkpoint.json").exists(),
        ),
    ]

    passed = sum(result for _, result in checks)

    print("\nRL Infrastructure v2 Evaluation")
    print("=" * 36)
    for name, result in checks:
        print(f"{'PASS' if result else 'FAIL'}: {name}")

    print(f"\nEvaluation complete: {passed}/{len(checks)} passed")

    if passed != len(checks):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
