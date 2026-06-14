"""
Pantalla de consumo de ingredientes y sobrantes estimados
"""
import tkinter as tk
from tkinter import ttk, messagebox

from core.consumo import ConsumoEstimador
from core.ventas import VentasManager
from core.compras import ComprasManager
from core.historial import HistorialMensual
from ui.charts import ChartPanel


class ConsumoScreen:
    """
    Muestra el consumo estimado de materia prima y los sobrantes aproximados.

    El consumo se calcula a partir de las recetas y las unidades vendidas. Usa
    las ventas registradas en el sistema; si aún no hay ventas registradas,
    utiliza el historial mensual como referencia.
    """

    def __init__(self, parent, inventario, ventas_manager: VentasManager,
                 compras_manager: ComprasManager, theme):
        self.inventario = inventario
        self.ventas_manager = ventas_manager
        self.compras_manager = compras_manager
        self.theme = theme
        self.estimador = ConsumoEstimador(
            inventario.insumos, inventario.masas, inventario.productos
        )
        self.historial = HistorialMensual()

        main_frame = ttk.Frame(parent)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        top = ttk.Frame(main_frame)
        top.pack(fill="x", pady=(0, 10))
        ttk.Label(
            top,
            text="Consumo de ingredientes y disponibilidad aproximada (sobrantes)",
            font=("Segoe UI", 11, "bold"),
        ).pack(side="left")
        ttk.Button(top, text="🔄 Recalcular", command=self.actualizar_datos).pack(side="right")
        self.lbl_fuente = ttk.Label(top, text="")
        self.lbl_fuente.pack(side="right", padx=10)

        # Panel dividido: tabla a la izquierda, grafica a la derecha
        cuerpo = ttk.Frame(main_frame)
        cuerpo.pack(fill="both", expand=True)

        tabla_frame = ttk.LabelFrame(cuerpo, text="📋 Detalle por insumo", padding=10)
        tabla_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))

        columns = ("insumo", "stock", "consumido", "sobrante", "unidad")
        self.tree = ttk.Treeview(tabla_frame, columns=columns, show="headings", height=18)
        encabezados = {
            "insumo": "📦 Insumo", "stock": "📥 Stock", "consumido": "🔥 Consumido",
            "sobrante": "📦 Sobrante", "unidad": "📏 Unidad",
        }
        anchos = {"insumo": 150, "stock": 90, "consumido": 100, "sobrante": 100, "unidad": 70}
        for col in columns:
            self.tree.heading(col, text=encabezados[col])
            anchor = "w" if col == "insumo" else ("center" if col == "unidad" else "e")
            self.tree.column(col, width=anchos[col], anchor=anchor)
        sb = ttk.Scrollbar(tabla_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        # Resaltar insumos con sobrante negativo (faltante)
        self.tree.tag_configure("faltante", foreground=self.theme.error)

        graf_frame = ttk.LabelFrame(cuerpo, text="📊 Consumo vs sobrante", padding=10)
        graf_frame.pack(side="left", fill="both", expand=True, padx=(5, 0))
        self.chart = ChartPanel(graf_frame, theme)
        self.chart.pack(fill="both", expand=True)

        self.actualizar_datos()

    def _obtener_ventas(self):
        """Devuelve {producto_id: unidades} y la fuente usada"""
        registradas = self.ventas_manager.unidades_por_producto()
        if registradas:
            return registradas, "ventas registradas"
        # Fallback: historial mensual
        por_producto = self.historial.datos.get("ventas", {}).get("por_producto", {})
        ventas = {pid: d.get("unidades_vendidas", 0) for pid, d in por_producto.items()}
        return ventas, "historial de mayo (simulado)"

    def actualizar_datos(self):
        ventas, fuente = self._obtener_ventas()
        self.lbl_fuente.config(text=f"Fuente: {fuente}")
        comprado = self.compras_manager.cantidad_comprada_por_insumo()
        sobrantes = self.estimador.estimar_sobrantes(ventas, comprado)

        for item in self.tree.get_children():
            self.tree.delete(item)

        # Ordenar por consumo descendente
        ordenados = sorted(sobrantes.values(), key=lambda d: d["consumido"], reverse=True)
        for d in ordenados:
            tags = ("faltante",) if d["sobrante"] < 0 else ()
            self.tree.insert("", "end", tags=tags, values=(
                d["nombre"],
                f"{d['stock']:,.2f}",
                f"{d['consumido']:,.2f}",
                f"{d['sobrante']:,.2f}",
                d["unidad"],
            ))

        self.chart.mostrar_sobrantes(sobrantes)
