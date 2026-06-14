"""Pruebas: cada pregunta sugiere la grafica correcta para la UI"""
import unittest

from tests.base import BotTestCase


class TestGraficaPorPregunta(BotTestCase):
    """El bot debe indicar que grafica mostrar segun la pregunta"""

    CASOS = [
        ("cuanto vendi en mayo", "ventas"),
        ("cuantas unidades vendi", "ventas"),
        ("que insumo subio mas", "insumos"),
        ("cuales insumos subieron mas", "insumos"),
        ("cual producto vendio mas", "productos"),
        ("cual producto es mas rentable", "productos"),
        ("resumen del mes", "resumen"),
        ("que pasa si la harina sube 15%", "impacto"),
        ("peor caso al 10%", "escenarios"),
        ("mejor caso al 10%", "escenarios"),
        ("cuanto cuesta el aceite", "insumos"),
        ("cuanto cuesta la empanada de carne", "productos"),
        ("cuantas empanadas de queso vendi", "productos"),
    ]

    def test_grafica_sugerida_por_pregunta(self):
        for pregunta, esperada in self.CASOS:
            resultado = self.responder(pregunta)
            self.assertEqual(
                resultado.get("grafica"),
                esperada,
                msg=(
                    f"'{pregunta}' -> grafica={resultado.get('grafica')} "
                    f"(esperada={esperada}), tipo={resultado.get('tipo')}"
                ),
            )

    def test_simulacion_sin_porcentaje_asume_historico(self):
        """'que pasa si sube el aceite' sin % debe simular con la variacion de mayo"""
        casos = [
            "que pasa si sube el precio del aceite",
            "que pasa si sube la harina",
            "que pasa si baja el queso",
        ]
        for pregunta in casos:
            resultado = self.responder(pregunta)
            self.assertFalse(
                resultado.get("sin_respuesta"),
                msg=f"'{pregunta}' no deberia quedar sin respuesta",
            )
            self.assertEqual(
                resultado.get("tipo"),
                "calculo",
                msg=f"'{pregunta}' -> tipo={resultado.get('tipo')}",
            )
            self.assertIn("asumi", resultado.get("respuesta", "").lower())

    def test_pregunta_conceptual_sin_grafica(self):
        resultado = self.responder("que es sensibilidad")
        self.assertIsNone(resultado.get("grafica"))

    def test_sin_respuesta_sin_grafica(self):
        resultado = self.responder("xyzabc pregunta sin sentido 999")
        self.assertIsNone(resultado.get("grafica"))


if __name__ == "__main__":
    unittest.main()
