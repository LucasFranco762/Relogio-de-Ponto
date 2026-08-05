"""Persistência das larguras das colunas das tabelas da interface."""

import json
from pathlib import Path

from PySide6.QtWidgets import QTableWidget


class TableColumnSettings:
    """Lê e grava as larguras das colunas no Config.json."""

    def __init__(self, config_path: Path) -> None:
        self.config_path = config_path
        self._data = self._load()
        self._handlers = []

    def _load(self) -> dict:
        try:
            content = self.config_path.read_text(encoding="utf-8")
            data = json.loads(content) if content.strip() else {}
            return data if isinstance(data, dict) else {}
        except (OSError, json.JSONDecodeError):
            return {}

    def apply(self, table: QTableWidget, table_id: str) -> None:
        all_widths = self._data.get("Larguras_Colunas", {})
        widths = all_widths.get(table_id, {}) if isinstance(all_widths, dict) else {}
        if not isinstance(widths, dict):
            widths = {}
        for column in range(table.columnCount()):
            width = widths.get(str(column))
            if isinstance(width, int) and width > 0:
                table.setColumnWidth(column, width)
        handler = lambda column, _old_width, width, table_id=table_id: self._save(table_id, column, width)
        self._handlers.append(handler)
        table.horizontalHeader().sectionResized.connect(handler)

    def _save(self, table_id: str, column: int, width: int) -> None:
        if width <= 0:
            return
        all_widths = self._data.setdefault("Larguras_Colunas", {})
        if not isinstance(all_widths, dict):
            all_widths = self._data["Larguras_Colunas"] = {}
        all_widths.setdefault(table_id, {})[str(column)] = width
        try:
            self.config_path.write_text(
                json.dumps(self._data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
            )
        except OSError:
            pass
