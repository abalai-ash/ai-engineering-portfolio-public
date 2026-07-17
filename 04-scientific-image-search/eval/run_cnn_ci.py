from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]

def main() -> None:
    subprocess.run(
        [sys.executable, str(ROOT / "src" / "train_cnn.py")],
        cwd=ROOT,
        check=True,
    )
    subprocess.run(
        [sys.executable, str(ROOT / "eval" / "evaluate_cnn.py")],
        cwd=ROOT,
        check=True,
    )

if __name__ == "__main__":
    main()
