from pathlib import Path
import csv


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"


WEIGHTS = {
    "interest": 3,
    "urgency": 2,
    "freshness": 1,
    "channel": 1,
}


def load_csv(path):
    rows = []

    with path.open("r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            rows.append(row)

    return rows


def split_tags(text):
    if not text:
        return set()

    return set(tag.strip() for tag in text.split(";") if tag.strip())


def score_breakdown(user, notification):
    user_interests = split_tags(user["interests"])
    notification_tags = split_tags(notification["tags"])

    matching_tags = sorted(user_interests & notification_tags)

    interest_score = len(matching_tags)
    urgency_score = int(notification["urgency"])
    freshness_score = int(notification["freshness"])
    channel_score = 1 if user["preferred_channel"] == notification["channel"] else 0

    total = (
        interest_score * WEIGHTS["interest"]
        + urgency_score * WEIGHTS["urgency"]
        + freshness_score * WEIGHTS["freshness"]
        + channel_score * WEIGHTS["channel"]
    )

    return {
        "interest_score": interest_score,
        "urgency_score": urgency_score,
        "freshness_score": freshness_score,
        "channel_score": channel_score,
        "matching_tags": matching_tags,
        "total_score": total,
    }


def score_notification(user, notification):
    return score_breakdown(user, notification)["total_score"]


def rank_notifications(user, notifications):
    ranked = []

    for notification in notifications:
        breakdown = score_breakdown(user, notification)

        item = notification.copy()
        item["score"] = breakdown["total_score"]
        item["matching_tags"] = ";".join(breakdown["matching_tags"])
        item["interest_score"] = breakdown["interest_score"]
        item["urgency_score"] = breakdown["urgency_score"]
        item["freshness_score"] = breakdown["freshness_score"]
        item["channel_score"] = breakdown["channel_score"]

        ranked.append(item)

    ranked.sort(
        key=lambda item: (
            item["score"],
            int(item["urgency"]),
            int(item["freshness"]),
            item["notification_id"],
        ),
        reverse=True,
    )

    return ranked


def print_ranked_results(user, ranked):
    print(f"User: {user['user_id']}")
    print(f"Interests: {user['interests']}")
    print(f"Preferred channel: {user['preferred_channel']}")
    print()

    print("Ranked notifications:")
    print()

    for item in ranked:
        print(f"{item['notification_id']} | score {item['score']} | {item['title']}")
        print(f"tags: {item['tags']}")
        print(f"matching tags: {item['matching_tags'] or 'none'}")
        print(
            "breakdown: "
            f"interest={item['interest_score']}, "
            f"urgency={item['urgency_score']}, "
            f"freshness={item['freshness_score']}, "
            f"channel={item['channel_score']}"
        )
        print()


def main():
    users = load_csv(DATA_DIR / "users.csv")
    notifications = load_csv(DATA_DIR / "notifications.csv")

    print("Notification Relevance Ranker v2")
    print("Available users:", ", ".join(user["user_id"] for user in users))
    print()

    user_id = input("Choose a user id: ").strip()

    selected_user = None
    for user in users:
        if user["user_id"] == user_id:
            selected_user = user
            break

    if selected_user is None:
        print("User not found.")
        return

    ranked = rank_notifications(selected_user, notifications)
    print()
    print_ranked_results(selected_user, ranked)


if __name__ == "__main__":
    main()
