from pathlib import Path
import subprocess
import sys


PROJECT_DIR = Path(__file__).resolve().parents[1]
DATASET_GENERATOR = PROJECT_DIR / "src" / "generate_cnn_dataset.py"
TRAINING_SCRIPT = PROJECT_DIR / "src" / "train_cnn.py"
EVALUATION_SCRIPT = PROJECT_DIR / "eval" / "evaluate_cnn.py"
CHECKPOINT = PROJECT_DIR / "models" / "cnn_demo_best.pt"


def run_script(path: Path) -> None:
    print(f"\nRunning {path.relative_to(PROJECT_DIR)}")
    subprocess.run(
        [sys.executable, str(path)],
        cwd=PROJECT_DIR,
        check=True,
    )


def main() -> None:
    required_scripts = [
        DATASET_GENERATOR,
        TRAINING_SCRIPT,
        EVALUATION_SCRIPT,
    ]

    missing = [str(path) for path in required_scripts if not path.exists()]
    if missing:
        raise FileNotFoundError(
            "Missing required CNN file(s): " + ", ".join(missing)
        )

    if not CHECKPOINT.exists():
        print("CNN checkpoint is missing. Creating synthetic data and training.")
        run_script(DATASET_GENERATOR)
        run_script(TRAINING_SCRIPT)
    else:
        print(f"Using existing CNN checkpoint: {CHECKPOINT}")

    run_script(EVALUATION_SCRIPT)


if __name__ == "__main__":
    main()
