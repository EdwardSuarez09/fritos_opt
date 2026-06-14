# -*- coding: utf-8 -*-
"""
Graficas embebidas en Tkinter con matplotlib
"""
import tkinter as tk
from typing import Dict, List, Optional

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


def _fmt_cop(valor: float) -> str:
    return f"${round(valor):,}".replace(",", ".")


class ChartPanel:
    """Panel reutilizable para mostrar graficas dentro de la app"""

    def __init__(self, parent, theme):
        self.parent = parent
        self.theme = theme
        self.container = tk.Frame(parent, bg=theme.frame)
        self._canvas = None
        self._figure = None

    def pack(self, **kwargs):
        self.container.pack(**kwargs)

    def _aplicar_tema(self, fig: Figure):
        bg = self.theme.frame
        fig.patch.set_facecolor(bg)
        for ax in fig.axes:
            ax.set_facecolor(self.theme.entry)
            ax.tick_params(colors=self.theme.fg, labelsize=8)
            ax.xaxis.label.set_color(self.theme.fg)
            ax.yaxis.label.set_color(self.theme.fg)
            ax.title.set_color(self.theme.fg)
            for spine in ax.spines.values():
                spine.set_color(self.theme.border)
            ax.grid(True, alpha=0.25, color=self.theme.border)

    def _mostrar(self, fig: Figure):
        if self._canvas:
            self._canvas.get_tk_widget().destroy()
        self._figure = fig
        self._aplicar_tema(fig)
        self._canvas = FigureCanvasTkAgg(fig, master=self.container)
        self._canvas.draw()
        self._canvas.get_tk_widget().pack(fill="both", expand=True)

    def mostrar_impacto_ganancia(self, resultados: dict):
        """Barras: impacto en ganancia por producto"""
        impactos = resultados.get("impacto_ganancias", {})
        if not impactos:
            self._mostrar_vacio("Sin productos afectados para graficar")
            return

        nombres = []
        valores = []
        for item in impactos.values():
            nombres.append(item["nombre"][:18])
            valores.append(item["impacto"])

        fig, ax = plt.subplots(figsize=(6, max(2.5, len(nombres) * 0.45)))
        colores = [self.theme.error if v < 0 else self.theme.success for v in valores]
        y_pos = range(len(nombres))
        ax.barh(list(y_pos), valores, color=colores, alpha=0.85)
        ax.set_yticks(list(y_pos))
        ax.set_yticklabels(nombres, fontsize=8)
        ax.axvline(0, color=self.theme.fg, linewidth=0.8, alpha=0.5)
        ax.set_xlabel("Cambio ganancia/unidad (COP)")
        insumo = resultados.get("insumo", "insumo")
        ax.set_title(f"Impacto en ganancia: {insumo}", fontsize=10, pad=8)
        fig.tight_layout()
        self._mostrar(fig)
        plt.close(fig)

    def mostrar_escenarios(self, escenarios: Dict[str, dict]):
        """Barras agrupadas: costo y ganancia por escenario"""
        orden = ["optimista", "realista", "pesimista"]
        etiquetas = ["Mejor", "Normal", "Peor"]
        costos = []
        ganancias = []
        for key in orden:
            res = escenarios[key]["resultados"]
            costos.append(res.get("impacto_total_costo", 0))
            ganancias.append(res.get("impacto_total_ganancia", 0))

        x = range(len(etiquetas))
        ancho = 0.35
        fig, ax = plt.subplots(figsize=(6, 3.2))
        ax.bar([i - ancho / 2 for i in x], costos, ancho, label="Costo", color=self.theme.warning, alpha=0.9)
        ax.bar([i + ancho / 2 for i in x], ganancias, ancho, label="Ganancia", color=self.theme.info, alpha=0.9)
        ax.set_xticks(list(x))
        ax.set_xticklabels(etiquetas)
        ax.axhline(0, color=self.theme.fg, linewidth=0.8, alpha=0.4)
        ax.set_ylabel("COP por unidad")
        ax.set_title("Comparacion de escenarios", fontsize=10, pad=8)
        ax.legend(facecolor=self.theme.entry, edgecolor=self.theme.border, labelcolor=self.theme.fg, fontsize=8)
        fig.tight_layout()
        self._mostrar(fig)
        plt.close(fig)

    def mostrar_ventas_semana(self, historial):
        """Linea + barras: ventas por semana"""
        semanas = historial.datos.get("ventas", {}).get("por_semana", {})
        if not semanas:
            self._mostrar_vacio("Sin datos de ventas por semana")
            return

        labels = [k.replace("_", " ").title() for k in semanas]
        unidades = [semanas[k].get("unidades", 0) for k in semanas]
        ingresos = [semanas[k].get("ingreso", 0) / 1_000_000 for k in semanas]

        fig, ax1 = plt.subplots(figsize=(6, 3.2))
        ax1.bar(labels, unidades, color=self.theme.select, alpha=0.85, label="Unidades")
        ax1.set_ylabel("Unidades vendidas")
        ax1.tick_params(axis="x", rotation=15)

        ax2 = ax1.twinx()
        ax2.plot(labels, ingresos, color=self.theme.warning, marker="o", linewidth=2, label="Ingreso (M COP)")
        ax2.set_ylabel("Millones COP")
        ax2.tick_params(colors=self.theme.fg, labelsize=8)

        mes = historial.meta.get("mes", "")
        ax1.set_title(f"Ventas por semana ({mes})", fontsize=10, pad=8)
        fig.tight_layout()
        self._mostrar(fig)
        plt.close(fig)

    def mostrar_top_productos(self, historial, n: int = 6):
        """Barras horizontales: productos mas vendidos"""
        tops = historial.top_productos(n)
        if not tops:
            self._mostrar_vacio("Sin datos de productos")
            return

        nombres = [t[0][:20] for t in tops]
        unidades = [t[1]["unidades_vendidas"] for t in tops]

        fig, ax = plt.subplots(figsize=(6, max(2.5, len(nombres) * 0.4)))
        y_pos = range(len(nombres))
        ax.barh(list(y_pos), unidades, color=self.theme.success, alpha=0.85)
        ax.set_yticks(list(y_pos))
        ax.set_yticklabels(nombres, fontsize=8)
        ax.set_xlabel("Unidades vendidas")
        mes = historial.meta.get("mes", "")
        ax.set_title(f"Top productos - {mes}", fontsize=10, pad=8)
        fig.tight_layout()
        self._mostrar(fig)
        plt.close(fig)

    def mostrar_variacion_insumos(self, historial, n: int = 6):
        """Barras: variacion % de insumos"""
        tops = historial.insumos_mas_volatiles(n)
        if not tops:
            self._mostrar_vacio("Sin datos de variacion de precios")
            return

        nombres = [t[0][:16] for t in tops]
        variaciones = [t[1]["variacion_pct"] for t in tops]

        fig, ax = plt.subplots(figsize=(6, max(2.5, len(nombres) * 0.4)))
        y_pos = range(len(nombres))
        ax.barh(list(y_pos), variaciones, color=self.theme.error, alpha=0.85)
        ax.set_yticks(list(y_pos))
        ax.set_yticklabels(nombres, fontsize=8)
        ax.set_xlabel("Variacion de precio (%)")
        mes = historial.meta.get("mes", "")
        ax.set_title(f"Insumos mas volatiles - {mes}", fontsize=10, pad=8)
        fig.tight_layout()
        self._mostrar(fig)
        plt.close(fig)

    def mostrar_resumen_financiero(self, historial):
        """Torta o barras: ingreso vs gasto vs ganancia"""
        resumen = historial.ventas_mes()
        ingreso = resumen.get("ingreso_bruto", 0)
        gasto = historial.total_gastado_mes()
        ganancia = max(resumen.get("ganancia_estimada", 0), 0)

        fig, axes = plt.subplots(1, 2, figsize=(7, 3))
        mes = historial.meta.get("mes", "")

        axes[0].bar(
            ["Ingreso", "Gasto", "Ganancia"],
            [ingreso / 1e6, gasto / 1e6, ganancia / 1e6],
            color=[self.theme.info, self.theme.warning, self.theme.success],
            alpha=0.9,
        )
        axes[0].set_ylabel("Millones COP")
        axes[0].set_title(f"Resumen financiero ({mes})", fontsize=9)
        axes[0].tick_params(axis="x", rotation=12)

        if ingreso > 0:
            axes[1].pie(
                [gasto, max(ganancia, 0.01)],
                labels=["Gastos", "Ganancia"],
                autopct="%1.0f%%",
                colors=[self.theme.warning, self.theme.success],
                textprops={"color": self.theme.fg, "fontsize": 8},
            )
            axes[1].set_title("Distribucion ingreso", fontsize=9)
        else:
            axes[1].text(0.5, 0.5, "Sin ingresos", ha="center", va="center", color=self.theme.fg)
            axes[1].set_axis_off()

        fig.tight_layout()
        self._mostrar(fig)
        plt.close(fig)

    def mostrar_sobrantes(self, sobrantes: Dict[str, dict], n: int = 10):
        """Barras horizontales: sobrante estimado por insumo"""
        items = [d for d in sobrantes.values() if d.get("consumido", 0) > 0 or d.get("stock", 0) > 0]
        if not items:
            self._mostrar_vacio("Sin datos para estimar sobrantes")
            return

        # Mostrar los insumos con mayor consumo primero
        items = sorted(items, key=lambda d: d.get("consumido", 0), reverse=True)[:n]
        nombres = [d["nombre"][:16] for d in items]
        sobrante = [d["sobrante"] for d in items]
        consumido = [d["consumido"] for d in items]

        fig, ax = plt.subplots(figsize=(6, max(2.5, len(nombres) * 0.45)))
        y_pos = list(range(len(nombres)))
        ax.barh([y + 0.2 for y in y_pos], consumido, height=0.4,
                color=self.theme.warning, alpha=0.9, label="Consumido")
        colores = [self.theme.error if v < 0 else self.theme.success for v in sobrante]
        ax.barh([y - 0.2 for y in y_pos], sobrante, height=0.4,
                color=colores, alpha=0.9, label="Sobrante")
        ax.axvline(0, color=self.theme.fg, linewidth=0.8, alpha=0.5)
        ax.set_yticks(y_pos)
        ax.set_yticklabels(nombres, fontsize=8)
        ax.set_xlabel("Cantidad (unidades del insumo)")
        ax.set_title("Consumo vs sobrante estimado", fontsize=10, pad=8)
        ax.legend(facecolor=self.theme.entry, edgecolor=self.theme.border,
                  labelcolor=self.theme.fg, fontsize=8)
        fig.tight_layout()
        self._mostrar(fig)
        plt.close(fig)

    def _mostrar_vacio(self, mensaje: str):
        fig, ax = plt.subplots(figsize=(6, 2.5))
        ax.text(0.5, 0.5, mensaje, ha="center", va="center", color=self.theme.fg, fontsize=10)
        ax.set_axis_off()
        self._mostrar(fig)
        plt.close(fig)
