"""Abstração do protocolo RWTECH; implementação de rede será adicionada depois."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class ClockPunch:
    matricula: str
    data_hora: datetime


class RWTechClock(ABC):
    """Porta para conectar, consultar status, funcionários e marcações."""

    @abstractmethod
    def conectar(self) -> None: """Estabelece conexão com o relógio."""
    @abstractmethod
    def buscar_marcacoes(self) -> list[ClockPunch]: """Busca marcações novas."""
    @abstractmethod
    def status(self) -> str: """Retorna o status do equipamento."""
    @abstractmethod
    def funcionarios(self) -> list[dict[str, str]]: """Consulta matrículas no relógio."""
    @abstractmethod
    def sincronizar(self) -> int: """Sincroniza dados e retorna quantidade processada."""
