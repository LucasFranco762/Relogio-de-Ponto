"""CRUD visual de funcionários."""

from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QDialog,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.services.employees import EmployeeService
from app.utils.table_columns import TableColumnSettings


LOWERCASE_NAME_WORDS = {
    "da", "das", "de", "des", "di", "do", "dos", "du",
    "a", "e", "i", "o", "u", "as", "os",
}


def title_case_name(value: str) -> str:
    """Aplica TitleCase ao nome, preservando preposições em minúsculo."""
    words = value.split(" ")
    formatted = []
    for word in words:
        if not word:
            formatted.append("")
            continue
        lowered = word.lower()
        formatted.append(
            lowered if lowered in LOWERCASE_NAME_WORDS
            else lowered[:1].upper() + lowered[1:]
        )
    return " ".join(formatted)


def valid_cpf(value: str) -> bool:
    """Valida os dígitos verificadores do CPF quando o campo foi informado."""
    digits = "".join(character for character in value if character.isdigit())
    if not digits:
        return True
    if len(digits) != 11 or len(set(digits)) == 1:
        return False
    first = sum(int(digits[index]) * (10 - index) for index in range(9))
    check_one = (first * 10 % 11) % 10
    second = sum(int(digits[index]) * (11 - index) for index in range(10))
    check_two = (second * 10 % 11) % 10
    return digits[-2:] == f"{check_one}{check_two}"


def confirm_action(parent: QWidget, title: str, message: str) -> bool:
    """Exibe confirmação com rótulos fixos em português brasileiro."""
    dialog = QMessageBox(QMessageBox.Icon.Question, title, message, parent=parent)
    yes_button = dialog.addButton("Sim", QMessageBox.ButtonRole.AcceptRole)
    dialog.addButton("Não", QMessageBox.ButtonRole.RejectRole)
    dialog.exec()
    return dialog.clickedButton() is yes_button


