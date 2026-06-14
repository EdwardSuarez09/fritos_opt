"""Pruebas de enrutamiento: cada pregunta va al tipo correcto de respuesta"""
import unittest

from tests.base import BotTestCase


class TestBotRouting(BotTestCase):
    """Verifica que responder() clasifique bien cada familia de preguntas"""

    def _assert_routing(
        self,
        pregunta: str,
        tipo_esperado: str,
        debe_contener: list = None,
        no_debe_contener: list = None,
    ):
        resultado = self.responder(pregunta)
        self.assertNotIn("sin_respuesta", resultado, msg=f"Sin respuesta para: {pregunta}")
        self.assertFalse(resultado.get("sin_respuesta"), msg=f"Sin respuesta para: {pregunta}")
        self.assertEqual(
            resultado.get("tipo"),
            tipo_esperado,
            msg=f"'{pregunta}' -> tipo {resultado.get('tipo')}, texto: {resultado.get('respuesta','')[:120]}",
        )
        texto = resultado.get("respuesta", "").lower()
        for frag in debe_contener or []:
            self.assertIn(
                frag.lower(),
                texto,
                msg=f"'{pregunta}' deberia contener '{frag}'",
            )
        for frag in no_debe_contener or []:
            self.assertNotIn(
                frag.lower(),
                texto,
                msg=f"'{pregunta}' NO deberia mezclar '{frag}'",
            )

    # --- Historial / ventas ---

    def test_ventas_mes(self):
        self._assert_routing(
            "cuanto vendi en mayo",
            "historial",
            ["3,450", "8.003.000", "cop"],
            ["precio actual", "carne molida", "analisis de"],
        )

    def test_unidades_mes(self):
        self._assert_routing(
            "cuantas unidades vendi en mayo",
            "historial",
            ["3,450", "unidades"],
            ["empanada de carne: costo"],
        )

    def test_producto_top(self):
        self._assert_routing(
            "cual producto vendio mas",
            "historial",
            ["empanada", "710"],
            ["precio actual"],
        )

    def test_ganancia_mes(self):
        self._assert_routing(
            "gane o perdi en mayo",
            "historial",
            ["ganancia", "cop"],
            ["analisis de harina"],
        )

    def test_resumen_mes(self):
        self._assert_routing(
            "resumen del mes",
            "historial",
            ["resumen", "mayo", "ventas", "gasto"],
            ["no entendi"],
        )

    def test_ventas_producto_especifico(self):
        self._assert_routing(
            "cuantas empanadas de queso vendi",
            "historial",
            ["empanada de queso", "710", "cop"],
            ["harina", "precio actual $3"],
        )

    # --- Costos e insumos (sin mezclar) ---

    def test_precio_insumo_aceite(self):
        self._assert_routing(
            "cuanto cuesta el aceite",
            "historial",
            ["aceite", "precio actual", "cop"],
            ["empanada", "analisis de", "productos afectados"],
        )

    def test_precio_insumo_harina(self):
        self._assert_routing(
            "cuanto vale la harina",
            "historial",
            ["harina", "cop"],
            ["que debo hacer", "empanada de carne: costo"],
        )

    def test_costo_producto_empanada(self):
        self._assert_routing(
            "cuanto cuesta la empanada de carne",
            "costo",
            ["empanada de carne", "costo", "ganancia", "cop"],
            ["carne: precio actual $12", "precio actual $12.000/lb"],
        )

    def test_rentabilidad_general(self):
        self._assert_routing(
            "cual producto es mas rentable",
            "historial",
            ["rentable", "ganancia", "cop"],
            ["no entendi"],
        )

    # --- Simulaciones y escenarios ---

    def test_simulacion_harina(self):
        self._assert_routing(
            "que pasa si la harina sube 15%",
            "calculo",
            ["harina", "analisis", "cop", "productos afectados"],
            ["que debo hacer si sube la harina"],
        )

    def test_escenario_pesimista(self):
        self._assert_routing(
            "peor caso al 10%",
            "escenario",
            ["pesimista", "productos afectados", "cop"],
            ["no entendi"],
        )

    def test_escenario_optimista(self):
        self._assert_routing(
            "mejor caso al 10%",
            "escenario",
            ["optimista", "cop"],
            ["no entendi"],
        )

    def test_insumo_mas_volatil(self):
        self._assert_routing(
            "que insumo subio mas",
            "historial",
            ["harina", "10.7", "cop"],
            ["empanada de carne: costo"],
        )

    # --- Conocimiento conceptual ---

    def test_concepto_sensibilidad(self):
        self._assert_routing(
            "que es sensibilidad",
            "conocimiento",
            ["sensible", "precios"],
            ["3.450 unidades", "analisis de"],
        )


if __name__ == "__main__":
    unittest.main()
