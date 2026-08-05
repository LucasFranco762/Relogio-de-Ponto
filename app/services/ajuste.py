"""Ajustes manuais com justificativa e auditoria."""

from app.models import AjusteManual
from app.services.auditoria import AuditoriaService


class AjusteService:
    """Cria ajustes sem alterar a marcação bruta."""

    def __init__(self, auditoria: AuditoriaService | None = None) -> None:
        self.auditoria = auditoria or AuditoriaService()

    def criar(self, session, funcionario_id: int | None, jornada_id: int | None, marcacao_bruta_id: int | None, tipo_ajuste: str, valor_anterior, valor_novo, justificativa: str, usuario_id: int) -> AjusteManual:
        if not justificativa or not justificativa.strip():
            raise ValueError("A justificativa do ajuste é obrigatória.")
        item = AjusteManual(
            funcionario_id=funcionario_id, jornada_id=jornada_id, marcacao_bruta_id=marcacao_bruta_id,
            tipo_ajuste=tipo_ajuste, valor_anterior=str(valor_anterior) if valor_anterior is not None else None,
            valor_novo=str(valor_novo) if valor_novo is not None else None, justificativa=justificativa.strip(), usuario_id=usuario_id,
        )
        session.add(item)
        session.flush()
        self.auditoria.registrar(session, usuario_id, "CRIACAO", "AjusteManual", item.id, valor_anterior, valor_novo, justificativa)
        return item
