"""Contrato de comunicação com o relógio de ponto."""

from abc import ABC, abstractmethod
from datetime import datetime

from app.integrations.rwtech.modelos import InformacoesRelogio, RegistroRelogio, StatusConexao


class RelogioPontoGateway(ABC):
    """Porta substituível para integração real ou simulada."""

    @abstractmethod
    def testar_conexao(self) -> StatusConexao:
        raise NotImplementedError

    @abstractmethod
    def buscar_marcacoes(self, inicio: datetime | None = None, fim: datetime | None = None) -> list[RegistroRelogio]:
        raise NotImplementedError

    @abstractmethod
    def obter_informacoes(self) -> InformacoesRelogio:
        raise NotImplementedError

