"""
Carga el historial operativo de compras y ventas desde historial_mensual.json
en data/compras.json y data/ventas.json (sin modificar stock de insumos).
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

FECHAS_COMPRA = {
    "semana_1": "2026-05-04",
    "semana_2": "2026-05-11",
    "semana_3": "2026-05-18",
    "semana_4": "2026-05-25",
}

FECHAS_VENTA = {
    "semana_1": "2026-05-05",
    "semana_2": "2026-05-12",
    "semana_3": "2026-05-17",
    "semana_4": "2026-05-24",
}

UNIDADES_SEMANA = [720, 810, 920, 800]
TOTAL_MES = 3450


def cargar_json(nombre: str) -> dict:
    with open(DATA / f"{nombre}.json", encoding="utf-8") as f:
        return json.load(f)


def guardar_json(nombre: str, data: dict):
    with open(DATA / f"{nombre}.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def nombres_insumos(insumos: dict) -> dict:
    return {k: v.get("nombre", k.replace("_", " ")) for k, v in insumos.items()}


def nombres_productos(productos: dict) -> dict:
    return {k: v.get("nombre", k.replace("_", " ")) for k, v in productos.items()}


def generar_compras(historial: dict, insumos: dict) -> list:
    compras = []
    nombres = nombres_insumos(insumos)
    for semana, datos in historial.get("compras", {}).items():
        fecha = FECHAS_COMPRA.get(semana, datos.get("fecha_inicio", "2026-05-01"))
        for idx, item in enumerate(datos.get("detalle", [])):
            insumo_id = item["insumo_id"]
            cantidad = item["cantidad"]
            precio = item["precio_unidad"]
            compras.append({
                "id": f"{insumo_id}_{fecha}_{idx}",
                "insumo_id": insumo_id,
                "nombre": nombres.get(insumo_id, insumo_id.replace("_", " ")),
                "cantidad": cantidad,
                "unidad": item.get("unidad", "unidad"),
                "precio_unidad": precio,
                "total": round(cantidad * precio, 2),
                "fecha": fecha,
            })
    compras.sort(key=lambda c: (c["fecha"], c["insumo_id"]))
    return compras


def generar_ventas(historial: dict, productos: dict) -> list:
    ventas = []
    nombres = nombres_productos(productos)
    por_producto = historial.get("ventas", {}).get("por_producto", {})
    semanas = list(FECHAS_VENTA.keys())

    for producto_id, info in por_producto.items():
        total = info["unidades_vendidas"]
        precio = info.get("precio_promedio") or productos.get(producto_id, {}).get("precio_venta", 0)
        nombre = nombres.get(producto_id, producto_id.replace("_", " "))
        repartido = 0
        for i, semana in enumerate(semanas):
            if i < len(semanas) - 1:
                cantidad = round(total * UNIDADES_SEMANA[i] / TOTAL_MES)
            else:
                cantidad = total - repartido
            repartido += cantidad
            if cantidad <= 0:
                continue
            fecha = FECHAS_VENTA[semana]
            ventas.append({
                "id": f"{producto_id}_{fecha}",
                "producto_id": producto_id,
                "nombre": nombre,
                "cantidad": int(cantidad),
                "precio_unitario": precio,
                "total": round(cantidad * precio, 2),
                "fecha": fecha,
            })

    ventas.sort(key=lambda v: (v["fecha"], v["producto_id"]))
    return ventas


def main():
    historial = cargar_json("historial_mensual")
    insumos = cargar_json("insumos")
    productos = cargar_json("productos")

    compras = generar_compras(historial, insumos)
    ventas = generar_ventas(historial, productos)

    guardar_json("compras", {"compras": compras})
    guardar_json("ventas", {"ventas": ventas})

    print(f"Compras registradas: {len(compras)}")
    print(f"Ventas registradas: {len(ventas)}")
    print(f"Total gastado (compras): ${sum(c['total'] for c in compras):,.0f} COP")
    print(f"Total ingresos (ventas): ${sum(v['total'] for v in ventas):,.0f} COP")
    print(f"Unidades vendidas: {sum(v['cantidad'] for v in ventas)}")


if __name__ == "__main__":
    main()
