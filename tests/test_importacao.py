"""Testes de idempotência da importação de marcações brutas."""

from datetime import datetime
from pathlib import Path
import tempfile
import unittest

from app.database.engine import Database
from app.integrations.rwtech.modelos import RegistroRelogio
from app.models import MarcacaoBruta
from app.repositories.marcacoes_brutas import MarcacaoBrutaRepository


class ImportacaoTests(unittest.TestCase):
    def test_nsr_impede_duplicidade(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "teste.db"
            database = Database(f"sqlite:///{path}")
            database.initialize()
            registro = RegistroRelogio("1", "001", datetime(2026, 8, 5, 8, 0), "DIGITAL", "linha-1")
            with database.session() as session:
                repository = MarcacaoBrutaRepository()
                first = repository.importar(session, [registro])
                second = repository.importar(session, [registro])
                self.assertEqual(first[:2], (1, 0))
                self.assertEqual(second[:2], (0, 1))
                self.assertEqual(session.query(MarcacaoBruta).count(), 1)
            database.engine.dispose()


if __name__ == "__main__":
    unittest.main()
