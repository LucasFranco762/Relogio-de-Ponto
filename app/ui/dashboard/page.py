"""Dashboard inicial."""

from PySide6.QtWidgets import QGridLayout, QLabel, QVBoxLayout, QWidget


class DashboardPage(QWidget):
    """Cartões preparados para os indicadores operacionais."""

    def __init__(self, employee_service=None) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        title = QLabel("Dashboard")
        title.setStyleSheet("font-size: 22pt; font-weight: 600;")
        layout.addWidget(title)
        grid = QGridLayout()
        active = len(employee_service.list(active=True)) if employee_service is not None else 0
        total = len(employee_service.list(active=None)) if employee_service is not None else 0
        cards = [("Funcionários", str(total)), ("Ativos", str(active)), ("Presentes", "—"), ("Ausentes", "—"), ("Jornadas em andamento", "—"), ("Horas extras", "—"), ("Última sincronização", "Nunca"), ("Relógio", "NÃO CONFIGURADO"), ("Alertas não lidos", "—"), ("Banco de dados", "Online"), ("Último backup", "Consultar logs")]
        for index, (label, value) in enumerate(cards):
            card = QLabel(f"{label}\n{value}"); card.setObjectName("card")
            grid.addWidget(card, index // 4, index % 4)
        layout.addLayout(grid)
        layout.addStretch()
