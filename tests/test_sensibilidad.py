"""Pruebas del analizador de sensibilidad numerico"""
import unittest

from tests.base import BotTestCase


class TestAnalizadorSensibilidad(BotTestCase):
    def test_cambio_precio_afecta_productos(self):
        insumo = self.bot.insumos.obtener("harina_trigo")
        precio_original = insumo.precio_unidad
        nuevo = precio_original * 1.15
        resultados = self.analizador.analizar_cambio_precio_insumo(
            insumo.id, nuevo, precio_original
        )
        self.assertGreater(len(resultados.get("productos_afectados", [])), 0)
        self.assertLess(resultados.get("impacto_total_ganancia", 0), 0)

    def test_precio_restaurado_tras_analisis(self):
        insumo = self.bot.insumos.obtener("aceite")
        precio_antes = insumo.precio_unidad
        self.analizador.analizar_cambio_precio_insumo(insumo.id, precio_antes * 1.2)
        self.assertEqual(insumo.precio_unidad, precio_antes)

    def test_escenario_pesimista_afecta_todos_los_productos(self):
        escenarios = self.analizador.generar_escenarios(10.0)
        res = escenarios["pesimista"]["resultados"]
        n_afectados = len(res.get("productos_afectados", []))
        n_productos = len(self.bot.productos.listar())
        self.assertGreater(n_afectados, 0)
        self.assertEqual(n_afectados, n_productos)

    def test_escenario_optimista_mejora_ganancia(self):
        escenarios = self.analizador.generar_escenarios(10.0)
        res = escenarios["optimista"]["resultados"]
        self.assertGreater(res.get("impacto_total_ganancia", 0), 0)

    def test_escenario_realista_sin_cambios(self):
        escenarios = self.analizador.generar_escenarios(10.0)
        res = escenarios["realista"]["resultados"]
        self.assertEqual(res.get("impacto_total_costo", 0), 0)
        self.assertEqual(res.get("impacto_total_ganancia", 0), 0)

    def test_escenario_usa_costos_originales(self):
        """Regresion: antes comparaba costos ya modificados y daba 0 afectados"""
        escenarios = self.analizador.generar_escenarios(10.0)
        pesimista = escenarios["pesimista"]["resultados"]
        self.assertNotEqual(pesimista.get("impacto_total_costo", 0), 0)


if __name__ == "__main__":
    unittest.main()
