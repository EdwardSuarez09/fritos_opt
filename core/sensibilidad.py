"""
Análisis de sensibilidad para el sistema de optimización

Este módulo permite analizar cómo cambios en los precios de insumos
afectan los costos, ganancias y la optimización de producción.
"""
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from typing import Dict, List, Tuple, Optional
from core.insumos import InsumoManager
from core.masas import MasaManager
from core.productos import ProductoManager
from core.costos import CalculadorCostos
from core.optimizador import Optimizador

class AnalizadorSensibilidad:
    """
    Analiza la sensibilidad del sistema ante cambios en precios de insumos
    """
    
    def __init__(self, insumo_manager: InsumoManager,
                 masa_manager: MasaManager,
                 producto_manager: ProductoManager,
                 calculador_costos: CalculadorCostos):
        """
        Inicializa el analizador de sensibilidad
        
        Args:
            insumo_manager: Gestor de insumos
            masa_manager: Gestor de masas
            producto_manager: Gestor de productos
            calculador_costos: Calculador de costos
        """
        self.insumo_manager = insumo_manager
        self.masa_manager = masa_manager
        self.producto_manager = producto_manager
        self.calculador_costos = calculador_costos
    
    def analizar_cambio_precio_insumo(self, insumo_id: str, 
                                      nuevo_precio: float,
                                      precio_original: Optional[float] = None) -> Dict:
        """
        Analiza el impacto de cambiar el precio de un insumo
        
        Args:
            insumo_id: ID del insumo a modificar
            nuevo_precio: Nuevo precio por unidad
            precio_original: Precio original (si no se proporciona, se obtiene del insumo)
        
        Returns:
            Diccionario con:
            - impacto_costos: Cambio en costos por producto
            - impacto_ganancias: Cambio en ganancias por producto
            - productos_afectados: Lista de productos afectados
            - cambio_porcentual: Cambio porcentual en costos/ganancias
        """
        insumo = self.insumo_manager.obtener(insumo_id)
        if not insumo:
            return {}
        
        if precio_original is None:
            precio_original = insumo.precio_unidad
        
        cambio_porcentual_precio = ((nuevo_precio - precio_original) / precio_original * 100) if precio_original > 0 else 0
        
        # Calcular costos ORIGINALES antes de cambiar el precio
        costos_originales = {}
        ganancias_originales = {}
        for producto in self.producto_manager.listar():
            costos_originales[producto.id] = self.calculador_costos.calcular_costo_producto(producto.id)
            ganancias_originales[producto.id] = self.calculador_costos.calcular_ganancia_producto(producto.id)
        
        # Guardar precio original temporalmente y cambiar al nuevo precio
        precio_original_temp = insumo.precio_unidad
        insumo.precio_unidad = nuevo_precio
        
        # Calcular costos y ganancias con el nuevo precio
        resultados = {
            "insumo": insumo.nombre,
            "precio_original": precio_original,
            "nuevo_precio": nuevo_precio,
            "cambio_porcentual_precio": cambio_porcentual_precio,
            "productos_afectados": [],
            "impacto_costos": {},
            "impacto_ganancias": {},
            "impacto_total_costo": 0,
            "impacto_total_ganancia": 0
        }
        
        # Calcular impacto por producto
        productos_afectados = []
        for producto in self.producto_manager.listar():
            # Usar costos originales ya calculados
            costo_original = costos_originales[producto.id]
            ganancia_original = ganancias_originales[producto.id]
            
            # Verificar si el producto usa este insumo
            usa_insumo = False
            insumo = self.insumo_manager.obtener(insumo_id)
            
            if not insumo:
                continue  # Si el insumo no existe, saltar este producto
            
            # Verificar en masa
            if producto.masa_id:
                masa = self.masa_manager.obtener(producto.masa_id)
                if masa:
                    # Verificar si el insumo está en los insumos usados de la masa
                    if insumo_id in masa.insumos_usados:
                        usa_insumo = True
            
            # Verificar en insumos extra (comparación directa de IDs)
            if insumo_id in producto.insumos_extra:
                usa_insumo = True
            
            # También verificar si el insumo se usa indirectamente (en aceite, empaques, etc.)
            # Verificar si es aceite
            if insumo.categoria == "Aceite":
                usa_insumo = True  # Todos los productos usan aceite
            
            # Verificar si es empaque
            if "empaque" in insumo.nombre.lower() or "servilleta" in insumo.nombre.lower():
                usa_insumo = True  # Todos los productos usan empaques
            
            if usa_insumo:
                # Recalcular costos con nuevo precio usando el método auxiliar
                costo_nuevo = self._recalcular_costo_producto(producto.id)
                ganancia_nueva = producto.precio_venta - costo_nuevo
                
                impacto_costo = costo_nuevo - costo_original
                impacto_ganancia = ganancia_nueva - ganancia_original
                
                # Agregar siempre que use el insumo
                resultados["productos_afectados"].append(producto.nombre)
                resultados["impacto_costos"][producto.id] = {
                    "nombre": producto.nombre,
                    "costo_original": costo_original,
                    "costo_nuevo": costo_nuevo,
                    "impacto": impacto_costo,
                    "cambio_porcentual": (impacto_costo / costo_original * 100) if costo_original > 0 else 0
                }
                resultados["impacto_ganancias"][producto.id] = {
                    "nombre": producto.nombre,
                    "ganancia_original": ganancia_original,
                    "ganancia_nueva": ganancia_nueva,
                    "impacto": impacto_ganancia,
                    "cambio_porcentual": (impacto_ganancia / ganancia_original * 100) if ganancia_original != 0 else 0
                }
                
                resultados["impacto_total_costo"] += impacto_costo
                resultados["impacto_total_ganancia"] += impacto_ganancia
        
        # Restaurar precio original
        insumo.precio_unidad = precio_original_temp
        
        return resultados
    
    def _recalcular_costo_producto(self, producto_id: str) -> float:
        """
        Recalcula el costo de un producto usando los precios actuales de los insumos
        (método auxiliar para análisis de sensibilidad)
        
        IMPORTANTE: Este método usa directamente los precios de los objetos insumo,
        que ya están actualizados con el nuevo precio.
        """
        producto = self.producto_manager.obtener(producto_id)
        if not producto:
            return 0.0
        
        costo_total = 0.0
        
        # 1. Costo de masa equivalente
        if producto.masa_id:
            masa = self.masa_manager.obtener(producto.masa_id)
            if masa:
                # Recalcular costo de masa con precios actuales
                # Calcular costo del lote manualmente para usar precios actualizados
                costo_masa_lote = 0.0
                for insumo_id_masa, cantidad_usada in masa.insumos_usados.items():
                    insumo_masa = self.insumo_manager.obtener(insumo_id_masa)
                    if insumo_masa:
                        # Calcular costo directamente: cantidad_usada × precio_unidad
                        # El precio_unidad ya está actualizado en el objeto insumo
                        costo_insumo_en_lote = cantidad_usada * insumo_masa.precio_unidad
                        costo_masa_lote += costo_insumo_en_lote
                
                total_unidades = sum(masa.rendimiento.values())
                if total_unidades > 0:
                    costo_masa_unidad = costo_masa_lote / total_unidades
                    costo_total += costo_masa_unidad
        
        # 2. Costo de insumos extra
        # IMPORTANTE: Aquí se usa el precio_unidad que ya está actualizado
        for insumo_id, porciones in producto.insumos_extra.items():
            insumo = self.insumo_manager.obtener(insumo_id)
            if insumo:
                # El precio_unidad del objeto insumo ya está actualizado
                costo_insumo_extra = insumo.precio_unidad * porciones
                costo_total += costo_insumo_extra
        
        # 3. Costos adicionales (aceite, empaques)
        # Estos también usan precios actualizados
        aceites = self.insumo_manager.obtener_por_categoria("Aceite")
        if aceites:
            # Sumar precios actualizados
            costo_aceite_promedio = sum(a.precio_unidad for a in aceites) / len(aceites)
            costo_total += costo_aceite_promedio * 0.1
        
        otros = self.insumo_manager.obtener_por_categoria("Otros")
        empaques = [o for o in otros if "empaque" in o.nombre.lower() or "servilleta" in o.nombre.lower()]
        if empaques:
            # Sumar precios actualizados
            costo_empaque_promedio = sum(e.precio_unidad for e in empaques) / len(empaques)
            costo_total += costo_empaque_promedio
        
        return costo_total
    
    def analizar_escenario(self, cambios_precios: Dict[str, float]) -> Dict:
        """
        Analiza un escenario con múltiples cambios de precios simultáneos
        
        Args:
            cambios_precios: Diccionario {insumo_id: nuevo_precio}
        
        Returns:
            Diccionario con impacto total del escenario
        """
        # Guardar precios originales y costos base antes de aplicar cambios
        precios_originales = {}
        costos_originales = {}
        ganancias_originales = {}
        for producto in self.producto_manager.listar():
            costos_originales[producto.id] = self.calculador_costos.calcular_costo_producto(producto.id)
            ganancias_originales[producto.id] = self.calculador_costos.calcular_ganancia_producto(producto.id)

        for insumo_id, nuevo_precio in cambios_precios.items():
            insumo = self.insumo_manager.obtener(insumo_id)
            if insumo:
                precios_originales[insumo_id] = insumo.precio_unidad
                insumo.precio_unidad = nuevo_precio

        # Calcular impacto total
        resultados = {
            "cambios_aplicados": len(cambios_precios),
            "productos_afectados": [],
            "impacto_costos": {},
            "impacto_ganancias": {},
            "impacto_total_costo": 0,
            "impacto_total_ganancia": 0
        }
        
        for producto in self.producto_manager.listar():
            costo_original = costos_originales[producto.id]
            ganancia_original = ganancias_originales[producto.id]

            # Recalcular con nuevos precios
            costo_nuevo = self._recalcular_costo_producto(producto.id)
            ganancia_nueva = producto.precio_venta - costo_nuevo
            
            if abs(costo_nuevo - costo_original) > 0.01:  # Solo si hay cambio significativo
                impacto_costo = costo_nuevo - costo_original
                impacto_ganancia = ganancia_nueva - ganancia_original
                
                resultados["productos_afectados"].append(producto.nombre)
                resultados["impacto_costos"][producto.id] = {
                    "nombre": producto.nombre,
                    "costo_original": costo_original,
                    "costo_nuevo": costo_nuevo,
                    "impacto": impacto_costo
                }
                resultados["impacto_ganancias"][producto.id] = {
                    "nombre": producto.nombre,
                    "ganancia_original": ganancia_original,
                    "ganancia_nueva": ganancia_nueva,
                    "impacto": impacto_ganancia
                }
                
                resultados["impacto_total_costo"] += impacto_costo
                resultados["impacto_total_ganancia"] += impacto_ganancia
        
        # Restaurar precios originales
        for insumo_id, precio_original in precios_originales.items():
            insumo = self.insumo_manager.obtener(insumo_id)
            if insumo:
                insumo.precio_unidad = precio_original
        
        return resultados
    
    def generar_escenarios(self, porcentaje_cambio: float = 10.0) -> Dict[str, Dict]:
        """
        Genera escenarios optimista, realista y pesimista
        
        Args:
            porcentaje_cambio: Porcentaje de cambio para los escenarios (default: 10%)
        
        Returns:
            Diccionario con tres escenarios:
            - optimista: Precios bajan
            - realista: Precios se mantienen
            - pesimista: Precios suben
        """
        escenarios = {}
        
        # Escenario Optimista: precios bajan
        cambios_optimista = {}
        for insumo in self.insumo_manager.listar():
            nuevo_precio = insumo.precio_unidad * (1 - porcentaje_cambio / 100)
            cambios_optimista[insumo.id] = nuevo_precio
        
        escenarios["optimista"] = {
            "nombre": "Optimista",
            "descripcion": f"Precios bajan {porcentaje_cambio}%",
            "resultados": self.analizar_escenario(cambios_optimista)
        }
        
        # Escenario Realista: precios se mantienen
        escenarios["realista"] = {
            "nombre": "Realista",
            "descripcion": "Precios se mantienen",
            "resultados": {
                "cambios_aplicados": 0,
                "productos_afectados": [],
                "impacto_costos": {},
                "impacto_ganancias": {},
                "impacto_total_costo": 0,
                "impacto_total_ganancia": 0
            }
        }
        
        # Escenario Pesimista: precios suben
        cambios_pesimista = {}
        for insumo in self.insumo_manager.listar():
            nuevo_precio = insumo.precio_unidad * (1 + porcentaje_cambio / 100)
            cambios_pesimista[insumo.id] = nuevo_precio
        
        escenarios["pesimista"] = {
            "nombre": "Pesimista",
            "descripcion": f"Precios suben {porcentaje_cambio}%",
            "resultados": self.analizar_escenario(cambios_pesimista)
        }
        
        return escenarios


if __name__ == "__main__":
    import runpy
    print("Este archivo es un modulo interno. Abriendo main.py...")
    runpy.run_path(os.path.join(_ROOT, "main.py"), run_name="__main__")

