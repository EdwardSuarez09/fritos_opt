"""Pruebas del calculador de costos unitarios"""
import unittest

from tests.base import BotTestCase


class TestCalculadorCostos(BotTestCase):
    """Verifica el costo unitario y el margen de ganancia por producto"""

    def test_costo_producto_es_positivo(self):
        costo = self.bot.calculador.calcular_costo_producto("empanada_carne")
        self.assertGreater(costo, 0)

    def test_ganancia_es_precio_menos_costo(self):
        producto = self.bot.productos.obtener("empanada_carne")
        costo = self.bot.calculador.calcular_costo_producto("empanada_carne")
        ganancia = self.bot.calculador.calcular_ganancia_producto("empanada_carne")
        self.assertAlmostEqual(ganancia, producto.precio_venta - costo, places=4)

    def test_producto_inexistente_costo_cero(self):
        self.assertEqual(self.bot.calculador.calcular_costo_producto("no_existe"), 0.0)

    def test_resumen_incluye_margen(self):
        resumen = self.bot.calculador.obtener_costos_todos_productos()
        self.assertIn("empanada_carne", resumen)
        datos = resumen["empanada_carne"]
        for clave in ("nombre", "costo", "precio_venta", "ganancia", "margen"):
            self.assertIn(clave, datos)

    def test_margen_coherente_con_ganancia(self):
        resumen = self.bot.calculador.obtener_costos_todos_productos()
        datos = resumen["empanada_carne"]
        margen_esperado = datos["ganancia"] / datos["precio_venta"] * 100
        self.assertAlmostEqual(datos["margen"], margen_esperado, places=4)


if __name__ == "__main__":
    unittest.main()
