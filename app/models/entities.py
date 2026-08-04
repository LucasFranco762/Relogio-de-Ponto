"""Entidades persistidas no SQLite."""

from datetime import date, datetime, time

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Integer, String, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class User(Base):
    __tablename__ = "usuarios"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    login: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    senha_hash: Mapped[str] = mapped_column(String(255))
    nome: Mapped[str] = mapped_column(String(120))
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)
    ultimo_login: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class Employee(Base):
    __tablename__ = "funcionarios"
    id: Mapped[int] = mapped_column(primary_key=True)
    matricula: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    nome: Mapped[str] = mapped_column(String(150))
    rg: Mapped[str | None] = mapped_column(String(20), nullable=True)
    cpf: Mapped[str | None] = mapped_column(String(14), nullable=True)
    endereco: Mapped[str | None] = mapped_column(String(250), nullable=True)
    data_inicio: Mapped[date | None] = mapped_column(Date, nullable=True)
    carga_horaria_formato: Mapped[str | None] = mapped_column(String(20), nullable=True)
    carga_horaria_valor: Mapped[float | None] = mapped_column(Float, nullable=True)
    cargo: Mapped[str | None] = mapped_column(String(100), nullable=True)
    setor: Mapped[str | None] = mapped_column(String(100), nullable=True)
    carga_horaria_diaria: Mapped[int] = mapped_column(Integer, default=8)
    limite_hora_extra: Mapped[int] = mapped_column(Integer, default=2)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)
    punchs: Mapped[list["Punch"]] = relationship(back_populates="employee", cascade="all, delete-orphan")


class Punch(Base):
    __tablename__ = "marcacoes"
    id: Mapped[int] = mapped_column(primary_key=True)
    funcionario_id: Mapped[int] = mapped_column(ForeignKey("funcionarios.id"))
    data_hora: Mapped[datetime] = mapped_column(DateTime, index=True)
    tipo: Mapped[str] = mapped_column(String(20), default="ENTRADA")
    origem: Mapped[str] = mapped_column(String(30), default="RWTECH")
    importado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    employee: Mapped[Employee] = relationship(back_populates="punchs")


class AppSetting(Base):
    __tablename__ = "configuracoes"
    id: Mapped[int] = mapped_column(primary_key=True)
    empresa: Mapped[str] = mapped_column(String(150), default="")
    horario_inicio: Mapped[time] = mapped_column(Time, default=time(8, 0))
    horario_fim: Mapped[time] = mapped_column(Time, default=time(18, 0))
    modo_controle_horas_extras: Mapped[str] = mapped_column(String(20), default="Mensal")
    limite_horas_extras: Mapped[int] = mapped_column(Integer, default=0)
