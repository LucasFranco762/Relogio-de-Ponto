"""Localização de recursos em execução normal ou empacotada."""

import sys
from pathlib import Path


def resource_path(name: str) -> Path:
    """Retorna o caminho de um recurso do projeto ou do pacote PyInstaller."""
    base_path = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[2]))
    return base_path / name
