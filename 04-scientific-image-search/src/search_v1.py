from pathlib import Path
import csv
import math


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_FILE = BASE_DIR / "data" / "image_features.csv"

FEATURES = [
    "brightness",
    "contrast",
    "roundness",
    "ring_score",
    "edge_score"
]


def load_images():
    rows = []

    with DATA_FILE.open("r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            for feature in FEATURES:
                row[feature] = float(row[feature])

            rows.append(row)

    return rows


def distance(image, target):
    total = 0.0

    for feature in FEATURES:
        total += (image[feature] - target[feature]) ** 2

    return math.sqrt(total)


def rank_images(images, target):
    ranked = []

    for image in images:
        item = image.copy()
        item["distance"] = distance(image, target)
        ranked.append(item)

    ranked.sort(key=lambda item: item["distance"])
    return ranked


def target_from_query(query):
    query = query.lower()

    if "ring" in query or "disk" in query:
        return {
            "brightness": 8,
            "contrast": 7,
            "roundness": 9,
            "ring_score": 9,
            "edge_score": 5
        }

    if "jet" in query or "edge" in query:
        return {
            "brightness": 5,
            "contrast": 8,
            "roundness": 2,
            "ring_score": 1,
            "edge_score": 9
        }

    if "star" in query or "compact" in query:
        return {
            "brightness": 9,
            "contrast": 5,
            "roundness": 9,
            "ring_score": 1,
            "edge_score": 3
        }

    return {
        "brightness": 6,
        "contrast": 6,
        "roundness": 5,
        "ring_score": 4,
        "edge_score": 5
    }


def search(query):
    images = load_images()
    target = target_from_query(query)
    ranked = rank_images(images, target)

    return {
        "query": query,
        "target": target,
        "results": ranked
    }


def print_results(output):
    print(f"Query: {output['query']}")
    print()
    print("Closest matches:")
    print()

    for item in output["results"][:3]:
        print(f"{item['image_id']} | distance {item['distance']:.2f} | {item['title']}")
        print(f"type: {item['object_type']}")
        print()


def main():
    print("Scientific Image Search v1")
    print()

    query = input("Search for an image type: ").strip()
    output = search(query)

    print()
    print_results(output)


if __name__ == "__main__":
    main()
