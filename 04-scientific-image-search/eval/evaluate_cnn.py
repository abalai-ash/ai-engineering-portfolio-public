from __future__ import annotations

import json
import sys
from pathlib import Path

import torch
from torch.utils.data import DataLoader
from torchvision import transforms

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "src"
DATA_DIR = ROOT / "data" / "cnn_demo"
MODEL_PATH = ROOT / "models" / "cnn_demo_best.pt"
RESULTS_JSON = ROOT / "eval" / "cnn_results.json"
RESULTS_MD = ROOT / "eval" / "cnn_results.md"

sys.path.insert(0, str(SRC_DIR))

from train_cnn import CLASSES, IMAGE_SIZE, FolderImageDataset, SmallCNN, choose_device, evaluate


def main() -> None:
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Missing checkpoint: {MODEL_PATH}. Run python src/train_cnn.py first."
        )

    checkpoint = torch.load(MODEL_PATH, map_location="cpu")
    classes = tuple(checkpoint.get("classes", CLASSES))
    image_size = int(checkpoint.get("image_size", IMAGE_SIZE))

    model = SmallCNN(num_classes=len(classes))
    model.load_state_dict(checkpoint["model_state_dict"])

    device = choose_device()
    model.to(device)

    eval_transform = transforms.Compose([
        transforms.Resize((image_size, image_size)),
        transforms.ToTensor(),
    ])

    test_dataset = FolderImageDataset(DATA_DIR / "test", eval_transform)
    test_loader = DataLoader(
        test_dataset,
        batch_size=16,
        shuffle=False,
        num_workers=0,
    )

    loss, accuracy, confusion = evaluate(
        model,
        test_loader,
        torch.nn.CrossEntropyLoss(),
        device,
    )
    accuracy = accuracy

    payload = {
        "project": "Scientific Image Search CNN Demo",
        "scope": "Synthetic images only; no private research images.",
        "device": str(device),
        "classes": list(classes),
        "test_images": total,
        "test_loss": round(loss, 6),
        "test_accuracy": round(accuracy, 6),
        "confusion_matrix": confusion,
        "checkpoint": str(MODEL_PATH.relative_to(ROOT)),
    }
    RESULTS_JSON.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# CNN Evaluation Results",
        "",
        f"- Device: `{device}`",
        f"- Test images: `{total}`",
        f"- Test loss: `{loss:.6f}`",
        f"- Test accuracy: `{accuracy:.3f}`",
        f"- Checkpoint: `{MODEL_PATH.relative_to(ROOT)}`",
        "",
        "## Confusion matrix",
        "",
        "| Actual / Predicted | " + " | ".join(classes) + " |",
        "|---|" + "---|" * len(classes),
    ]

    for class_name, row in zip(classes, confusion):
        lines.append(
            "| " + class_name + " | " + " | ".join(str(value) for value in row) + " |"
        )

    lines.extend([
        "",
        "## Scope",
        "",
        "This is a small local CNN demonstration trained only on deterministic synthetic images.",
        "It does not use private research images and does not claim production-scale performance.",
        "",
    ])
    RESULTS_MD.write_text("\n".join(lines), encoding="utf-8")

    print("CNN evaluation complete")
    print(f"Device: {device}")
    print(f"Test images: {total}")
    print(f"Test loss: {loss:.6f}")
    print(f"Test accuracy: {accuracy:.3f}")
    print(f"Results written to {RESULTS_JSON}")
    print(f"Report written to {RESULTS_MD}")

    if total == 0:
        raise SystemExit("No test images were found.")
    if accuracy < 0.90:
        raise SystemExit(f"CNN accuracy below expected demo threshold: {accuracy:.3f}")


if __name__ == "__main__":
    main()
