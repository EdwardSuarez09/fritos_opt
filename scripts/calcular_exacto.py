"""
Script para calcular costos exactos y presupuesto necesario
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.insumos import InsumoManager
from core.masas import MasaManager
from core.productos import ProductoManager
from core.costos import CalculadorCostos

# Cargar datos
im = InsumoManager()
mm = MasaManager()
pm = ProductoManager()
cc = CalculadorCostos(im, mm, pm)

print("=" * 80)
print("CALCULO EXACTO DE COSTOS Y PRESUPUESTO NECESARIO")
print("=" * 80)
print()

productos_test = ["empanada_queso", "empanada_pollo", "papa_rellena"]

for producto_id in productos_test:
    producto = pm.obtener(producto_id)
    if producto:
        costo = cc.calcular_costo_producto(producto_id)
        ganancia = cc.calcular_ganancia_producto(producto_id)
        
        print(f"Producto: {producto.nombre}")
        print(f"  Costo unitario: ${costo:,.2f}")
        print(f"  Ganancia unitaria: ${ganancia:,.2f}")
        print()
        print(f"  PRESUPUESTO NECESARIO:")
        for demanda in [5, 10, 15, 20]:
            presupuesto_min = costo * demanda
            presupuesto_recomendado = presupuesto_min * 1.2
            print(f"    - {demanda} unidades/dia: Min=${presupuesto_min:,.0f}, Recomendado=${presupuesto_recomendado:,.0f}")
        print()
        print("-" * 80)
        print()
