"""Regras de faixa para alertas de horas extras."""

from datetime import datetime

from sqlalchemy import select

from app.core.enums import NivelAlerta
from app.models import Alerta


class AlertaService:
    """Persiste alertas somente quando a faixa relevante muda."""

    def nivel_para(self, valor_minutos: int, limite_minutos: int, percentual_atencao: int = 80) -> NivelAlerta:
        if limite_minutos <= 0:
            return NivelAlerta.INFORMACAO
        percentual = valor_minutos * 100 / limite_minutos
        if percentual > 100:
            return NivelAlerta.LIMITE_EXCEDIDO
        if percentual >= 100:
            return NivelAlerta.LIMITE_ATINGIDO
        if percentual >= percentual_atencao:
            return NivelAlerta.ATENCAO
        return NivelAlerta.INFORMACAO

    def avaliar(self, session, funcionario_id: int, valor_minutos: int, limite_minutos: int, percentual_atencao: int = 80) -> Alerta | None:
        nivel = self.nivel_para(valor_minutos, limite_minutos, percentual_atencao)
        previous = session.scalars(select(Alerta).where(Alerta.funcionario_id == funcionario_id).order_by(Alerta.criado_em.desc())).first()
        if previous and previous.nivel == nivel.value:
            return None
        percentual = valor_minutos * 100 / limite_minutos if limite_minutos > 0 else 0
        alert = Alerta(
            funcionario_id=funcionario_id,
            tipo="HORA_EXTRA",
            nivel=nivel.value,
            titulo=f"Horas extras: {nivel.value}",
            mensagem=f"O saldo de horas extras atingiu {percentual:.1f}% do limite.",
            valor_atual_minutos=valor_minutos,
            limite_minutos=limite_minutos,
            percentual=percentual,
        )
        session.add(alert)
        return alert

    def marcar_lido(self, session, alerta_id: int, usuario_id: int) -> None:
        alert = session.get(Alerta, alerta_id)
        if alert:
            alert.lido, alert.lido_em, alert.usuario_leitura_id = True, datetime.now(), usuario_id
