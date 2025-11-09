"""Main application window for the screen zone selection utility."""

from __future__ import annotations

import platform
from dataclasses import dataclass
from typing import Iterable, Sequence, Tuple

from PySide6 import QtCore, QtGui, QtWidgets

from .selection_overlay import ScreenSelectionOverlay
from .screenshot import capture_region
from .suggestions import Suggestion, SuggestionSource, gather_suggestions


@dataclass
class Region:
    """Simple dataclass describing a rectangular region on the screen."""

    x: int
    y: int
    width: int
    height: int

    @property
    def rect(self) -> QtCore.QRect:
        """Return the region as a :class:`~PySide6.QtCore.QRect`."""

        return QtCore.QRect(self.x, self.y, self.width, self.height)

    def as_tuple(self) -> Tuple[int, int, int, int]:
        """Return the region as a tuple that ``mss`` and PIL understand."""

        return (self.x, self.y, self.x + self.width, self.y + self.height)


class MainWindow(QtWidgets.QMainWindow):
    """Main application window orchestrating selection and suggestion flow."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Select Screen Zone")
        self.resize(800, 600)

        self._overlay: ScreenSelectionOverlay | None = None

        self._list_widget = QtWidgets.QListWidget()
        self._list_widget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

        self._status_label = QtWidgets.QLabel(
            "Click the button below to select a region on the screen."
        )
        self._status_label.setWordWrap(True)

        self._select_button = QtWidgets.QPushButton("Select Screen Zone")
        self._select_button.clicked.connect(self._on_select_clicked)  # type: ignore[arg-type]

        self._copy_button = QtWidgets.QPushButton("Copy Selected Suggestions")
        self._copy_button.clicked.connect(self._copy_selected)  # type: ignore[arg-type]
        self._copy_button.setEnabled(False)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self._status_label)
        layout.addWidget(self._select_button)
        layout.addWidget(self._list_widget, stretch=1)
        layout.addWidget(self._copy_button)

        central = QtWidgets.QWidget()
        central.setLayout(layout)
        self.setCentralWidget(central)

        self._list_widget.itemSelectionChanged.connect(self._update_copy_button)

    # ------------------------------------------------------------------
    # Slots
    # ------------------------------------------------------------------
    def _on_select_clicked(self) -> None:
        """Display the overlay and start the selection workflow."""

        if self._overlay is not None:
            self._overlay.deleteLater()
        self._overlay = ScreenSelectionOverlay()
        self._overlay.selection_made.connect(self._on_region_selected)
        self._overlay.selection_cancelled.connect(self._on_selection_cancelled)
        self._status_label.setText("Drag to select a region. Press Esc to cancel.")
        self._overlay.show_overlay()

    def _on_region_selected(self, rect: QtCore.QRect) -> None:
        region = Region(rect.x(), rect.y(), rect.width(), rect.height())
        self._status_label.setText(
            f"Selected region at ({region.x}, {region.y}) — {region.width}×{region.height}."
        )

        try:
            image = capture_region(region.as_tuple())
        except Exception as exc:  # pragma: no cover - UI feedback
            QtWidgets.QMessageBox.critical(
                self, "Capture error", f"Failed to capture the screen region: {exc}"
            )
            return

        self._populate_suggestions(region, image)

    def _on_selection_cancelled(self) -> None:
        self._status_label.setText("Selection cancelled. You can try again.")

    def _populate_suggestions(
        self, region: Region, image: "Image.Image"
    ) -> None:  # pragma: no cover - Qt UI
        """Populate the list widget with suggestions for the given region."""

        self._list_widget.clear()
        self._list_widget.addItem("Analyzing the captured region…")
        QtWidgets.QApplication.processEvents()

        suggestions: Sequence[Suggestion]
        sources: Sequence[SuggestionSource]
        suggestions, sources = gather_suggestions(region.as_tuple(), image)

        self._list_widget.clear()

        if not suggestions:
            self._status_label.setText(
                "No suggestions were generated. Try a different region or install optional dependencies."
            )
            return

        source_badges = {
            SuggestionSource.OCR: "OCR",
            SuggestionSource.ACCESSIBILITY: "Accessibility",
        }

        for suggestion in suggestions:
            source_label = source_badges.get(suggestion.source, "Unknown")
            item = QtWidgets.QListWidgetItem(f"[{source_label}] {suggestion.label}")
            if suggestion.metadata:
                item.setToolTip("\n".join(f"{k}: {v}" for k, v in suggestion.metadata.items()))
            self._list_widget.addItem(item)

        active_sources = ", ".join(sorted({source_badges[s] for s in sources}))
        platform_label = platform.system()
        self._status_label.setText(
            f"Generated {len(suggestions)} suggestions using: {active_sources} (Platform: {platform_label})."
        )

    def _copy_selected(self) -> None:  # pragma: no cover - Qt UI
        """Copy the selected suggestion labels to the clipboard."""

        selected: Iterable[QtWidgets.QListWidgetItem] = self._list_widget.selectedItems()
        text = "\n".join(item.text() for item in selected)
        QtWidgets.QApplication.clipboard().setText(text)

    def _update_copy_button(self) -> None:
        self._copy_button.setEnabled(bool(self._list_widget.selectedItems()))


def run() -> None:  # pragma: no cover - Qt UI entry point
    """Run the Qt application."""

    import sys

    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


__all__ = ["MainWindow", "run", "Region"]
