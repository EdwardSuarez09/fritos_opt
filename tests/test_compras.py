"""Pruebas del modulo de compras de insumos

El guardado en disco se anula para no modificar data/compras.json ni
data/insumos.json durante las pruebas.
"""
import unittest
from unittest import mock

from tests.base import ROOT  # noqa: F401  (asegura ROOT en sys.path)
from core.insumos import InsumoManager
from core.compras import ComprasManager
from core.json_manager import JSONManager


class TestComprasManager(unittest.TestCase):
    def setUp(self):
        patcher = mock.patch.object(JSONManager, "save", return_value=True)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.insumos = InsumoManager()
        self.compras = ComprasManager(self.insumos)
        self.compras.compras = []  # historial limpio para pruebas deterministas
        # Tomamos un insumo existente cualquiera como referencia
        self.insumo = self.insumos.listar()[0]

    def test_registrar_compra_valida(self):
        compra = self.compras.registrar(self.insumo.id, 5.0, 1000.0)
        self.assertIsNotNone(compra)
        self.assertEqual(compra.total, 5000.0)

    def test_registrar_actualiza_stock(self):
        stock_previo = self.insumo.cantidad
        self.compras.registrar(self.insumo.id, 5.0, 1200.0)
        self.assertEqual(self.insumo.cantidad, stock_previo + 5.0)
        self.assertEqual(self.insumo.precio_unidad, 1200.0)

    def test_registrar_insumo_inexistente(self):
        self.assertIsNone(self.compras.registrar("no_existe", 5.0, 1000.0))

    def test_total_gastado(self):
        self.compras.registrar(self.insumo.id, 2.0, 1000.0)
        self.compras.registrar(self.insumo.id, 3.0, 1000.0)
        self.assertEqual(self.compras.total_gastado(), 5000.0)

    def test_cantidad_comprada_por_insumo(self):
        self.compras.registrar(self.insumo.id, 2.0, 1000.0)
        self.compras.registrar(self.insumo.id, 3.0, 1000.0)
        cantidades = self.compras.cantidad_comprada_por_insumo()
        self.assertEqual(cantidades[self.insumo.id], 5.0)

    def test_eliminar_compra(self):
        compra = self.compras.registrar(self.insumo.id, 2.0, 1000.0)
        self.assertTrue(self.compras.eliminar(compra.id))
        self.assertEqual(len(self.compras.listar()), 0)


if __name__ == "__main__":
    unittest.main()
