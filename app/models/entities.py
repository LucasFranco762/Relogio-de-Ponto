"""Entidades persistidas no SQLite."""

from datetime import date, datetime, time

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Integer, String, Text, Time, UniqueConstraint
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
    codigo_relogio: Mapped[str | None] = mapped_column(String(30), unique=True, nullable=True)
    pis_pasep: Mapped[str | None] = mapped_column(String(20), nullable=True)
    data_desligamento: Mapped[date | None] = mapped_column(Date, nullable=True)
    carga_horaria_diaria_minutos: Mapped[int | None] = mapped_column(Integer, nullable=True)
    carga_horaria_semanal_minutos: Mapped[int | None] = mapped_column(Integer, nullable=True)
    carga_horaria_mensal_minutos: Mapped[int | None] = mapped_column(Integer, nullable=True)
    limite_horas_extras_minutos: Mapped[int | None] = mapped_column(Integer, nullable=True)
    biometria_cadastrada: Mapped[bool] = mapped_column(Boolean, default=False)
    data_cadastro_biometria: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    punchs: Mapped[list["Punch"]] = relationship(back_populates="employee", cascade="all, delete-orphan")
    marcacoes_brutas: Mapped[list["MarcacaoBruta"]] = relationship(back_populates="employee")
    jornadas: Mapped[list["JornadaDiaria"]] = relationship(back_populates="employee")


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
    horario_corte: Mapped[time] = mapped_column(Time, default=time(0, 0))
    carga_horaria_diaria_padrao_minutos: Mapped[int] = mapped_column(Integer, default=480)
    carga_horaria_semanal_padrao_minutos: Mapped[int] = mapped_column(Integer, default=2400)
    carga_horaria_mensal_padrao_minutos: Mapped[int] = mapped_column(Integer, default=10400)
    modo_hora_extra: Mapped[str] = mapped_column(String(20), default="MENSAL")
    percentual_alerta_hora_extra: Mapped[int] = mapped_column(Integer, default=80)
    intervalo_suspeita_duplicidade_segundos: Mapped[int] = mapped_column(Integer, default=30)


class MarcacaoBruta(Base):
    """Registro original recebido do relógio ou de uma importação."""

    __tablename__ = "marcacoes_brutas"
    id: Mapped[int] = mapped_column(primary_key=True)
    nsr: Mapped[str | None] = mapped_column(String(40), nullable=True)
    equipamento_id: Mapped[str] = mapped_column(String(80), default="RELOGIO_PRINCIPAL")
    funcionario_id: Mapped[int | None] = mapped_column(ForeignKey("funcionarios.id"), nullable=True)
    codigo_funcionario_relogio: Mapped[str] = mapped_column(String(30), index=True)
    data_hora_marcacao: Mapped[datetime] = mapped_column(DateTime, index=True)
    metodo_identificacao: Mapped[str | None] = mapped_column(String(30), nullable=True)
    origem: Mapped[str] = mapped_column(String(30), default="RELOGIO")
    codigo_original: Mapped[str | None] = mapped_column(String(255), nullable=True)
    dados_brutos: Mapped[str | None] = mapped_column(Text, nullable=True)
    hash_integridade: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    importado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    arquivo_origem: Mapped[str | None] = mapped_column(String(255), nullable=True)
    layout_origem: Mapped[str | None] = mapped_column(String(40), nullable=True)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)
    employee: Mapped[Employee | None] = relationship(back_populates="marcacoes_brutas")
    apuracoes: Mapped[list["ApuracaoMarcacao"]] = relationship(back_populates="marcacao_bruta", cascade="all, delete-orphan")


class ApuracaoMarcacao(Base):
    __tablename__ = "apuracoes_marcacoes"
    id: Mapped[int] = mapped_column(primary_key=True)
    marcacao_bruta_id: Mapped[int] = mapped_column(ForeignKey("marcacoes_brutas.id"), unique=True)
    jornada_id: Mapped[int | None] = mapped_column(ForeignKey("jornadas_diarias.id"), nullable=True)
    tipo_classificado: Mapped[str] = mapped_column(String(30), default="NAO_CLASSIFICADA")
    ordem_no_periodo: Mapped[int | None] = mapped_column(Integer, nullable=True)
    classificada_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    origem_classificacao: Mapped[str] = mapped_column(String(30), default="MOTOR_APURACAO")
    versao_calculo: Mapped[int] = mapped_column(Integer, default=1)
    observacao: Mapped[str | None] = mapped_column(Text, nullable=True)
    marcacao_bruta: Mapped[MarcacaoBruta] = relationship(back_populates="apuracoes")
    jornada: Mapped["JornadaDiaria | None"] = relationship(back_populates="apuracoes")


