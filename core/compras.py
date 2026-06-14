"""
Gestión de compras de insumos

Este módulo permite registrar las compras de insumos (materias primas) que
realiza el negocio. Cada compra queda almacenada con su fecha, cantidad y
precio, y al registrarse incrementa el stock disponible del insumo en el
inventario. Sirve de apoyo al control operativo y a la estimación de
disponibilidad y sobrantes.
"""
from datetime import date
from typing import Dict, List, Optional

from core.json_manager import JSONManager
from core.insumos import Insumo, InsumoManager


class Compra:
    """Representa una compra puntual de un insumo"""

    def __init__(self, insumo_id: str, nombre: str, cantidad: float,
                 unidad: str, precio_unidad: float, fecha: str,
                 id: Optional[str] = None):
        self.insumo_id = insumo_id
        self.nombre = nombre
        self.cantidad = cantidad
        self.unidad = unidad
        self.precio_unidad = precio_unidad
        self.fecha = fecha
        # ID único basado en insumo + fecha + un sufijo incremental opcional
        self.id = id or f"{insumo_id}_{fecha}"

    @property
    def total(self) -> float:
        """Valor total de la compra (cantidad x precio unitario)"""
        return self.cantidad * self.precio_unidad

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "insumo_id": self.insumo_id,
            "nombre": self.nombre,
            "cantidad": self.cantidad,
            "unidad": self.unidad,
            "precio_unidad": self.precio_unidad,
            "total": self.total,
            "fecha": self.fecha,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Compra":
        return cls(
            insumo_id=data["insumo_id"],
            nombre=data.get("nombre", data["insumo_id"]),
            cantidad=data["cantidad"],
            unidad=data.get("unidad", "unidad"),
            precio_unidad=data["precio_unidad"],
            fecha=data.get("fecha", ""),
            id=data.get("id"),
        )


class ComprasManager:
    """
    Gestiona el historial de compras de insumos

    Persiste las compras en data/compras.json. Al registrar una compra,
    actualiza el stock del insumo correspondiente en el inventario y, si el
    precio cambió, actualiza también el precio unitario del insumo.
    """

    def __init__(self, insumo_manager: Optional[InsumoManager] = None):
        self.json_manager = JSONManager()
        self.insumo_manager = insumo_manager
        self.compras: List[Compra] = []
        self.load()

    def load(self):
        data = self.json_manager.load("compras", default={"compras": []})
        self.compras = [Compra.from_dict(c) for c in data.get("compras", [])]

    def save(self) -> bool:
        data = {"compras": [c.to_dict() for c in self.compras]}
        return self.json_manager.save("compras", data)

    def registrar(self, insumo_id: str, cantidad: float, precio_unidad: float,
                  fecha: Optional[str] = None,
                  actualizar_stock: bool = True) -> Optional[Compra]:
        """
        Registra una nueva compra de un insumo existente.

        Args:
            insumo_id: ID del insumo comprado (debe existir en el inventario)
            cantidad: Cantidad comprada
            precio_unidad: Precio pagado por unidad
            fecha: Fecha de la compra (YYYY-MM-DD); hoy por defecto
            actualizar_stock: Si True, suma la cantidad al stock del insumo

        Returns:
            La compra registrada, o None si el insumo no existe.
        """
        fecha = fecha or date.today().isoformat()
        nombre = insumo_id.replace("_", " ")
        unidad = "unidad"

        insumo = None
        if self.insumo_manager:
            insumo = self.insumo_manager.obtener(insumo_id)
            if insumo is None:
                return None
            nombre = insumo.nombre
            unidad = insumo.unidad

        compra = Compra(insumo_id, nombre, cantidad, unidad, precio_unidad, fecha)
        self.compras.append(compra)

        if actualizar_stock and insumo is not None:
            # Suma al stock y actualiza el precio al último de compra
            self.insumo_manager.aumentar_stock(insumo_id, cantidad, precio_unidad)

        self.save()
        return compra

    def eliminar(self, compra_id: str) -> bool:
        for i, c in enumerate(self.compras):
            if c.id == compra_id:
                del self.compras[i]
                self.save()
                return True
        return False

    def listar(self) -> List[Compra]:
        return list(self.compras)

    def total_gastado(self) -> float:
        return sum(c.total for c in self.compras)

    def total_por_insumo(self) -> Dict[str, float]:
        """Total gastado agrupado por insumo"""
        totales: Dict[str, float] = {}
        for c in self.compras:
            totales[c.insumo_id] = totales.get(c.insumo_id, 0.0) + c.total
        return totales

    def cantidad_comprada_por_insumo(self) -> Dict[str, float]:
        """Cantidad total comprada agrupada por insumo (para sobrantes)"""
        cantidades: Dict[str, float] = {}
        for c in self.compras:
            cantidades[c.insumo_id] = cantidades.get(c.insumo_id, 0.0) + c.cantidad
        return cantidades
