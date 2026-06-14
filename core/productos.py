"""
Gestión de productos del negocio

Este módulo maneja los productos finales que se venden, incluyendo su
composición (masa e insumos extra), precios y demanda.
"""
from core.json_manager import JSONManager
from typing import Dict, List, Optional

class Producto:
    """
    Representa un producto del negocio
    
    Un producto es el resultado final que se vende. Está compuesto por:
    - Una masa (opcional)
    - Insumos extra (rellenos, salsas, etc.)
    - Tiene un precio de venta y una demanda estimada
    """
    
    def __init__(self, nombre: str, masa_id: Optional[str], 
                 insumos_extra: Dict[str, float], precio_venta: float,
                 demanda_estimada: int, categoria: str, id: Optional[str] = None):
        """
        Inicializa un producto
        
        Args:
            nombre: Nombre del producto (ej: "Empanada de carne")
            masa_id: ID de la masa asociada (puede ser None si no usa masa)
            insumos_extra: Diccionario con {insumo_id: porciones_usadas}
                          que indica qué insumos adicionales usa y en qué cantidad
            precio_venta: Precio de venta del producto
            demanda_estimada: Demanda estimada promedio por día
            categoria: Categoría del producto
            id: ID único del producto (se genera automáticamente si no se proporciona)
        """
        self.id = id or nombre.lower().replace(" ", "_")
        self.nombre = nombre
        self.masa_id = masa_id  # ID de la masa que usa este producto
        self.insumos_extra = insumos_extra  # {insumo_id: porciones} - insumos adicionales
        self.precio_venta = precio_venta
        self.demanda_estimada = demanda_estimada  # Demanda promedio estimada
        self.categoria = categoria
        self.demanda_diaria = {}  # {dia: cantidad} - demanda específica por día
    
    def agregar_demanda_diaria(self, dia: str, cantidad: float):
        """
        Agrega demanda para un día específico
        
        Permite especificar la demanda mínima de un producto para un día
        particular, lo cual se usa en la optimización.
        
        Args:
            dia: Día de la semana (ej: "Lunes")
            cantidad: Cantidad mínima a producir ese día
        """
        self.demanda_diaria[dia] = cantidad
    
    def to_dict(self):
        """
        Convierte el producto a diccionario para almacenamiento
        
        Returns:
            Diccionario con todos los atributos del producto
        """
        return {
            "id": self.id,
            "nombre": self.nombre,
            "masa_id": self.masa_id,
            "insumos_extra": self.insumos_extra,
            "precio_venta": self.precio_venta,
            "demanda_estimada": self.demanda_estimada,
            "categoria": self.categoria,
            "demanda_diaria": self.demanda_diaria
        }
    
    @classmethod
    def from_dict(cls, data: Dict):
        """
        Crea un producto desde un diccionario (método de clase)
        
        Útil para reconstruir productos desde datos almacenados en JSON
        
        Args:
            data: Diccionario con los datos del producto
        
        Returns:
            Instancia de Producto con los datos proporcionados
        """
        producto = cls(
            nombre=data["nombre"],
            masa_id=data.get("masa_id"),
            insumos_extra=data.get("insumos_extra", {}),
            precio_venta=data["precio_venta"],
            demanda_estimada=data.get("demanda_estimada", 0),
            categoria=data.get("categoria", ""),
            id=data.get("id")
        )
        producto.demanda_diaria = data.get("demanda_diaria", {})
        return producto

class ProductoManager:
    """
    Gestiona los productos del negocio
    
    Esta clase maneja el almacenamiento, carga, guardado y consulta de productos.
    Los datos se persisten en archivos JSON y se cargan automáticamente al inicializar.
    """
    
    def __init__(self):
        """Inicializa el gestor de productos y carga los datos desde JSON"""
        self.json_manager = JSONManager()
        self.productos: Dict[str, Producto] = {}  # Diccionario {producto_id: Producto}
        self.load()  # Cargar productos existentes al inicializar
    
    def load(self):
        """
        Carga productos desde el archivo JSON
        
        Lee el archivo productos.json y reconstruye los objetos Producto
        """
        data = self.json_manager.load("productos", default={})
        # Convertir cada entrada del diccionario en un objeto Producto
        self.productos = {
            producto_id: Producto.from_dict(producto_data)
            for producto_id, producto_data in data.items()
        }
    
    def save(self):
        """
        Guarda los productos en el archivo JSON
        
        Convierte todos los productos a diccionarios y los guarda en productos.json
        
        Returns:
            True si se guardó correctamente, False en caso contrario
        """
        data = {
            producto_id: producto.to_dict()
            for producto_id, producto in self.productos.items()
        }
        return self.json_manager.save("productos", data)
    
    def agregar(self, producto: Producto):
        """
        Agrega un nuevo producto
        
        Args:
            producto: Producto a agregar
        
        Returns:
            ID del producto agregado
        """
        self.productos[producto.id] = producto
        self.save()  # Guardar cambios en disco
        return producto.id
    
    def eliminar(self, producto_id: str):
        """
        Elimina un producto del sistema
        
        Args:
            producto_id: ID del producto a eliminar
        
        Returns:
            True si se eliminó correctamente, False si no existía
        """
        if producto_id in self.productos:
            del self.productos[producto_id]
            self.save()  # Guardar cambios en disco
            return True
        return False
    
    def obtener(self, producto_id: str) -> Optional[Producto]:
        """
        Obtiene un producto por su ID
        
        Args:
            producto_id: ID del producto a buscar
        
        Returns:
            Objeto Producto si existe, None en caso contrario
        """
        return self.productos.get(producto_id)
    
    def listar(self) -> List[Producto]:
        """
        Lista todos los productos registrados
        
        Returns:
            Lista de objetos Producto
        """
        return list(self.productos.values())

