"""Persistência de marcações brutas e deduplicação por integridade."""

from datetime import datetime
from dataclasses import asdict
import hashlib
import json

from sqlalchemy import or_, select
from sqlalchemy.orm import Session, joinedload

from app.integrations.rwtech.modelos import RegistroRelogio
from app.models import Employee, MarcacaoBruta


class MarcacaoBrutaRepository:
    """Repositório que nunca altera registros brutos existentes."""

    @staticmethod
    def hash_registro(registro: RegistroRelogio, equipamento_id: str) -> str:
        identity = (
            f"{equipamento_id}|NSR|{registro.nsr}"
            if registro.nsr
            else f"{equipamento_id}|{registro.codigo_funcionario}|{registro.data_hora.isoformat()}|{registro.codigo_original or ''}"
        )
        return hashlib.sha256(identity.encode("utf-8")).hexdigest()

    def importar(self, session: Session, registros: list[RegistroRelogio], equipamento_id: str = "RELOGIO_PRINCIPAL", origem: str = "MOCK") -> tuple[int, int, int]:
        novos = duplicados = falhas = 0
        employees = {
            value: employee
            for employee in session.scalars(select(Employee))
            for value in (employee.codigo_relogio, employee.matricula)
            if value
        }
        for registro in registros:
            marker_hash = self.hash_registro(registro, equipamento_id)
            if session.scalar(select(MarcacaoBruta).where(MarcacaoBruta.hash_integridade == marker_hash)):
                duplicados += 1
                continue
            try:
                employee = employees.get(registro.codigo_funcionario)
                session.add(MarcacaoBruta(
                    funcionario_id=employee.id if employee else None,
                    equipamento_id=equipamento_id,
                    codigo_funcionario_relogio=registro.codigo_funcionario,
                    nsr=registro.nsr,
                    data_hora_marcacao=registro.data_hora,
                    metodo_identificacao=registro.metodo_identificacao,
                    origem=origem,
                    codigo_original=registro.codigo_original,
                    dados_brutos=registro.dados_brutos or json.dumps(asdict(registro), ensure_ascii=False, default=str),
                    hash_integridade=marker_hash,
                    importado_em=datetime.now(),
                ))
                novos += 1
            except Exception:
                falhas += 1
        return novos, duplicados, falhas

    def listar(self, session: Session, inicio: datetime, fim: datetime, busca: str = "") -> list[MarcacaoBruta]:
        query = (
            select(MarcacaoBruta)
            .options(joinedload(MarcacaoBruta.employee), joinedload(MarcacaoBruta.apuracoes))
            .where(MarcacaoBruta.data_hora_marcacao >= inicio, MarcacaoBruta.data_hora_marcacao < fim)
            .order_by(MarcacaoBruta.data_hora_marcacao.desc())
        )
        if busca:
            termo = f"%{busca}%"
            query = query.join(MarcacaoBruta.employee, isouter=True).where(
                or_(MarcacaoBruta.codigo_funcionario_relogio.ilike(termo), Employee.nome.ilike(termo), Employee.matricula.ilike(termo))
            )
        return list(session.scalars(query).unique())

    def historico_funcionario(self, session: Session, funcionario_id: int, inicio: datetime, fim: datetime) -> list[MarcacaoBruta]:
        return list(session.scalars(
            select(MarcacaoBruta)
            .where(MarcacaoBruta.funcionario_id == funcionario_id, MarcacaoBruta.data_hora_marcacao >= inicio, MarcacaoBruta.data_hora_marcacao < fim)
            .order_by(MarcacaoBruta.data_hora_marcacao)
        ))
