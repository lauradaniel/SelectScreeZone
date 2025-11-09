"""Extract textual suggestions from a screenshot using Tesseract OCR."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Generator, Iterable, Tuple

from PIL import Image

LOGGER = logging.getLogger(__name__)

try:  # pragma: no cover - optional dependency
    import pytesseract
    from pytesseract import Output as TesseractOutput
except ImportError:  # pragma: no cover - optional dependency
    pytesseract = None
    TesseractOutput = None  # type: ignore[assignment]


@dataclass
class RawSuggestion:
    """Intermediate representation for textual suggestions."""

    label: str
    metadata: dict[str, str]


Bounds = Tuple[int, int, int, int]


def _iter_ocr_results(image: Image.Image) -> Generator[RawSuggestion, None, None]:
    assert pytesseract is not None and TesseractOutput is not None

    data = pytesseract.image_to_data(image, output_type=TesseractOutput.DICT)
    n_items = len(data.get("text", []))
    for idx in range(n_items):
        text = data["text"][idx].strip()
        if not text:
            continue

        confidence = data.get("conf", [""])[idx]
        try:
            conf_value = float(confidence)
        except ValueError:
            conf_value = 0.0

        if conf_value < 60:
            continue

        x = int(data.get("left", [0])[idx])
        y = int(data.get("top", [0])[idx])
        width = int(data.get("width", [0])[idx])
        height = int(data.get("height", [0])[idx])

        metadata = {
            "confidence": f"{conf_value:.0f}%",
            "bbox": f"{x},{y},{width},{height}",
        }

        yield RawSuggestion(label=text, metadata=metadata)


def extract_suggestions(bounds: Bounds, image: Image.Image) -> Iterable[RawSuggestion]:
    """Return OCR-based suggestions for the given screenshot."""

    if pytesseract is None or TesseractOutput is None:
        LOGGER.info("pytesseract not installed; skipping OCR suggestions")
        return []

    return list(_iter_ocr_results(image))


__all__ = ["extract_suggestions", "RawSuggestion"]
