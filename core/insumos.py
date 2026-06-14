"""
Gestión de insumos del negocio

Este módulo maneja los insumos (materias primas) utilizados en la producción,
incluyendo su almacenamiento, categorización y costos.
"""
from core.json_manager import JSONManager
from typing import Dict, List, Optional

class Insumo:
    """
    Representa un insumo (materia prima) del negocio
    
    Un insumo es cualquier material necesario para la producción, como harina,
    aceite, rellenos, empaques, etc. Cada insumo tiene un precio por unidad
    y pertenece a una categoría específica.
    """
    
    # Categorías predefinidas para organizar los insumos
    CATEGORIAS = [
        "Masa tradicional",
        "Masa de yuca",
        "Masa de plátano",
        "Masa de avena",
        "Relleno",
        "Aceite",
        "Salsas",
        "Otros"
    ]
    
    # Unidades de medida disponibles para los insumos
    UNIDADES = ["kg", "g", "lb", "ml", "L", "unidad"]
    
    def __init__(self, nombre: str, cantidad: float, unidad: str, 
                 precio_unidad: float, categoria: str, id: Optional[str] = None):
        """
        Inicializa un insumo
        
        Args:
            nombre: Nombre del insumo (ej: "Harina de trigo")
            cantidad: Cantidad disponible del insumo
            unidad: Unidad de medida (kg, g, lb, ml, L, unidad)
            precio_unidad: Precio por unidad del insumo
            categoria: Categoría del insumo (debe estar en CATEGORIAS)
            id: ID único del insumo (se genera automáticamente si no se proporciona)
        """
        # Generar ID automáticamente si no se proporciona (nombre en minúsculas con guiones bajos)
        self.id = id or nombre.lower().replace(" ", "_")
        self.nombre = nombre
        self.cantidad = cantidad
        self.unidad = unidad
        self.precio_unidad = precio_unidad
        self.categoria = categoria
    
    def to_dict(self):
        """
        Convierte el insumo a diccionario para almacenamiento
        
        Returns:
            Diccionario con todos los atributos del insumo
        """
        return {
            "id": self.id,
            "nombre": self.nombre,
            "cantidad": self.cantidad,
            "unidad": self.unidad,
            "precio_unidad": self.precio_unidad,
            "categoria": self.categoria
        }
    
    @classmethod
    def from_dict(cls, data: Dict):
        """
        Crea un insumo desde un diccionario (método de clase)
        
        Útil para reconstruir insumos desde datos almacenados en JSON
        
        Args:
            data: Diccionario con los datos del insumo
        
        Returns:
            Instancia de Insumo con los datos proporcionados
        """
        return cls(
            nombre=data["nombre"],
            cantidad=data["cantidad"],
            unidad=data["unidad"],
            precio_unidad=data["precio_unidad"],
            categoria=data["categoria"],
            id=data.get("id")
        )
    
    def costo_total(self):
        """
        Calcula el costo total del insumo disponible
        
        Returns:
            Costo total = cantidad × precio_unidad
        """
        return self.cantidad * self.precio_unidad

class InsumoManager:
    """
    Gestiona los insumos del negocio
    
    Esta clase maneja el almacenamiento, carga, guardado y consulta de insumos.
    Los datos se persisten en archivos JSON y se cargan automáticamente al inicializar.
    """
    
    def __init__(self):
        """Inicializa el gestor de insumos y carga los datos desde JSON"""
        self.json_manager = JSONManager()
        self.insumos: Dict[str, Insumo] = {}  # Diccionario {insumo_id: Insumo}
        self.load()  # Cargar insumos existentes al inicializar
    
    def load(self):
        """
        Carga insumos desde el archivo JSON
        
        Lee el archivo insumos.json y reconstruye los objetos Insumo
        """
        data = self.json_manager.load("insumos", default={})
        # Convertir cada entrada del diccionario en un objeto Insumo
        self.insumos = {
            insumo_id: Insumo.from_dict(insumo_data)
            for insumo_id, insumo_data in data.items()
        }
    
    def save(self):
        """
        Guarda los insumos en el archivo JSON
        
        Convierte todos los insumos a diccionarios y los guarda en insumos.json
        
        Returns:
            True si se guardó correctamente, False en caso contrario
        """
        data = {
            insumo_id: insumo.to_dict()
            for insumo_id, insumo in self.insumos.items()
        }
        return self.json_manager.save("insumos", data)
    
    def agregar(self, insumo: Insumo):
        """
        Crea o edita la ficha de un insumo (catálogo).

        Esta operación define o corrige los datos del insumo. Si el insumo ya
        existe (mismo ID), REEMPLAZA su ficha con los valores dados (nombre,
        unidad, precio y categoría), incluido el stock indicado como
        corrección. El aumento de stock por reposición se hace registrando
        Compras, no aquí.

        Args:
            insumo: Insumo a crear o editar

        Returns:
            ID del insumo
        """
        # Crear nuevo o reemplazar la ficha existente (no suma cantidades)
        self.insumos[insumo.id] = insumo
        self.save()  # Guardar cambios en disco
        return insumo.id

    def aumentar_stock(self, insumo_id: str, cantidad: float,
                       precio_unidad: Optional[float] = None) -> bool:
        """
        Aumenta el stock de un insumo existente (usado por el módulo de Compras).

        Args:
            insumo_id: ID del insumo a reponer
            cantidad: Cantidad a sumar al stock
            precio_unidad: Si se indica, actualiza el precio al de la compra

        Returns:
            True si el insumo existe y se actualizó, False si no existe.
        """
        insumo = self.insumos.get(insumo_id)
        if insumo is None:
            return False
        insumo.cantidad += cantidad
        if precio_unidad is not None:
            insumo.precio_unidad = precio_unidad
        self.save()
        return True
    
    def eliminar(self, insumo_id: str):
        """
        Elimina un insumo del sistema
        
        Args:
            insumo_id: ID del insumo a eliminar
        
        Returns:
            True si se eliminó correctamente, False si no existía
        """
        if insumo_id in self.insumos:
            del self.insumos[insumo_id]
            self.save()  # Guardar cambios en disco
            return True
        return False
    
    def obtener(self, insumo_id: str) -> Optional[Insumo]:
        """
        Obtiene un insumo por su ID
        
        Args:
            insumo_id: ID del insumo a buscar
        
        Returns:
            Objeto Insumo si existe, None en caso contrario
        """
        return self.insumos.get(insumo_id)
    
    def listar(self, categoria: Optional[str] = None) -> List[Insumo]:
        """
        Lista todos los insumos, opcionalmente filtrados por categoría
        
        Args:
            categoria: Si se proporciona, solo retorna insumos de esa categoría
        
        Returns:
            Lista de objetos Insumo
        """
        if categoria:
            # Filtrar por categoría
            return [insumo for insumo in self.insumos.values() 
                   if insumo.categoria == categoria]
        # Retornar todos los insumos
        return list(self.insumos.values())
    
    def obtener_por_categoria(self, categoria: str) -> List[Insumo]:
        """
        Obtiene insumos de una categoría específica
        
        Método de conveniencia que llama a listar() con la categoría
        
        Args:
            categoria: Categoría de insumos a buscar
        
        Returns:
            Lista de insumos de la categoría especificada
        """
        return self.listar(categoria)

