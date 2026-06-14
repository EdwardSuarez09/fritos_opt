"""Pruebas del optimizador de produccion (Programacion Lineal)"""
import unittest

from tests.base import BotTestCase
from core.optimizador import Optimizador, DIAS_SEMANA


class TestOptimizador(BotTestCase):
    """Verifica factibilidad y restricciones del modelo de PuLP"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.optimizador = Optimizador(cls.bot.productos, cls.bot.calculador)

    def test_caso_factible_es_optimo(self):
        demanda = {("empanada_carne", "Lunes"): 5}
        fondos = {dia: 1_000_000 for dia in DIAS_SEMANA}
        resultado = self.optimizador.optimizar(demanda, fondos)
        self.assertEqual(resultado["estado"], "Optimal")

    def test_respeta_demanda_minima(self):
        demanda = {("empanada_carne", "Lunes"): 5}
        fondos = {dia: 1_000_000 for dia in DIAS_SEMANA}
        resultado = self.optimizador.optimizar(demanda, fondos)
        produccion = resultado["produccion"]["empanada_carne"]["Lunes"]
        self.assertGreaterEqual(produccion, 5)

    def test_presupuesto_insuficiente_es_infactible(self):
        demanda = {("empanada_carne", "Lunes"): 100}
        fondos = {dia: 1 for dia in DIAS_SEMANA}
        resultado = self.optimizador.optimizar(demanda, fondos)
        self.assertEqual(resultado["estado"], "Infeasible")

    def test_ganancia_no_negativa_en_optimo(self):
        demanda = {("empanada_carne", "Lunes"): 5}
        fondos = {dia: 1_000_000 for dia in DIAS_SEMANA}
        resultado = self.optimizador.optimizar(demanda, fondos)
        self.assertGreaterEqual(resultado["ganancia_total"], 0)


if __name__ == "__main__":
    unittest.main()
