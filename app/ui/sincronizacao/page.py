"""Tela operacional da sincronização, sem presumir protocolo de rede."""

from pathlib import Path

from PySide6.QtWidgets import QFileDialog, QFormLayout, QLabel, QMessageBox, QPushButton, QVBoxLayout, QWidget

from app.database.engine import Database
from app.integrations.rwtech.mock_gateway import MockRwtechGateway
from app.services.importacao import AfdImportService
from app.services.sincronizacao import SincronizacaoService


class SynchronizationPage(QWidget):
    """Expõe o estado do módulo e o gateway mock de desenvolvimento."""

    def __init__(self, database: Database) -> None:
        super().__init__()
        self.database = database
        self.sync_service = SincronizacaoService(database, MockRwtechGateway())
        self.afd_service = AfdImportService()
        layout = QVBoxLayout(self)
        title = QLabel("Sincronização")
        title.setStyleSheet("font-size: 22pt; font-weight: 600;")
        layout.addWidget(title)
        form = QFormLayout()
        form.addRow("Modelo do relógio", QLabel("RWTECH PointLine BIOPROX-C (960)"))
        self.status = QLabel("NÃO CONFIGURADO")
        form.addRow("Status", self.status)
        self.last_result = QLabel("Nenhuma sincronização realizada")
        form.addRow("Última operação", self.last_result)
        layout.addLayout(form)
        test = QPushButton("Testar conexão")
        test.clicked.connect(self.test_connection)
        sync = QPushButton("Sincronizar agora (Mock)")
        sync.clicked.connect(self.sync_now)
        afd = QPushButton("Importar arquivo AFD")
        afd.clicked.connect(self.import_afd)
        logs = QPushButton("Ver logs")
        logs.clicked.connect(lambda: QMessageBox.information(self, "Logs", "Consulte o arquivo app/logs/app.log."))
        for button in (test, sync, afd, logs):
            button.setFixedWidth(280)
            layout.addWidget(button)
        layout.addStretch()

    def test_connection(self) -> None:
        QMessageBox.information(self, "Relógio", "A comunicação real RWTECH ainda não está configurada. Nenhuma conexão de rede foi tentada.")

    def sync_now(self) -> None:
        result = self.sync_service.sincronizar()
        self.last_result.setText(f"Encontrados: {result.encontrados} | Novos: {result.novos} | Duplicados: {result.duplicados} | Falhas: {result.falhas}")
        QMessageBox.information(self, "Sincronização", self.last_result.text())

    def import_afd(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Selecionar arquivo AFD", "", "Arquivos de texto (*.txt *.afd);;Todos os arquivos (*.*)")
        if not path:
            return
        result = self.afd_service.importar(Path(path))
        QMessageBox.information(self, "Importação AFD", f"Linhas lidas: {result.linhas_lidas}\nRegistros prontos: {len(result.registros)}\nAvisos: {len(result.erros)}")
