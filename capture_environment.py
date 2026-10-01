"""Capture the exact Python environment used for the manuscript calculations."""

import platform
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent

python_info = (
    f"Python version: {sys.version}\n"
    f"Python executable: {sys.executable}\n"
    f"Platform: {platform.platform()}\n"
)

(ROOT / "PYTHON_VERSION.txt").write_text(
    python_info,
    encoding="utf-8"
)

with (ROOT / "requirements-lock.txt").open(
    "w",
    encoding="utf-8"
) as f:
    subprocess.run(
        [sys.executable, "-m", "pip", "freeze", "--all"],
        stdout=f,
        check=True
    )

print("Environment captured successfully.")
print(f"Python information: {ROOT / 'PYTHON_VERSION.txt'}")
print(f"Package lock file: {ROOT / 'requirements-lock.txt'}")
