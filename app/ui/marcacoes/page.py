"""Consulta das marcações importadas para o banco de dados local."""

from datetime import datetime, time, timedelta

from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDateEdit,
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


class MarkingsPage(QWidget):
    """Exibe as marcações armazenadas no banco de dados."""

    def __init__(self, service: EmployeeService, column_settings: TableColumnSettings | None = None) -> None:
        super().__init__()
        self.service = service
        layout = QVBoxLayout(self)

        heading = QHBoxLayout()
        heading.setSpacing(4)
        heading.addWidget(QLabel("Marcações"))
        self.start_date = QDateEdit(QDate.currentDate().addMonths(-1))
        self.start_date.setCalendarPopup(True)
        self.start_date.setFixedWidth(140)
        self.start_date.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.end_date = QDateEdit(QDate.currentDate())
        self.end_date.setCalendarPopup(True)
        self.end_date.setFixedWidth(140)
        self.end_date.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        date_filters = QHBoxLayout()
        date_filters.setSpacing(4)
        date_filters.addWidget(QLabel("De"))
        date_filters.addWidget(self.start_date)
        date_filters.addWidget(QLabel("Até"))
        date_filters.addWidget(self.end_date)
        date_filters.addStretch()

        filter_row = QHBoxLayout()
        filter_row.setSpacing(4)
        self.search = QLineEdit()
        self.search.setPlaceholderText("Nome ou matrícula...")
        self.search.setMinimumWidth(180)
        filter_row.addWidget(self.search)
        self.origin_filter = QComboBox()
        self.origin_filter.addItems(["Todas as origens", "RELOGIO", "RWTECH", "AFD", "IMPORTACAO_MANUAL", "MOCK"])
        filter_row.addWidget(self.origin_filter)
        self.type_filter = QComboBox()
        self.type_filter.addItems(["Todas as classificações", "ENTRADA", "SAIDA", "NAO_CLASSIFICADA", "POSSIVEL_DUPLICIDADE"])
        filter_row.addWidget(self.type_filter)
        self.only_inconsistent = QCheckBox("Somente inconsistências")
        filter_row.addWidget(self.only_inconsistent)
        refresh = QPushButton("Atualizar")
        refresh.clicked.connect(self.refresh)
        filter_row.addWidget(refresh)
        sync = QPushButton("Sincronizar com o relógio")
        sync.clicked.connect(self.sync_clock)
        filter_row.addWidget(sync)
        layout.addLayout(heading)
        layout.addLayout(date_filters)
        layout.addLayout(filter_row)

        self.status = QLabel("Exibindo marcações armazenadas localmente")
        layout.addWidget(self.status)
        self.table = QTableWidget(0, 11)
        self.table.setHorizontalHeaderLabels([
            "Data e hora", "Funcionário", "Matrícula", "Código relógio", "NSR", "Origem",
            "Classificação", "Ordem", "Jornada", "Status", "Inconsistência",
        ])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setStretchLastSection(True)
        if column_settings:
            column_settings.apply(self.table, "marcacoes")
        layout.addWidget(self.table)
        self.start_date.dateChanged.connect(self.refresh)
        self.end_date.dateChanged.connect(self.refresh)
        self.search.textChanged.connect(self.refresh)
        self.origin_filter.currentIndexChanged.connect(self.refresh)
        self.type_filter.currentIndexChanged.connect(self.refresh)
        self.only_inconsistent.stateChanged.connect(self.refresh)
        self.table.cellDoubleClicked.connect(self.show_details)
        self._visible_markings = []
        self.refresh()

    def refresh(self) -> None:
        start = datetime.combine(self.start_date.date().toPython(), time.min)
        end_date = self.end_date.date().toPython()
        if start.date() > end_date:
            self.table.setRowCount(0)
            self.status.setText("Período inválido")
            return
        end = datetime.combine(end_date + timedelta(days=1), time.min)
        markings = self.service.list_raw_markings(start, end, self.search.text().strip())
        origin = self.origin_filter.currentText()
        classification = self.type_filter.currentText()
        rows = []
        for marking in markings:
            apuracao = marking.apuracoes[0] if marking.apuracoes else None
            current_type = apuracao.tipo_classificado if apuracao else "NAO_CLASSIFICADA"
            if origin != "Todas as origens" and marking.origem != origin:
                continue
            if classification != "Todas as classificações" and current_type != classification:
                continue
            inconsistent = current_type == "POSSIVEL_DUPLICIDADE"
            if self.only_inconsistent.isChecked() and not inconsistent:
                continue
            rows.append((marking, apuracao, inconsistent))
        self.table.setRowCount(len(rows))
        self._visible_markings = [item[0] for item in rows]
        for row, (marking, apuracao, inconsistent) in enumerate(rows):
            employee = marking.employee
            values = [
                marking.data_hora_marcacao.strftime("%d/%m/%Y %H:%M:%S"),
                employee.nome if employee else "Não identificado",
                employee.matricula if employee else "",
                marking.codigo_funcionario_relogio,
                marking.nsr or "",
                marking.origem,
                apuracao.tipo_classificado if apuracao else "NAO_CLASSIFICADA",
                str(apuracao.ordem_no_periodo) if apuracao and apuracao.ordem_no_periodo else "",
                str(apuracao.jornada_id) if apuracao and apuracao.jornada_id else "",
                "Com inconsistência" if inconsistent else "Normal",
                apuracao.observacao if apuracao and apuracao.observacao else "",
            ]
            for column, value in enumerate(values):
                self.table.setItem(row, column, QTableWidgetItem(str(value or "")))
        self.status.setText(f"{len(rows)} marcação(ões) encontrada(s)")

    def show_details(self, row: int, _column: int) -> None:
        if not 0 <= row < len(self._visible_markings):
            return
        marking = self._visible_markings[row]
        apuracao = marking.apuracoes[0] if marking.apuracoes else None
        employee = marking.employee
        details = (
            f"Funcionário: {employee.nome if employee else 'Não identificado'}\n"
            f"Código: {marking.codigo_funcionario_relogio}\n"
            f"Data/hora original: {marking.data_hora_marcacao:%d/%m/%Y %H:%M:%S}\n"
            f"Origem: {marking.origem}\n"
            f"NSR: {marking.nsr or 'Não informado'}\n"
            f"Hash: {marking.hash_integridade}\n"
            f"Importado em: {marking.importado_em:%d/%m/%Y %H:%M:%S}\n"
            f"Classificação: {apuracao.tipo_classificado if apuracao else 'NAO_CLASSIFICADA'}\n"
            f"Observação: {apuracao.observacao if apuracao and apuracao.observacao else 'Nenhuma'}\n"
            f"Dados brutos: {marking.dados_brutos or 'Não informado'}"
        )
        QMessageBox.information(self, "Detalhes da marcação", details)

    def sync_clock(self) -> None:
        QMessageBox.information(
            self,
            "Sincronização",
            "A conexão com o relógio RWTECH ainda não foi configurada. "
            "As marcações já salvas no banco de dados estão disponíveis nesta tela.",
        )
