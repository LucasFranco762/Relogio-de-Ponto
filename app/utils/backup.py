"""Backup consistente do banco SQLite."""

from datetime import datetime
from pathlib import Path
import logging
import sqlite3

from app.database.engine import Database


class BackupService:
    """Executa cópias consistentes usando a API nativa de backup do SQLite."""

    def __init__(self, database: Database | None, backup_dir: Path, retention: int = 7, logger: logging.Logger | None = None) -> None:
        self.database, self.backup_dir = database, backup_dir
        self.retention = max(1, retention)
        self.logger = logger or logging.getLogger("controle_ponto.backup")

    def execute(self) -> Path | None:
        """Cria backup datado e remove somente arquivos além da retenção."""
        if self.database is None:
            return None
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        target = self.backup_dir / f"controle_ponto_{datetime.now():%Y-%m-%d_%H-%M-%S}.db"
        source = self.database.engine.raw_connection()
        destination = sqlite3.connect(target)
        try:
            source.driver_connection.backup(destination)
            destination.commit()
        finally:
            destination.close()
            source.close()
        with sqlite3.connect(target) as connection:
            integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
        if integrity != "ok":
            target.unlink(missing_ok=True)
            raise RuntimeError(f"Backup inválido: {integrity}")
        backups = sorted(self.backup_dir.glob("controle_ponto_*.db"), key=lambda path: path.stat().st_mtime, reverse=True)
        for old_backup in backups[self.retention:]:
            old_backup.unlink(missing_ok=True)
        self.logger.info("Backup concluído: %s", target)
        return target
