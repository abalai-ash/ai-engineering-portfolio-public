from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
RESULTS_FILE = PROJECT_ROOT / "eval" / "eval_results.md"

sys.path.insert(0, str(SRC_DIR))

from rl_loop_v1 import demo_scenarios, run_episode


def main():
    scenarios = demo_scenarios()
    results = []

    for scenario in scenarios:
        result = run_episode(scenario)
        results.append(result)

    passed_count = sum(1 for item in results if item["passed"])
    total_reward = sum(item["reward"] for item in results)
    total = len(results)

    lines = [
        "# RL Agent Evaluation Loop Results",
        "",
        f"Passed: {passed_count}/{total}",
        f"Total reward: {total_reward}",
        "",
        "| Scenario | Risk level | Expected action | Chosen action | Reward | Result |",
        "|---|---|---|---|---|---|"
    ]

    for item in results:
        result_text = "PASS" if item["passed"] else "FAIL"
        lines.append(
            f"| {item['scenario']} | {item['risk_level']} | {item['expected_action']} | {item['chosen_action']} | {item['reward']} | {result_text} |"
        )

    lines.extend([
        "",
        "## Notes",
        "",
        "This evaluation checks whether the agent chooses the expected action for each scenario.",
        "The reward score is a simple proxy for behavior quality, not a production reinforcement learning reward model.",
        "The goal is to show the structure of an agent evaluation loop: define scenarios, choose actions, assign rewards, and inspect outcomes."
    ])

    RESULTS_FILE.write_text("\n".join(lines), encoding="utf-8")

    print(f"Evaluation complete: {passed_count}/{total} passed")
    print(f"Total reward: {total_reward}")
    print(f"Results written to: {RESULTS_FILE}")


if __name__ == "__main__":
    main()
