"""Pruebas del modulo de ventas de productos

El guardado en disco se anula para no modificar data/ventas.json.
"""
import unittest
from unittest import mock

from tests.base import ROOT  # noqa: F401  (asegura ROOT en sys.path)
from core.inventario import Inventario
from core.ventas import VentasManager
from core.json_manager import JSONManager


class TestVentasManager(unittest.TestCase):
    def setUp(self):
        patcher = mock.patch.object(JSONManager, "save", return_value=True)
        patcher.start()
        self.addCleanup(patcher.stop)
        inventario = Inventario()
        self.productos = inventario.productos
        self.ventas = VentasManager(self.productos)
        self.ventas.ventas = []  # historial limpio
        self.producto = self.productos.listar()[0]

    def test_registrar_venta_valida(self):
        venta = self.ventas.registrar(self.producto.id, 10)
        self.assertIsNotNone(venta)
        self.assertEqual(venta.cantidad, 10)

    def test_precio_por_defecto_es_del_producto(self):
        venta = self.ventas.registrar(self.producto.id, 1)
        self.assertEqual(venta.precio_unitario, self.producto.precio_venta)

    def test_registrar_producto_inexistente(self):
        self.assertIsNone(self.ventas.registrar("no_existe", 5))

    def test_total_unidades_e_ingresos(self):
        self.ventas.registrar(self.producto.id, 4, precio_unitario=2000.0)
        self.ventas.registrar(self.producto.id, 6, precio_unitario=2000.0)
        self.assertEqual(self.ventas.total_unidades(), 10)
        self.assertEqual(self.ventas.total_ingresos(), 20000.0)

    def test_resumen_por_producto(self):
        self.ventas.registrar(self.producto.id, 3, precio_unitario=2000.0)
        resumen = self.ventas.resumen_por_producto()
        self.assertIn(self.producto.id, resumen)
        self.assertEqual(resumen[self.producto.id]["unidades"], 3)
        self.assertEqual(resumen[self.producto.id]["ingreso"], 6000.0)

    def test_eliminar_venta(self):
        venta = self.ventas.registrar(self.producto.id, 2)
        self.assertTrue(self.ventas.eliminar(venta.id))
        self.assertEqual(len(self.ventas.listar()), 0)


if __name__ == "__main__":
    unittest.main()
