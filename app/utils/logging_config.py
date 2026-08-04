"""Configuração de logging corporativo."""

import logging
from pathlib import Path


def configure_logging(log_dir: Path) -> logging.Logger:
    log_dir.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s", handlers=[logging.FileHandler(log_dir / "app.log", encoding="utf-8"), logging.StreamHandler()])
    return logging.getLogger("controle_ponto")