class NewEmployeeDialog(QDialog):
    """Formulário de inclusão de funcionário."""

    def __init__(self, employee=None, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.editing = employee is not None
        self.setWindowTitle("Editar funcionário" if self.editing else "Novo funcionário")
        self.setModal(True)

        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.name = QLineEdit()
        self._formatting_name = False
        self.name.textChanged.connect(self._format_name)
        self.registration = QLineEdit()
        self.clock_code = QLineEdit()
        self.rg = QLineEdit()
        self.cpf = QLineEdit()
        self.pis_pasep = QLineEdit()
        self.cpf.setInputMask("000.000.000-00;_")
        self.address = QLineEdit()
        self.role = QLineEdit()
        self.department = QLineEdit()
        self.start_date = QDateEdit(QDate.currentDate())
        self.start_date.setCalendarPopup(True)
        self.hours_format = QComboBox()
        self.hours_format.addItems(["Selecione", "Diária", "Semanal", "Mensal"])
        self.hours_format.currentIndexChanged.connect(self._update_hours_value)
        self.hours_value_label = QLabel("Valor da carga horária")
        self.hours_value = QDoubleSpinBox()
        self.hours_value.setRange(0.01, 9999.99)
        self.hours_value.setDecimals(2)
        self.hours_value.setSingleStep(0.5)

        form.addRow("Nome completo", self.name)
        form.addRow("Matrícula", self.registration)
        form.addRow("Código no relógio", self.clock_code)
        form.addRow("RG", self.rg)
        form.addRow("CPF", self.cpf)
        form.addRow("PIS/PASEP", self.pis_pasep)
        form.addRow("Endereço", self.address)
        form.addRow("Cargo", self.role)
        form.addRow("Setor", self.department)
        form.addRow("Data início", self.start_date)
        form.addRow("Carga horária", self.hours_format)
        form.addRow(self.hours_value_label, self.hours_value)
        layout.addLayout(form)

        if self.editing:
            self.name.setText(employee.nome or "")
            self.registration.setText(employee.matricula or "")
            self.clock_code.setText(employee.codigo_relogio or "")
            self.rg.setText(employee.rg or "")
            self.cpf.setText(employee.cpf or "")
            self.pis_pasep.setText(employee.pis_pasep or "")
            self.address.setText(employee.endereco or "")
            self.role.setText(employee.cargo or "")
            self.department.setText(employee.setor or "")
            if employee.data_inicio:
                self.start_date.setDate(QDate(employee.data_inicio.year, employee.data_inicio.month, employee.data_inicio.day))
            if employee.carga_horaria_formato:
                self.hours_format.setCurrentText(employee.carga_horaria_formato)
            self.hours_value.setValue(employee.carga_horaria_valor or employee.carga_horaria_diaria or 8)

        buttons = QHBoxLayout()
        cancel = QPushButton("Cancelar")
        cancel.clicked.connect(self.reject)
        save = QPushButton("Salvar alterações" if self.editing else "Salvar")
        save.clicked.connect(self._validate_and_accept)
        buttons.addStretch()
        buttons.addWidget(cancel)
        buttons.addWidget(save)
        layout.addLayout(buttons)
        self._update_hours_value(0)
        self.resize(self.sizeHint().width() * 3, self.sizeHint().height())

    def _format_name(self, value: str) -> None:
        if self._formatting_name:
            return
        formatted = title_case_name(value)
        if formatted == value:
            return
        self._formatting_name = True
        cursor_position = self.name.cursorPosition()
        self.name.setText(formatted)
        self.name.setCursorPosition(min(cursor_position, len(formatted)))
        self._formatting_name = False

    def _update_hours_value(self, index: int) -> None:
        selected = index > 0
        self.hours_value_label.setVisible(selected)
        self.hours_value.setVisible(selected)
        self.hours_value.setEnabled(selected)

    def _validate_and_accept(self) -> None:
        if not self.name.text().strip() or not self.registration.text().strip():
            QMessageBox.warning(self, "Dados obrigatórios", "Informe o nome completo e a matrícula.")
            return
        if self.hours_format.currentIndex() == 0:
            QMessageBox.warning(self, "Dados obrigatórios", "Selecione o formato da carga horária.")
            self.hours_format.setFocus()
            return
        if self.hours_value.value() <= 0:
            QMessageBox.warning(self, "Dados obrigatórios", "Informe um valor válido para a carga horária.")
            self.hours_value.setFocus()
            return
        if not valid_cpf(self.cpf.text()):
            QMessageBox.warning(self, "CPF inválido", "Informe um CPF válido ou deixe o campo em branco.")
            self.cpf.setFocus()
            return
        self.accept()

    def employee_data(self) -> dict:
        return {
            "nome": self.name.text().strip(),
            "matricula": self.registration.text().strip(),
            "codigo_relogio": self.clock_code.text().strip(),
            "rg": self.rg.text().strip(),
            "cpf": self.cpf.text().strip(),
            "pis_pasep": self.pis_pasep.text().strip(),
            "endereco": self.address.text().strip(),
            "cargo": self.role.text().strip(),
            "setor": self.department.text().strip(),
            "data_inicio": self.start_date.date().toPython(),
            "carga_horaria_formato": self.hours_format.currentText(),
            "carga_horaria_valor": self.hours_value.value(),
        }


class EmployeesPage(QWidget):
    """Gerencia funcionários ativos e inativos em abas mutuamente exclusivas."""

    def __init__(self, service: EmployeeService, column_settings: TableColumnSettings) -> None:
        super().__init__(); self.service = service
        layout = QVBoxLayout(self)
        heading = QHBoxLayout(); heading.addWidget(QLabel("Funcionários"))
        self.search = QLineEdit(); self.search.setPlaceholderText("Pesquisar por nome ou matrícula..."); self.search.textChanged.connect(self.refresh)
        heading.addWidget(self.search)
        add = QPushButton("+ Cadastrar"); add.clicked.connect(self.add_employee); heading.addWidget(add)
        self.edit_button = QPushButton("Editar"); self.edit_button.setEnabled(False); self.edit_button.clicked.connect(self.edit_employee); heading.addWidget(self.edit_button)
        self.move_button = QPushButton(); self.move_button.clicked.connect(self.move_selected); heading.addWidget(self.move_button)
        remove = QPushButton("Excluir"); remove.clicked.connect(self.delete_employee); heading.addWidget(remove)
        layout.addLayout(heading)
        self.tabs = QTabWidget()
        self.active_table = self._create_table(column_settings, "funcionarios_ativos")
        self.inactive_table = self._create_table(column_settings, "funcionarios_inativos")
        self.tabs.addTab(self.active_table, "Funcionários Ativos")
        self.tabs.addTab(self.inactive_table, "Funcionários Inativos")
        self.tabs.currentChanged.connect(self._update_move_button)
        self.active_table.itemSelectionChanged.connect(self._update_actions)
        self.inactive_table.itemSelectionChanged.connect(self._update_actions)
        layout.addWidget(self.tabs); self._update_move_button(0); self.refresh()

    def _create_table(self, column_settings: TableColumnSettings, table_id: str) -> QTableWidget:
        table = QTableWidget(0, 5)
        table.setHorizontalHeaderLabels(["Matrícula", "Nome", "Cargo", "Setor", "Status"])
        table.horizontalHeader().setStretchLastSection(True)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        column_settings.apply(table, table_id)
        return table

    def _update_move_button(self, index: int) -> None:
        self.move_button.setText("Mover para Inativos" if index == 0 else "Mover para Ativos")

    def _update_actions(self) -> None:
        self.edit_button.setEnabled(len(self._current_table().selectionModel().selectedRows()) == 1)

    def _current_table(self) -> QTableWidget:
        return self.active_table if self.tabs.currentIndex() == 0 else self.inactive_table

    def refresh(self) -> None:
        search = self.search.text() if hasattr(self, "search") else ""
        for table, active in ((self.active_table, True), (self.inactive_table, False)):
            employees = self.service.list(search, active=active)
            table.setRowCount(len(employees))
            for row, employee in enumerate(employees):
                values = [employee.matricula, employee.nome, employee.cargo or "—", employee.setor or "—", "Ativo" if employee.ativo else "Inativo"]
                for col, value in enumerate(values): table.setItem(row, col, QTableWidgetItem(value))

    def _selected_id(self):
        table = self._current_table()
        row = table.currentRow()
        employees = self.service.list(self.search.text(), active=self.tabs.currentIndex() == 0)
        return employees[row].id if 0 <= row < len(employees) else None

    def _selected_employee(self):
        employee_id = self._selected_id()
        return self.service.get(employee_id) if employee_id is not None else None

    def add_employee(self) -> None:
        dialog = NewEmployeeDialog(parent=self)
        if dialog.exec():
            try:
                self.service.save(dialog.employee_data())
                self.refresh()
            except Exception as error:
                QMessageBox.critical(self, "Erro", str(error))

    def edit_employee(self) -> None:
        employee_id = self._selected_id()
        employee = self._selected_employee()
        if employee_id is None or employee is None:
            return
        dialog = NewEmployeeDialog(employee, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                self.service.save(dialog.employee_data(), employee_id)
                self.refresh()
            except Exception as error:
                QMessageBox.critical(self, "Erro ao editar funcionário", str(error))

    def move_selected(self) -> None:
        employee_id = self._selected_id()
        if employee_id is None:
            return
        moving_to_active = self.tabs.currentIndex() == 1
        destination = "Funcionários Ativos" if moving_to_active else "Funcionários Inativos"
        if confirm_action(self, "Alterar situação", f"Mover o funcionário selecionado para {destination}?"):
            self.service.set_active(employee_id, moving_to_active)
            self.refresh()

    def delete_employee(self) -> None:
        employee_id = self._selected_id()
        if employee_id is not None and confirm_action(self, "Excluir", "Excluir o funcionário selecionado?"):
            self.service.delete(employee_id); self.refresh()
