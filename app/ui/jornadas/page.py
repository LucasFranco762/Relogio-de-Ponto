"""Consulta das jornadas diárias calculadas."""

from datetime import date

from PySide6.QtCore import QDate
from PySide6.QtWidgets import QDateEdit, QHBoxLayout, QLabel, QMessageBox, QPushButton, QSizePolicy, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget

from app.database.engine import Database
from app.repositories.jornadas import JornadaRepository
from app.services.jornada import JornadaService


def _duration(minutes: int) -> str:
    sign = "-" if minutes < 0 else ""
    hours, remainder = divmod(abs(minutes), 60)
    return f"{sign}{hours:02d}:{remainder:02d}"


class JourneysPage(QWidget):
    """Exibe jornadas por funcionário e data de referência."""

    def __init__(self, database: Database) -> None:
        super().__init__()
        self.database = database
        self.repository = JornadaRepository()
        self.journey_service = JornadaService(database)
        layout = QVBoxLayout(self)
        heading = QHBoxLayout()
        heading.setSpacing(4)
        heading.addWidget(QLabel("Jornadas"))
        self.start_date = QDateEdit(QDate.currentDate().addMonths(-1)); self.start_date.setCalendarPopup(True); self.start_date.setFixedWidth(140); self.start_date.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.end_date = QDateEdit(QDate.currentDate()); self.end_date.setCalendarPopup(True); self.end_date.setFixedWidth(140); self.end_date.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        date_filters = QHBoxLayout(); date_filters.setSpacing(4)
        date_filters.addWidget(QLabel("De")); date_filters.addWidget(self.start_date)
        date_filters.addWidget(QLabel("Até")); date_filters.addWidget(self.end_date); date_filters.addStretch()
        actions = QHBoxLayout(); actions.setSpacing(4)
        refresh = QPushButton("Atualizar"); refresh.clicked.connect(self.refresh); actions.addWidget(refresh)
        recalculate = QPushButton("Recalcular período"); recalculate.clicked.connect(self.recalculate); actions.addWidget(recalculate); actions.addStretch()
        layout.addLayout(heading)
        layout.addLayout(date_filters)
        layout.addLayout(actions)
        self.status = QLabel()
        layout.addWidget(self.status)
        self.table = QTableWidget(0, 10)
        self.table.setHorizontalHeaderLabels(["Data", "Funcionário", "Primeira entrada", "Última saída", "Marcações", "Carga prevista", "Trabalhado", "Hora extra", "Saldo", "Status"])
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)
        self.start_date.dateChanged.connect(self.refresh); self.end_date.dateChanged.connect(self.refresh)
        self.refresh()

    def refresh(self) -> None:
        start = self.start_date.date().toPython(); end = self.end_date.date().toPython()
        if start > end:
            self.table.setRowCount(0); self.status.setText("Período inválido"); return
        with self.database.session() as session:
            journeys = self.repository.listar(session, start, end)
            self.table.setRowCount(len(journeys))
            for row, journey in enumerate(journeys):
                times = [item.marcacao_bruta.data_hora_marcacao for item in journey.apuracoes if item.marcacao_bruta]
                values = [
                    journey.data_referencia.strftime("%d/%m/%Y"), journey.employee.nome,
                    min(times).strftime("%H:%M") if times else "", max(times).strftime("%H:%M") if times else "",
                    str(len(times)), _duration(journey.carga_prevista_minutos), _duration(journey.total_trabalhado_minutos),
                    _duration(journey.total_extra_minutos), _duration(journey.saldo_minutos), journey.status,
                ]
                for column, value in enumerate(values): self.table.setItem(row, column, QTableWidgetItem(value))
        self.status.setText(f"{len(journeys)} jornada(s) encontrada(s)")

    def recalculate(self) -> None:
        start = self.start_date.date().toPython(); end = self.end_date.date().toPython()
        if start > end:
            QMessageBox.warning(self, "Período inválido", "A data inicial deve ser anterior ou igual à data final.")
            return
        count = self.journey_service.recalcular_periodo(start, end)
        self.refresh()
        QMessageBox.information(self, "Apuração", f"{count} jornada(s) recalculada(s).")
