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
        self._background = QtGui.QPixmap()
        self._virtual_geometry = QtCore.QRect()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def show_overlay(self) -> None:
        self._virtual_geometry = self._compute_virtual_geometry()
        self.setGeometry(self._virtual_geometry)
        self._background = self._grab_virtual_desktop(self._virtual_geometry)
        self.show()
        self.raise_()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _compute_virtual_geometry(self) -> QtCore.QRect:
        screens = QtGui.QGuiApplication.screens()
        if not screens:
            primary = QtGui.QGuiApplication.primaryScreen()
            return primary.geometry() if primary is not None else QtCore.QRect()
        geometry = QtCore.QRect(screens[0].geometry())
        for screen in screens[1:]:
            geometry = geometry.united(screen.geometry())
        return geometry

    def _grab_virtual_desktop(self, geometry: QtCore.QRect) -> QtGui.QPixmap:
        result = QtGui.QPixmap(geometry.size())
        result.fill(QtCore.Qt.GlobalColor.transparent)

        painter = QtGui.QPainter(result)
        screens = QtGui.QGuiApplication.screens()
        if not screens:
            primary = QtGui.QGuiApplication.primaryScreen()
            if primary is not None:
                painter.drawPixmap(QtCore.QPoint(), primary.grabWindow(0))
            painter.end()
            return result

        for screen in screens:
            pixmap = screen.grabWindow(0)
            top_left = screen.geometry().topLeft() - geometry.topLeft()
            target_rect = QtCore.QRect(top_left, screen.geometry().size())
            painter.drawPixmap(target_rect, pixmap)
        painter.end()
        return result

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

        if not self._background.isNull():
            painter.drawPixmap(0, 0, self._background)

        overlay_color = QtGui.QColor(0, 0, 0, 160)
        painter.fillRect(self.rect(), overlay_color)

        if not self._current_rect.isNull() and self._current_rect.isValid():
            painter.setCompositionMode(QtGui.QPainter.CompositionMode_Clear)
            painter.fillRect(self._current_rect, QtCore.Qt.GlobalColor.transparent)
            painter.setCompositionMode(QtGui.QPainter.CompositionMode_SourceOver)
            painter.fillRect(self._current_rect, QtGui.QColor(30, 144, 255, 60))
        super().paintEvent(event)


__all__ = ["ScreenSelectionOverlay"]
