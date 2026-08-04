"""Ponto de extensão para backup automático do SQLite."""

from pathlib import Path


class BackupService:
    """Contrato simples; a rotina automática será implementada em etapa futura."""

    def __init__(self, backup_dir: Path) -> None:
        self.backup_dir = backup_dir

    def execute(self) -> None:
        """Reservado para cópia consistente do banco."""
        self.backup_dir.mkdir(parents=True, exist_ok=True)
