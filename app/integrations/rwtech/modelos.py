"""Modelos independentes do fabricante para integração com relógios."""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class StatusConexao(StrEnum):
    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"
    NAO_CONFIGURADO = "NAO_CONFIGURADO"
    ERRO = "ERRO"


@dataclass(frozen=True, slots=True)
class RegistroRelogio:
    nsr: str | None
    codigo_funcionario: str
    data_hora: datetime
    metodo_identificacao: str | None = None
    codigo_original: str | None = None
    dados_brutos: str | None = None


@dataclass(frozen=True, slots=True)
class InformacoesRelogio:
    modelo: str
    identificador: str
    status: StatusConexao


@dataclass(frozen=True, slots=True)
class ResultadoSincronizacao:
    encontrados: int
    novos: int
    duplicados: int
    falhas: int

