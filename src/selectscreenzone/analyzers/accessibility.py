"""Accessibility-based suggestion extractor using Windows UI Automation."""

from __future__ import annotations

import logging
import platform
from dataclasses import dataclass
from typing import Iterable, Iterator, Tuple

LOGGER = logging.getLogger(__name__)

try:  # pragma: no cover - optional dependency
    import uiautomation as automation
except ImportError:  # pragma: no cover - optional dependency
    automation = None


@dataclass
class RawSuggestion:
    """Intermediate representation for accessibility suggestions."""

    label: str
    metadata: dict[str, str]


Bounds = Tuple[int, int, int, int]


def _iter_controls(root: "automation.Control", max_depth: int = 5) -> Iterator["automation.Control"]:
    stack = [(root, 0)]
    while stack:
        control, depth = stack.pop()
        yield control
        if depth >= max_depth:
            continue
        try:
            children = list(control.GetChildren())
        except Exception:
            continue
        for child in children:
            stack.append((child, depth + 1))


def _control_rect(control: "automation.Control") -> Tuple[int, int, int, int] | None:
    try:
        rect = control.BoundingRectangle
    except Exception:
        return None
    if rect is None:
        return None
    return rect.left, rect.top, rect.right, rect.bottom


def _intersects(bounds: Bounds, rect: Tuple[int, int, int, int]) -> bool:
    left, top, right, bottom = bounds
    r_left, r_top, r_right, r_bottom = rect
    return not (r_right <= left or r_left >= right or r_bottom <= top or r_top >= bottom)


def _control_label(control: "automation.Control") -> str:
    parts: list[str] = []
    try:
        ctrl_type = control.ControlTypeName
    except Exception:
        ctrl_type = "Control"
    if ctrl_type:
        parts.append(ctrl_type)

    try:
        name = control.Name
    except Exception:
        name = ""
    if name:
        parts.append(name)
    else:
        try:
            automation_id = control.AutomationId
        except Exception:
            automation_id = ""
        if automation_id:
            parts.append(f"#{automation_id}")

    return " › ".join(parts) if parts else "Control"


def extract_suggestions(bounds: Bounds, image) -> Iterable[RawSuggestion]:
    """Return suggestions from the Windows UI Automation tree."""

    if platform.system() != "Windows":
        LOGGER.info("Accessibility suggestions available only on Windows")
        return []

    if automation is None:
        LOGGER.info("uiautomation not installed; skipping accessibility suggestions")
        return []

    try:
        root = automation.GetRootControl()
    except Exception as exc:  # pragma: no cover - runtime feedback
        LOGGER.warning("Failed to obtain root control: %s", exc)
        return []

    suggestions: list[RawSuggestion] = []
    for control in _iter_controls(root):
        rect = _control_rect(control)
        if rect is None:
            continue
        if not _intersects(bounds, rect):
            continue

        label = _control_label(control)

        metadata = {
            "bounds": f"{rect[0]},{rect[1]},{rect[2]-rect[0]},{rect[3]-rect[1]}",
        }

        try:
            class_name = control.ClassName
        except Exception:
            class_name = ""
        if class_name:
            metadata["class"] = class_name

        try:
            process_id = control.ProcessId
        except Exception:
            process_id = None
        if process_id:
            metadata["pid"] = str(process_id)

        suggestions.append(RawSuggestion(label=label, metadata=metadata))

    return suggestions


__all__ = ["extract_suggestions", "RawSuggestion"]
