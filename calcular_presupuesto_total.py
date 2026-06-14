"""
Script para calcular el presupuesto diario necesario para TODOS los productos
"""
import sys
sys.path.insert(0, 'fritos_opt')

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
print("CALCULO DE PRESUPUESTO DIARIO PARA TODOS LOS PRODUCTOS")
print("=" * 80)
print()

# Calcular costo diario de todos los productos usando demanda_estimada
costo_total_diario = 0
productos_info = []

for producto in pm.listar():
    costo_unitario = cc.calcular_costo_producto(producto.id)
    demanda_diaria = producto.demanda_estimada
    costo_producto_diario = costo_unitario * demanda_diaria
    
    productos_info.append({
        'nombre': producto.nombre,
        'costo_unitario': costo_unitario,
        'demanda': demanda_diaria,
        'costo_diario': costo_producto_diario
    })
    
    costo_total_diario += costo_producto_diario

# Mostrar desglose
print("DESGLOSE POR PRODUCTO:")
print("-" * 80)
for info in productos_info:
    print(f"{info['nombre']:30} | Demanda: {info['demanda']:3} | "
          f"Costo/Unidad: ${info['costo_unitario']:8,.2f} | "
          f"Costo Diario: ${info['costo_diario']:10,.2f}")

print()
print("=" * 80)
print("RESUMEN")
print("=" * 80)
print(f"Costo total diario (todos los productos): ${costo_total_diario:,.2f}")
print(f"Presupuesto diario mínimo necesario:     ${costo_total_diario:,.2f}")
print(f"Presupuesto diario recomendado (+20%):    ${costo_total_diario * 1.2:,.2f}")
print()
print(f"Presupuesto semanal mínimo:                ${costo_total_diario * 7:,.2f}")
print(f"Presupuesto semanal recomendado:          ${costo_total_diario * 1.2 * 7:,.2f}")
print()
print("=" * 80)
print("VALORES PARA INGRESAR EN LA OPTIMIZACIÓN")
print("=" * 80)
print(f"Presupuesto diario (mínimo):  {int(costo_total_diario):,}")
print(f"Presupuesto diario (recomendado): {int(costo_total_diario * 1.2):,}")
print()
print("Ingresa estos valores en TODOS los días de la semana")

