"""Testes unitários das regras básicas de apuração."""

from datetime import datetime, time
from types import SimpleNamespace
import unittest

from app.core.enums import StatusJornada, TipoMarcacao
from app.services.apuracao import MotorApuracaoService


def markers(*hours: str):
    return [SimpleNamespace(data_hora_marcacao=datetime.fromisoformat(f"2026-08-05T{hour}")) for hour in hours]


class MotorApuracaoTests(unittest.TestCase):
    def setUp(self):
        self.motor = MotorApuracaoService()

    def test_jornada_completa(self):
        result = self.motor.calcular(markers("08:00:00", "12:00:00", "13:00:00", "17:00:00"), 480)
        self.assertEqual(result.total_trabalhado_minutos, 480)
        self.assertEqual(result.total_extra_minutos, 0)
        self.assertEqual(result.status, StatusJornada.CONCLUIDA)

    def test_hora_extra(self):
        result = self.motor.calcular(markers("08:00:00", "12:00:00", "13:00:00", "18:30:00"), 480)
        self.assertEqual(result.total_trabalhado_minutos, 570)
        self.assertEqual(result.total_extra_minutos, 90)

    def test_jornada_aberta(self):
        result = self.motor.calcular(markers("08:00:00", "12:00:00", "13:00:00"), 480, periodo_aberto=True)
        self.assertEqual(result.status, StatusJornada.EM_ANDAMENTO)
        self.assertEqual(result.total_trabalhado_minutos, 240)

    def test_seis_marcacoes_formam_tres_intervalos(self):
        result = self.motor.calcular(markers("08:00:00", "10:00:00", "10:15:00", "12:00:00", "13:00:00", "17:00:00"), 480)
        self.assertEqual([item.tipo for item in result.classificacoes], [TipoMarcacao.ENTRADA, TipoMarcacao.SAIDA] * 3)
        self.assertEqual(result.total_trabalhado_minutos, 465)

    def test_ordena_marcacoes_fora_de_ordem(self):
        result = self.motor.calcular(markers("17:00:00", "08:00:00", "13:00:00", "12:00:00"), 480)
        self.assertEqual(result.total_trabalhado_minutos, 480)

    def test_duplicidade_exata_e_possivel_duplicidade(self):
        result = self.motor.calcular(markers("08:00:00", "08:00:05", "12:00:00", "13:00:00", "17:00:00"), 480)
        self.assertEqual(result.classificacoes[1].tipo, TipoMarcacao.POSSIVEL_DUPLICIDADE)
        self.assertEqual(result.status, StatusJornada.COM_INCONSISTENCIA)

    def test_horario_de_corte(self):
        timestamp = datetime.fromisoformat("2026-08-06T03:30:00")
        self.assertEqual(self.motor.data_referencia(timestamp, time(4, 0)), datetime(2026, 8, 5).date())


if __name__ == "__main__":
    unittest.main()
