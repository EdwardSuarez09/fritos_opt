"""
Script para calcular el presupuesto mínimo necesario
"""
import sys
sys.path.insert(0, '.')

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
print("CALCULO DE PRESUPUESTO MINIMO NECESARIO")
print("=" * 80)
print()

# Analizar cada producto
for producto in producto_manager.listar():
    costo = calculador.calcular_costo_producto(producto.id)
    
    print(f"Producto: {producto.nombre}")
    print(f"  Costo unitario: ${costo:,.2f}")
    
    # Calcular para diferentes demandas
    demandas = [5, 10, 15, 20, 25, 30]
    print(f"  Presupuesto diario necesario:")
    for demanda in demandas:
        presupuesto_necesario = costo * demanda
        print(f"    - {demanda} unidades/dia: ${presupuesto_necesario:,.2f}")
    
    print()
    print("-" * 80)
    print()

# Ejemplo específico
print("=" * 80)
print("EJEMPLO: Papa Rellena con demanda de 20 unidades/dia")
print("=" * 80)
producto = producto_manager.obtener("papa_rellena")
if producto:
    costo = calculador.calcular_costo_producto("papa_rellena")
    demanda = 20
    presupuesto_diario = costo * demanda
    presupuesto_semanal = presupuesto_diario * 7
    
    print(f"Costo unitario: ${costo:,.2f}")
    print(f"Demanda: {demanda} unidades/dia")
    print(f"Presupuesto diario necesario: ${presupuesto_diario:,.2f}")
    print(f"Presupuesto semanal necesario: ${presupuesto_semanal:,.2f}")
    print()
    print(f"RECOMENDACION:")
    print(f"  - Presupuesto diario MINIMO: ${int(presupuesto_diario * 1.1):,} (con 10% margen)")
    print(f"  - O reduce la demanda a 5-10 unidades/dia")

