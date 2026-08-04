"""Tela de configurações da jornada."""

from PySide6.QtCore import QTime, QSize
from PySide6.QtWidgets import (
    QAbstractSpinBox,
    QApplication,
    QButtonGroup,
    QComboBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QSpinBox,
    QTabWidget,
    QTimeEdit,
    QVBoxLayout,
    QWidget,
)

from app.services.settings import SettingsService
from app.utils.theme import LAYOUT_THEMES


class _HorizontalArrowsMixin:
    """Adiciona setas de decremento/incremento com repetição ao segurar."""

    def _setup_horizontal_arrows(self) -> None:
        self.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.lineEdit().setTextMargins(0, 0, 48, 0)
        self._decrease_button = self._create_arrow_button("▼", "Diminuir em 1")
        self._increase_button = self._create_arrow_button("▲", "Aumentar em 1")
        self._decrease_button.clicked.connect(lambda: self.stepBy(-1))
        self._increase_button.clicked.connect(lambda: self.stepBy(1))

    def _create_arrow_button(self, text: str, tooltip: str) -> QPushButton:
        button = QPushButton(text, self)
        button.setToolTip(tooltip)
        button.setAccessibleName(tooltip)
        button.setAutoRepeat(True)
        button.setAutoRepeatDelay(350)
        button.setAutoRepeatInterval(60)
        button.setFixedSize(QSize(24, 24))
        button.setStyleSheet(
            "QPushButton { padding: 0; margin: 0; border: 0; border-radius: 3px; "
            "background: #223149; color: #e6edf7; }"
            "QPushButton:hover { background: #1769aa; }"
            "QPushButton:pressed { background: #0f4f80; }"
        )
        return button

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        button_y = max(0, (self.height() - self._decrease_button.height()) // 2)
        right = self.width() - 2
        self._increase_button.move(right - self._increase_button.width(), button_y)
        self._decrease_button.move(
            right - self._increase_button.width() - self._decrease_button.width(),
            button_y,
        )


class SettingsTimeEdit(_HorizontalArrowsMixin, QTimeEdit):
    """Campo de horário com setas horizontais de um minuto."""

    def __init__(self) -> None:
        super().__init__()
        self._setup_horizontal_arrows()

    def stepBy(self, steps: int) -> None:
        self.setTime(self.time().addSecs(steps * 60))


class SettingsSpinBox(_HorizontalArrowsMixin, QSpinBox):
    """Campo numérico com setas horizontais de uma unidade."""

    def __init__(self) -> None:
        super().__init__()
        self._setup_horizontal_arrows()


class SettingsPage(QWidget):
    """Edita a configuração da empresa e da jornada padrão."""

    def __init__(self, service: SettingsService) -> None:
        super().__init__(); self.service = service
        layout = QVBoxLayout(self); title = QLabel("Configurações"); title.setStyleSheet("font-size: 22pt; font-weight: 600;"); layout.addWidget(title)
        self.tabs = QTabWidget(); general_tab = QWidget(); general_layout = QVBoxLayout(general_tab); self.tabs.addTab(general_tab, "Geral")
        self.tabs.addTab(self._build_layout_tab(), "Layout"); layout.addWidget(self.tabs)
        form = QFormLayout(); self.company = QLineEdit(); self.start = SettingsTimeEdit(); self.end = SettingsTimeEdit(); self.limit = SettingsSpinBox(); self.limit.setRange(0, 24); self.mode = QComboBox(); self.mode.addItems(["Mensal", "Acumulado"])
        for field in (self.company, self.start, self.end, self.limit, self.mode):
            field.setFixedWidth(280); field.setEnabled(True)
        self.company.setReadOnly(False); self.start.setReadOnly(False); self.end.setReadOnly(False); self.limit.setReadOnly(False)
        form.addRow("Empresa", self.company); form.addRow("Início do expediente", self.start); form.addRow("Fim do expediente", self.end); form.addRow("Limite de horas extras", self.limit); form.addRow("Modo de controle", self.mode); general_layout.addLayout(form)
        save = QPushButton("Salvar configurações"); save.setFixedWidth(280); save.clicked.connect(self.save); general_layout.addWidget(save); general_layout.addStretch(); self.load()

    def _build_layout_tab(self) -> QWidget:
        tab = QWidget(); tab_layout = QVBoxLayout(tab)
        heading = QLabel("Escolha o estilo visual do sistema")
        heading.setStyleSheet("font-size: 13pt; font-weight: 600;")
        tab_layout.addWidget(heading)
        description = QLabel("A alteração é aplicada imediatamente em todas as telas.")
        description.setStyleSheet("color: #9fb0c7; margin-bottom: 8px;")
        tab_layout.addWidget(description)

        options = QButtonGroup(tab)
        for index, (name, details) in enumerate((
            ("Layout 01 — Azul Noturno", "Tema atual, com contraste alto e visual corporativo."),
            ("Layout 02 — Brisa Esmeralda", "Interface clara com azul petróleo e detalhes verde-água."),
            ("Layout 03 — Aurora Violeta", "Tema escuro elegante com acentos violeta e lavanda."),
        )):
            option = QRadioButton(f"{name}\n{details}")
            option.setObjectName("layoutOption")
            option.setFixedWidth(520)
            options.addButton(option, index)
            tab_layout.addWidget(option)
            if index == 0:
                option.setChecked(True)
        options.idClicked.connect(self._apply_layout)
        self.layout_options = options
        tab_layout.addStretch()
        return tab

    def _apply_layout(self, index: int) -> None:
        application = QApplication.instance()
        if application is not None and 0 <= index < len(LAYOUT_THEMES):
            application.setStyleSheet(LAYOUT_THEMES[index])

    def load(self) -> None:
        item = self.service.get(); self.company.setText(item.empresa); self.start.setTime(QTime(item.horario_inicio.hour, item.horario_inicio.minute)); self.end.setTime(QTime(item.horario_fim.hour, item.horario_fim.minute)); self.limit.setValue(item.limite_horas_extras); self.mode.setCurrentText(item.modo_controle_horas_extras)

    def save(self) -> None:
        self.service.save(self.company.text(), self.start.time().toPython(), self.end.time().toPython(), self.mode.currentText(), self.limit.value()); QMessageBox.information(self, "Configurações", "Configurações salvas com sucesso.")
