"""Dashboard inicial."""

from PySide6.QtWidgets import QGridLayout, QLabel, QVBoxLayout, QWidget


class DashboardPage(QWidget):
    """Cartões preparados para os indicadores operacionais."""

    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        title = QLabel("Dashboard")
        title.setStyleSheet("font-size: 22pt; font-weight: 600;")
        layout.addWidget(title)
        grid = QGridLayout()
        cards = [("Funcionários", "0"), ("Ativos", "0"), ("Presentes", "0"), ("Ausentes", "0"), ("Horas extras", "—"), ("Última sincronização", "Nunca"), ("Relógio", "Não conectado"), ("Banco de dados", "Online")]
        for index, (label, value) in enumerate(cards):
            card = QLabel(f"{label}\n{value}"); card.setObjectName("card")
            grid.addWidget(card, index // 4, index % 4)
        layout.addLayout(grid)
        layout.addStretch()
