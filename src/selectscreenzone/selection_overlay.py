"""Overlay window that lets the user draw a rectangular selection on the screen."""

from __future__ import annotations

from PySide6 import QtCore, QtGui, QtWidgets


class ScreenSelectionOverlay(QtWidgets.QWidget):  # pragma: no cover - interactive widget
    """Transparent full-screen widget used to capture a rectangular selection."""

    selection_made = QtCore.Signal(QtCore.QRect)
    selection_cancelled = QtCore.Signal()

    def __init__(self) -> None:
        super().__init__(None, QtCore.Qt.WindowType.FramelessWindowHint)
        self.setWindowState(QtCore.Qt.WindowState.WindowFullScreen)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_NoSystemBackground, True)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_DeleteOnClose, True)
        self.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.CrossCursor))

        self._origin = QtCore.QPoint()
        self._rubber_band = QtWidgets.QRubberBand(QtWidgets.QRubberBand.Shape.Rectangle, self)
        self._current_rect = QtCore.QRect()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def show_overlay(self) -> None:
        self.show()
        self.raise_()

    # ------------------------------------------------------------------
    # QWidget overrides
    # ------------------------------------------------------------------
    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self._origin = event.position().toPoint()
            self._rubber_band.setGeometry(QtCore.QRect(self._origin, QtCore.QSize()))
            self._rubber_band.show()
            self._current_rect = QtCore.QRect(self._origin, self._origin)
            self.update()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        if not self._rubber_band.isHidden():
            point = event.position().toPoint()
            rect = QtCore.QRect(self._origin, point).normalized()
            self._rubber_band.setGeometry(rect)
            self._current_rect = rect
            self.update()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
        if event.button() == QtCore.Qt.MouseButton.LeftButton and not self._rubber_band.isHidden():
            self._rubber_band.hide()
            rect = self._rubber_band.geometry()
            if rect.width() > 0 and rect.height() > 0:
                self.selection_made.emit(rect)
            else:
                self.selection_cancelled.emit()
            self._current_rect = QtCore.QRect()
            self.update()
            self.close()
        super().mouseReleaseEvent(event)

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        if event.key() in (QtCore.Qt.Key.Key_Escape, QtCore.Qt.Key.Key_Q):
            self.selection_cancelled.emit()
            self.close()
            return
        super().keyPressEvent(event)

    def paintEvent(self, event: QtGui.QPaintEvent) -> None:
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing, True)

        overlay_color = QtGui.QColor(0, 0, 0, 120)
        painter.setPen(QtCore.Qt.PenStyle.NoPen)

        full_rect = QtCore.QRectF(self.rect())
        path = QtGui.QPainterPath()
        path.addRect(full_rect)

        if not self._current_rect.isNull() and self._current_rect.isValid():
            selection_path = QtGui.QPainterPath()
            selection_path.addRect(QtCore.QRectF(self._current_rect))
            path = path.subtracted(selection_path)

        painter.fillPath(path, overlay_color)
        super().paintEvent(event)


__all__ = ["ScreenSelectionOverlay"]
