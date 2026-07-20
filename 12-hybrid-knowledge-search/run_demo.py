"""Run example grounded searches."""

from __future__ import annotations

import json
import sys
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent
SRC_DIR = PROJECT_DIR / "src"

sys.path.insert(0, str(SRC_DIR))

from answering import answer_question


def main() -> None:
    records = json.loads(
        (
            PROJECT_DIR
            / "data"
            / "records.json"
        ).read_text(encoding="utf-8")
    )

    questions = [
        (
            "Why can payment requests time out after the "
            "identity service slows down?"
        ),
        (
            "What should be inspected when an event backlog "
            "appears?"
        ),
        (
            "What was the payroll system's database password?"
        ),
    ]

    for question in questions:
        response = answer_question(
            question,
            records,
            limit=3,
        )

        print("=" * 72)
        print(f"Question: {question}")
        print(f"Status: {response['status']}")
        print(
            "Top score: "
            f"{response['confidence']['top_score']}"
        )
        print(f"Answer: {response['answer']}")

        if response["citations"]:
            print("Evidence:")

            for citation in response["citations"]:
                print(
                    f"- {citation['record_id']} "
                    f"({citation['score']})"
                )

        print()


if __name__ == "__main__":
    main()
