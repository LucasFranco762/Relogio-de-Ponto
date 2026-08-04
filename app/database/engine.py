"""Fábrica de engine e sessões SQLAlchemy."""

from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy import create_engine, inspect, text
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
        }
        missing = [(name, definition) for name, definition in additions.items() if name not in columns]
        if missing:
            with self.engine.begin() as connection:
                for name, definition in missing:
                    connection.execute(text(f"ALTER TABLE funcionarios ADD COLUMN {name} {definition}"))

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
