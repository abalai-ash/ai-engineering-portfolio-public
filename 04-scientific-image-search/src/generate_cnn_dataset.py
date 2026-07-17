from __future__ import annotations

import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = ROOT / "data" / "cnn_demo"

IMAGE_SIZE = 64
SEED = 42

SPLIT_COUNTS = {
    "train": 60,
    "validation": 15,
    "test": 15,
}

CLASSES = ("ring", "spiral", "compact")


def clipped(value: float) -> int:
    return max(0, min(255, int(value)))


def background(rng: random.Random) -> Image.Image:
    image = Image.new("L", (IMAGE_SIZE, IMAGE_SIZE))
    pixels = image.load()

    for y in range(IMAGE_SIZE):
        for x in range(IMAGE_SIZE):
            pixels[x, y] = clipped(rng.gauss(18, 7))

    return image


def add_noise(image: Image.Image, rng: random.Random) -> Image.Image:
    pixels = image.load()

    for y in range(IMAGE_SIZE):
        for x in range(IMAGE_SIZE):
            pixels[x, y] = clipped(pixels[x, y] + rng.gauss(0, 6))

    return image


def make_ring(rng: random.Random) -> Image.Image:
    image = background(rng)
    draw = ImageDraw.Draw(image)

    center_x = IMAGE_SIZE // 2 + rng.randint(-4, 4)
    center_y = IMAGE_SIZE // 2 + rng.randint(-4, 4)
    radius = rng.randint(15, 21)
    width = rng.randint(3, 6)
    brightness = rng.randint(175, 235)

    box = (
        center_x - radius,
        center_y - radius,
        center_x + radius,
        center_y + radius,
    )

    draw.ellipse(box, outline=brightness, width=width)

    image = image.filter(ImageFilter.GaussianBlur(radius=rng.uniform(0.6, 1.3)))
    return add_noise(image, rng)


def make_spiral(rng: random.Random) -> Image.Image:
    image = background(rng)
    draw = ImageDraw.Draw(image)

    center_x = IMAGE_SIZE // 2 + rng.randint(-3, 3)
    center_y = IMAGE_SIZE // 2 + rng.randint(-3, 3)
    rotation = rng.uniform(0, 2 * math.pi)
    brightness = rng.randint(175, 235)

    points: list[tuple[float, float]] = []

    for step in range(150):
        theta = rotation + step * 0.12
        radius = 2.5 + step * 0.12

        x = center_x + radius * math.cos(theta)
        y = center_y + radius * math.sin(theta)

        points.append((x, y))

    draw.line(points, fill=brightness, width=rng.randint(2, 4))

    image = image.filter(ImageFilter.GaussianBlur(radius=rng.uniform(0.7, 1.4)))
    return add_noise(image, rng)


def make_compact(rng: random.Random) -> Image.Image:
    image = background(rng)
    draw = ImageDraw.Draw(image)

    center_x = IMAGE_SIZE // 2 + rng.randint(-5, 5)
    center_y = IMAGE_SIZE // 2 + rng.randint(-5, 5)
    radius = rng.randint(6, 11)
    brightness = rng.randint(190, 250)

    box = (
        center_x - radius,
        center_y - radius,
        center_x + radius,
        center_y + radius,
    )

    draw.ellipse(box, fill=brightness)

    image = image.filter(ImageFilter.GaussianBlur(radius=rng.uniform(2.0, 3.8)))
    return add_noise(image, rng)


GENERATORS = {
    "ring": make_ring,
    "spiral": make_spiral,
    "compact": make_compact,
}


def clear_existing_pngs() -> None:
    for path in DATA_ROOT.rglob("*.png"):
        path.unlink()


def generate_dataset() -> dict[str, dict[str, int]]:
    rng = random.Random(SEED)
    clear_existing_pngs()

    summary: dict[str, dict[str, int]] = {}

    for split, count in SPLIT_COUNTS.items():
        summary[split] = {}

        for class_name in CLASSES:
            output_dir = DATA_ROOT / split / class_name
            output_dir.mkdir(parents=True, exist_ok=True)

            generator = GENERATORS[class_name]

            for index in range(count):
                image = generator(rng)
                output_path = output_dir / f"{class_name}_{index:03d}.png"
                image.save(output_path)

            summary[split][class_name] = count

    return summary


def main() -> None:
    summary = generate_dataset()

    print("Synthetic CNN dataset created")
    print(f"Location: {DATA_ROOT}")
    print(f"Image size: {IMAGE_SIZE}x{IMAGE_SIZE}")
    print(f"Seed: {SEED}")

    total = 0

    for split, class_counts in summary.items():
        split_total = sum(class_counts.values())
        total += split_total
        print(f"{split}: {split_total} images — {class_counts}")

    print(f"Total: {total} images")
    print("All images are synthetic and contain no private research data.")


if __name__ == "__main__":
    main()
