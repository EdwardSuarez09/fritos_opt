"""
Cálculo automático de costos unitarios

Este módulo calcula los costos unitarios de los productos considerando
todos los insumos necesarios: masa, rellenos, aceite, salsas, empaques, etc.
"""
from core.insumos import InsumoManager
from core.masas import MasaManager
from core.productos import ProductoManager
from typing import Dict, Optional

class CalculadorCostos:
    """
    Calcula costos unitarios de productos
    
    Esta clase determina el costo total de producción de una unidad de cada
    producto, sumando todos los componentes: masa, rellenos, aceite, empaques, etc.
    """
    
    def __init__(self, insumo_manager: InsumoManager, 
                 masa_manager: MasaManager, 
                 producto_manager: ProductoManager):
        """
        Inicializa el calculador de costos
        
        Args:
            insumo_manager: Gestor de insumos del negocio
            masa_manager: Gestor de lotes de masa
            producto_manager: Gestor de productos del negocio
        """
        self.insumo_manager = insumo_manager
        self.masa_manager = masa_manager
        self.producto_manager = producto_manager
    
    def calcular_costo_producto(self, producto_id: str) -> float:
        """
        Calcula el costo unitario total de un producto
        
        El costo total se compone de:
        1. Costo de masa equivalente (calculado desde el lote de masa)
        2. Costo de rellenos e insumos extra (especificados en el producto)
        3. Costo de aceite (estimado: 0.1 unidades por producto)
        4. Costo de empaques y servilletas (promedio de insumos de categoría "Otros")
        
        Args:
            producto_id: ID del producto cuyo costo se desea calcular
        
        Returns:
            Costo unitario total del producto en unidades monetarias
        """
        producto = self.producto_manager.obtener(producto_id)
        if not producto:
            return 0.0
        
        costo_total = 0.0
        
        # 1. Costo de masa equivalente
        # Si el producto usa una masa, calculamos su costo por unidad equivalente
        # El costo se distribuye entre todos los productos que se pueden hacer con ese lote
        if producto.masa_id:
            masa = self.masa_manager.obtener(producto.masa_id)
            if masa:
                # Obtiene el costo de masa por unidad de producto
                costo_masa_unidad = masa.costo_por_unidad_equivalente(self.insumo_manager)
                costo_total += costo_masa_unidad
        
        # 2. Costo de insumos extra (rellenos, salsas, etc.)
        # Estos son insumos adicionales específicos del producto
        # El diccionario insumos_extra contiene {insumo_id: cantidad_porciones}
        for insumo_id, porciones in producto.insumos_extra.items():
            insumo = self.insumo_manager.obtener(insumo_id)
            if insumo:
                # Calcula costo proporcional basado en porciones
                # Asume que 1 porción = 1 unidad del insumo
                costo_insumo = insumo.precio_unidad * porciones
                costo_total += costo_insumo
        
        # 3. Costos adicionales (aceite, empaques, servilletas)
        # Estos se calculan como insumos con categoría específica
        aceites = self.insumo_manager.obtener_por_categoria("Aceite")
        salsas = self.insumo_manager.obtener_por_categoria("Salsas")
        
        # Costo de aceite (estimado por porción)
        # Se asume que cada producto requiere aproximadamente 0.1 unidades de aceite
        if aceites:
            # Promedio de costo de aceite por unidad
            costo_aceite_promedio = sum(a.precio_unidad for a in aceites) / len(aceites)
            # Multiplicar por la cantidad estimada de aceite por producto
            costo_total += costo_aceite_promedio * 0.1  # Estimación: 0.1 unidades de aceite por producto
        
        # Costo de salsas (si aplica)
        # Nota: Si el producto usa salsas específicas, ya están incluidas en insumos_extra
        
        # Costo de empaques (buscar en "Otros" o categoría específica)
        # Busca insumos que contengan "empaque" o "servilleta" en su nombre
        otros = self.insumo_manager.obtener_por_categoria("Otros")
        empaques = [o for o in otros if "empaque" in o.nombre.lower() or "servilleta" in o.nombre.lower()]
        if empaques:
            # Usa el promedio del costo de empaques disponibles
            costo_empaque_promedio = sum(e.precio_unidad for e in empaques) / len(empaques)
            costo_total += costo_empaque_promedio
        
        return costo_total
    
    def calcular_ganancia_producto(self, producto_id: str) -> float:
        """
        Calcula la ganancia unitaria de un producto
        
        La ganancia es la diferencia entre el precio de venta y el costo unitario.
        Esta es la métrica clave para la optimización, ya que el modelo busca
        maximizar la ganancia total.
        
        Args:
            producto_id: ID del producto
        
        Returns:
            Ganancia unitaria (precio_venta - costo_unitario)
        """
        producto = self.producto_manager.obtener(producto_id)
        if not producto:
            return 0.0
        
        costo = self.calcular_costo_producto(producto_id)
        return producto.precio_venta - costo
    
    def obtener_costos_todos_productos(self) -> Dict[str, Dict]:
        """
        Obtiene costos y ganancias de todos los productos
        
        Calcula para cada producto:
        - Costo unitario
        - Ganancia unitaria
        - Margen de ganancia (porcentaje)
        
        Returns:
            Diccionario con {producto_id: {nombre, costo, precio_venta, ganancia, margen}}
        """
        resultados = {}
        for producto in self.producto_manager.listar():
            costo = self.calcular_costo_producto(producto.id)
            ganancia = self.calcular_ganancia_producto(producto.id)
            resultados[producto.id] = {
                "nombre": producto.nombre,
                "costo": costo,
                "precio_venta": producto.precio_venta,
                "ganancia": ganancia,
                # Margen de ganancia como porcentaje del precio de venta
                "margen": (ganancia / producto.precio_venta * 100) if producto.precio_venta > 0 else 0
            }
        return resultados

