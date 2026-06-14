"""
Gestión de lotes de masa

Este módulo maneja los lotes de masa utilizados en la producción. Un lote
de masa se crea a partir de varios insumos y puede producir múltiples productos.
"""
from core.json_manager import JSONManager
from core.insumos import InsumoManager
from typing import Dict, List, Optional

class LoteMasa:
    """
    Representa un lote de masa
    
    Un lote de masa es una mezcla de insumos que se usa para producir productos.
    El costo del lote se distribuye entre los productos que se pueden hacer con él.
    """
    
    def __init__(self, nombre: str, cantidad_total: float, unidad: str,
                 insumos_usados: Dict[str, float], id: Optional[str] = None):
        """
        Inicializa un lote de masa
        
        Args:
            nombre: Nombre del lote (ej. "Masa tradicional")
            cantidad_total: Cantidad total del lote producido
            unidad: Unidad de medida (kg, g, lb)
            insumos_usados: Diccionario con {insumo_id: cantidad_usada}
                          que indica qué insumos y en qué cantidad se usaron
            id: ID único del lote (se genera automáticamente si no se proporciona)
        """
        self.id = id or nombre.lower().replace(" ", "_")
        self.nombre = nombre
        self.cantidad_total = cantidad_total
        self.unidad = unidad
        self.insumos_usados = insumos_usados  # {insumo_id: cantidad_usada}
        self.rendimiento = {}  # {producto_id: cantidad_producida} - cuántos productos se hacen con este lote
    
    def calcular_costo(self, insumo_manager: InsumoManager) -> float:
        """
        Calcula el costo total del lote de masa
        
        Suma el costo proporcional de cada insumo usado en el lote.
        El costo proporcional se calcula como:
        (cantidad_usada / cantidad_disponible) × costo_total_insumo
        
        Args:
            insumo_manager: Gestor de insumos para obtener precios
        
        Returns:
            Costo total del lote
        """
        costo_total = 0.0
        for insumo_id, cantidad_usada in self.insumos_usados.items():
            insumo = insumo_manager.obtener(insumo_id)
            if insumo:
                # Calcula el costo proporcional del insumo usado
                # Ejemplo: si usamos 0.5 kg de un insumo que cuesta $10 por 1 kg,
                # el costo proporcional es (0.5 / 1.0) * 10 = $5
                costo_proporcional = (cantidad_usada / insumo.cantidad) * insumo.costo_total()
                costo_total += costo_proporcional
        return costo_total
    
    def costo_por_unidad_equivalente(self, insumo_manager: InsumoManager) -> float:
        """
        Calcula el costo por unidad equivalente de masa
        
        Este método distribuye el costo total del lote entre todos los productos
        que se pueden producir con él. Es el costo que se asigna a cada producto
        que usa esta masa.
        
        Args:
            insumo_manager: Gestor de insumos para calcular el costo del lote
        
        Returns:
            Costo por unidad de producto (costo_lote / total_productos_producidos)
        """
        total_productos = sum(self.rendimiento.values())
        if total_productos == 0:
            return 0.0  # Si no hay productos, el costo por unidad es 0
        costo_lote = self.calcular_costo(insumo_manager)
        # Distribuir el costo del lote entre todos los productos
        return costo_lote / total_productos
    
    def agregar_rendimiento(self, producto_id: str, cantidad: int):
        """
        Agrega el rendimiento de un producto para este lote
        
        El rendimiento indica cuántas unidades de un producto se pueden
        producir con este lote de masa. Esto se usa para calcular el costo
        por unidad equivalente.
        
        Args:
            producto_id: ID del producto
            cantidad: Cantidad de productos que se pueden hacer con este lote
        """
        self.rendimiento[producto_id] = cantidad
    
    def to_dict(self):
        """
        Convierte el lote a diccionario para almacenamiento
        
        Returns:
            Diccionario con todos los atributos del lote
        """
        return {
            "id": self.id,
            "nombre": self.nombre,
            "cantidad_total": self.cantidad_total,
            "unidad": self.unidad,
            "insumos_usados": self.insumos_usados,
            "rendimiento": self.rendimiento
        }
    
    @classmethod
    def from_dict(cls, data: Dict):
        """
        Crea un lote desde un diccionario (método de clase)
        
        Útil para reconstruir lotes desde datos almacenados en JSON
        
        Args:
            data: Diccionario con los datos del lote
        
        Returns:
            Instancia de LoteMasa con los datos proporcionados
        """
        lote = cls(
            nombre=data["nombre"],
            cantidad_total=data["cantidad_total"],
            unidad=data["unidad"],
            insumos_usados=data["insumos_usados"],
            id=data.get("id")
        )
        lote.rendimiento = data.get("rendimiento", {})
        return lote

class MasaManager:
    """
    Gestiona los lotes de masa
    
    Esta clase maneja el almacenamiento, carga, guardado y consulta de lotes de masa.
    Los datos se persisten en archivos JSON y se cargan automáticamente al inicializar.
    """
    
    def __init__(self):
        """Inicializa el gestor de masas y carga los datos desde JSON"""
        self.json_manager = JSONManager()
        self.masas: Dict[str, LoteMasa] = {}  # Diccionario {masa_id: LoteMasa}
        self.load()  # Cargar masas existentes al inicializar
    
    def load(self):
        """
        Carga lotes de masa desde el archivo JSON
        
        Lee el archivo masas.json y reconstruye los objetos LoteMasa
        """
        data = self.json_manager.load("masas", default={})
        # Convertir cada entrada del diccionario en un objeto LoteMasa
        self.masas = {
            masa_id: LoteMasa.from_dict(masa_data)
            for masa_id, masa_data in data.items()
        }
    
    def save(self):
        """
        Guarda los lotes de masa en el archivo JSON
        
        Convierte todos los lotes a diccionarios y los guarda en masas.json
        
        Returns:
            True si se guardó correctamente, False en caso contrario
        """
        data = {
            masa_id: masa.to_dict()
            for masa_id, masa in self.masas.items()
        }
        return self.json_manager.save("masas", data)
    
    def agregar(self, lote: LoteMasa):
        """
        Agrega un nuevo lote de masa
        
        Args:
            lote: Lote de masa a agregar
        
        Returns:
            ID del lote agregado
        """
        self.masas[lote.id] = lote
        self.save()  # Guardar cambios en disco
        return lote.id
    
    def eliminar(self, masa_id: str):
        """
        Elimina un lote de masa del sistema
        
        Args:
            masa_id: ID del lote a eliminar
        
        Returns:
            True si se eliminó correctamente, False si no existía
        """
        if masa_id in self.masas:
            del self.masas[masa_id]
            self.save()  # Guardar cambios en disco
            return True
        return False
    
    def obtener(self, masa_id: str) -> Optional[LoteMasa]:
        """
        Obtiene un lote de masa por su ID
        
        Args:
            masa_id: ID del lote a buscar
        
        Returns:
            Objeto LoteMasa si existe, None en caso contrario
        """
        return self.masas.get(masa_id)
    
    def listar(self) -> List[LoteMasa]:
        """
        Lista todos los lotes de masa registrados
        
        Returns:
            Lista de objetos LoteMasa
        """
        return list(self.masas.values())

