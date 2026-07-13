from __future__ import annotations

import argparse
import hashlib
import json
import random
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from rl_loop_v1 import demo_scenarios, run_episode


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = PROJECT_ROOT / "config" / "experiment_v2.json"
RUNS_DIR = PROJECT_ROOT / "runs"


@dataclass
class EpisodeRecord:
    episode_index: int
    scenario: str
    chosen_action: str
    expected_action: str
    reward: int
    passed: bool
    duration_ms: float
    attempt: int
    status: str
    error: str | None = None


def load_config(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        config = json.load(handle)

    required = {
        "experiment_name",
        "seed",
        "max_retries",
        "checkpoint_every",
        "simulate_failure_once",
    }
    missing = sorted(required - set(config))
    if missing:
        raise ValueError(f"Missing configuration keys: {missing}")

    return config


def make_run_id(config: dict[str, Any]) -> str:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    stable_config = json.dumps(config, sort_keys=True).encode("utf-8")
    digest = hashlib.sha256(stable_config).hexdigest()[:8]
    return f"{config['experiment_name']}-{timestamp}-{digest}"


def save_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def load_checkpoint(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def execute_episode(
    scenario: Any,
    episode_index: int,
    max_retries: int,
    simulate_failure_once: bool,
) -> EpisodeRecord:
    last_error: str | None = None

    for attempt in range(1, max_retries + 2):
        start = time.perf_counter()

        try:
            if simulate_failure_once and episode_index == 1 and attempt == 1:
                raise RuntimeError("Simulated transient research-run failure")

            result = run_episode(scenario)
            duration_ms = (time.perf_counter() - start) * 1000.0

            return EpisodeRecord(
                episode_index=episode_index,
                scenario=result["scenario"],
                chosen_action=result["chosen_action"],
                expected_action=result["expected_action"],
                reward=result["reward"],
                passed=result["passed"],
                duration_ms=round(duration_ms, 3),
                attempt=attempt,
                status="completed",
            )

        except Exception as exc:
            duration_ms = (time.perf_counter() - start) * 1000.0
            last_error = f"{type(exc).__name__}: {exc}"

            if attempt > max_retries:
                return EpisodeRecord(
                    episode_index=episode_index,
                    scenario=scenario.name,
                    chosen_action="not_completed",
                    expected_action=scenario.expected_action,
                    reward=0,
                    passed=False,
                    duration_ms=round(duration_ms, 3),
                    attempt=attempt,
                    status="failed",
                    error=last_error,
                )

    raise RuntimeError(last_error or "Unexpected episode failure")


def summarize(records: list[EpisodeRecord], run_id: str) -> dict[str, Any]:
    completed = [record for record in records if record.status == "completed"]
    failures = [record for record in records if record.status == "failed"]

    passed = sum(record.passed for record in records)
    total_reward = sum(record.reward for record in records)
    retried = sum(record.attempt > 1 for record in records)
    total_duration = sum(record.duration_ms for record in records)

    return {
        "run_id": run_id,
        "episodes_total": len(records),
        "episodes_completed": len(completed),
        "episodes_failed": len(failures),
        "episodes_passed": passed,
        "pass_rate": round(passed / len(records), 3) if records else 0.0,
        "total_reward": total_reward,
        "retried_episodes": retried,
        "total_duration_ms": round(total_duration, 3),
        "mean_episode_duration_ms": (
            round(total_duration / len(records), 3) if records else 0.0
        ),
    }


def run_experiment(config_path: Path, resume: bool = False) -> Path:
    config = load_config(config_path)
    random.seed(config["seed"])

    run_id = make_run_id(config)
    run_dir = RUNS_DIR / run_id
    checkpoint_path = run_dir / "checkpoint.json"
    records_path = run_dir / "episode_records.json"
    summary_path = run_dir / "summary.json"
    metadata_path = run_dir / "run_metadata.json"

    scenarios = demo_scenarios()
    records: list[EpisodeRecord] = []
    start_index = 0

    if resume:
        existing_runs = sorted(
            RUNS_DIR.glob(f"{config['experiment_name']}-*"),
            key=lambda path: path.stat().st_mtime,
        )
        if existing_runs:
            run_dir = existing_runs[-1]
            run_id = run_dir.name
            checkpoint_path = run_dir / "checkpoint.json"
            records_path = run_dir / "episode_records.json"
            summary_path = run_dir / "summary.json"
            metadata_path = run_dir / "run_metadata.json"

            checkpoint = load_checkpoint(checkpoint_path)
            if checkpoint:
                records = [
                    EpisodeRecord(**item)
                    for item in checkpoint.get("records", [])
                ]
                start_index = checkpoint.get("next_episode_index", 0)

    run_dir.mkdir(parents=True, exist_ok=True)

    save_json(
        metadata_path,
        {
            "run_id": run_id,
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
            "config": config,
            "config_path": str(config_path.relative_to(PROJECT_ROOT)),
            "python_random_seed": config["seed"],
        },
    )

    for index in range(start_index, len(scenarios)):
        record = execute_episode(
            scenario=scenarios[index],
            episode_index=index,
            max_retries=config["max_retries"],
            simulate_failure_once=config["simulate_failure_once"],
        )
        records.append(record)

        if (
            (index + 1) % config["checkpoint_every"] == 0
            or index == len(scenarios) - 1
        ):
            save_json(
                checkpoint_path,
                {
                    "run_id": run_id,
                    "next_episode_index": index + 1,
                    "records": [asdict(item) for item in records],
                },
            )

    save_json(records_path, [asdict(item) for item in records])
    save_json(summary_path, summarize(records, run_id))

    print(f"Run ID: {run_id}")
    print(f"Run directory: {run_dir}")
    print(json.dumps(summarize(records, run_id), indent=2))

    return run_dir


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the deterministic RL-style agent reliability experiment."
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG,
        help="Path to the experiment JSON configuration.",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume the newest compatible checkpoint.",
    )
    args = parser.parse_args()

    run_experiment(args.config, resume=args.resume)


if __name__ == "__main__":
    main()
