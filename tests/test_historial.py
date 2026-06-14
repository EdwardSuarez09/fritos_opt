"""Pruebas del historial mensual"""
import unittest

from tests.base import ROOT  # noqa: F401
from core.historial import HistorialMensual
from core.inventario import Inventario


class TestHistorialMensual(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.historial = HistorialMensual()
        inv = Inventario()
        cls.historial.set_nombres_insumos(inv.insumos)
        cls.historial.set_nombres_productos(inv.productos)

    def test_meta_cargada(self):
        self.assertEqual(self.historial.meta.get("mes"), "mayo")
        self.assertEqual(self.historial.meta.get("moneda"), "COP")

    def test_ventas_mes_coherentes(self):
        resumen = self.historial.ventas_mes()
        self.assertEqual(resumen.get("total_unidades"), 3450)
        self.assertGreater(resumen.get("ingreso_bruto", 0), 0)

    def test_producto_top_es_empanada_queso(self):
        nombre, datos = self.historial.producto_mas_vendido()
        self.assertIn("queso", nombre.lower())
        self.assertEqual(datos["unidades_vendidas"], 710)

    def test_insumo_mas_volatil_harina(self):
        nombre, datos = self.historial.insumo_mas_volatil()
        self.assertIn("harina", nombre.lower())
        self.assertAlmostEqual(datos["variacion_pct"], 10.7, places=1)

    def test_top_productos_orden_descendente(self):
        tops = self.historial.top_productos(3)
        unidades = [t[1]["unidades_vendidas"] for t in tops]
        self.assertEqual(unidades, sorted(unidades, reverse=True))

    def test_total_gastado_suma_semanas(self):
        compras = self.historial.datos.get("compras", {})
        esperado = sum(s.get("total_gastado", 0) for s in compras.values())
        self.assertEqual(self.historial.total_gastado_mes(), esperado)


if __name__ == "__main__":
    unittest.main()
