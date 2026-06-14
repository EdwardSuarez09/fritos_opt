"""Utilidades compartidas para las pruebas"""
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from core.inventario import Inventario
from core.costos import CalculadorCostos
from core.sensibilidad import AnalizadorSensibilidad
from core.bot_sensibilidad import BotSensibilidad


class BotTestCase(unittest.TestCase):
    """Caso base con bot configurado una sola vez"""

    bot: BotSensibilidad = None
    analizador: AnalizadorSensibilidad = None

    @classmethod
    def setUpClass(cls):
        inventario = Inventario()
        calculador = CalculadorCostos(
            inventario.insumos, inventario.masas, inventario.productos
        )
        cls.analizador = AnalizadorSensibilidad(
            inventario.insumos,
            inventario.masas,
            inventario.productos,
            calculador,
        )
        cls.bot = BotSensibilidad(
            inventario.insumos,
            inventario.productos,
            calculador,
            cls.analizador,
        )

    def responder(self, pregunta: str) -> dict:
        return self.bot.responder(pregunta)

    def texto(self, pregunta: str) -> str:
        return self.responder(pregunta).get("respuesta", "")
