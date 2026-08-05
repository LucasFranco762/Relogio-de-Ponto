"""Gateway simulado para testes e desenvolvimento sem comunicação presumida."""

from datetime import datetime

from app.integrations.rwtech.gateway import RelogioPontoGateway
from app.integrations.rwtech.modelos import InformacoesRelogio, RegistroRelogio, StatusConexao


class MockRwtechGateway(RelogioPontoGateway):
    """Fonte controlada de registros simulados."""

    def __init__(self, registros: list[RegistroRelogio] | None = None, modelo: str = "RWTECH PointLine BIOPROX-C (960)") -> None:
        self.registros = list(registros or [])
        self.modelo = modelo

    def testar_conexao(self) -> StatusConexao:
        return StatusConexao.ONLINE

    def buscar_marcacoes(self, inicio: datetime | None = None, fim: datetime | None = None) -> list[RegistroRelogio]:
        return [
            item for item in self.registros
            if (inicio is None or item.data_hora >= inicio) and (fim is None or item.data_hora < fim)
        ]

    def obter_informacoes(self) -> InformacoesRelogio:
        return InformacoesRelogio(self.modelo, "MOCK", StatusConexao.ONLINE)

