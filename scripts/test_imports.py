"""
Script de prueba para verificar que todas las importaciones funcionan
"""
import sys
from pathlib import Path

# Agregar la raíz del proyecto al path al ejecutarse desde scripts/.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

try:
    print("Probando importaciones...")
    
    from core.json_manager import JSONManager
    print("[OK] JSONManager importado")
    
    from core.insumos import Insumo, InsumoManager
    print("[OK] Insumo e InsumoManager importados")
    
    from core.masas import LoteMasa, MasaManager
    print("[OK] LoteMasa y MasaManager importados")
    
    from core.productos import Producto, ProductoManager
    print("[OK] Producto y ProductoManager importados")
    
    from core.inventario import Inventario
    print("[OK] Inventario importado")
    
    from core.costos import CalculadorCostos
    print("[OK] CalculadorCostos importado")
    
    from core.optimizador import Optimizador
    print("[OK] Optimizador importado")
    
    from ui.theme import Theme
    print("[OK] Theme importado")
    
    from ui.main_window import MainWindow
    print("[OK] MainWindow importado")
    
    print("\n[SUCCESS] Todas las importaciones funcionan correctamente!")
    print("Puedes ejecutar el sistema con: python main.py")
    
except ImportError as e:
    print(f"[ERROR] Error de importacion: {e}")
    sys.exit(1)
