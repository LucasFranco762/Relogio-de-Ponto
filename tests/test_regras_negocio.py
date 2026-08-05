"""Testes de alertas e da regra de não sobrescrever marcação bruta."""

from datetime import datetime
from pathlib import Path
import tempfile
import unittest

from app.database.engine import Database
from app.models import Employee, MarcacaoBruta, User
from app.services.ajuste import AjusteService
from app.services.alerta import AlertaService


class RegrasNegocioTests(unittest.TestCase):
    def test_faixas_de_alerta(self):
        service = AlertaService()
        self.assertEqual(service.nivel_para(79, 100).value, "INFORMACAO")
        self.assertEqual(service.nivel_para(80, 100).value, "ATENCAO")
        self.assertEqual(service.nivel_para(100, 100).value, "LIMITE_ATINGIDO")
        self.assertEqual(service.nivel_para(101, 100).value, "LIMITE_EXCEDIDO")

    def test_ajuste_preserva_maracacao_bruta(self):
        with tempfile.TemporaryDirectory() as folder:
            database = Database(f"sqlite:///{Path(folder) / 'teste.db'}")
            database.initialize()
            with database.session() as session:
                employee = Employee(matricula="001", nome="Teste")
                user = User(login="admin", senha_hash="hash", nome="Admin")
                session.add_all([employee, user]); session.flush()
                raw = MarcacaoBruta(
                    funcionario_id=employee.id, codigo_funcionario_relogio="001", data_hora_marcacao=datetime(2026, 8, 5, 8), hash_integridade="a" * 64,
                )
                session.add(raw); session.flush()
                original = raw.data_hora_marcacao
                AjusteService().criar(session, employee.id, None, raw.id, "ALTERACAO_CLASSIFICACAO", "ENTRADA", "SAIDA", "Correção autorizada", user.id)
                self.assertEqual(session.get(MarcacaoBruta, raw.id).data_hora_marcacao, original)
            database.engine.dispose()


if __name__ == "__main__":
    unittest.main()
