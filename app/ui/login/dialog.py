"""Diálogo de login."""

from PySide6.QtWidgets import QDialog, QFormLayout, QLineEdit, QPushButton, QVBoxLayout, QLabel

from app.services.auth import AuthenticationService


class LoginDialog(QDialog):
    """Solicita credenciais antes da abertura do sistema."""

    def __init__(self, auth: AuthenticationService) -> None:
        super().__init__()
        self.auth, self.user = auth, None
        self.setWindowTitle("Acesso ao sistema")
        self.setFixedSize(380, 260)
        layout = QVBoxLayout(self)
        title = QLabel("CONTROLE DE PONTO")
        title.setObjectName("brand")
        layout.addWidget(title)
        form = QFormLayout()
        self.login = QLineEdit(); self.login.setPlaceholderText("Login")
        self.password = QLineEdit(); self.password.setEchoMode(QLineEdit.EchoMode.Password); self.password.setPlaceholderText("Senha")
        form.addRow("Usuário", self.login); form.addRow("Senha", self.password)
        layout.addLayout(form)
        self.error_message = QLabel("")
        self.error_message.setStyleSheet("color: #ff7b72;")
        layout.addWidget(self.error_message)
        button = QPushButton("Entrar")
        button.setStyleSheet("text-align: center;")
        button.clicked.connect(self._authenticate)
        self.password.returnPressed.connect(self._authenticate)
        layout.addWidget(button)

    def _authenticate(self) -> None:
        self.user = self.auth.authenticate(self.login.text(), self.password.text())
        if self.user:
            self.accept()
        else:
            self.error_message.setText("Login ou senha inválidos.")
            self.password.clear()
            self.password.setFocus()
