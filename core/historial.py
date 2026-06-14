"""
Consulta del historial mensual de compras y ventas
"""
from typing import Dict, List, Optional, Tuple
from core.json_manager import JSONManager


class HistorialMensual:
    """Carga y consulta datos historicos de un mes de operacion"""

    def __init__(self):
        self.datos = JSONManager().load("historial_mensual", {})
        self._nombres_insumos: Dict[str, str] = {}

    def set_nombres_insumos(self, insumos_manager):
        """Mapea insumo_id a nombre legible desde el inventario actual"""
        self._nombres_insumos = {
            i.id: i.nombre for i in insumos_manager.listar()
        }

    def set_nombres_productos(self, productos_manager):
        """Mapea producto_id a nombre legible"""
        self._nombres_productos = {
            p.id: p.nombre for p in productos_manager.listar()
        }

    @property
    def meta(self) -> dict:
        return self.datos.get("meta", {})

    def insumo_mas_volatil(self) -> Optional[Tuple[str, dict]]:
        variaciones = self.datos.get("variacion_precios", {})
        if not variaciones:
            return None
        mejor_id = max(variaciones, key=lambda k: variaciones[k].get("variacion_pct", 0))
        nombre = self._nombres_insumos.get(mejor_id, mejor_id.replace("_", " "))
        return nombre, variaciones[mejor_id]

    def producto_mas_vendido(self) -> Optional[Tuple[str, dict]]:
        ventas = self.datos.get("ventas", {}).get("por_producto", {})
        if not ventas:
            return None
        mejor_id = max(ventas, key=lambda k: ventas[k].get("unidades_vendidas", 0))
        nombre = getattr(self, "_nombres_productos", {}).get(mejor_id, mejor_id.replace("_", " "))
        return nombre, ventas[mejor_id]

    def ventas_mes(self) -> dict:
        return self.datos.get("ventas", {}).get("resumen_mes", {})

    def ventas_producto(self, producto_id: str) -> int:
        prod = self.datos.get("ventas", {}).get("por_producto", {}).get(producto_id, {})
        return prod.get("unidades_vendidas", 0)

    def precio_historico_insumo(self, insumo_id: str) -> Optional[dict]:
        return self.datos.get("variacion_precios", {}).get(insumo_id)

    def variacion_precios(self) -> Dict[str, dict]:
        return self.datos.get("variacion_precios", {})

    def compras_semana(self, semana: str) -> dict:
        return self.datos.get("compras", {}).get(semana, {})

    def total_gastado_mes(self) -> float:
        compras = self.datos.get("compras", {})
        return sum(s.get("total_gastado", 0) for s in compras.values())

    def producto_menos_vendido(self) -> Optional[Tuple[str, dict]]:
        ventas = self.datos.get("ventas", {}).get("por_producto", {})
        if not ventas:
            return None
        peor_id = min(ventas, key=lambda k: ventas[k].get("unidades_vendidas", 0))
        nombre = getattr(self, "_nombres_productos", {}).get(peor_id, peor_id.replace("_", " "))
        return nombre, ventas[peor_id]

    def top_productos(self, n: int = 3) -> List[Tuple[str, dict]]:
        ventas = self.datos.get("ventas", {}).get("por_producto", {})
        ordenados = sorted(
            ventas.items(),
            key=lambda x: x[1].get("unidades_vendidas", 0),
            reverse=True,
        )
        resultado = []
        for prod_id, datos in ordenados[:n]:
            nombre = getattr(self, "_nombres_productos", {}).get(prod_id, prod_id.replace("_", " "))
            resultado.append((nombre, datos))
        return resultado

    def semana_mejor_ventas(self) -> Optional[Tuple[str, dict]]:
        semanas = self.datos.get("ventas", {}).get("por_semana", {})
        if not semanas:
            return None
        mejor = max(semanas, key=lambda k: semanas[k].get("ingreso", 0))
        return mejor.replace("_", " ").title(), semanas[mejor]

    def semana_mayor_gasto(self) -> Optional[Tuple[str, dict]]:
        compras = self.datos.get("compras", {})
        if not compras:
            return None
        peor = max(compras, key=lambda k: compras[k].get("total_gastado", 0))
        return peor.replace("_", " ").title(), compras[peor]

    def ventas_por_producto_nombre(self, producto_id: str) -> Optional[dict]:
        return self.datos.get("ventas", {}).get("por_producto", {}).get(producto_id)

    def insumos_mas_volatiles(self, n: int = 3) -> List[Tuple[str, dict]]:
        variaciones = self.datos.get("variacion_precios", {})
        ordenados = sorted(
            variaciones.items(),
            key=lambda x: x[1].get("variacion_pct", 0),
            reverse=True,
        )
        resultado = []
        for ins_id, datos in ordenados[:n]:
            nombre = self._nombres_insumos.get(ins_id, ins_id.replace("_", " "))
            resultado.append((nombre, datos))
        return resultado
