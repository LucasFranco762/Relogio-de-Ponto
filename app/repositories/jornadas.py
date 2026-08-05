"""Consultas de jornadas diárias calculadas."""

from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models import JornadaDiaria


class JornadaRepository:
    """Acesso às jornadas sem conter regras de cálculo."""

    def listar(self, session: Session, inicio: date, fim: date, funcionario_id: int | None = None) -> list[JornadaDiaria]:
        query = (
            select(JornadaDiaria)
            .options(joinedload(JornadaDiaria.employee))
            .where(JornadaDiaria.data_referencia >= inicio, JornadaDiaria.data_referencia <= fim)
            .order_by(JornadaDiaria.data_referencia.desc(), JornadaDiaria.funcionario_id)
        )
        if funcionario_id is not None:
            query = query.where(JornadaDiaria.funcionario_id == funcionario_id)
        return list(session.scalars(query))
