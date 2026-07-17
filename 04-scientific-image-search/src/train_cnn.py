from __future__ import annotations

import json
import random
import time
from pathlib import Path

import numpy as np
import torch
from PIL import Image
from torch import nn
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "cnn_demo"
MODEL_DIR = ROOT / "models"
RESULTS_DIR = ROOT / "eval"

SEED = 42
BATCH_SIZE = 16
EPOCHS = 12
LEARNING_RATE = 1e-3
IMAGE_SIZE = 64
CLASSES = ["compact", "rings", "spirals"]


def set_seed(seed: int = SEED) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.backends.mps.is_available():
        torch.mps.manual_seed(seed)


class FolderImageDataset(Dataset):
    def __init__(self, split: str, transform: transforms.Compose) -> None:
        self.samples: list[tuple[Path, int]] = []
        self.transform = transform
        split_dir = DATA_DIR / split

        for class_index, class_name in enumerate(CLASSES):
            class_dir = split_dir / class_name
            for image_path in sorted(class_dir.glob("*.png")):
                self.samples.append((image_path, class_index))

        if not self.samples:
            raise RuntimeError(f"No images found in {split_dir}")

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, index: int) -> tuple[torch.Tensor, int]:
        image_path, label = self.samples[index]
        with Image.open(image_path) as image:
            image = image.convert("RGB")
            tensor = self.transform(image)
        return tensor, label