class JornadaDiaria(Base):
    __tablename__ = "jornadas_diarias"
    __table_args__ = (UniqueConstraint("funcionario_id", "data_referencia", name="uq_jornada_funcionario_data"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    funcionario_id: Mapped[int] = mapped_column(ForeignKey("funcionarios.id"), index=True)
    data_referencia: Mapped[date] = mapped_column(Date, index=True)
    inicio_periodo: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    fim_periodo: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    carga_prevista_minutos: Mapped[int] = mapped_column(Integer, default=0)
    total_trabalhado_minutos: Mapped[int] = mapped_column(Integer, default=0)
    total_extra_minutos: Mapped[int] = mapped_column(Integer, default=0)
    total_falta_minutos: Mapped[int] = mapped_column(Integer, default=0)
    saldo_minutos: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(30), default="NAO_INICIADA")
    calculada_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    versao_calculo: Mapped[int] = mapped_column(Integer, default=1)
    employee: Mapped[Employee] = relationship(back_populates="jornadas")
    apuracoes: Mapped[list[ApuracaoMarcacao]] = relationship(back_populates="jornada")


class MovimentacaoBancoHoras(Base):
    __tablename__ = "movimentacoes_banco_horas"
    id: Mapped[int] = mapped_column(primary_key=True)
    funcionario_id: Mapped[int] = mapped_column(ForeignKey("funcionarios.id"), index=True)
    tipo: Mapped[str] = mapped_column(String(20))
    quantidade_minutos: Mapped[int] = mapped_column(Integer)
    data_hora: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    descricao: Mapped[str] = mapped_column(Text)
    usuario_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"), nullable=True)
    jornada_id: Mapped[int | None] = mapped_column(ForeignKey("jornadas_diarias.id"), nullable=True)


class Alerta(Base):
    __tablename__ = "alertas"
    id: Mapped[int] = mapped_column(primary_key=True)
    funcionario_id: Mapped[int | None] = mapped_column(ForeignKey("funcionarios.id"), nullable=True, index=True)
    tipo: Mapped[str] = mapped_column(String(40))
    nivel: Mapped[str] = mapped_column(String(30))
    titulo: Mapped[str] = mapped_column(String(150))
    mensagem: Mapped[str] = mapped_column(Text)
    valor_atual_minutos: Mapped[int] = mapped_column(Integer, default=0)
    limite_minutos: Mapped[int] = mapped_column(Integer, default=0)
    percentual: Mapped[float] = mapped_column(Float, default=0)
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    lido: Mapped[bool] = mapped_column(Boolean, default=False)
    lido_em: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    usuario_leitura_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"), nullable=True)


class AjusteManual(Base):
    __tablename__ = "ajustes_manuais"
    id: Mapped[int] = mapped_column(primary_key=True)
    funcionario_id: Mapped[int | None] = mapped_column(ForeignKey("funcionarios.id"), nullable=True)
    jornada_id: Mapped[int | None] = mapped_column(ForeignKey("jornadas_diarias.id"), nullable=True)
    marcacao_bruta_id: Mapped[int | None] = mapped_column(ForeignKey("marcacoes_brutas.id"), nullable=True)
    tipo_ajuste: Mapped[str] = mapped_column(String(40))
    valor_anterior: Mapped[str | None] = mapped_column(Text, nullable=True)
    valor_novo: Mapped[str | None] = mapped_column(Text, nullable=True)
    justificativa: Mapped[str] = mapped_column(Text)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)


class Auditoria(Base):
    __tablename__ = "auditoria"
    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"), nullable=True)
    acao: Mapped[str] = mapped_column(String(60))
    entidade: Mapped[str] = mapped_column(String(80))
    entidade_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    valor_anterior: Mapped[str | None] = mapped_column(Text, nullable=True)
    valor_novo: Mapped[str | None] = mapped_column(Text, nullable=True)
    data_hora: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    descricao: Mapped[str] = mapped_column(Text)
