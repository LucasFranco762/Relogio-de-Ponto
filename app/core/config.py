"""Configuração central, sem estado global mutável."""

from dataclasses import dataclass
from pathlib import Path
import sys


@dataclass(frozen=True, slots=True)
class Settings:
    """Configurações imutáveis derivadas da raiz do projeto."""

    project_root: Path
    database_url: str
    app_name: str = "Controle de Ponto"

    @classmethod
    def from_root(cls, root: Path) -> "Settings":
        # Em uma distribuição PyInstaller, os dados graváveis devem ficar ao
        # lado do executável, e não dentro do diretório temporário do pacote.
        data_dir = root if getattr(sys, "frozen", False) else root / "app" / "resources"
        data_dir.mkdir(parents=True, exist_ok=True)
        return cls(root, f"sqlite:///{data_dir / 'controle_ponto.db'}")
