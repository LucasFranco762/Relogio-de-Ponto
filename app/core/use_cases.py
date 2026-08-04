"""Estruturas futuras para cálculo, alertas e relatórios."""

from abc import ABC


class CalculationService(ABC): """Porta para cálculo de carga horária."""
class OvertimeService(ABC): """Porta para cálculo de horas extras."""
class AlertService(ABC): """Porta para alertas de jornada."""
class ReportService(ABC): """Porta para relatórios."""
