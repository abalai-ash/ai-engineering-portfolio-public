from pathlib import Path
import csv
import sys


BASE_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = BASE_DIR / "src"
DATA_DIR = BASE_DIR / "data"
EVAL_FILE = BASE_DIR / "eval" / "eval_cases.csv"
RESULTS_FILE = BASE_DIR / "eval" / "eval_results.md"

sys.path.append(str(SRC_DIR))

from ranker_v1 import load_csv, rank_notifications  # noqa: E402


def main():
    users = load_csv(DATA_DIR / "users.csv")
    notifications = load_csv(DATA_DIR / "notifications.csv")

    users_by_id = {user["user_id"]: user for user in users}

    results = []

    with EVAL_FILE.open("r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            user = users_by_id[row["user_id"]]
            ranked = rank_notifications(user, notifications)

            top_item = ranked[0]
            expected = row["expected_top_notification"]
            passed = top_item["notification_id"] == expected

            results.append({
                "user_id": row["user_id"],
                "expected": expected,
                "top": top_item["notification_id"],
                "top_score": top_item["score"],
                "matching_tags": top_item["matching_tags"],
                "passed": passed,
                "reason": row["reason"],
            })

    passed_count = sum(1 for item in results if item["passed"])
    total = len(results)

    lines = [
        "# Notification Ranking Evaluation Results",
        "",
        f"Passed: {passed_count}/{total}",
        "",
        "| User | Expected top | Actual top | Score | Matching tags | Result |",
        "|---|---|---|---:|---|---|",
    ]

    for item in results:
        result_text = "PASS" if item["passed"] else "FAIL"

        lines.append(
            f"| {item['user_id']} | {item['expected']} | {item['top']} | "
            f"{item['top_score']} | {item['matching_tags']} | {result_text} |"
        )

    lines.extend([
        "",
        "## What this evaluation checks",
        "",
        "This evaluation checks whether the highest-ranked notification matches the expected top result for each fake user.",
        "It also records the top score and matching tags so the ranking decision is easier to inspect.",
        "",
        "## Limitations",
        "",
        "This demo uses fake data and hand-written weights. It does not train on real user behavior.",
    ])

    RESULTS_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Evaluation complete: {passed_count}/{total} passed")
    print(f"Results written to: {RESULTS_FILE}")


if __name__ == "__main__":
    main()
