"""Composição da aplicação; mantém o main deliberadamente pequeno."""

import logging
from pathlib import Path
import sys

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from app.core.config import Settings
from app.core.security import PasswordHasher
from app.database.engine import Database
from app.repositories.employees import EmployeeRepository
from app.services.auth import AuthenticationService
from app.services.employees import EmployeeService
from app.services.settings import SettingsService
from app.ui.login.dialog import LoginDialog
from app.ui.main_window import MainWindow
from app.utils.logging_config import configure_logging
from app.utils.cursor import ClickCursorFilter
from app.utils.resources import resource_path
from app.utils.theme import THEME


class Application:
    """Orquestra inicialização, autenticação e janela principal."""

    def __init__(self, qt_app: QApplication, database: Database, auth: AuthenticationService, employees: EmployeeService, logger: logging.Logger) -> None:
        self.qt_app, self.database, self.auth, self.employees, self.logger = qt_app, database, auth, employees, logger

    def run(self) -> int:
        self.logger.info("Inicialização do sistema")
        self.auth.ensure_initial_user()
        login = LoginDialog(self.auth)
        if login.exec() != LoginDialog.DialogCode.Accepted or login.user is None:
            self.logger.info("Aplicação fechada na tela de login")
            return 0
        self.logger.info("Login realizado: %s", login.user.login)
        window = MainWindow(self.employees, SettingsService(self.database), self.auth, login.user.id, login.user.nome); window.showMaximized()
        result = self.qt_app.exec(); self.logger.info("Fechamento do sistema"); return result


def create_application(root: Path | None = None) -> Application:
    """Cria todas as dependências da aplicação."""
    project_root = root or (
        Path(sys.executable).resolve().parent
        if getattr(sys, "frozen", False)
        else Path(__file__).resolve().parent.parent
    )
    settings = Settings.from_root(project_root)
    logger = configure_logging(project_root / "app" / "logs")
    database = Database(settings.database_url); database.initialize()
    auth = AuthenticationService(database, PasswordHasher())
    employees = EmployeeService(database, EmployeeRepository())
    qt_app = QApplication([]); qt_app.setApplicationName(settings.app_name); qt_app.setWindowIcon(QIcon(str(resource_path("Icone.png")))); qt_app.setStyleSheet(THEME)
    qt_app.installEventFilter(ClickCursorFilter(qt_app))
    return Application(qt_app, database, auth, employees, logger)
