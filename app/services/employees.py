"""Casos de uso de funcionários."""

from app.database.engine import Database
from app.models import Employee
from app.repositories.employees import EmployeeRepository
from app.repositories.marcacoes_brutas import MarcacaoBrutaRepository


class EmployeeService:
    """Orquestra CRUD e validações básicas."""

    def __init__(self, database: Database, repository: EmployeeRepository, raw_repository: MarcacaoBrutaRepository | None = None) -> None:
        self.database, self.repository = database, repository
        self.raw_repository = raw_repository or MarcacaoBrutaRepository()

    def list(self, search: str = "", active: bool | None = True) -> list[Employee]:
        with self.database.session() as session:
            return self.repository.list(session, search, active)

    def get(self, employee_id: int):
        with self.database.session() as session:
            return self.repository.get(session, employee_id)

    def punch_history(self, employee_id: int, start, end):
        with self.database.session() as session:
            return self.repository.punch_history(session, employee_id, start, end)

    def raw_punch_history(self, employee_id: int, start, end):
        with self.database.session() as session:
            return self.raw_repository.historico_funcionario(session, employee_id, start, end)

    def list_punches(self, start, end, search: str = ""):
        with self.database.session() as session:
            return self.repository.list_punches(session, start, end, search)

    def list_raw_markings(self, start, end, search: str = ""):
        with self.database.session() as session:
            return self.raw_repository.listar(session, start, end, search)

    def save(self, data: dict, employee_id: int | None = None) -> Employee:
        with self.database.session() as session:
            employee = self.repository.get(session, employee_id) if employee_id else Employee(matricula="", nome="")
            if employee is None:
                raise ValueError("Funcionário não encontrado")
            employee.matricula, employee.nome = data["matricula"].strip(), data["nome"].strip()
            employee.codigo_relogio = data.get("codigo_relogio") or None
            employee.rg = data.get("rg") or None
            employee.cpf = data.get("cpf") or None
            employee.pis_pasep = data.get("pis_pasep") or None
            employee.endereco = data.get("endereco") or None
            employee.data_inicio = data.get("data_inicio")
            employee.cargo, employee.setor = data.get("cargo"), data.get("setor")
            employee.carga_horaria_formato = data.get("carga_horaria_formato") or "Diária"
            employee.carga_horaria_valor = float(data.get("carga_horaria_valor", data.get("carga_horaria_diaria", 8)))
            employee.carga_horaria_diaria = int(round(employee.carga_horaria_valor))
            employee.carga_horaria_diaria_minutos = int(round(employee.carga_horaria_valor * 60))
            employee.carga_horaria_semanal_minutos = int(data.get("carga_horaria_semanal_minutos", employee.carga_horaria_diaria_minutos * 5))
            employee.carga_horaria_mensal_minutos = int(data.get("carga_horaria_mensal_minutos", employee.carga_horaria_diaria_minutos * 22))
            employee.limite_hora_extra = int(data.get("limite_hora_extra", 2))
            employee.limite_horas_extras_minutos = int(data.get("limite_horas_extras_minutos", employee.limite_hora_extra * 60))
            if not employee_id or "ativo" in data:
                employee.ativo = bool(data.get("ativo", True))
            return self.repository.save(session, employee)

    def set_active(self, employee_id: int, active: bool) -> None:
        with self.database.session() as session:
            employee = self.repository.get(session, employee_id)
            if employee:
                employee.ativo = active

    def toggle(self, employee_id: int) -> None:
        with self.database.session() as session:
            employee = self.repository.get(session, employee_id)
            if employee:
                employee.ativo = not employee.ativo

    def delete(self, employee_id: int) -> None:
        with self.database.session() as session:
            employee = self.repository.get(session, employee_id)
            if employee:
                self.repository.delete(session, employee)
