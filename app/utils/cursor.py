"""Comportamentos visuais para controles clicáveis."""

from PySide6.QtCore import QEvent, QObject, Qt
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import QAbstractButton, QListWidget


class ClickCursorFilter(QObject):
    """Exibe cursor de mão ao passar sobre controles clicáveis."""

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if isinstance(watched, (QAbstractButton, QListWidget)):
            if event.type() == QEvent.Type.Enter:
                watched.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            elif event.type() == QEvent.Type.Leave:
                watched.unsetCursor()
        return False
