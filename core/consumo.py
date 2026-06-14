"""
Estimación de consumo de ingredientes y sobrantes

A partir de las recetas (masa + insumos extra) y de las unidades vendidas o
producidas, este módulo estima cuánta materia prima se consumió y cuánta queda
disponible de forma aproximada (sobrantes). No realiza control de inventario en
tiempo real; es una estimación de apoyo para la operación diaria.
"""
from typing import Dict, Optional

from core.insumos import InsumoManager
from core.masas import MasaManager
from core.productos import ProductoManager

# Estimaciones de consumo no incluidas en la receta explícita
ACEITE_POR_UNIDAD = 0.1   # unidades de aceite por producto frito
EMPAQUE_POR_UNIDAD = 1.0  # 1 empaque por producto


class ConsumoEstimador:
    """Estima consumo de insumos y sobrantes a partir de ventas y recetas"""

    def __init__(self, insumo_manager: InsumoManager,
                 masa_manager: MasaManager,
                 producto_manager: ProductoManager):
        self.insumo_manager = insumo_manager
        self.masa_manager = masa_manager
        self.producto_manager = producto_manager

    def insumos_por_unidad(self, producto_id: str) -> Dict[str, float]:
        """
        Calcula cuánta cantidad de cada insumo consume UNA unidad del producto.

        Combina la parte proporcional de la masa (repartida según el rendimiento
        del lote) con los insumos extra de la receta, más el aceite y el empaque
        estimados por unidad.
        """
        producto = self.producto_manager.obtener(producto_id)
        if not producto:
            return {}

        consumo: Dict[str, float] = {}

        # 1. Parte proporcional de la masa
        if producto.masa_id:
            masa = self.masa_manager.obtener(producto.masa_id)
            if masa:
                total_rend = sum(masa.rendimiento.values())
                if total_rend > 0:
                    for insumo_id, cantidad in masa.insumos_usados.items():
                        consumo[insumo_id] = consumo.get(insumo_id, 0.0) + cantidad / total_rend

        # 2. Insumos extra de la receta (1 porción = 1 unidad del insumo)
        for insumo_id, porciones in producto.insumos_extra.items():
            consumo[insumo_id] = consumo.get(insumo_id, 0.0) + porciones

        # 3. Aceite y empaque estimados por unidad
        if self.insumo_manager.obtener("aceite"):
            consumo["aceite"] = consumo.get("aceite", 0.0) + ACEITE_POR_UNIDAD
        if self.insumo_manager.obtener("empaque_papel"):
            consumo["empaque_papel"] = consumo.get("empaque_papel", 0.0) + EMPAQUE_POR_UNIDAD

        return consumo

    def estimar_consumo(self, ventas: Dict[str, int]) -> Dict[str, float]:
        """
        Estima el consumo total de cada insumo dadas las unidades vendidas.

        Args:
            ventas: Diccionario {producto_id: unidades_vendidas}

        Returns:
            Diccionario {insumo_id: cantidad_total_consumida}
        """
        total: Dict[str, float] = {}
        for producto_id, unidades in ventas.items():
            if not unidades:
                continue
            por_unidad = self.insumos_por_unidad(producto_id)
            for insumo_id, cantidad in por_unidad.items():
                total[insumo_id] = total.get(insumo_id, 0.0) + cantidad * unidades
        return total

    def estimar_sobrantes(self, ventas: Dict[str, int],
                          comprado: Optional[Dict[str, float]] = None) -> Dict[str, dict]:
        """
        Estima el sobrante (disponibilidad aproximada) de cada insumo.

        Sobrante = stock actual del insumo - consumo estimado por las ventas.
        El stock actual ya refleja las compras registradas, por lo que no se
        suma de nuevo (se muestra como dato informativo).

        Args:
            ventas: Diccionario {producto_id: unidades_vendidas}
            comprado: Opcional {insumo_id: cantidad_comprada} solo informativo

        Returns:
            {insumo_id: {nombre, unidad, stock, comprado, consumido, sobrante}}
        """
        comprado = comprado or {}
        consumo = self.estimar_consumo(ventas)
        resultado: Dict[str, dict] = {}

        for insumo in self.insumo_manager.listar():
            consumido = consumo.get(insumo.id, 0.0)
            sobrante = insumo.cantidad - consumido
            resultado[insumo.id] = {
                "nombre": insumo.nombre,
                "unidad": insumo.unidad,
                "stock": insumo.cantidad,
                "comprado": comprado.get(insumo.id, 0.0),
                "consumido": consumido,
                "sobrante": sobrante,
            }
        return resultado
