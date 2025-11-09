"""Utilities for capturing screenshots of the selected region."""

from __future__ import annotations

from typing import Tuple

from PIL import Image

try:  # pragma: no cover - optional dependency wrapper
    import mss
except ImportError as exc:  # pragma: no cover - fallback
    mss = None
    _IMPORT_ERROR = exc
else:
    _IMPORT_ERROR = None


def capture_region(bounds: Tuple[int, int, int, int]) -> Image.Image:
    """Capture a rectangular screen region and return it as a :class:`PIL.Image`.

    Parameters
    ----------
    bounds:
        The region to capture expressed as ``(left, top, right, bottom)`` coordinates.
    """

    if mss is None:  # pragma: no cover - runtime feedback
        raise RuntimeError(
            "The 'mss' package is required for screen capture. Install it with 'pip install mss'."
        ) from _IMPORT_ERROR

    left, top, right, bottom = bounds
    width = right - left
    height = bottom - top

    with mss.mss() as sct:  # type: ignore[operator]
        monitor = {"left": left, "top": top, "width": width, "height": height}
        raw = sct.grab(monitor)

    return Image.frombytes("RGB", raw.size, raw.rgb)


__all__ = ["capture_region"]
