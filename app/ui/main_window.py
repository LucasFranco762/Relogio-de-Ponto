"""Janela principal e navegação."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QListWidget, QListWidgetItem, QMainWindow, QStackedWidget, QStatusBar, QVBoxLayout, QWidget

from app.services.employees import EmployeeService
from app.services.auth import AuthenticationService
from app.services.settings import SettingsService
from app.ui.dashboard.page import DashboardPage
from app.ui.carga_horaria.page import WorkloadPage
from app.ui.funcionarios.page import EmployeesPage
from app.ui.usuarios.page import UsersPage


class MainWindow(QMainWindow):
    """Shell da aplicação: menu, conteúdo e status."""

    def __init__(self, employee_service: EmployeeService, settings_service: SettingsService, auth_service: AuthenticationService, current_user_id: int, user_name: str) -> None:
        super().__init__(); self.setWindowTitle("Controle de Ponto | RWTECH"); self.resize(1280, 760)
        root = QWidget(); self.setCentralWidget(root); main = QHBoxLayout(root); main.setContentsMargins(0, 0, 0, 0)
        side = QFrame(); side.setObjectName("sidebar"); side.setFixedWidth(220); side_layout = QVBoxLayout(side)
        brand = QLabel("PONTO\nCORPORATIVO"); brand.setObjectName("brand"); side_layout.addWidget(brand)
        self.menu = QListWidget(); self.menu.setSpacing(4); self.menu.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff); self.menu.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        for label in ["Dashboard", "Funcionários", "Marcações", "Carga Horária", "Usuários", "Configurações", "Logs", "Sobre"]: QListWidgetItem(label, self.menu)
        self.menu.currentRowChanged.connect(self._change_page); self.menu.setCurrentRow(0); side_layout.addWidget(self.menu); side_layout.addStretch(); side_layout.addWidget(QLabel(f"Usuário: {user_name}")); main.addWidget(side)
        content = QVBoxLayout(); top = QLabel("  Sistema de Controle de Ponto"); top.setObjectName("topbar"); top.setStyleSheet("font-size: 15pt; padding: 16px;"); content.addWidget(top)
        self.pages = QStackedWidget(); self.pages.addWidget(DashboardPage()); self.pages.addWidget(EmployeesPage(employee_service))
        self.pages.addWidget(self._placeholder("Marcações")); self.pages.addWidget(WorkloadPage(employee_service, settings_service.get().empresa)); self.pages.addWidget(UsersPage(auth_service, current_user_id))
        from app.ui.configuracoes.page import SettingsPage
        self.pages.addWidget(SettingsPage(settings_service))
        for text in ["Logs", "Sobre"]: self.pages.addWidget(self._placeholder(text))
        content.addWidget(self.pages); main.addLayout(content)
        status = QStatusBar(); status.showMessage("Sistema pronto • Banco de dados online"); self.setStatusBar(status)

    def _change_page(self, row: int) -> None:
        if hasattr(self, "pages"):
            self.pages.setCurrentIndex(row)

    def _placeholder(self, title: str) -> QWidget:
        widget = QWidget(); layout = QVBoxLayout(widget); label = QLabel(f"{title}\n\nMódulo preparado para a próxima etapa."); label.setAlignment(Qt.AlignmentFlag.AlignCenter); label.setStyleSheet("font-size: 18pt; color: #9fb0c7;"); layout.addWidget(label); return widget
