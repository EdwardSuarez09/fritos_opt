"""
Script para calcular y mostrar los costos reales de los productos
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.insumos import InsumoManager
from core.masas import MasaManager
from core.productos import ProductoManager
from core.costos import CalculadorCostos

# Cargar datos
insumo_manager = InsumoManager()
masa_manager = MasaManager()
producto_manager = ProductoManager()
calculador = CalculadorCostos(insumo_manager, masa_manager, producto_manager)

print("=" * 80)
print("ANÁLISIS DE COSTOS Y GANANCIAS")
print("=" * 80)
print()

# Analizar cada producto
for producto in producto_manager.listar():
    costo = calculador.calcular_costo_producto(producto.id)
    ganancia = calculador.calcular_ganancia_producto(producto.id)
    margen = (ganancia / producto.precio_venta * 100) if producto.precio_venta > 0 else 0
    
    print(f"Producto: {producto.nombre}")
    print(f"  Precio de venta: ${producto.precio_venta:,.2f}")
    print(f"  Costo unitario:  ${costo:,.2f}")
    print(f"  Ganancia:        ${ganancia:,.2f}")
    print(f"  Margen:          {margen:.1f}%")
    
    if ganancia < 0:
        print(f"  [PROBLEMA] Ganancia NEGATIVA (perdida por unidad)")
    elif ganancia == 0:
        print(f"  [PROBLEMA] Sin ganancia")
    else:
        print(f"  [OK] Ganancia positiva")
    
    # Desglose del costo
    print(f"  Desglose de costos:")
    
    # Costo de masa
    if producto.masa_id:
        masa = masa_manager.obtener(producto.masa_id)
        if masa:
            costo_masa = masa.costo_por_unidad_equivalente(insumo_manager)
            print(f"    - Masa: ${costo_masa:,.2f}")
            
            # Mostrar costo del lote completo
            costo_lote = masa.calcular_costo(insumo_manager)
            total_productos = sum(masa.rendimiento.values())
            print(f"      (Lote completo: ${costo_lote:,.2f} para {total_productos} productos)")
    
    # Costo de insumos extra
    costo_insumos_extra = 0
    for insumo_id, porciones in producto.insumos_extra.items():
        insumo = insumo_manager.obtener(insumo_id)
        if insumo:
            costo_insumo = insumo.precio_unidad * porciones
            costo_insumos_extra += costo_insumo
            print(f"    - {insumo.nombre} ({porciones} porciones): ${costo_insumo:,.2f}")
    
    # Costo de aceite
    aceites = insumo_manager.obtener_por_categoria("Aceite")
    if aceites:
        costo_aceite_promedio = sum(a.precio_unidad for a in aceites) / len(aceites)
        costo_aceite = costo_aceite_promedio * 0.1
        print(f"    - Aceite (0.1 unidades): ${costo_aceite:,.2f}")
    
    # Costo de empaques
    otros = insumo_manager.obtener_por_categoria("Otros")
    empaques = [o for o in otros if "empaque" in o.nombre.lower() or "servilleta" in o.nombre.lower()]
    if empaques:
        costo_empaque_promedio = sum(e.precio_unidad for e in empaques) / len(empaques)
        print(f"    - Empaque: ${costo_empaque_promedio:,.2f}")
    
    print()
    print("-" * 80)
    print()

# Resumen
print("=" * 80)
print("RESUMEN")
print("=" * 80)
productos_rentables = 0
productos_no_rentables = 0

for producto in producto_manager.listar():
    ganancia = calculador.calcular_ganancia_producto(producto.id)
    if ganancia > 0:
        productos_rentables += 1
    else:
        productos_no_rentables += 1

print(f"Productos rentables: {productos_rentables}")
print(f"Productos NO rentables: {productos_no_rentables}")

if productos_no_rentables > 0:
    print()
    print("[PROBLEMA DETECTADO]")
    print("   Hay productos con ganancia negativa o cero.")
    print("   Esto hace que el modelo sea NO FACTIBLE porque no puede maximizar ganancias.")
    print()
    print("   SOLUCIONES:")
    print("   1. Aumentar los precios de venta")
    print("   2. Reducir los precios de los insumos")
    print("   3. Reducir las cantidades de insumos extra en los productos")
