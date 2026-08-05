"""Estrutura inicial para importação de arquivos AFD."""

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
import logging

from app.integrations.rwtech.modelos import RegistroRelogio


class LayoutAfd(StrEnum):
    AUTO = "AUTO"
    PORTARIA_1510 = "PORTARIA_1510"
    PORTARIA_671_PIS = "PORTARIA_671_PIS"
    PORTARIA_671_CPF = "PORTARIA_671_CPF"


@dataclass(frozen=True, slots=True)
class ResultadoImportacaoAfd:
    arquivo: str
    layout: LayoutAfd
    linhas_lidas: int
    registros: tuple[RegistroRelogio, ...]
    erros: tuple[str, ...]


class AfdParser:
    """Valida o arquivo e preserva linhas para parser específico futuro."""

    def parse(self, path: Path, layout: LayoutAfd = LayoutAfd.AUTO) -> ResultadoImportacaoAfd:
        if not path.is_file():
            return ResultadoImportacaoAfd(str(path), layout, 0, (), ("Arquivo não encontrado.",))
        try:
            lines = path.read_text(encoding="utf-8-sig").splitlines()
        except (OSError, UnicodeError) as error:
            return ResultadoImportacaoAfd(str(path), layout, 0, (), (f"Não foi possível ler o arquivo: {error}",))
        if not lines:
            return ResultadoImportacaoAfd(str(path), layout, 0, (), ("Arquivo vazio.",))
        return ResultadoImportacaoAfd(str(path), layout, len(lines), (), ("Parser do layout ainda não implementado; nenhuma linha foi importada.",))


class AfdImportService:
    """Ponto de entrada para parser, persistência e logging de AFD."""

    def __init__(self, parser: AfdParser | None = None, logger: logging.Logger | None = None) -> None:
        self.parser = parser or AfdParser()
        self.logger = logger or logging.getLogger("controle_ponto.afd")

    def importar(self, path: Path, layout: LayoutAfd = LayoutAfd.AUTO) -> ResultadoImportacaoAfd:
        result = self.parser.parse(path, layout)
        self.logger.info("Importação AFD: arquivo=%s linhas=%d registros=%d erros=%d", path, result.linhas_lidas, len(result.registros), len(result.erros))
        return result
