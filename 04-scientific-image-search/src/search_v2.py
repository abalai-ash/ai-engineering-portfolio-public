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
    "edge_score",
]

WEIGHTS = {
    "brightness": 1.0,
    "contrast": 1.0,
    "roundness": 1.2,
    "ring_score": 1.5,
    "edge_score": 1.3,
}


def load_images():
    rows = []

    with DATA_FILE.open("r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            for feature in FEATURES:
                row[feature] = float(row[feature])

            rows.append(row)

    return rows


def weighted_distance(image, target):
    total = 0.0

    for feature in FEATURES:
        difference = image[feature] - target[feature]
        total += WEIGHTS[feature] * difference * difference

    return math.sqrt(total)


def similarity_score(distance_value):
    return 1.0 / (1.0 + distance_value)


def target_from_query(query):
    query_lower = query.lower()

    target = {
        "brightness": 6,
        "contrast": 6,
        "roundness": 5,
        "ring_score": 4,
        "edge_score": 5,
    }

    reasons = []

    if "bright" in query_lower:
        target["brightness"] = 8
        reasons.append("bright -> higher brightness")

    if "faint" in query_lower:
        target["brightness"] = 4
        reasons.append("faint -> lower brightness")

    if "ring" in query_lower or "disk" in query_lower:
        target["roundness"] = 9
        target["ring_score"] = 9
        target["contrast"] = 7
        reasons.append("ring/disk -> high roundness and ring score")

    if "edge" in query_lower or "jet" in query_lower:
        target["edge_score"] = 9
        target["contrast"] = 8
        target["roundness"] = 2
        target["ring_score"] = 1
        reasons.append("edge/jet -> high edge score and low roundness")

    if "star" in query_lower or "compact" in query_lower:
        target["brightness"] = 9
        target["roundness"] = 9
        target["ring_score"] = 1
        target["edge_score"] = 3
        reasons.append("star/compact -> bright and round but not ring-like")

    if not reasons:
        reasons.append("general query -> neutral target vector")

    return target, reasons


def feature_differences(image, target):
    differences = []

    for feature in FEATURES:
        difference = abs(image[feature] - target[feature])
        differences.append((feature, difference))

    differences.sort(key=lambda item: item[1])
    return differences


def explain_match(image, target):
    closest = feature_differences(image, target)[:2]
    parts = []

    for feature, difference in closest:
        parts.append(f"{feature} close by {difference:.1f}")

    return "; ".join(parts)


def rank_images(images, target):
    ranked = []

    for image in images:
        item = image.copy()
        item["distance"] = weighted_distance(image, target)
        item["similarity"] = similarity_score(item["distance"])
        item["match_reason"] = explain_match(image, target)
        ranked.append(item)

    ranked.sort(key=lambda item: (item["distance"], item["image_id"]))
    return ranked


def search(query, top_k=3):
    images = load_images()
    target, query_reasons = target_from_query(query)
    ranked = rank_images(images, target)

    return {
        "query": query,
        "target": target,
        "query_reasons": query_reasons,
        "results": ranked[:top_k],
        "all_results": ranked,
    }


def print_results(output):
    print(f"Query: {output['query']}")
    print()

    print("Query interpretation:")
    for reason in output["query_reasons"]:
        print(f"- {reason}")

    print()
    print("Target vector:")
    for feature in FEATURES:
        print(f"- {feature}: {output['target'][feature]}")

    print()
    print("Closest matches:")
    print()

    for item in output["results"]:
        print(
            f"{item['image_id']} | similarity {item['similarity']:.3f} | "
            f"distance {item['distance']:.2f} | {item['title']}"
        )
        print(f"type: {item['object_type']}")
        print(f"reason: {item['match_reason']}")
        print()


def main():
    print("Scientific Image Search v2")
    print()

    query = input("Search for an image type: ").strip()
    output = search(query)

    print()
    print_results(output)


if __name__ == "__main__":
    main()
