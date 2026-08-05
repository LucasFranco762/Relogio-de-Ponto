"""Motor determinístico para classificar marcações e calcular jornadas."""

from dataclasses import dataclass
from datetime import date, datetime, timedelta
import logging

from sqlalchemy import select

from app.core.enums import StatusJornada, TipoMarcacao
from app.models import ApuracaoMarcacao, JornadaDiaria


@dataclass(frozen=True, slots=True)
class MarcacaoClassificada:
    """Resultado da classificação de uma marcação bruta."""

    marcacao: object
    tipo: TipoMarcacao
    ordem: int
    observacao: str = ""


@dataclass(frozen=True, slots=True)
class IntervaloApurado:
    entrada: object
    saida: object
    minutos: int


@dataclass(frozen=True, slots=True)
class ResultadoApuracao:
    """Resultado calculado sem modificar as marcações de origem."""

    classificacoes: tuple[MarcacaoClassificada, ...]
    intervalos: tuple[IntervaloApurado, ...]
    total_trabalhado_minutos: int
    carga_prevista_minutos: int
    total_extra_minutos: int
    saldo_minutos: int
    status: StatusJornada


class MotorApuracaoService:
    """Classifica marcações em ordem cronológica e calcula períodos trabalhados."""

    def __init__(self, duplicidade_segundos: int = 30, logger: logging.Logger | None = None) -> None:
        self.duplicidade_segundos = max(0, duplicidade_segundos)
        self.logger = logger or logging.getLogger("controle_ponto.apuracao")

    @staticmethod
    def _timestamp(marker: object) -> datetime:
        value = getattr(marker, "data_hora_marcacao", None)
        if value is None:
            value = getattr(marker, "data_hora")
        return value

    def classificar(self, marcacoes: list[object]) -> tuple[MarcacaoClassificada, ...]:
        ordered = sorted(marcacoes, key=self._timestamp)
        result: list[MarcacaoClassificada] = []
        for index, marker in enumerate(ordered, start=1):
            tipo = TipoMarcacao.ENTRADA if index % 2 else TipoMarcacao.SAIDA
            observation = ""
            if result:
                difference = self._timestamp(marker) - self._timestamp(result[-1].marcacao)
                if difference <= timedelta(seconds=self.duplicidade_segundos):
                    tipo = TipoMarcacao.POSSIVEL_DUPLICIDADE
                    observation = f"Marcação com intervalo inferior a {self.duplicidade_segundos} segundos."
            result.append(MarcacaoClassificada(marker, tipo, index, observation))
        return tuple(result)

    def calcular(
        self,
        marcacoes: list[object],
        carga_prevista_minutos: int,
        periodo_aberto: bool = False,
    ) -> ResultadoApuracao:
        classifications = self.classificar(marcacoes)
        valid = [item for item in classifications if item.tipo != TipoMarcacao.POSSIVEL_DUPLICIDADE]
        intervals: list[IntervaloApurado] = []
        for position in range(0, len(valid) - 1, 2):
            entrada, saida = valid[position], valid[position + 1]
            minutes = int((self._timestamp(saida.marcacao) - self._timestamp(entrada.marcacao)).total_seconds() // 60)
            if minutes >= 0:
                intervals.append(IntervaloApurado(entrada.marcacao, saida.marcacao, minutes))
        total = sum(interval.minutos for interval in intervals)
        saldo = total - carga_prevista_minutos
        open_journey = len(valid) % 2 == 1
        if open_journey:
            status = StatusJornada.EM_ANDAMENTO if periodo_aberto else StatusJornada.INCOMPLETA
        elif any(item.tipo == TipoMarcacao.POSSIVEL_DUPLICIDADE for item in classifications):
            status = StatusJornada.COM_INCONSISTENCIA
        else:
            status = StatusJornada.CONCLUIDA
        self.logger.info(
            "Apuração concluída: marcações=%d, trabalhado=%d, saldo=%d, status=%s",
            len(classifications), total, saldo, status,
        )
        return ResultadoApuracao(
            classificacoes=classifications,
            intervalos=tuple(intervals),
            total_trabalhado_minutos=total,
            carga_prevista_minutos=carga_prevista_minutos,
            total_extra_minutos=max(saldo, 0),
            saldo_minutos=saldo,
            status=status,
        )

    def data_referencia(self, timestamp: datetime, horario_corte) -> date:
        """Obtém a data de referência respeitando o horário de corte configurado."""
        if timestamp.time() < horario_corte:
            return timestamp.date() - timedelta(days=1)
        return timestamp.date()

    def apurar_e_persistir(self, session, funcionario_id: int, data_referencia: date, marcacoes: list[object], carga_prevista_minutos: int, periodo_aberto: bool = False) -> JornadaDiaria:
        """Calcula e persiste somente apuração/jornada, preservando a origem."""
        result = self.calcular(marcacoes, carga_prevista_minutos, periodo_aberto)
        journey = session.scalar(select(JornadaDiaria).where(
            JornadaDiaria.funcionario_id == funcionario_id,
            JornadaDiaria.data_referencia == data_referencia,
        ))
        if journey is None:
            journey = JornadaDiaria(funcionario_id=funcionario_id, data_referencia=data_referencia)
            session.add(journey)
            session.flush()
        journey.carga_prevista_minutos = carga_prevista_minutos
        journey.total_trabalhado_minutos = result.total_trabalhado_minutos
        journey.total_extra_minutos = result.total_extra_minutos
        journey.total_falta_minutos = max(-result.saldo_minutos, 0)
        journey.saldo_minutos = result.saldo_minutos
        journey.status = result.status.value
        journey.calculada_em = datetime.now()
        journey.versao_calculo += 1
        timestamps = [self._timestamp(marker) for marker in marcacoes]
        journey.inicio_periodo = min(timestamps) if timestamps else None
        journey.fim_periodo = max(timestamps) if timestamps else None
        for item in result.classificacoes:
            marker_id = getattr(item.marcacao, "id", None)
            if marker_id is None:
                continue
            apuracao = session.scalar(select(ApuracaoMarcacao).where(ApuracaoMarcacao.marcacao_bruta_id == marker_id))
            if apuracao is None:
                apuracao = ApuracaoMarcacao(marcacao_bruta_id=marker_id)
                session.add(apuracao)
            apuracao.jornada_id = journey.id
            apuracao.tipo_classificado = item.tipo.value
            apuracao.ordem_no_periodo = item.ordem
            apuracao.classificada_em = datetime.now()
            apuracao.versao_calculo = journey.versao_calculo
            apuracao.observacao = item.observacao or None
        session.flush()
        return journey
