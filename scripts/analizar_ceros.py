"""
Script para analizar por qué algunos productos aparecen en cero en la optimización
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
print("ANÁLISIS: ¿POR QUÉ ALGUNOS PRODUCTOS APARECEN EN CERO?")
print("=" * 80)
print()

# Analizar cada producto
productos_info = []

for producto in pm.listar():
    costo_unitario = cc.calcular_costo_producto(producto.id)
    ganancia_unitaria = cc.calcular_ganancia_producto(producto.id)
    margen = (ganancia_unitaria / producto.precio_venta * 100) if producto.precio_venta > 0 else 0
    
    productos_info.append({
        'nombre': producto.nombre,
        'costo': costo_unitario,
        'precio': producto.precio_venta,
        'ganancia': ganancia_unitaria,
        'margen': margen,
        'demanda_estimada': producto.demanda_estimada
    })

# Ordenar por ganancia unitaria (de mayor a menor)
productos_info.sort(key=lambda x: x['ganancia'], reverse=True)

print("PRODUCTOS ORDENADOS POR GANANCIA UNITARIA (de mayor a menor):")
print("-" * 80)
print(f"{'Producto':<30} | {'Costo':>10} | {'Precio':>10} | {'Ganancia':>10} | {'Margen':>7} | {'Demanda':>8}")
print("-" * 80)

for info in productos_info:
    print(f"{info['nombre']:<30} | ${info['costo']:>8,.2f} | ${info['precio']:>8,.2f} | "
          f"${info['ganancia']:>8,.2f} | {info['margen']:>6.1f}% | {info['demanda_estimada']:>8}")

print()
print("=" * 80)
print("EXPLICACIÓN")
print("=" * 80)
print()
print("El modelo de optimización maximiza la ganancia total.")
print("Si un producto NO tiene demanda mínima especificada, el modelo puede")
print("decidir NO producirlo (ponerlo en 0) si:")
print()
print("1. Es más rentable usar el presupuesto en otros productos con mayor ganancia")
print("2. El producto tiene ganancia negativa o muy baja")
print("3. El presupuesto no alcanza para producir todos los productos")
print()
print("SOLUCIÓN:")
print("- Si quieres que un producto se produzca, DEBES especificar su demanda mínima")
print("- El modelo solo garantiza la producción de productos con demanda mínima")
print("- Los productos sin demanda mínima pueden quedar en 0 si no son rentables")
print()
print("=" * 80)
print("RECOMENDACIÓN")
print("=" * 80)
print("Para que TODOS los productos aparezcan con producción:")
print("1. Especifica demanda mínima para cada producto que quieras producir")
print("2. Asegúrate de tener suficiente presupuesto para cubrir todas las demandas")
print("3. Verifica que todos los productos tengan ganancia positiva")
