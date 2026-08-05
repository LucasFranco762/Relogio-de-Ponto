"""Consulta do histórico de carga horária dos funcionários."""

from collections import defaultdict
from datetime import datetime, time, timedelta

from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QDialog,
    QFileDialog,
    QFormLayout,
    QHeaderView,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.services.employees import EmployeeService
from app.utils.table_columns import TableColumnSettings
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def _hours(seconds: int, signed: bool = False) -> str:
    sign = "-" if seconds < 0 else ("+" if signed else "")
    seconds = abs(seconds)
    hours, remainder = divmod(seconds, 3600)
    minutes = remainder // 60
    return f"{sign}{hours:02d}:{minutes:02d}"


class WorkloadDetailDialog(QDialog):
    """Exibe marcações diárias e balanços mensais de um funcionário."""

    def __init__(self, service: EmployeeService, employee_id: int, company_name: str = "", parent: QWidget | None = None, column_settings: TableColumnSettings | None = None) -> None:
        super().__init__(parent)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowSystemMenuHint | Qt.WindowType.WindowMaximizeButtonHint)
        self.service, self.employee_id, self.company_name = service, employee_id, company_name
        self.employee = service.get(employee_id)
        if self.employee is None:
            self.reject()
            return
        self.setWindowTitle(f"Carga Horária — {self.employee.nome}")
        self.resize(900, 620)
        layout = QVBoxLayout(self)
        title = QLabel(f"{self.employee.nome}  •  {self.employee.cargo or 'Cargo não informado'}")
        title.setStyleSheet("font-size: 15pt; font-weight: 600;")
        layout.addWidget(title)

        filters = QFormLayout()
        today = QDate.currentDate()
        first_day = QDate(self.employee.data_inicio.year, self.employee.data_inicio.month, self.employee.data_inicio.day) if self.employee.data_inicio else today.addYears(-10)
        self.start_date = QDateEdit(first_day); self.start_date.setCalendarPopup(True); self.start_date.setMaximumDate(today)
        self.end_date = QDateEdit(today); self.end_date.setCalendarPopup(True); self.end_date.setMaximumDate(today)
        apply_button = QPushButton("Atualizar histórico"); apply_button.clicked.connect(self.refresh)
        report_button = QPushButton("Gerar Relatório"); report_button.clicked.connect(self.generate_report)
        apply_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        report_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        action_buttons = QHBoxLayout()
        action_buttons.addWidget(apply_button)
        action_buttons.addSpacing(80)
        action_buttons.addWidget(report_button)
        filters.addRow("Data Início", self.start_date); filters.addRow("Data Fim", self.end_date); filters.addRow("", action_buttons)
        layout.addLayout(filters)

        layout.addWidget(QLabel("Histórico diário"))
        self.daily_table = QTableWidget(0, 4)
        self.daily_table.setHorizontalHeaderLabels(["Data", "Horários registrados", "Horas trabalhadas", "Saldo do dia"])
        daily_header = self.daily_table.horizontalHeader()
        daily_header.setStretchLastSection(False)
        daily_header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        daily_header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        daily_header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        daily_header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self.daily_table.setColumnWidth(0, 105)
        self.daily_table.setColumnWidth(2, 155)
        self.daily_table.setColumnWidth(3, 125)
        self.daily_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.daily_table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.daily_table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        if column_settings:
            column_settings.apply(self.daily_table, "carga_detalhe_diario")
        layout.addWidget(self.daily_table)

        layout.addWidget(QLabel("Balanço mensal"))
        self.monthly_table = QTableWidget(0, 4)
        self.monthly_table.setHorizontalHeaderLabels(["Mês", "Horas positivas", "Horas negativas", "Saldo mensal"])
        monthly_header = self.monthly_table.horizontalHeader()
        monthly_header.setStretchLastSection(False)
        monthly_header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        monthly_header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        monthly_header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        monthly_header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self.monthly_table.setColumnWidth(1, 150)
        self.monthly_table.setColumnWidth(2, 150)
        self.monthly_table.setColumnWidth(3, 135)
        self.monthly_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.monthly_table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.monthly_table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        if column_settings:
            column_settings.apply(self.monthly_table, "carga_detalhe_mensal")
        layout.addWidget(self.monthly_table)
        self.refresh()

    def refresh(self) -> None:
        start = self.start_date.date().toPython()
        end = self.end_date.date().toPython()
        if start > end:
            self.daily_table.setRowCount(0); self.monthly_table.setRowCount(0)
            return
        daily_rows, monthly = self._history_data(start, end)

        self.daily_table.setRowCount(len(daily_rows))
        for row, (day, times, worked, balance) in enumerate(daily_rows):
            values = [day.strftime("%d/%m/%Y"), times, _hours(worked), _hours(balance, signed=True)]
            for column, value in enumerate(values):
                self.daily_table.setItem(row, column, QTableWidgetItem(value))

        self.monthly_table.setRowCount(len(monthly))
        for row, (month, values) in enumerate(sorted(monthly.items())):
            positive, negative, balance = values
            rendered = [month, _hours(positive), _hours(negative), _hours(balance, signed=True)]
            for column, value in enumerate(rendered):
                self.monthly_table.setItem(row, column, QTableWidgetItem(value))

    def _history_data(self, start, end):
        punches = self.service.raw_punch_history(self.employee_id, datetime.combine(start, time.min), datetime.combine(end + timedelta(days=1), time.min))
        by_day = defaultdict(list)
        for punch in punches:
            by_day[punch.data_hora_marcacao.date()].append(punch.data_hora_marcacao)

        expected_seconds = int(round((self.employee.carga_horaria_diaria or self.employee.carga_horaria_valor or 8) * 3600))
        daily_rows = []
        monthly = defaultdict(lambda: [0, 0, 0])
        for day in sorted(by_day):
            timestamps = by_day[day]
            worked = sum((timestamps[index + 1] - timestamps[index]).total_seconds() for index in range(0, len(timestamps) - 1, 2))
            worked = int(worked)
            balance = worked - expected_seconds
            month = day.strftime("%Y-%m")
            monthly[month][0] += max(balance, 0)
            monthly[month][1] += abs(min(balance, 0))
            monthly[month][2] += balance
            daily_rows.append((day, ", ".join(item.strftime("%H:%M") for item in timestamps), worked, balance))

        return daily_rows, monthly

    def generate_report(self) -> None:
        start = self.start_date.date().toPython()
        end = self.end_date.date().toPython()
        if start > end:
            QMessageBox.warning(self, "Período inválido", "A Data Início deve ser anterior ou igual à Data Fim.")
            return
        filename = f"relatorio_carga_horaria_{self.employee.nome.replace(' ', '_')}"
        path, _ = QFileDialog.getSaveFileName(self, "Salvar relatório PDF", filename + ".pdf", "Arquivo PDF (*.pdf)")
        if not path:
            return
        if not path.lower().endswith(".pdf"):
            path += ".pdf"
        try:
            daily_rows, monthly = self._history_data(start, end)
            self._write_pdf(path, start, end, daily_rows, monthly)
            QMessageBox.information(self, "Relatório", "Relatório PDF gerado com sucesso.")
        except Exception as error:
            QMessageBox.critical(self, "Erro ao gerar relatório", str(error))

    def _write_pdf(self, path, start, end, daily_rows, monthly) -> None:
        document = SimpleDocTemplate(path, pagesize=A4, rightMargin=12 * mm, leftMargin=12 * mm, topMargin=12 * mm, bottomMargin=12 * mm)
        styles = getSampleStyleSheet()
        center = ParagraphStyle("center", parent=styles["Normal"], alignment=TA_CENTER, fontSize=11, leading=14)
        title = ParagraphStyle("title", parent=center, fontSize=16, leading=20, spaceAfter=4)
        subtitle = ParagraphStyle("subtitle", parent=center, fontSize=12, leading=16, spaceAfter=12)
        story = [
            Paragraph(self.company_name or "Empresa não informada", title),
            Paragraph("Relatório de Carga Horária", title),
            Paragraph(self.employee.nome, subtitle),
            Paragraph(f"Período: {start.strftime('%d/%m/%Y')} a {end.strftime('%d/%m/%Y')}", center),
            Spacer(1, 8 * mm),
        ]
        daily_data = [["Data", "Horários registrados", "Horas trabalhadas", "Saldo do dia"]]
        daily_data.extend([[day.strftime("%d/%m/%Y"), times, _hours(worked), _hours(balance, signed=True)] for day, times, worked, balance in daily_rows])
        story.append(Paragraph("Histórico diário", styles["Heading3"]))
        story.append(self._pdf_table(daily_data, [28 * mm, 72 * mm, 35 * mm, 35 * mm]))
        story.append(Spacer(1, 7 * mm))
        monthly_data = [["Mês", "Horas positivas", "Horas negativas", "Saldo mensal"]]
        monthly_data.extend([[month, _hours(values[0]), _hours(values[1]), _hours(values[2], signed=True)] for month, values in sorted(monthly.items())])
        story.append(Paragraph("Balanço mensal", styles["Heading3"]))
        story.append(self._pdf_table(monthly_data, [42 * mm, 42 * mm, 42 * mm, 42 * mm]))
        document.build(story)

    @staticmethod
    def _pdf_table(data, widths):
        table = Table(data, colWidths=widths, repeatRows=1)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#223149")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#b9c5d2")),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#eef3f7")]),
            ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ]))
        return table


