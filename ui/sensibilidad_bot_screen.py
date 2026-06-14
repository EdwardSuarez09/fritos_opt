# -*- coding: utf-8 -*-
"""
Pantalla de chat: Bot hibrido de analisis de sensibilidad
"""
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk

from core.bot_sensibilidad import BotSensibilidad, normalizar
from core.sensibilidad import AnalizadorSensibilidad
from core.inventario import Inventario
from core.costos import CalculadorCostos
from ui.charts import ChartPanel


class SensibilidadBotScreen:
    """Interfaz conversacional para analisis de sensibilidad"""

    def __init__(self, parent, inventario: Inventario, calculador_costos: CalculadorCostos, theme,
                 optimizador=None):
        self.theme = theme
        self.esperando_continuar = False

        analizador = AnalizadorSensibilidad(
            inventario.insumos,
            inventario.masas,
            inventario.productos,
            calculador_costos,
        )
        self.bot = BotSensibilidad(
            inventario.insumos,
            inventario.productos,
            calculador_costos,
            analizador,
            optimizador,
        )
        self.analizador = analizador

        marco = ttk.Frame(parent, padding=14)
        marco.pack(fill="both", expand=True)

        titulo = ttk.Label(
            marco,
            text="Asistente de Sensibilidad",
            font=("Segoe UI", 16, "bold"),
        )
        titulo.pack(anchor="w")

        descripcion = ttk.Label(
            marco,
            text=(
                "Pregunta en lenguaje natural. Montos en pesos colombianos (COP). "
                "Abajo veras graficas del historial y del ultimo analisis."
            ),
            font=("Segoe UI", 9),
            wraplength=800,
            justify="left",
        )
        descripcion.pack(anchor="w", pady=(2, 8))

        contenido = ttk.PanedWindow(marco, orient=tk.VERTICAL)
        contenido.pack(fill="both", expand=True)

        panel_chat = ttk.Frame(contenido)
        contenido.add(panel_chat, weight=3)

        self.chat = scrolledtext.ScrolledText(
            panel_chat,
            wrap="word",
            height=14,
            state="disabled",
            font=("Segoe UI", 10),
            bg=theme.entry,
            fg=theme.fg,
            relief="solid",
            borderwidth=1,
            padx=10,
            pady=10,
        )
        self.chat.pack(fill="both", expand=True)

        fila_pregunta = ttk.Frame(panel_chat)
        fila_pregunta.pack(fill="x", pady=(8, 0))

        self.entrada = ttk.Entry(fila_pregunta, font=("Segoe UI", 10))
        self.entrada.pack(side="left", fill="x", expand=True)
        self.entrada.bind("<Return>", lambda _e: self.enviar())

        ttk.Button(fila_pregunta, text="Preguntar", command=self.enviar).pack(side="left", padx=(8, 0))
        ttk.Button(fila_pregunta, text="Limpiar", command=self.limpiar).pack(side="left", padx=(8, 0))
        ttk.Button(fila_pregunta, text="Graficas", command=self._mostrar_graficas_historial).pack(
            side="left", padx=(8, 0)
        )

        panel_graficas = ttk.LabelFrame(contenido, text="Graficas (COP)", padding=6)
        contenido.add(panel_graficas, weight=2)

        self.notebook_charts = ttk.Notebook(panel_graficas)
        self.notebook_charts.pack(fill="both", expand=True)

        tabs = {
            "ventas": "Ventas/semana",
            "productos": "Top productos",
            "insumos": "Precios insumos",
            "resumen": "Resumen mes",
            "impacto": "Ultimo analisis",
        }
        self.charts = {}
        self.tab_index = {}
        for i, (key, label) in enumerate(tabs.items()):
            frame = ttk.Frame(self.notebook_charts)
            self.notebook_charts.add(frame, text=label)
            self.charts[key] = ChartPanel(frame, theme)
            self.charts[key].pack(fill="both", expand=True)
            self.tab_index[key] = i

        ejemplos_frame = ttk.LabelFrame(marco, text="Ejemplos rapidos (COP)", padding=8)
        ejemplos_frame.pack(fill="x", pady=(10, 0))

        ejemplos = [
            "Cuanto vendi en mayo?",
            "Que insumo subio mas?",
            "Que pasa si la harina sube 15%?",
            "Cuanto cuesta la empanada de carne?",
            "Cual producto es mas rentable?",
            "Resumen del mes",
            "Peor caso al 10%",
            "Cuantas empanadas de queso vendi?",
        ]
        for i, ejemplo in enumerate(ejemplos):
            fila = i // 4
            col = i % 4
            ttk.Button(
                ejemplos_frame,
                text=ejemplo,
                command=lambda e=ejemplo: self._preguntar_ejemplo(e),
            ).grid(row=fila, column=col, padx=4, pady=2, sticky="ew")
            ejemplos_frame.columnconfigure(col, weight=1)

        self.saludar()
        self._mostrar_graficas_historial()

    def _mostrar_graficas_historial(self):
        h = self.bot.historial
        self.charts["ventas"].mostrar_ventas_semana(h)
        self.charts["productos"].mostrar_top_productos(h)
        self.charts["insumos"].mostrar_variacion_insumos(h)
        self.charts["resumen"].mostrar_resumen_financiero(h)

    def saludar(self):
        total = self.bot.total_preguntas()
        meta = self.bot.historial.meta
        mes = meta.get("mes", "el mes")
        anio = meta.get("anio", "")
        fuentes = ", ".join(sorted(self.bot.fuentes.keys())) or "ninguna"
        self.escribir_bot(
            f"Hola. Tengo {total} preguntas en memoria ({fuentes}) "
            f"y datos historicos de {mes} {anio} en pesos colombianos (COP)."
        )
        self.escribir_bot(
            "Pregunta por ventas, costos, ganancias o simula cambios. "
            "Las graficas del mes estan abajo; al simular un precio se actualiza 'Ultimo analisis'."
        )

    def escribir(self, autor: str, mensaje: str):
        self.chat.configure(state="normal")
        self.chat.insert("end", f"{autor}: {mensaje}\n\n")
        self.chat.configure(state="disabled")
        self.chat.see("end")

    def escribir_bot(self, mensaje: str):
        self.escribir("Bot", mensaje)

    def _preguntar_ejemplo(self, texto: str):
        self.entrada.delete(0, "end")
        self.entrada.insert(0, texto)
        self.enviar()

    def _mostrar_grafica_segun_pregunta(self, pregunta: str, resultado: dict):
        """Selecciona y actualiza la grafica que corresponde a la pregunta"""
        grafica = resultado.get("grafica")

        if grafica == "impacto" or resultado.get("tipo") == "calculo":
            insumo, _ = self.bot._encontrar_insumo(pregunta)
            if insumo:
                nuevo_precio = self.bot._calcular_nuevo_precio(insumo.precio_unidad, pregunta)
                if nuevo_precio:
                    datos = self.analizador.analizar_cambio_precio_insumo(insumo.id, nuevo_precio)
                    if datos:
                        self.charts["impacto"].mostrar_impacto_ganancia(datos)
                        self.notebook_charts.select(self.tab_index["impacto"])
            return

        if grafica == "escenarios" or resultado.get("tipo") == "escenario":
            pct = abs(self.bot._extraer_porcentaje(pregunta) or 10.0)
            escenarios = self.analizador.generar_escenarios(pct)
            self.charts["impacto"].mostrar_escenarios(escenarios)
            self.notebook_charts.select(self.tab_index["impacto"])
            return

        if grafica in self.charts:
            h = self.bot.historial
            if grafica == "ventas":
                self.charts["ventas"].mostrar_ventas_semana(h)
            elif grafica == "productos":
                self.charts["productos"].mostrar_top_productos(h)
            elif grafica == "insumos":
                self.charts["insumos"].mostrar_variacion_insumos(h)
            elif grafica == "resumen":
                self.charts["resumen"].mostrar_resumen_financiero(h)
            self.notebook_charts.select(self.tab_index[grafica])

    def responder_pregunta(self, texto: str):
        resultado = self.bot.responder(texto)

        if resultado.get("sin_respuesta"):
            self.escribir_bot(resultado["respuesta"])
            sugerencias = resultado.get("sugerencias", [])
            if sugerencias:
                self.escribir_bot("Quizas querias: " + "; ".join(sugerencias[:5]))
            self._preguntar_continuar()
            return

        self.escribir_bot(resultado["respuesta"])
        self._mostrar_grafica_segun_pregunta(texto, resultado)
        self._preguntar_continuar()

    def _preguntar_continuar(self):
        self.esperando_continuar = True
        self.escribir_bot("Deseas consultar algo mas?")

    def enviar(self):
        texto = self.entrada.get().strip()
        if not texto:
            messagebox.showinfo("Pregunta vacia", "Escribe una pregunta para el asistente.")
            return

        self.entrada.delete(0, "end")
        self.escribir("Usuario", texto)

        decision = normalizar(texto)
        if self.esperando_continuar:
            if decision in {"si", "s", "claro", "continuar", "otra", "otra pregunta", "dale"}:
                self.esperando_continuar = False
                self.escribir_bot("Claro, que otra cosa quieres saber?")
                return
            if decision in {"no", "n", "salir", "hasta alli", "dejarlo", "terminar", "listo"}:
                self.esperando_continuar = False
                self.escribir_bot("Listo. Gracias por usar el asistente.")
                return

        self.responder_pregunta(texto)

    def limpiar(self):
        self.chat.configure(state="normal")
        self.chat.delete("1.0", "end")
        self.chat.configure(state="disabled")
        self.esperando_continuar = False
        self.saludar()

    def actualizar_datos(self):
        """Refresca nombres de insumos/productos en el historial"""
        self.bot.historial.set_nombres_insumos(self.bot.insumos)
        self.bot.historial.set_nombres_productos(self.bot.productos)
        self._mostrar_graficas_historial()
