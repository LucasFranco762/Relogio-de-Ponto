"""Contratos para o relógio RWTECH PointLine BIOPROX-C (960)."""
from app.integrations.rwtech.gateway import RelogioPontoGateway
from app.integrations.rwtech.mock_gateway import MockRwtechGateway
from app.integrations.rwtech.modelos import InformacoesRelogio, RegistroRelogio, StatusConexao

__all__ = ["InformacoesRelogio", "MockRwtechGateway", "RegistroRelogio", "RelogioPontoGateway", "StatusConexao"]
