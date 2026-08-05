"""Registro central da trilha de auditoria."""

import json

from app.models import Auditoria


class AuditoriaService:
    """Grava ações de negócio sem sobrescrever valores anteriores."""

    def registrar(self, session, usuario_id: int | None, acao: str, entidade: str, entidade_id: int | None = None, anterior=None, novo=None, descricao: str = "") -> Auditoria:
        item = Auditoria(
            usuario_id=usuario_id,
            acao=acao,
            entidade=entidade,
            entidade_id=entidade_id,
            valor_anterior=json.dumps(anterior, ensure_ascii=False, default=str) if anterior is not None else None,
            valor_novo=json.dumps(novo, ensure_ascii=False, default=str) if novo is not None else None,
            descricao=descricao,
        )
        session.add(item)
        return item
