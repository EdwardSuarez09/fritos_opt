"""Pruebas del estimador de consumo de insumos y sobrantes"""
import unittest

from tests.base import ROOT  # noqa: F401  (asegura ROOT en sys.path)
from core.inventario import Inventario
from core.consumo import ConsumoEstimador


class TestConsumoEstimador(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        inventario = Inventario()
        cls.insumos = inventario.insumos
        cls.masas = inventario.masas
        cls.productos = inventario.productos
        cls.estimador = ConsumoEstimador(cls.insumos, cls.masas, cls.productos)
        cls.producto = cls.productos.listar()[0]

    def test_insumos_por_unidad_no_vacio(self):
        consumo = self.estimador.insumos_por_unidad(self.producto.id)
        self.assertGreater(len(consumo), 0)

    def test_producto_inexistente_vacio(self):
        self.assertEqual(self.estimador.insumos_por_unidad("no_existe"), {})

    def test_consumo_escala_linealmente(self):
        por_unidad = self.estimador.insumos_por_unidad(self.producto.id)
        consumo_10 = self.estimador.estimar_consumo({self.producto.id: 10})
        for insumo_id, cantidad in por_unidad.items():
            self.assertAlmostEqual(consumo_10[insumo_id], cantidad * 10, places=4)

    def test_consumo_unidades_cero(self):
        self.assertEqual(self.estimador.estimar_consumo({self.producto.id: 0}), {})

    def test_sobrante_es_stock_menos_consumido(self):
        ventas = {self.producto.id: 5}
        sobrantes = self.estimador.estimar_sobrantes(ventas)
        for insumo in self.insumos.listar():
            datos = sobrantes[insumo.id]
            self.assertAlmostEqual(
                datos["sobrante"], datos["stock"] - datos["consumido"], places=4
            )


if __name__ == "__main__":
    unittest.main()
