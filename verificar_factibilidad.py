"""
Script para verificar factibilidad y calcular valores exactos
"""
import sys
sys.path.insert(0, 'fritos_opt')

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
print("VERIFICACION DE FACTIBILIDAD")
print("=" * 80)
print()

# Analizar cada producto
for producto in producto_manager.listar():
    costo = calculador.calcular_costo_producto(producto.id)
    ganancia = calculador.calcular_ganancia_producto(producto.id)
    
    print(f"Producto: {producto.nombre}")
    print(f"  Costo unitario: ${costo:,.2f}")
    print(f"  Ganancia unitaria: ${ganancia:,.2f}")
    
    if ganancia < 0:
        print(f"  [PROBLEMA] Ganancia NEGATIVA")
    else:
        print(f"  [OK] Ganancia positiva")
    
    # Calcular para diferentes escenarios
    print(f"  Escenarios factibles:")
    for demanda in [5, 10, 15, 20]:
        costo_diario = costo * demanda
        presupuesto_min = int(costo_diario * 1.1)  # 10% margen
        print(f"    - {demanda} unidades/dia: necesita ${presupuesto_min:,}/dia (costo: ${costo_diario:,.2f})")
    
    print()
    print("-" * 80)
    print()

# Recomendación específica
print("=" * 80)
print("RECOMENDACION PARA PROBAR")
print("=" * 80)
print()
print("Producto: empanada de queso (mas barata)")
producto = producto_manager.obtener("empanada_queso")
if producto:
    costo = calculador.calcular_costo_producto("empanada_queso")
    demanda = 10
    costo_diario = costo * demanda
    presupuesto = int(costo_diario * 1.2)
    
    print(f"  Costo unitario: ${costo:,.2f}")
    print(f"  Demanda: {demanda} unidades/dia")
    print(f"  Presupuesto recomendado: ${presupuesto:,}/dia")
    print()
    print(f"  VALORES EXACTOS PARA USAR:")
    print(f"    - Producto: empanada de queso")
    print(f"    - Demanda: {demanda} (todos los dias)")
    print(f"    - Presupuesto: {presupuesto} (todos los dias)")

