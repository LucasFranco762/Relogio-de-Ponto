"""Fábrica de engine e sessões SQLAlchemy."""

from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime
import hashlib
import json

from sqlalchemy import create_engine, inspect, select, text
from sqlalchemy.orm import Session, sessionmaker


class Database:
    """Gerencia o ciclo de vida do banco e deixa migrações futuras isoladas."""

    def __init__(self, url: str) -> None:
        self.engine = create_engine(url, future=True)
        self.session_factory = sessionmaker(bind=self.engine, expire_on_commit=False)

    def initialize(self) -> None:
        from app.models.base import Base
        Base.metadata.create_all(self.engine)
        self._migrate_employees()
        self._migrate_settings()
        self._migrate_legacy_punches()

    def _migrate_employees(self) -> None:
        """Adiciona campos novos sem apagar dados de bancos existentes."""
        columns = {
            column["name"] for column in inspect(self.engine).get_columns("funcionarios")
        }
        additions = {
            "rg": "VARCHAR(20)",
            "endereco": "VARCHAR(250)",
            "data_inicio": "DATE",
            "carga_horaria_formato": "VARCHAR(20)",
            "carga_horaria_valor": "FLOAT",
            "ativo": "BOOLEAN DEFAULT 1",
            "codigo_relogio": "VARCHAR(30)",
            "pis_pasep": "VARCHAR(20)",
            "data_desligamento": "DATE",
            "carga_horaria_diaria_minutos": "INTEGER",
            "carga_horaria_semanal_minutos": "INTEGER",
            "carga_horaria_mensal_minutos": "INTEGER",
            "limite_horas_extras_minutos": "INTEGER",
            "biometria_cadastrada": "BOOLEAN DEFAULT 0",
            "data_cadastro_biometria": "DATETIME",
        }
        missing = [(name, definition) for name, definition in additions.items() if name not in columns]
        if missing:
            with self.engine.begin() as connection:
                for name, definition in missing:
                    connection.execute(text(f"ALTER TABLE funcionarios ADD COLUMN {name} {definition}"))
        with self.engine.begin() as connection:
            connection.execute(text(
                "CREATE UNIQUE INDEX IF NOT EXISTS uq_funcionarios_codigo_relogio "
                "ON funcionarios(codigo_relogio) WHERE codigo_relogio IS NOT NULL"
            ))

    def _migrate_settings(self) -> None:
        """Adiciona configurações novas sem remover valores existentes."""
        from app.models.entities import AppSetting

        columns = {column["name"] for column in inspect(self.engine).get_columns("configuracoes")}
        additions = {
            "horario_corte": "TIME DEFAULT '00:00:00'",
            "carga_horaria_diaria_padrao_minutos": "INTEGER DEFAULT 480",
            "carga_horaria_semanal_padrao_minutos": "INTEGER DEFAULT 2400",
            "carga_horaria_mensal_padrao_minutos": "INTEGER DEFAULT 10400",
            "modo_hora_extra": "VARCHAR(20) DEFAULT 'MENSAL'",
            "percentual_alerta_hora_extra": "INTEGER DEFAULT 80",
            "intervalo_suspeita_duplicidade_segundos": "INTEGER DEFAULT 30",
        }
        missing = [(name, definition) for name, definition in additions.items() if name not in columns]
        if missing:
            with self.engine.begin() as connection:
                for name, definition in missing:
                    connection.execute(text(f"ALTER TABLE configuracoes ADD COLUMN {name} {definition}"))

    def _migrate_legacy_punches(self) -> None:
        """Copia registros legados para a camada bruta de forma idempotente."""
        from app.models import ApuracaoMarcacao, MarcacaoBruta, Punch

        with self.session() as session:
            legacy_punches = session.scalars(select(Punch).order_by(Punch.id)).all()
            for punch in legacy_punches:
                marker_hash = hashlib.sha256(
                    f"LEGACY|{punch.id}|{punch.funcionario_id}|{punch.data_hora.isoformat()}".encode()
                ).hexdigest()
                if session.scalar(select(MarcacaoBruta).where(MarcacaoBruta.hash_integridade == marker_hash)):
                    continue
                employee = punch.employee
                raw = MarcacaoBruta(
                    id=punch.id,
                    funcionario_id=punch.funcionario_id,
                    codigo_funcionario_relogio=employee.codigo_relogio or employee.matricula,
                    data_hora_marcacao=punch.data_hora,
                    origem=punch.origem or "RELOGIO",
                    codigo_original=str(punch.id),
                    dados_brutos=json.dumps({"tipo_legado": punch.tipo, "id_legado": punch.id}),
                    hash_integridade=marker_hash,
                    importado_em=punch.importado_em or datetime.now(),
                )
                session.add(raw)
                session.flush()
                tipo = punch.tipo if punch.tipo in {"ENTRADA", "SAIDA"} else "NAO_CLASSIFICADA"
                session.add(ApuracaoMarcacao(
                    marcacao_bruta_id=raw.id,
                    tipo_classificado=tipo,
                    origem_classificacao="MIGRACAO_LEGADA",
                    observacao="Classificação preservada da tabela legada.",
                ))

    @contextmanager
    def session(self) -> Iterator[Session]:
        session = self.session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
