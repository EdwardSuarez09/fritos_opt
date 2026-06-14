"""
Gestión de ventas de productos

Este módulo permite registrar las ventas de productos terminados. Lleva un
historial general y por producto, calcula los ingresos y sirve de base para
estimar el consumo de materia prima y los sobrantes de insumos.
"""
from datetime import date
from typing import Dict, List, Optional

from core.json_manager import JSONManager
from core.productos import ProductoManager


class Venta:
    """Representa una venta puntual de un producto"""

    def __init__(self, producto_id: str, nombre: str, cantidad: int,
                 precio_unitario: float, fecha: str, id: Optional[str] = None):
        self.producto_id = producto_id
        self.nombre = nombre
        self.cantidad = cantidad
        self.precio_unitario = precio_unitario
        self.fecha = fecha
        self.id = id or f"{producto_id}_{fecha}"

    @property
    def total(self) -> float:
        """Ingreso total de la venta (cantidad x precio unitario)"""
        return self.cantidad * self.precio_unitario

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "producto_id": self.producto_id,
            "nombre": self.nombre,
            "cantidad": self.cantidad,
            "precio_unitario": self.precio_unitario,
            "total": self.total,
            "fecha": self.fecha,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Venta":
        return cls(
            producto_id=data["producto_id"],
            nombre=data.get("nombre", data["producto_id"]),
            cantidad=data["cantidad"],
            precio_unitario=data["precio_unitario"],
            fecha=data.get("fecha", ""),
            id=data.get("id"),
        )


class VentasManager:
    """
    Gestiona el historial de ventas de productos

    Persiste las ventas en data/ventas.json y ofrece consultas de historial
    general y por producto, además de totales de unidades e ingresos.
    """

    def __init__(self, producto_manager: Optional[ProductoManager] = None):
        self.json_manager = JSONManager()
        self.producto_manager = producto_manager
        self.ventas: List[Venta] = []
        self.load()

    def load(self):
        data = self.json_manager.load("ventas", default={"ventas": []})
        self.ventas = [Venta.from_dict(v) for v in data.get("ventas", [])]

    def save(self) -> bool:
        data = {"ventas": [v.to_dict() for v in self.ventas]}
        return self.json_manager.save("ventas", data)

    def registrar(self, producto_id: str, cantidad: int,
                  precio_unitario: Optional[float] = None,
                  fecha: Optional[str] = None) -> Optional[Venta]:
        """
        Registra una nueva venta de un producto existente.

        Args:
            producto_id: ID del producto vendido (debe existir)
            cantidad: Unidades vendidas
            precio_unitario: Precio de venta; usa el del producto si es None
            fecha: Fecha (YYYY-MM-DD); hoy por defecto

        Returns:
            La venta registrada, o None si el producto no existe.
        """
        fecha = fecha or date.today().isoformat()
        nombre = producto_id.replace("_", " ")

        if self.producto_manager:
            producto = self.producto_manager.obtener(producto_id)
            if producto is None:
                return None
            nombre = producto.nombre
            if precio_unitario is None:
                precio_unitario = producto.precio_venta

        if precio_unitario is None:
            precio_unitario = 0.0

        venta = Venta(producto_id, nombre, cantidad, precio_unitario, fecha)
        self.ventas.append(venta)
        self.save()
        return venta

    def eliminar(self, venta_id: str) -> bool:
        for i, v in enumerate(self.ventas):
            if v.id == venta_id:
                del self.ventas[i]
                self.save()
                return True
        return False

    def listar(self) -> List[Venta]:
        return list(self.ventas)

    def total_ingresos(self) -> float:
        return sum(v.total for v in self.ventas)

    def total_unidades(self) -> int:
        return sum(v.cantidad for v in self.ventas)

    def unidades_por_producto(self) -> Dict[str, int]:
        """Unidades vendidas agrupadas por producto"""
        totales: Dict[str, int] = {}
        for v in self.ventas:
            totales[v.producto_id] = totales.get(v.producto_id, 0) + v.cantidad
        return totales

    def ingresos_por_producto(self) -> Dict[str, float]:
        """Ingresos agrupados por producto"""
        totales: Dict[str, float] = {}
        for v in self.ventas:
            totales[v.producto_id] = totales.get(v.producto_id, 0.0) + v.total
        return totales

    def resumen_por_producto(self) -> Dict[str, dict]:
        """Resumen con unidades e ingresos por producto"""
        resumen: Dict[str, dict] = {}
        for v in self.ventas:
            r = resumen.setdefault(v.producto_id, {
                "nombre": v.nombre, "unidades": 0, "ingreso": 0.0
            })
            r["unidades"] += v.cantidad
            r["ingreso"] += v.total
        return resumen
