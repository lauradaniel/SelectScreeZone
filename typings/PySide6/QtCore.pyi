from __future__ import annotations

from typing import Any, Callable, Generic, Iterable, Optional, TypeVar

_T = TypeVar("_T")

class QObject: ...

class QPoint:
    def __init__(self, x: int = ..., y: int = ...) -> None: ...
    def x(self) -> int: ...
    def y(self) -> int: ...

class QSize:
    def __init__(self, width: int = ..., height: int = ...) -> None: ...
    def width(self) -> int: ...
    def height(self) -> int: ...

class QRect:
    def __init__(self, top_left: QPoint | tuple[int, int] | int = ..., bottom_right: QPoint | tuple[int, int] | int = ..., width: int | None = ..., height: int | None = ...) -> None: ...
    def width(self) -> int: ...
    def height(self) -> int: ...
    def normalized(self) -> QRect: ...
    def isNull(self) -> bool: ...
    def isValid(self) -> bool: ...

class QRectF:
    def __init__(self, rect: QRect | tuple[float, float, float, float] | float = ..., y: float | None = ..., width: float | None = ..., height: float | None = ...) -> None: ...

class Signal(Generic[_T]):
    def __init__(self, *types: Any) -> None: ...
    def connect(self, slot: Callable[..., Any]) -> None: ...
    def emit(self, *args: Any) -> None: ...

class QObjectCleanupHandler(QObject): ...

class QEvent: ...

class QTimer(QObject): ...

class Qt:
    class WindowType:
        FramelessWindowHint: int
    class WindowState:
        WindowFullScreen: int
    class WidgetAttribute:
        WA_NoSystemBackground: int
        WA_TranslucentBackground: int
        WA_DeleteOnClose: int
    class CursorShape:
        CrossCursor: int
    class MouseButton:
        LeftButton: int
    class Key:
        Key_Escape: int
        Key_Q: int
    class PenStyle:
        NoPen: int

__all__ = [
    "QObject",
    "QPoint",
    "QRect",
    "QRectF",
    "QSize",
    "Signal",
    "Qt",
]
