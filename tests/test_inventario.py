"""Pruebas del gestor de insumos (catalogo y stock)

Las pruebas anulan el guardado en disco para no modificar data/insumos.json.
"""
import unittest
from unittest import mock

from tests.base import ROOT  # noqa: F401  (asegura ROOT en sys.path)
from core.insumos import Insumo, InsumoManager
from core.json_manager import JSONManager


class TestInsumoManager(unittest.TestCase):
    def setUp(self):
        patcher = mock.patch.object(JSONManager, "save", return_value=True)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.manager = InsumoManager()

    def _nuevo(self, cantidad=5.0, precio=1000.0):
        return Insumo("Prueba X", cantidad, "kg", precio, "Otros", id="prueba_x")

    def test_agregar_crea_insumo(self):
        self.manager.agregar(self._nuevo())
        insumo = self.manager.obtener("prueba_x")
        self.assertIsNotNone(insumo)
        self.assertEqual(insumo.cantidad, 5.0)

    def test_agregar_reemplaza_no_suma(self):
        self.manager.agregar(self._nuevo(cantidad=5.0))
        self.manager.agregar(self._nuevo(cantidad=3.0))
        self.assertEqual(self.manager.obtener("prueba_x").cantidad, 3.0)

    def test_aumentar_stock_suma_y_actualiza_precio(self):
        self.manager.agregar(self._nuevo(cantidad=5.0, precio=1000.0))
        ok = self.manager.aumentar_stock("prueba_x", 10.0, precio_unidad=1200.0)
        self.assertTrue(ok)
        insumo = self.manager.obtener("prueba_x")
        self.assertEqual(insumo.cantidad, 15.0)
        self.assertEqual(insumo.precio_unidad, 1200.0)

    def test_aumentar_stock_insumo_inexistente(self):
        self.assertFalse(self.manager.aumentar_stock("no_existe", 5.0))

    def test_eliminar_insumo(self):
        self.manager.agregar(self._nuevo())
        self.assertTrue(self.manager.eliminar("prueba_x"))
        self.assertIsNone(self.manager.obtener("prueba_x"))

    def test_filtrar_por_categoria(self):
        self.manager.agregar(self._nuevo())
        otros = self.manager.obtener_por_categoria("Otros")
        self.assertIn("prueba_x", [i.id for i in otros])


if __name__ == "__main__":
    unittest.main()
