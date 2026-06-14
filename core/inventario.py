"""
Gestión de inventario (wrapper para facilitar acceso)
"""
from core.insumos import InsumoManager
from core.masas import MasaManager
from core.productos import ProductoManager
from typing import List

class Inventario:
    """Clase unificada para acceder a todos los datos del negocio"""
    
    def __init__(self):
        self.insumos = InsumoManager()
        self.masas = MasaManager()
        self.productos = ProductoManager()
    
    def obtener_resumen(self) -> dict:
        """Obtiene un resumen del inventario"""
        return {
            "total_insumos": len(self.insumos.listar()),
            "total_masas": len(self.masas.listar()),
            "total_productos": len(self.productos.listar())
        }

