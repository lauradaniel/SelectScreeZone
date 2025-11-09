"""Entry point for the Select Screen Zone desktop application."""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure the ``src`` directory is on ``sys.path`` so the local package can be imported
ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from selectscreenzone.app import run


if __name__ == "__main__":  # pragma: no cover
    run()
