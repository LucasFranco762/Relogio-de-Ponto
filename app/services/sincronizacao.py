"""Orquestra sincronizações através de um gateway injetado."""

import logging
from datetime import datetime

from app.database.engine import Database
from app.integrations.rwtech.gateway import RelogioPontoGateway
from app.integrations.rwtech.modelos import ResultadoSincronizacao
from app.repositories.marcacoes_brutas import MarcacaoBrutaRepository


class SincronizacaoService:
    """Importa registros do gateway sem presumir protocolo de rede."""

    def __init__(self, database: Database, gateway: RelogioPontoGateway, repository: MarcacaoBrutaRepository | None = None, logger: logging.Logger | None = None) -> None:
        self.database = database
        self.gateway = gateway
        self.repository = repository or MarcacaoBrutaRepository()
        self.logger = logger or logging.getLogger("controle_ponto.sincronizacao")

    def sincronizar(self, inicio: datetime | None = None, fim: datetime | None = None) -> ResultadoSincronizacao:
        registros = self.gateway.buscar_marcacoes(inicio, fim)
        with self.database.session() as session:
            novos, duplicados, falhas = self.repository.importar(session, registros, origem="MOCK")
        resultado = ResultadoSincronizacao(len(registros), novos, duplicados, falhas)
        self.logger.info("Sincronização concluída: %s", resultado)
        return resultado
