"""Pruebas de funciones auxiliares del bot"""
import unittest

from tests.base import ROOT  # noqa: F401 - asegura path
from core.bot_sensibilidad import (
    BotSensibilidad,
    formato_cop,
    normalizar,
    palabras_clave,
    cargar_fuentes,
    TAGS_DINAMICOS,
)


class TestFormatoCOP(unittest.TestCase):
    def test_positivo(self):
        self.assertEqual(formato_cop(8003000), "$8.003.000 COP")

    def test_negativo(self):
        self.assertEqual(formato_cop(-3450), "-$3.450 COP")

    def test_cero(self):
        self.assertEqual(formato_cop(0), "$0 COP")


class TestNormalizar(unittest.TestCase):
    def test_quita_tildes_y_signos(self):
        self.assertEqual(
            normalizar("¿Qué pasa si la harina sube 15%?"),
            "que pasa si la harina sube 15",
        )

    def test_minusculas(self):
        self.assertEqual(normalizar("EMPANADA DE CARNE"), "empanada de carne")


class TestPalabrasClave(unittest.TestCase):
    def test_excluye_vacias(self):
        kw = palabras_clave("que es el precio de la harina")
        self.assertIn("harina", kw)
        self.assertNotIn("que", kw)
        self.assertNotIn("el", kw)


class TestFuentes(unittest.TestCase):
    def test_hay_fuentes_cargadas(self):
        fuentes = cargar_fuentes()
        self.assertGreaterEqual(len(fuentes), 3)
        total = sum(len(m) for m in fuentes.values())
        self.assertGreaterEqual(total, 50)

    def test_tags_dinamicos_son_resolvibles(self):
        self.assertIn("HISTORIAL_VENTAS_MES", TAGS_DINAMICOS)
        self.assertIn("ESCENARIO_PESIMISTA", TAGS_DINAMICOS)


class TestClasificacionPreguntas(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from tests.base import BotTestCase
        BotTestCase.setUpClass()
        cls.bot = BotTestCase.bot

    def test_cambio_precio_detecta_simulacion(self):
        self.assertTrue(self.bot._es_pregunta_cambio_precio("que pasa si la harina sube 15%"))
        self.assertTrue(self.bot._es_pregunta_cambio_precio("que pasa si el aceite sube 10 por ciento"))

    def test_cambio_precio_no_detecta_consulta_simple(self):
        self.assertFalse(self.bot._es_pregunta_cambio_precio("cuanto cuesta el aceite"))
        self.assertFalse(self.bot._es_pregunta_cambio_precio("cuanto vale la harina"))

    def test_costo_producto_vs_insumo(self):
        self.assertTrue(self.bot._es_pregunta_costo("cuanto cuesta la empanada de carne"))
        self.assertFalse(self.bot._es_pregunta_costo("cuanto cuesta el aceite"))

    def test_ventas_mes_no_es_precio_insumo(self):
        clave = normalizar("cuanto vendi en mayo")
        self.assertTrue(self.bot._pregunta_es_de_ventas(clave))


if __name__ == "__main__":
    unittest.main()
