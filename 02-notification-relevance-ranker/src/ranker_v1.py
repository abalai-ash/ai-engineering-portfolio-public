from pathlib import Path
import csv


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"


def load_csv(path):
    rows = []

    with path.open("r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            rows.append(row)

    return rows


def split_tags(text):
    return set(text.split(";"))


def score_notification(user, notification):
    user_interests = split_tags(user["interests"])
    notification_tags = split_tags(notification["tags"])

    interest_score = len(user_interests & notification_tags)
    urgency_score = int(notification["urgency"])
    freshness_score = int(notification["freshness"])
    channel_score = 1 if user["preferred_channel"] == notification["channel"] else 0

    total = (
        interest_score * 3
        + urgency_score * 2
        + freshness_score
        + channel_score
    )

    return total


def rank_notifications(user, notifications):
    ranked = []

    for notification in notifications:
        score = score_notification(user, notification)
        item = notification.copy()
        item["score"] = score
        ranked.append(item)

    ranked.sort(key=lambda item: item["score"], reverse=True)
    return ranked


def print_ranked_results(user, ranked):
    print(f"User: {user['user_id']}")
    print(f"Interests: {user['interests']}")
    print()

    print("Ranked notifications:")
    print()

    for item in ranked:
        print(f"{item['notification_id']} | score {item['score']} | {item['title']}")
        print(f"tags: {item['tags']}")
        print()


def main():
    users = load_csv(DATA_DIR / "users.csv")
    notifications = load_csv(DATA_DIR / "notifications.csv")

    print("Notification Relevance Ranker v1")
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
