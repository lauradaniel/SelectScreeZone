"""Suggestion aggregation helpers."""

from __future__ import annotations

import enum
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Sequence, Tuple

from PIL import Image

from .analyzers import accessibility, ocr

LOGGER = logging.getLogger(__name__)


class SuggestionSource(enum.Enum):
    """Enumerates the origin of a suggestion."""

    OCR = "ocr"
    ACCESSIBILITY = "accessibility"


@dataclass
class Suggestion:
    """Simple description of an element detected within the selection."""

    label: str
    source: SuggestionSource
    metadata: Dict[str, str] = field(default_factory=dict)


def gather_suggestions(
    bounds: Tuple[int, int, int, int], image: Image.Image
) -> Tuple[Sequence[Suggestion], Sequence[SuggestionSource]]:
    """Return collected suggestions and a list of sources that produced them."""

    collected: List[Suggestion] = []
    sources: List[SuggestionSource] = []

    for extractor, source in (
        (ocr.extract_suggestions, SuggestionSource.OCR),
        (accessibility.extract_suggestions, SuggestionSource.ACCESSIBILITY),
    ):
        try:
            suggestions = list(extractor(bounds, image))
        except Exception as exc:  # pragma: no cover - optional path
            LOGGER.debug("Suggestion extractor %s failed: %s", source.value, exc, exc_info=True)
            continue

        if suggestions:
            collected.extend(
                Suggestion(label=s.label, source=source, metadata=s.metadata)
                for s in suggestions
            )
            sources.append(source)

    # Deduplicate by label/source pair, preserving insertion order
    unique: Dict[Tuple[str, SuggestionSource], Suggestion] = {}
    for suggestion in collected:
        unique.setdefault((suggestion.label, suggestion.source), suggestion)

    return list(unique.values()), sources


__all__ = ["Suggestion", "SuggestionSource", "gather_suggestions"]
