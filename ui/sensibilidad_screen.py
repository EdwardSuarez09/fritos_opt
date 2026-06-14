"""
Pantalla de análisis de sensibilidad
"""
import tkinter as tk
from tkinter import ttk, messagebox
from core.sensibilidad import AnalizadorSensibilidad
from core.inventario import Inventario
from core.costos import CalculadorCostos
from ui.charts import ChartPanel

class SensibilidadScreen:
    """Pantalla para análisis de sensibilidad"""
    
    def __init__(self, parent, inventario: Inventario, 
                 calculador_costos: CalculadorCostos, theme):
        self.inventario = inventario
        self.calculador_costos = calculador_costos
        self.theme = theme
        
        # Crear analizador
        self.analizador = AnalizadorSensibilidad(
            inventario.insumos,
            inventario.masas,
            inventario.productos,
            calculador_costos
        )
        
        # Frame principal con dos columnas
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Columna izquierda: Configuración
        left_frame = ttk.LabelFrame(main_frame, text="💡 ¿Qué quieres analizar?", padding=15)
        left_frame.pack(side="left", fill="y", expand=False, padx=(0, 10))
        
        # Explicación simple
        explicacion = ttk.Label(
            left_frame, 
            text="Aquí puedes ver qué pasa si cambia el precio de algún insumo.\n"
                 "Por ejemplo: ¿Qué pasa si la harina sube de precio?",
            font=("Segoe UI", 9),
            foreground=self.theme.fg,
            wraplength=280,
            justify="left"
        )
        explicacion.pack(anchor="w", pady=(0, 15))
        
        # Selección de insumo
        ttk.Label(left_frame, text="1️⃣ Elige el insumo:", 
                 font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 5))
        
        self.combo_insumo = ttk.Combobox(left_frame, width=30, state="readonly")
        self.combo_insumo.pack(fill="x", pady=5)
        self.combo_insumo.bind("<<ComboboxSelected>>", self.on_insumo_selected)
        
        # Información del insumo actual
        self.info_frame = ttk.LabelFrame(left_frame, text="📋 Precio actual", padding=10)
        self.info_frame.pack(fill="x", pady=10)
        
        self.label_precio_actual = ttk.Label(
            self.info_frame, 
            text="Precio actual: -",
            font=("Segoe UI", 9)
        )
        self.label_precio_actual.pack(anchor="w")
        
        self.label_unidad = ttk.Label(
            self.info_frame, 
            text="Unidad: -",
            font=("Segoe UI", 9)
        )
        self.label_unidad.pack(anchor="w")
        
        # Campo para nuevo precio
        ttk.Label(
            left_frame, 
            text="2️⃣ ¿Cuál sería el nuevo precio?",
            font=("Segoe UI", 10, "bold")
        ).pack(anchor="w", pady=(10, 5))
        
        ttk.Label(
            left_frame,
            text="Ejemplo: Si el precio actual es $5,000 y quieres ver qué pasa si sube a $6,000, escribe 6000",
            font=("Segoe UI", 8),
            foreground="#888888",
            wraplength=280,
            justify="left"
        ).pack(anchor="w", pady=(0, 5))
        
        precio_frame = ttk.Frame(left_frame)
        precio_frame.pack(fill="x", pady=5)
        
        self.entry_nuevo_precio = ttk.Entry(precio_frame, width=15)
        self.entry_nuevo_precio.pack(side="left", padx=5)
        
        ttk.Button(
            precio_frame, 
            text="✅ Ver Resultado", 
            command=self.analizar_cambio
        ).pack(side="left", padx=5)
        
        # Separador visual
        ttk.Separator(left_frame, orient='horizontal').pack(fill="x", pady=15)
        
        # Análisis de escenarios
        escenarios_frame = ttk.LabelFrame(
            left_frame, 
            text="🎯 Comparar 3 Situaciones", 
            padding=10
        )
        escenarios_frame.pack(fill="x", pady=10)
        
        ttk.Label(
            escenarios_frame,
            text="¿Cuánto pueden cambiar los precios?",
            font=("Segoe UI", 9)
        ).pack(anchor="w")
        
        porcentaje_frame = ttk.Frame(escenarios_frame)
        porcentaje_frame.pack(fill="x", pady=5)
        
        self.entry_porcentaje = ttk.Entry(porcentaje_frame, width=8)
        self.entry_porcentaje.insert(0, "10")
        self.entry_porcentaje.pack(side="left", padx=(0, 5))
        
        ttk.Label(
            porcentaje_frame,
            text="%",
            font=("Segoe UI", 9)
        ).pack(side="left")
        
        ttk.Label(
            escenarios_frame,
            text="Ejemplo: 10% = ver qué pasa si los precios suben o bajan 10%",
            font=("Segoe UI", 8),
            foreground="#888888",
            wraplength=280,
            justify="left"
        ).pack(anchor="w", pady=(5, 10))
        
        ttk.Button(
            escenarios_frame, 
            text="🔄 Comparar Situaciones", 
            command=self.generar_escenarios
        ).pack(fill="x", pady=5)
        
        # Columna derecha: Resultados
        right_frame = ttk.LabelFrame(main_frame, text="📊 Aquí verás los resultados", padding=15)
        right_frame.pack(side="right", fill="both", expand=True)

        self.notebook_resultados = ttk.Notebook(right_frame)
        self.notebook_resultados.pack(fill="both", expand=True, pady=(0, 10))

        tab_detalle = ttk.Frame(self.notebook_resultados)
        tab_grafica = ttk.Frame(self.notebook_resultados)
        self.notebook_resultados.add(tab_detalle, text="📝 Detalle")
        self.notebook_resultados.add(tab_grafica, text="📊 Grafica")

        self.resultados_frame = ttk.LabelFrame(
            tab_detalle,
            text="💡 ¿Qué cambia en tu negocio?",
            padding=10
        )
        self.resultados_frame.pack(fill="both", expand=True)

        self.chart_impacto = ChartPanel(tab_grafica, self.theme)
        self.chart_impacto.pack(fill="both", expand=True)

        # Text widget para mostrar resultados
        text_frame = tk.Frame(self.resultados_frame, bg=self.theme.frame)
        text_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.text_resultados = tk.Text(
            text_frame,
            height=12,
            wrap=tk.WORD,
            font=('Segoe UI', 9),
            bg=self.theme.entry,
            fg=self.theme.fg,
            relief='solid',
            borderwidth=1,
            padx=12,
            pady=12,
            state='disabled'
        )
        
        scrollbar_resultados = ttk.Scrollbar(text_frame, orient="vertical", 
                                            command=self.text_resultados.yview)
        self.text_resultados.configure(yscrollcommand=scrollbar_resultados.set)
        
        self.text_resultados.pack(side="left", fill="both", expand=True)
        scrollbar_resultados.pack(side="right", fill="y")
        
        # Frame para escenarios
        self.escenarios_resultados_frame = ttk.LabelFrame(
            right_frame, 
            text="📈 Comparación: Mejor, Normal y Peor Caso", 
            padding=10
        )
        self.escenarios_resultados_frame.pack(fill="both", expand=True)
        
        columns = ("escenario", "descripcion", "impacto_costo", "impacto_ganancia", "productos")
        escenarios_body = ttk.Frame(self.escenarios_resultados_frame)
        escenarios_body.pack(fill="both", expand=True)

        tabla_frame = ttk.Frame(escenarios_body)
        tabla_frame.pack(side="left", fill="both", expand=True)

        self.tree_escenarios = ttk.Treeview(tabla_frame,
                                           columns=columns, show="headings", height=4)
        self.tree_escenarios.heading("escenario", text="Situación")
        self.tree_escenarios.heading("descripcion", text="¿Qué pasa?")
        self.tree_escenarios.heading("impacto_costo", text="Cambio en Costos")
        self.tree_escenarios.heading("impacto_ganancia", text="Cambio en Ganancias")
        self.tree_escenarios.heading("productos", text="Productos Afectados")
        self.tree_escenarios.column("escenario", width=90, anchor="w")
        self.tree_escenarios.column("descripcion", width=120, anchor="w")
        self.tree_escenarios.column("impacto_costo", width=110, anchor="e")
        self.tree_escenarios.column("impacto_ganancia", width=110, anchor="e")
        self.tree_escenarios.column("productos", width=100, anchor="w")
        scrollbar_escenarios = ttk.Scrollbar(tabla_frame,
                                            orient="vertical",
                                            command=self.tree_escenarios.yview)
        self.tree_escenarios.configure(yscrollcommand=scrollbar_escenarios.set)
        self.tree_escenarios.pack(side="left", fill="both", expand=True)
        scrollbar_escenarios.pack(side="right", fill="y")

        grafica_esc_frame = ttk.Frame(escenarios_body)
        grafica_esc_frame.pack(side="right", fill="both", expand=True, padx=(8, 0))
        self.chart_escenarios = ChartPanel(grafica_esc_frame, self.theme)
        self.chart_escenarios.pack(fill="both", expand=True)

        # Mensaje inicial
        self.mostrar_mensaje_inicial()
        
        # Actualizar combo de insumos después de crear todos los widgets
        self.actualizar_combo_insumos()
    
    def actualizar_combo_insumos(self):
        """Actualiza el combo de insumos"""
        insumos = self.inventario.insumos.listar()
        valores = [f"{insumo.nombre} ({insumo.categoria})" for insumo in insumos]
        self.combo_insumo["values"] = valores
        if valores:
            self.combo_insumo.set(valores[0])
            # Solo llamar on_insumo_selected si los widgets ya están creados
            if hasattr(self, 'label_precio_actual'):
                self.on_insumo_selected()
    
    def on_insumo_selected(self, event=None):
        """Cuando se selecciona un insumo"""
        seleccion = self.combo_insumo.get()
        if not seleccion:
            return
        
        nombre_insumo = seleccion.split(" (")[0]
        insumos = self.inventario.insumos.listar()
        for insumo in insumos:
            if insumo.nombre == nombre_insumo:
                self.insumo_actual = insumo
                self.label_precio_actual.config(
                    text=f"Precio actual: ${insumo.precio_unidad:,.2f}")
                self.label_unidad.config(text=f"Unidad: {insumo.unidad}")
                self.entry_nuevo_precio.delete(0, tk.END)
                self.entry_nuevo_precio.insert(0, str(insumo.precio_unidad))
                break
    
    def analizar_cambio(self):
        """Analiza el impacto de cambiar el precio de un insumo"""
        try:
            if not hasattr(self, 'insumo_actual'):
                messagebox.showwarning("Advertencia", "Selecciona un insumo primero")
                return
            
            nuevo_precio = float(self.entry_nuevo_precio.get())
            if nuevo_precio <= 0:
                messagebox.showerror("Error", "El precio debe ser mayor a 0")
                return
            
            # Realizar análisis
            resultados = self.analizador.analizar_cambio_precio_insumo(
                self.insumo_actual.id, nuevo_precio
            )
            
            # Mostrar resultados
            self.mostrar_resultados(resultados)
            
        except ValueError:
            messagebox.showerror("Error", "Ingresa un precio válido")
        except Exception as e:
            messagebox.showerror("Error", f"Error al analizar: {e}")
    
    def mostrar_resultados(self, resultados: dict):
        """Muestra los resultados del análisis de forma simple y clara"""
        self.text_resultados.config(state='normal')
        self.text_resultados.delete('1.0', tk.END)
        
        if not resultados:
            self.text_resultados.insert('1.0', "No hay resultados disponibles.")
            self.text_resultados.config(state='disabled')
            return
        
        # Encabezado simple
        texto = f"📦 Análisis: {resultados['insumo']}\n"
        texto += "═" * 50 + "\n\n"
        
        # Cambio de precio explicado de forma simple
        cambio = resultados['cambio_porcentual_precio']
        if cambio > 0:
            texto += f"📈 El precio SUBE:\n"
            texto += f"   De ${resultados['precio_original']:,.0f} a ${resultados['nuevo_precio']:,.0f}\n"
            texto += f"   (Sube {cambio:.1f}%)\n\n"
        elif cambio < 0:
            texto += f"📉 El precio BAJA:\n"
            texto += f"   De ${resultados['precio_original']:,.0f} a ${resultados['nuevo_precio']:,.0f}\n"
            texto += f"   (Baja {abs(cambio):.1f}%)\n\n"
        else:
            texto += f"➡️ El precio se mantiene igual\n\n"
        
        if resultados['productos_afectados']:
            texto += f"🍽️ Productos que se ven afectados ({len(resultados['productos_afectados'])}):\n"
            texto += "─" * 50 + "\n\n"
            
            for producto_id, impacto_costo in resultados['impacto_costos'].items():
                impacto_ganancia = resultados['impacto_ganancias'][producto_id]
                nombre = impacto_costo['nombre']
                
                texto += f"📌 {nombre}\n"
                
                # Costo explicado de forma simple
                if impacto_costo['impacto'] > 0:
                    texto += f"   💰 Costo: Sube ${abs(impacto_costo['impacto']):,.0f} "
                    texto += f"(de ${impacto_costo['costo_original']:,.0f} a ${impacto_costo['costo_nuevo']:,.0f})\n"
                elif impacto_costo['impacto'] < 0:
                    texto += f"   💰 Costo: Baja ${abs(impacto_costo['impacto']):,.0f} "
                    texto += f"(de ${impacto_costo['costo_original']:,.0f} a ${impacto_costo['costo_nuevo']:,.0f})\n"
                else:
                    texto += f"   💰 Costo: No cambia\n"
                
                # Ganancia explicada de forma simple
                if impacto_ganancia['impacto'] < 0:
                    texto += f"   📉 Ganancia: Baja ${abs(impacto_ganancia['impacto']):,.0f} "
                    texto += f"(de ${impacto_ganancia['ganancia_original']:,.0f} a ${impacto_ganancia['ganancia_nueva']:,.0f})\n"
                elif impacto_ganancia['impacto'] > 0:
                    texto += f"   📈 Ganancia: Sube ${impacto_ganancia['impacto']:,.0f} "
                    texto += f"(de ${impacto_ganancia['ganancia_original']:,.0f} a ${impacto_ganancia['ganancia_nueva']:,.0f})\n"
                else:
                    texto += f"   ➡️ Ganancia: No cambia\n"
                
                texto += "\n"
        else:
            texto += "✅ Ningún producto se ve afectado por este cambio.\n"
            texto += "   (Este insumo no se usa en ningún producto)\n\n"
        
        # Resumen final simple
        texto += "═" * 50 + "\n"
        texto += "📊 RESUMEN TOTAL:\n"
        texto += "─" * 50 + "\n"
        
        if resultados['impacto_total_costo'] > 0:
            texto += f"💰 Tus costos totales SUBEN: ${abs(resultados['impacto_total_costo']):,.0f}\n"
        elif resultados['impacto_total_costo'] < 0:
            texto += f"💰 Tus costos totales BAJAN: ${abs(resultados['impacto_total_costo']):,.0f}\n"
        else:
            texto += f"💰 Tus costos totales: No cambian\n"
        
        if resultados['impacto_total_ganancia'] < 0:
            texto += f"📉 Tus ganancias totales BAJAN: ${abs(resultados['impacto_total_ganancia']):,.0f}\n"
        elif resultados['impacto_total_ganancia'] > 0:
            texto += f"📈 Tus ganancias totales SUBEN: ${resultados['impacto_total_ganancia']:,.0f}\n"
        else:
            texto += f"➡️ Tus ganancias totales: No cambian\n"
        
        texto += "\n💡 CONSEJO:\n"
        if resultados['impacto_total_ganancia'] < -1000:
            texto += "   ⚠️ Este cambio te afecta mucho. Considera:\n"
            texto += "   • Buscar otro proveedor\n"
            texto += "   • Ajustar tus precios de venta\n"
            texto += "   • Usar menos de este insumo\n"
        elif resultados['impacto_total_ganancia'] < 0:
            texto += "   ⚠️ Este cambio te afecta un poco. Revisa si puedes ajustar.\n"
        elif resultados['impacto_total_ganancia'] > 0:
            texto += "   ✅ Este cambio te beneficia. ¡Aprovecha la oportunidad!\n"
        else:
            texto += "   ℹ️ Este cambio no tiene mucho impacto en tu negocio.\n"
        
        self.text_resultados.insert('1.0', texto)
        self.text_resultados.config(state='disabled')
        self.text_resultados.see('1.0')
        self.chart_impacto.mostrar_impacto_ganancia(resultados)
    
    def generar_escenarios(self):
        """Genera y muestra los escenarios"""
        try:
            porcentaje = float(self.entry_porcentaje.get())
            if porcentaje <= 0 or porcentaje > 100:
                messagebox.showerror("Error", "El porcentaje debe estar entre 0 y 100")
                return
            
            # Generar escenarios
            escenarios = self.analizador.generar_escenarios(porcentaje)
            
            # Limpiar tabla
            for item in self.tree_escenarios.get_children():
                self.tree_escenarios.delete(item)
            
            # Agregar escenarios a la tabla
            for key, escenario in escenarios.items():
                resultados = escenario['resultados']
                productos_afectados = len(resultados.get('productos_afectados', []))

                impacto_costo = resultados.get('impacto_total_costo', 0)
                impacto_ganancia = resultados.get('impacto_total_ganancia', 0)

                if key == "optimista":
                    tag = "optimista"
                    nombre_display = "✅ Mejor Caso"
                elif key == "pesimista":
                    tag = "pesimista"
                    nombre_display = "⚠️ Peor Caso"
                else:
                    tag = "realista"
                    nombre_display = "➡️ Caso Normal"

                if impacto_costo > 0:
                    costo_str = f"Sube ${abs(impacto_costo):,.0f}"
                elif impacto_costo < 0:
                    costo_str = f"Baja ${abs(impacto_costo):,.0f}"
                else:
                    costo_str = "No cambia"

                if impacto_ganancia > 0:
                    ganancia_str = f"Sube ${abs(impacto_ganancia):,.0f}"
                elif impacto_ganancia < 0:
                    ganancia_str = f"Baja ${abs(impacto_ganancia):,.0f}"
                else:
                    ganancia_str = "No cambia"

                self.tree_escenarios.insert("", "end", values=(
                    nombre_display,
                    escenario['descripcion'],
                    costo_str,
                    ganancia_str,
                    f"{productos_afectados} productos"
                ), tags=(tag,))

            # Configurar colores
            self.tree_escenarios.tag_configure("optimista",
                                             background="#1e4d2e" if self.theme.dark_mode else "#e8f5e9")
            self.tree_escenarios.tag_configure("pesimista",
                                             background="#4d1e1e" if self.theme.dark_mode else "#ffebee")
            self.tree_escenarios.tag_configure("realista",
                                             background=self.theme.frame)

            self.chart_escenarios.mostrar_escenarios(escenarios)
            
        except ValueError:
            messagebox.showerror("Error", "Ingresa un porcentaje válido")
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar escenarios: {e}")
    
    def mostrar_mensaje_inicial(self):
        """Muestra mensaje inicial en el área de resultados"""
        self.text_resultados.config(state='normal')
        self.text_resultados.delete('1.0', tk.END)
        mensaje = (
            "👋 ¡Hola! Bienvenido al Análisis de Precios\n"
            "═" * 50 + "\n\n"
            "📖 ¿Para qué sirve esto?\n"
            "   Te ayuda a saber qué pasa si cambia el precio de algún insumo.\n\n"
            "💡 Ejemplo práctico:\n"
            "   Si la harina sube de $5,000 a $6,000:\n"
            "   • ¿Cuánto más costará hacer cada empanada?\n"
            "   • ¿Cuánto menos ganarás?\n"
            "   • ¿Vale la pena cambiar de proveedor?\n\n"
            "🚀 Cómo usarlo (3 pasos):\n"
            "   1️⃣ Elige el insumo que quieres analizar\n"
            "   2️⃣ Escribe el nuevo precio\n"
            "   3️⃣ Haz clic en 'Ver Resultado'\n\n"
            "🎯 También puedes comparar 3 situaciones:\n"
            "   • Mejor caso: precios bajan\n"
            "   • Caso normal: precios se mantienen\n"
            "   • Peor caso: precios suben\n\n"
            "👉 Empieza eligiendo un insumo de la lista de la izquierda."
        )
        self.text_resultados.insert('1.0', mensaje)
        self.text_resultados.config(state='disabled')
    
    def actualizar_datos(self):
        """Actualiza los datos cuando cambian en otras pantallas"""
        self.actualizar_combo_insumos()
        if hasattr(self, 'insumo_actual'):
            self.on_insumo_selected()

