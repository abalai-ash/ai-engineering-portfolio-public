import os
from datetime import datetime, UTC


APP_NAME = os.getenv("APP_NAME", "Cloud ML Demo")
APP_ENV = os.getenv("APP_ENV", "local")


HIGH_PRIORITY_WORDS = {
    "urgent",
    "deadline",
    "failure",
    "error",
    "blocked",
    "security"
}

AI_CLOUD_WORDS = {
    "ai",
    "model",
    "cloud",
    "api",
    "deploy",
    "deployment",
    "pipeline"
}

ACTION_WORDS = {
    "review",
    "fix",
    "check",
    "send",
    "update",
    "run"
}


def tokenize(text):
    cleaned = text.lower()

    for symbol in [".", ",", ":", ";", "!", "?", "(", ")"]:
        cleaned = cleaned.replace(symbol, "")

    return set(cleaned.split())


def predict_priority(message):
    words = tokenize(message)

    high_matches = words & HIGH_PRIORITY_WORDS
    ai_cloud_matches = words & AI_CLOUD_WORDS
    action_matches = words & ACTION_WORDS

    score = 0
    score += len(high_matches) * 3
    score += len(ai_cloud_matches) * 2
    score += len(action_matches)

    if score >= 7:
        label = "high"
    elif score >= 3:
        label = "medium"
    else:
        label = "low"

    return {
        "label": label,
        "score": score,
        "matched_signals": {
            "high_priority": sorted(high_matches),
            "ai_or_cloud": sorted(ai_cloud_matches),
            "action_words": sorted(action_matches)
        }
    }


def make_response(message):
    prediction = predict_priority(message)

    return {
        "app": APP_NAME,
        "environment": APP_ENV,
        "timestamp": datetime.now(UTC).isoformat(),
        "input": message,
        "prediction": prediction,
        "note": "This is a local demo response. It does not use private data or external services."
    }


def print_response(response):
    print(f"App: {response['app']}")
    print(f"Environment: {response['environment']}")
    print(f"Prediction: {response['prediction']['label']}")
    print(f"Score: {response['prediction']['score']}")
    print("Matched signals:", response["prediction"]["matched_signals"])
    print("Note:", response["note"])


def main():
    print("Cloud ML Deployment Demo v1")
    print()

    message = input("Enter a message to classify: ").strip()
    response = make_response(message)

    print()
    print_response(response)


if __name__ == "__main__":
    main()
