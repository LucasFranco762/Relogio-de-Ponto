"""Orquestra o reprocessamento de jornadas a partir de marcações brutas."""

from collections import defaultdict
from datetime import date, datetime, time, timedelta
import logging

from sqlalchemy import select

from app.database.engine import Database
from app.models import AppSetting, Employee, MarcacaoBruta
from app.repositories.marcacoes_brutas import MarcacaoBrutaRepository
from app.services.apuracao import MotorApuracaoService


class JornadaService:
    """Agrupa registros por funcionário e data de referência e persiste apurações."""

    def __init__(self, database: Database, motor: MotorApuracaoService | None = None, logger: logging.Logger | None = None) -> None:
        self.database = database
        self.motor = motor or MotorApuracaoService()
        self.logger = logger or logging.getLogger("controle_ponto.jornada")

    def recalcular_periodo(self, inicio: date, fim: date) -> int:
        with self.database.session() as session:
            setting = session.scalar(select(AppSetting).limit(1))
            cutoff = setting.horario_corte if setting and setting.horario_corte else time(0, 0)
            window_start = datetime.combine(inicio, cutoff)
            window_end = datetime.combine(fim + timedelta(days=1), cutoff)
            markers = list(session.scalars(
                select(MarcacaoBruta)
                .where(MarcacaoBruta.data_hora_marcacao >= window_start, MarcacaoBruta.data_hora_marcacao < window_end)
                .order_by(MarcacaoBruta.data_hora_marcacao)
            ))
            employees = {employee.id: employee for employee in session.scalars(select(Employee))}
            groups: dict[tuple[int, date], list[MarcacaoBruta]] = defaultdict(list)
            for marker in markers:
                if marker.funcionario_id is None or marker.funcionario_id not in employees:
                    continue
                reference = self.motor.data_referencia(marker.data_hora_marcacao, cutoff)
                if inicio <= reference <= fim:
                    groups[(marker.funcionario_id, reference)].append(marker)
            for (employee_id, reference), grouped in groups.items():
                employee = employees[employee_id]
                minutes = employee.carga_horaria_diaria_minutos or round((employee.carga_horaria_valor or employee.carga_horaria_diaria or 8) * 60)
                period_open = reference == date.today()
                self.motor.apurar_e_persistir(session, employee_id, reference, grouped, minutes, period_open)
            self.logger.info("Jornadas recalculadas: %d", len(groups))
            return len(groups)