class WorkloadPage(QWidget):
    """Lista funcionários e abre o histórico individual de carga horária."""

    def __init__(self, service: EmployeeService, company_name: str = "") -> None:
        super().__init__(); self.service, self.company_name = service, company_name
        layout = QVBoxLayout(self)
        heading = QHBoxLayout(); heading.addWidget(QLabel("Carga Horária"))
        self.search = QLineEdit(); self.search.setPlaceholderText("Pesquisar por nome ou matrícula..."); self.search.textChanged.connect(self.refresh); heading.addWidget(self.search)
        heading.addWidget(QLabel("Exibir"))
        self.status_filter = QComboBox(); self.status_filter.addItem("Ativos", True); self.status_filter.addItem("Inativos", False); self.status_filter.addItem("Todos", None); self.status_filter.currentIndexChanged.connect(self.refresh); heading.addWidget(self.status_filter)
        layout.addLayout(heading)
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Matrícula", "Nome", "Cargo", "Carga Horária"])
        header = self.table.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(3, 155)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table)
        self.refresh()

    def refresh(self) -> None:
        employees = self.service.list(self.search.text(), active=self.status_filter.currentData())
        self.table.setRowCount(len(employees))
        for row, employee in enumerate(employees):
            values = [employee.matricula, employee.nome, employee.cargo or "—", ""]
            for column, value in enumerate(values[:3]):
                self.table.setItem(row, column, QTableWidgetItem(value))
            button = QPushButton("Carga Horária")
            button.setFixedSize(140, 36)
            button.clicked.connect(lambda checked=False, employee_id=employee.id: self.open_detail(employee_id))
            self.table.setCellWidget(row, 3, button)
            self.table.setRowHeight(row, 48)

    def open_detail(self, employee_id: int) -> None:
        dialog = WorkloadDetailDialog(self.service, employee_id, self.company_name, self, getattr(self, "column_settings", None))
        if dialog.exec() == QDialog.DialogCode.Rejected and dialog.employee is None:
            QMessageBox.warning(self, "Funcionário", "Não foi possível carregar os dados do funcionário.")
