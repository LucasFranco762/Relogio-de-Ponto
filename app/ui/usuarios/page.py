"""Administração dos usuários autorizados a acessar o sistema."""

from PySide6.QtWidgets import (
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.services.auth import AuthenticationService


def confirm_action(parent: QWidget, title: str, message: str) -> bool:
    dialog = QMessageBox(QMessageBox.Icon.Question, title, message, parent=parent)
    yes_button = dialog.addButton("Sim", QMessageBox.ButtonRole.AcceptRole)
    dialog.addButton("Não", QMessageBox.ButtonRole.RejectRole)
    dialog.exec()
    return dialog.clickedButton() is yes_button


class NewUserDialog(QDialog):
    """Formulário de criação de um usuário autorizado."""

    def __init__(self, user=None, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.editing = user is not None
        self.setWindowTitle("Editar usuário" if self.editing else "Novo usuário")
        self.setModal(True)
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.name = QLineEdit(); self.name.setPlaceholderText("Nome completo")
        self.login = QLineEdit(); self.login.setPlaceholderText("Login de acesso")
        self.password = QLineEdit(); self.password.setEchoMode(QLineEdit.EchoMode.Password); self.password.setPlaceholderText("Nova senha (opcional)" if self.editing else "Senha")
        self.confirm_password = QLineEdit(); self.confirm_password.setEchoMode(QLineEdit.EchoMode.Password); self.confirm_password.setPlaceholderText("Confirme a senha")
        if self.editing:
            self.name.setText(user.nome); self.login.setText(user.login)
        form.addRow("Nome", self.name); form.addRow("Login", self.login); form.addRow("Senha", self.password); form.addRow("Confirmar senha", self.confirm_password)
        layout.addLayout(form)
        buttons = QHBoxLayout(); buttons.addStretch()
        cancel = QPushButton("Cancelar"); cancel.clicked.connect(self.reject)
        save = QPushButton("Salvar alterações" if self.editing else "Criar usuário"); save.clicked.connect(self._validate)
        buttons.addWidget(cancel); buttons.addWidget(save); layout.addLayout(buttons)
        self.resize(self.sizeHint().width() * 2, self.sizeHint().height())

    def _validate(self) -> None:
        if not self.name.text().strip() or not self.login.text().strip() or (not self.editing and not self.password.text()):
            QMessageBox.warning(self, "Dados obrigatórios", "Informe nome e login; para novo usuário, informe também a senha.")
            return
        if self.password.text() and self.password.text() != self.confirm_password.text():
            QMessageBox.warning(self, "Senha", "As senhas informadas não são iguais.")
            return
        self.accept()


class UsersPage(QWidget):
    """Lista, cria e exclui usuários com permissão de login."""

    def __init__(self, service: AuthenticationService, current_user_id: int) -> None:
        super().__init__(); self.service, self.current_user_id = service, current_user_id
        layout = QVBoxLayout(self)
        heading = QHBoxLayout(); heading.addWidget(QLabel("Usuários do sistema")); heading.addStretch()
        add = QPushButton("+ Novo usuário"); add.clicked.connect(self.add_user); heading.addWidget(add)
        self.edit_button = QPushButton("Editar usuário"); self.edit_button.setEnabled(False); self.edit_button.clicked.connect(self.edit_user); heading.addWidget(self.edit_button)
        remove = QPushButton("Excluir usuário"); remove.clicked.connect(self.delete_user); heading.addWidget(remove)
        layout.addLayout(heading)
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Nome", "Login", "Situação", "Último acesso"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.itemSelectionChanged.connect(self.update_actions)
        layout.addWidget(self.table)
        self.refresh()

    def update_actions(self) -> None:
        self.edit_button.setEnabled(len(self.table.selectionModel().selectedRows()) == 1)

    def refresh(self) -> None:
        users = self.service.list_users()
        self.table.setRowCount(len(users))
        for row, user in enumerate(users):
            last_access = user.ultimo_login.strftime("%d/%m/%Y %H:%M") if user.ultimo_login else "Nunca"
            values = [user.nome, user.login, "Autorizado" if user.ativo else "Bloqueado", last_access]
            for column, value in enumerate(values):
                self.table.setItem(row, column, QTableWidgetItem(value))

    def _selected_id(self) -> int | None:
        row = self.table.currentRow()
        users = self.service.list_users()
        return users[row].id if 0 <= row < len(users) else None

    def _selected_user(self):
        row = self.table.currentRow()
        users = self.service.list_users()
        return users[row] if 0 <= row < len(users) else None

    def add_user(self) -> None:
        dialog = NewUserDialog(parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                self.service.create_user(dialog.name.text(), dialog.login.text(), dialog.password.text())
                self.refresh()
            except Exception as error:
                QMessageBox.critical(self, "Erro ao criar usuário", str(error))

    def edit_user(self) -> None:
        user = self._selected_user()
        if user is None:
            return
        dialog = NewUserDialog(user, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                self.service.update_user(user.id, dialog.name.text(), dialog.login.text(), dialog.password.text())
                self.refresh()
            except Exception as error:
                QMessageBox.critical(self, "Erro ao editar usuário", str(error))

    def delete_user(self) -> None:
        user_id = self._selected_id()
        if user_id is None:
            return
        if confirm_action(self, "Excluir usuário", "Excluir o usuário selecionado? Esta ação não pode ser desfeita."):
            try:
                self.service.delete_user(user_id, self.current_user_id)
                self.refresh()
            except Exception as error:
                QMessageBox.warning(self, "Não foi possível excluir", str(error))