class SmallCNN(nn.Module):
    def __init__(self, num_classes: int) -> None:
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(3, 16, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(16, 32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.AdaptiveAvgPool2d((1, 1)),
        )
        self.classifier = nn.Linear(64, num_classes)

    def forward(self, inputs: torch.Tensor) -> torch.Tensor:
        features = self.features(inputs)
        return self.classifier(features.flatten(1))


def choose_device() -> torch.device:
    if torch.backends.mps.is_available():
        return torch.device("mps")
    if torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


def make_loaders() -> tuple[DataLoader, DataLoader, DataLoader]:
    train_transform = transforms.Compose(
        [
            transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
            transforms.RandomHorizontalFlip(),
            transforms.RandomRotation(8),
            transforms.ToTensor(),
        ]
    )
    eval_transform = transforms.Compose(
        [
            transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
            transforms.ToTensor(),
        ]
    )

    generator = torch.Generator().manual_seed(SEED)

    train_loader = DataLoader(
        FolderImageDataset("train", train_transform),
        batch_size=BATCH_SIZE,
        shuffle=True,
        num_workers=0,
        generator=generator,
    )
    validation_loader = DataLoader(
        FolderImageDataset("validation", eval_transform),
        batch_size=BATCH_SIZE,
        shuffle=False,
        num_workers=0,
    )
    test_loader = DataLoader(
        FolderImageDataset("test", eval_transform),
        batch_size=BATCH_SIZE,
        shuffle=False,
        num_workers=0,
    )
    return train_loader, validation_loader, test_loader


def evaluate(
    model: nn.Module,
    loader: DataLoader,
    loss_fn: nn.Module,
    device: torch.device,
) -> tuple[float, float, list[list[int]]]:
    model.eval()
    total_loss = 0.0
    correct = 0
    total = 0
    confusion = [[0 for _ in CLASSES] for _ in CLASSES]

    with torch.no_grad():
        for inputs, labels in loader:
            inputs = inputs.to(device)
            labels = labels.to(device)
            logits = model(inputs)
            loss = loss_fn(logits, labels)
            predictions = logits.argmax(dim=1)

            total_loss += loss.item() * labels.size(0)
            correct += (predictions == labels).sum().item()
            total += labels.size(0)

            for truth, prediction in zip(labels.cpu().tolist(), predictions.cpu().tolist()):
                confusion[truth][prediction] += 1

    return total_loss / total, correct / total, confusion


def main() -> None:
    set_seed()
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    device = choose_device()
    train_loader, validation_loader, test_loader = make_loaders()

    model = SmallCNN(num_classes=len(CLASSES)).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE)
    loss_fn = nn.CrossEntropyLoss()

    checkpoint_path = MODEL_DIR / "cnn_demo_best.pt"
    history: list[dict[str, float | int]] = []
    best_validation_accuracy = -1.0
    started = time.perf_counter()

    print(f"Device: {device}")
    print(f"Train images: {len(train_loader.dataset)}")
    print(f"Validation images: {len(validation_loader.dataset)}")
    print(f"Test images: {len(test_loader.dataset)}")

    for epoch in range(1, EPOCHS + 1):
        model.train()
        running_loss = 0.0
        correct = 0
        total = 0

        for inputs, labels in train_loader:
            inputs = inputs.to(device)
            labels = labels.to(device)

            optimizer.zero_grad()
            logits = model(inputs)
            loss = loss_fn(logits, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item() * labels.size(0)
            predictions = logits.argmax(dim=1)
            correct += (predictions == labels).sum().item()
            total += labels.size(0)

        train_loss = running_loss / total
        train_accuracy = correct / total
        validation_loss, validation_accuracy, _ = evaluate(
            model,
            validation_loader,
            loss_fn,
            device,
        )

        history.append(
            {
                "epoch": epoch,
                "train_loss": round(train_loss, 6),
                "train_accuracy": round(train_accuracy, 6),
                "validation_loss": round(validation_loss, 6),
                "validation_accuracy": round(validation_accuracy, 6),
            }
        )

        print(
            f"Epoch {epoch:02d}/{EPOCHS} | "
            f"train_acc={train_accuracy:.3f} | "
            f"val_acc={validation_accuracy:.3f}"
        )

        if validation_accuracy > best_validation_accuracy:
            best_validation_accuracy = validation_accuracy
            torch.save(
                {
                    "model_state_dict": model.state_dict(),
                    "classes": CLASSES,
                    "image_size": IMAGE_SIZE,
                    "seed": SEED,
                },
                checkpoint_path,
            )

    checkpoint = torch.load(checkpoint_path, map_location=device)
    model.load_state_dict(checkpoint["model_state_dict"])
    test_loss, test_accuracy, confusion_matrix = evaluate(
        model,
        test_loader,
        loss_fn,
        device,
    )

    elapsed = time.perf_counter() - started
    results = {
        "project": "Scientific Image Search CNN Demo",
        "scope": "Synthetic images only; no private research images.",
        "device": str(device),
        "classes": CLASSES,
        "seed": SEED,
        "epochs": EPOCHS,
        "batch_size": BATCH_SIZE,
        "learning_rate": LEARNING_RATE,
        "best_validation_accuracy": round(best_validation_accuracy, 6),
        "test_loss": round(test_loss, 6),
        "test_accuracy": round(test_accuracy, 6),
        "confusion_matrix": confusion_matrix,
        "history": history,
        "elapsed_seconds": round(elapsed, 3),
        "checkpoint": str(checkpoint_path.relative_to(ROOT)),
    }

    results_path = RESULTS_DIR / "cnn_results.json"
    results_path.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")

    report_lines = [
        "# CNN Evaluation Results",
        "",
        f"- Device: `{device}`",
        f"- Best validation accuracy: `{best_validation_accuracy:.3f}`",
        f"- Held-out test accuracy: `{test_accuracy:.3f}`",
        f"- Test loss: `{test_loss:.4f}`",
        f"- Checkpoint: `{checkpoint_path.relative_to(ROOT)}`",
        "",
        "## Confusion matrix",
        "",
        "| Actual \\ Predicted | compact | rings | spirals |",
        "|---|---:|---:|---:|",
    ]
    for class_name, row in zip(CLASSES, confusion_matrix):
        report_lines.append(
            f"| {class_name} | {row[0]} | {row[1]} | {row[2]} |"
        )

    report_lines.extend(
        [
            "",
            "## Scope",
            "",
            "This is a small local CNN demonstration trained only on deterministic synthetic images.",
            "It does not use private research images and does not claim production-scale performance.",
            "",
        ]
    )

    report_path = RESULTS_DIR / "cnn_results.md"
    report_path.write_text("\n".join(report_lines), encoding="utf-8")

    print("")
    print(f"Best validation accuracy: {best_validation_accuracy:.3f}")
    print(f"Held-out test accuracy: {test_accuracy:.3f}")
    print(f"Results written to: {results_path}")
    print(f"Report written to: {report_path}")
    print(f"Checkpoint written to: {checkpoint_path}")


if __name__ == "__main__":
    main()
