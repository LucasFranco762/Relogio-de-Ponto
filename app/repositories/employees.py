"""Acesso a funcionários, sem regras de apresentação."""

from __future__ import annotations

from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session

from app.models import Employee, Punch


class EmployeeRepository:
    """Operações CRUD de funcionários."""

    def list(self, session: Session, search: str = "", active: bool | None = True) -> list[Employee]:
        query = select(Employee).order_by(Employee.nome)
        if active is not None:
            query = query.where(Employee.ativo.is_(active))
        if search:
            term = f"%{search}%"
            query = query.where(or_(Employee.nome.ilike(term), Employee.matricula.ilike(term)))
        return list(session.scalars(query))

    def get(self, session: Session, employee_id: int) -> Employee | None:
        return session.get(Employee, employee_id)

    def punch_history(self, session: Session, employee_id: int, start, end) -> list[Punch]:
        query = (
            select(Punch)
            .where(and_(Punch.funcionario_id == employee_id, Punch.data_hora >= start, Punch.data_hora < end))
            .order_by(Punch.data_hora)
        )
        return list(session.scalars(query))

    def save(self, session: Session, employee: Employee) -> Employee:
        session.add(employee)
        session.flush()
        return employee

    def delete(self, session: Session, employee: Employee) -> None:
        session.delete(employee)
