"""Caso de uso das configurações operacionais."""

from datetime import time

from sqlalchemy import select

from app.database.engine import Database
from app.models import AppSetting


class SettingsService:
    """Lê e grava a configuração única da empresa."""

    def __init__(self, database: Database) -> None:
        self.database = database

    def get(self) -> AppSetting:
        with self.database.session() as session:
            item = session.scalar(select(AppSetting).limit(1))
            if item is None:
                item = AppSetting(); session.add(item); session.flush()
            return item

    def save(self, empresa: str, inicio: time, fim: time, modo: str, limite: int) -> None:
        with self.database.session() as session:
            item = session.scalar(select(AppSetting).limit(1)) or AppSetting()
            item.empresa, item.horario_inicio, item.horario_fim = empresa, inicio, fim
            item.modo_controle_horas_extras, item.limite_horas_extras = modo, limite
            session.add(item)
