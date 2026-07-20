"""Run the synthetic monitoring evaluation."""

from __future__ import annotations

import json
import sys
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_DIR / "src"

sys.path.insert(0, str(SRC_DIR))

from monitoring import choose_action, compare_metrics, load_metrics


def main() -> None:
    baseline = load_metrics(
        PROJECT_DIR / "data" / "baseline_metrics.json"
    )

    current = load_metrics(
        PROJECT_DIR / "data" / "current_metrics.json"
    )

    alerts = compare_metrics(baseline, current)
    decision = choose_action(alerts)

    results = {
        "baseline_version": baseline["model_version"],
        "current_version": current["model_version"],
        "alerts": alerts,
        "decision": decision,
        "scope": (
            "This local example uses synthetic metrics. "
            "It demonstrates monitoring rules and incident decisions. "
            "It is not a production monitoring service."
        ),
    }

    output_path = PROJECT_DIR / "eval" / "evaluation_results.json"

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(results, file, indent=2)
        file.write("\n")

    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
