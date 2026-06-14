"""
Pantalla de optimización de producción
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from core.optimizador import Optimizador, DIAS_SEMANA
from core.productos import ProductoManager

class OptimizacionScreen:
    """Pantalla para optimizar la producción"""
    
    def __init__(self, parent, optimizador: Optimizador,
                 producto_manager: ProductoManager, theme):
        self.optimizador = optimizador
        self.producto_manager = producto_manager
        self.theme = theme
        
        # Frame principal con dos columnas
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Frame de configuración a la izquierda
        config_frame = ttk.LabelFrame(main_frame, text="⚙️ Configuración de Optimización", padding=15)
        config_frame.pack(side="left", fill="y", expand=False, padx=(0, 10))
        
        # Frame de demanda para TODOS los productos mejorado
        demanda_frame = ttk.LabelFrame(config_frame, text="📊 Demanda Mínima por Día (Todos los Productos)", padding=15)
        demanda_frame.pack(fill="x", pady=(0, 10))
        
        # Frame con scrollbar para la tabla de demanda
        canvas_frame = ttk.Frame(demanda_frame)
        canvas_frame.pack(fill="both", expand=True, pady=5)
        
        # Canvas y scrollbar para hacer la tabla scrolleable (altura reducida para dar más espacio a resultados)
        canvas = tk.Canvas(canvas_frame, height=120, highlightthickness=1, highlightbackground="gray")
        scrollbar_demanda = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        def on_frame_configure(event):
            """Actualiza el scrollregion cuando el frame cambia de tamaño"""
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        def on_canvas_configure(event):
            """Ajusta el ancho del scrollable_frame al ancho del canvas"""
            canvas_width = event.width
            canvas.itemconfig(canvas_window, width=canvas_width)
        
        scrollable_frame.bind("<Configure>", on_frame_configure)
        canvas.bind("<Configure>", on_canvas_configure)
        
        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar_demanda.set)
        
        # Encabezados de la tabla directamente en scrollable_frame
        ttk.Label(scrollable_frame, text="Producto", font=("Arial", 9, "bold"), width=20).grid(
            row=0, column=0, padx=5, pady=3, sticky="w"
        )
        for i, dia in enumerate(DIAS_SEMANA):
            ttk.Label(scrollable_frame, text=dia[:3], font=("Arial", 9, "bold"), width=8, anchor="center").grid(
                row=0, column=i+1, padx=2, pady=3
            )
        
        # Configurar columnas del scrollable_frame
        scrollable_frame.columnconfigure(0, minsize=150)
        for i in range(1, 8):
            scrollable_frame.columnconfigure(i, minsize=70)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar_demanda.pack(side="right", fill="y")
        
        # Diccionario para almacenar los entries de demanda por producto
        # Estructura: demanda_entries[producto_id][dia] = Entry widget
        self.demanda_entries = {}
        self.scrollable_frame_demanda = scrollable_frame
        self.canvas_demanda = canvas
        
        # Botón para cargar demanda estimada automáticamente mejorado
        btn_cargar_demanda = ttk.Button(demanda_frame, text="📥 Cargar Demanda Estimada", 
                                       command=self.cargar_demanda_estimada)
        btn_cargar_demanda.pack(pady=8)
        
        # Actualizar la tabla de demanda
        self.actualizar_tabla_demanda()
        
        # Frame de fondos mejorado
        fondos_frame = ttk.LabelFrame(config_frame, text="💵 Disponibilidad Financiera Diaria", padding=15)
        fondos_frame.pack(fill="x", pady=(0, 10))
        
        self.fondos_entries = {}
        # Crear dos filas para los fondos
        fondos_row1 = ttk.Frame(fondos_frame)
        fondos_row1.pack(fill="x", pady=2)
        fondos_row2 = ttk.Frame(fondos_frame)
        fondos_row2.pack(fill="x", pady=2)
        
        for i, dia in enumerate(DIAS_SEMANA):
            row_frame = fondos_row1 if i < 4 else fondos_row2
            ttk.Label(row_frame, text=f"{dia}:").pack(side="left", padx=5)
            entry = ttk.Entry(row_frame, width=12)
            entry.pack(side="left", padx=5)
            # Sin valor por defecto - el usuario debe ingresar el presupuesto manualmente
            entry.insert(0, "")
            self.fondos_entries[dia] = entry
        
        # Botones mejorados
        btn_frame = ttk.Frame(config_frame)
        btn_frame.pack(fill="x", pady=10)
        
        ttk.Button(btn_frame, text="🚀 Resolver Optimización", 
                  command=self.resolver_optimizacion).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="🔄 Nueva Optimización", 
                  command=self.limpiar_resultados).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="📊 Exportar a Excel", 
                  command=self.exportar_excel).pack(side="left", padx=5)
        
        # Frame de resultados a la derecha
        resultados_frame = ttk.LabelFrame(main_frame, text="📈 Resultados de la Optimización", padding=15)
        resultados_frame.pack(side="right", fill="both", expand=True)
        self.resultados_frame = resultados_frame  # Guardar referencia
        
        # Resumen mejorado
        resumen_frame = ttk.Frame(resultados_frame)
        resumen_frame.pack(fill="x", pady=(0, 10))
        
        self.label_resumen = ttk.Label(resumen_frame, text="⏳ Estado: No resuelto", 
                                       font=("Segoe UI", 11, "bold"))
        self.label_resumen.pack(anchor="w", pady=5)
        
        self.label_ganancia = ttk.Label(resumen_frame, text="💰 Ganancia Total: $0.00",
                                       font=("Segoe UI", 10))
        self.label_ganancia.pack(anchor="w", pady=2)
        
        # Frame para recomendaciones mejorado (con Text widget para texto largo)
        recomendaciones_frame = ttk.LabelFrame(resultados_frame, text="💡 Recomendaciones", padding=15)
        recomendaciones_frame.pack(fill="x", pady=10, padx=5)
        
        # Usar Text widget en lugar de Label para mejor manejo de texto largo
        text_frame = tk.Frame(recomendaciones_frame, bg=self.theme.frame)
        text_frame.pack(fill="x", padx=5, pady=5)
        
        self.text_recomendaciones = tk.Text(
            text_frame,
            height=5,
            wrap=tk.WORD,
            font=('Segoe UI', 9),
            bg=self.theme.entry,
            fg=self.theme.fg,
            relief='solid',
            borderwidth=1,
            padx=12,
            pady=12,
            insertbackground=self.theme.fg,
            selectbackground=self.theme.select,
            selectforeground='#ffffff'
        )
        texto_inicial = "Ejecuta la optimización para obtener sugerencias."
        self.text_recomendaciones.insert('1.0', texto_inicial)
        self.text_recomendaciones.config(state='disabled')  # Solo lectura
        
        scrollbar_recom = ttk.Scrollbar(text_frame, orient="vertical", command=self.text_recomendaciones.yview)
        self.text_recomendaciones.configure(yscrollcommand=scrollbar_recom.set)
        
        self.text_recomendaciones.pack(side="left", fill="both", expand=True)
        scrollbar_recom.pack(side="right", fill="y")
        
        # Título de la tabla mejorado
        ttk.Label(resultados_frame, text="📅 Plan de Producción Semanal:", 
                 font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(15, 8), padx=5)
        
        # Frame contenedor para tabla y scrollbars
        tabla_container = ttk.Frame(resultados_frame)
        tabla_container.pack(fill="both", expand=True, pady=5, padx=5)
        
        # Frame interno para la tabla y scrollbar vertical
        tabla_frame = ttk.Frame(tabla_container)
        tabla_frame.pack(side="left", fill="both", expand=True)
        
        # Tabla de producción
        columns = ["producto"] + DIAS_SEMANA + ["total"]
        self.tree = ttk.Treeview(tabla_frame, columns=columns, show="headings", height=12)
        
        self.tree.heading("producto", text="📦 Producto")
        for dia in DIAS_SEMANA:
            self.tree.heading(dia, text=dia[:3])
        self.tree.heading("total", text="📊 Total")
        
        self.tree.column("producto", width=220, anchor="w")
        for dia in DIAS_SEMANA:
            self.tree.column(dia, width=90, anchor="e")
        self.tree.column("total", width=110, anchor="e")
        
        # Scrollbars
        scrollbar_v = ttk.Scrollbar(tabla_frame, orient="vertical", command=self.tree.yview)
        scrollbar_h = ttk.Scrollbar(tabla_container, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=scrollbar_v.set, xscrollcommand=scrollbar_h.set)
        
        # Layout de tabla y scrollbar vertical
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar_v.pack(side="right", fill="y")
        
        # Scrollbar horizontal debajo de todo
        scrollbar_h.pack(side="bottom", fill="x")
        
        self.resultados = None
        self.ultima_demanda = {}
        self.ultimos_fondos = {}
        self.masa_actual = None  # Para compatibilidad
    
    def actualizar_productos(self):
        """Actualiza la lista de productos en la tabla de demanda"""
        self.actualizar_tabla_demanda()
    
    def actualizar_tabla_demanda(self):
        """Actualiza la tabla de demanda con todos los productos"""
        # Limpiar entries anteriores
        self.demanda_entries = {}
        
        # Limpiar frame (excepto el header_frame que está en row=0)
        for widget in self.scrollable_frame_demanda.winfo_children():
            grid_info = widget.grid_info()
            if grid_info.get('row', 0) > 0:  # Mantener encabezados (row 0)
                widget.destroy()
        
        productos = self.producto_manager.listar()
        for row, producto in enumerate(productos, start=1):
            # Nombre del producto
            ttk.Label(self.scrollable_frame_demanda, text=producto.nombre, width=20, anchor="w").grid(
                row=row, column=0, padx=5, pady=2, sticky="w"
            )
            
            # Entries para cada día
            self.demanda_entries[producto.id] = {}
            for i, dia in enumerate(DIAS_SEMANA):
                entry = ttk.Entry(self.scrollable_frame_demanda, width=8)
                # Usar demanda_estimada como valor por defecto si existe
                if producto.demanda_estimada > 0:
                    entry.insert(0, str(min(producto.demanda_estimada, 15)))
                else:
                    entry.insert(0, "0")
                entry.grid(row=row, column=i+1, padx=2, pady=2)
                self.demanda_entries[producto.id][dia] = entry
        
        # Actualizar scrollregion del canvas
        self.scrollable_frame_demanda.update_idletasks()
        self.canvas_demanda.configure(scrollregion=self.canvas_demanda.bbox("all"))
    
    def cargar_demanda_estimada(self):
        """Carga la demanda estimada de todos los productos en la tabla"""
        productos = self.producto_manager.listar()
        for producto in productos:
            if producto.id in self.demanda_entries:
                for dia in DIAS_SEMANA:
                    if dia in self.demanda_entries[producto.id]:
                        entry = self.demanda_entries[producto.id][dia]
                        # Usar demanda_estimada limitada a 15 para evitar problemas
                        valor = min(producto.demanda_estimada, 15) if producto.demanda_estimada > 0 else 0
                        entry.delete(0, "end")
                        entry.insert(0, str(int(valor)))
        
        messagebox.showinfo("Éxito", "Demanda estimada cargada para todos los productos")
    
    def resolver_optimizacion(self):
        """Resuelve el modelo de optimización"""
        try:
            # Validar que hay productos registrados
            productos = self.producto_manager.listar()
            if not productos:
                messagebox.showerror("Error", "No hay productos registrados. Agrega productos primero.")
                return
            
            # Obtener demanda para TODOS los productos
            demanda = {}
            for producto in productos:
                if producto.id in self.demanda_entries:
                    for dia in DIAS_SEMANA:
                        if dia in self.demanda_entries[producto.id]:
                            try:
                                valor_texto = self.demanda_entries[producto.id][dia].get().strip()
                                if valor_texto:
                                    valor = float(valor_texto)
                                    if valor > 0:  # Solo agregar si hay demanda
                                        demanda[(producto.id, dia)] = valor
                            except ValueError:
                                # Si el valor no es numérico, se ignora (tratado como 0)
                                pass
            
            # OPCION: Optimizar solo el producto seleccionado O todos los productos
            # Por defecto, optimizamos solo el seleccionado para evitar problemas de factibilidad
            # Si quieres optimizar todos, descomenta las siguientes líneas:
            # for producto in productos:
            #     if producto.id != producto_id:
            #         for dia in DIAS_SEMANA:
            #             # Usar demanda_estimada como mínimo (pero solo si es razonable)
            #             demanda_min = producto.demanda_estimada if producto.demanda_estimada > 0 else 0
            #             if demanda_min > 0:
            #                 demanda[(producto.id, dia)] = demanda_min
            
            # Validar que hay al menos alguna demanda
            if not demanda:
                messagebox.showwarning("Advertencia", "No hay demanda especificada. Ingresa valores de demanda mayores a 0.")
                return
            
            # Obtener fondos
            fondos = {}
            for dia in DIAS_SEMANA:
                valor_texto = self.fondos_entries[dia].get().strip()
                if not valor_texto:
                    messagebox.showerror("Error", f"Debes ingresar el presupuesto para {dia}")
                    return
                try:
                    valor = float(valor_texto)
                    if valor <= 0:
                        messagebox.showerror("Error", f"El presupuesto para {dia} debe ser mayor a 0")
                        return
                    fondos[dia] = valor
                except ValueError:
                    messagebox.showerror("Error", f"El presupuesto para {dia} debe ser un número válido")
                    return
            
            # Calcular costos estimados para validación
            from core.costos import CalculadorCostos
            from core.insumos import InsumoManager
            from core.masas import MasaManager
            insumo_manager = InsumoManager()
            masa_manager = MasaManager()
            calculador = CalculadorCostos(
                insumo_manager,
                masa_manager,
                self.producto_manager
            )
            
            # Validar que los productos tengan costos calculables
            costo_total_estimado = 0
            for (prod_id, dia), dem in demanda.items():
                costo_unitario = calculador.calcular_costo_producto(prod_id)
                if costo_unitario <= 0:
                    messagebox.showwarning(
                        "Advertencia",
                        f"El producto {prod_id} no tiene costo calculado. "
                        "Verifica que tenga masa asociada o insumos definidos."
                    )
                costo_total_estimado += dem * costo_unitario
            
            # Advertencia si el costo estimado es muy alto comparado con el presupuesto
            presupuesto_total = sum(fondos.values())
            if costo_total_estimado > presupuesto_total * 1.5:
                respuesta = messagebox.askyesno(
                    "Advertencia",
                    f"El costo estimado de la demanda ({costo_total_estimado:.2f}) es mucho mayor "
                    f"que el presupuesto total ({presupuesto_total:.2f}).\n\n"
                    "Esto puede resultar en un problema no factible.\n\n"
                    "¿Deseas continuar de todas formas?"
                )
                if not respuesta:
                    return
            
            # Guardar datos utilizados
            self.ultima_demanda = demanda.copy()
            self.ultimos_fondos = fondos.copy()
            
            # Resolver
            self.resultados = self.optimizador.optimizar(demanda, fondos)
            
            # Mostrar resultados
            self.mostrar_resultados()
            
        except ValueError:
            messagebox.showerror("Error", "Verifica que todos los valores sean números válidos")
        except Exception as e:
            messagebox.showerror("Error", f"Error al resolver optimización: {e}")
            import traceback
            print(traceback.format_exc())
    
    def mostrar_resultados(self):
        """Muestra los resultados en la tabla"""
        if not self.resultados:
            return
        
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Actualizar resumen con mensaje más descriptivo mejorado
        estado = self.resultados['estado']
        if estado == "Infeasible":
            estado_texto = "❌ Estado: No Factible (Las restricciones son incompatibles)"
            # Mostrar mensaje de ayuda
            messagebox.showwarning(
                "Problema No Factible",
                "El modelo no puede encontrar una solución que satisfaga todas las restricciones.\n\n"
                "Posibles causas:\n"
                "• La demanda es muy alta para el presupuesto disponible\n"
                "• Los costos de los productos son muy altos\n"
                "• El presupuesto diario es insuficiente\n\n"
                "Sugerencias:\n"
                "• Reduce la demanda mínima\n"
                "• Aumenta el presupuesto diario\n"
                "• Verifica que los productos tengan costos calculados correctamente"
            )
        elif estado == "Optimal":
            estado_texto = "✅ Estado: Óptimo"
        else:
            estado_texto = f"⚠️ Estado: {estado}"
        
        self.label_resumen.config(text=estado_texto)
        ganancia_formateada = f"${self.resultados['ganancia_total']:,.2f}"
        self.label_ganancia.config(text=f"💰 Ganancia Total: {ganancia_formateada}")
        
        # Agregar producción solo si hay resultados
        productos_agregados = 0
        if self.resultados.get("productos"):
            for producto_info in self.resultados["productos"]:
                valores = [producto_info["nombre"]]
                total = 0
                for dia in DIAS_SEMANA:
                    cantidad = producto_info["produccion"].get(dia, 0)
                    valores.append(f"{cantidad:,.2f}")
                    total += cantidad
                valores.append(f"{total:,.2f}")
                
                self.tree.insert("", "end", values=valores)
                productos_agregados += 1
        
        # Si no hay productos, mostrar mensaje
        if productos_agregados == 0:
            # Insertar una fila con mensaje
            self.tree.insert("", "end", values=(["No hay datos disponibles"] + [""] * 8))
        
        # Asegurar que la tabla sea visible y se actualice
        self.tree.update_idletasks()
        
        # Actualizar recomendaciones después de mostrar resultados
        self.actualizar_recomendaciones()
        
        # Forzar actualización de toda la ventana de resultados
        if hasattr(self, 'resultados_frame'):
            self.resultados_frame.update_idletasks()
            self.resultados_frame.update()
    
    def generar_recomendaciones(self):
        """Genera texto de recomendaciones basadas en los resultados."""
        if not self.resultados:
            return "Ejecuta la optimización para obtener sugerencias específicas."
        
        estado = self.resultados.get("estado", "Sin datos")
        recomendaciones = []
        
        if estado != "Optimal":
            recomendaciones.append(
                "• Ajusta la demanda mínima o aumenta el presupuesto diario para lograr una solución factible."
            )
            if not self.ultimos_fondos:
                recomendaciones.append("• Define presupuestos diarios mayores a 0 en la sección de fondos.")
            return "\n".join(recomendaciones) if recomendaciones else "No hay recomendaciones disponibles."
        
        ganancia = self.resultados.get("ganancia_total", 0)
        if ganancia <= 0:
            recomendaciones.append("• La ganancia proyectada es baja o negativa. Revisa precios o reduce costos.")
        else:
            ganancia_formateada = f"${ganancia:,.2f}"
            recomendaciones.append(f"• Ganancia proyectada: {ganancia_formateada}. Mantén los precios actuales o busca mejoras.")
        
        costos_totales = self.resultados.get("costos_totales", {})
        costo_total = sum(costos_totales.values())
        presupuesto_total = sum(self.ultimos_fondos.values()) if self.ultimos_fondos else 0
        if presupuesto_total > 0:
            uso_presupuesto = (costo_total / presupuesto_total) * 100 if presupuesto_total else 0
            if uso_presupuesto > 90:
                recomendaciones.append("• El presupuesto se utiliza casi al máximo. Considera aumentar fondos para tener margen.")
            elif uso_presupuesto < 60:
                recomendaciones.append("• El presupuesto tiene espacio libre. Puedes aumentar demanda o planear promociones.")
        
        productos = self.resultados.get("productos", [])
        if productos:
            producto_top = max(
                productos,
                key=lambda p: sum(p["produccion"].values())
            )
            total_top = sum(producto_top["produccion"].values())
            recomendaciones.append(
                f"• El producto con mayor producción es {producto_top['nombre']} ({total_top:,.0f} unidades/semana)."
            )
        
        if self.ultima_demanda:
            demanda_total = sum(self.ultima_demanda.values())
            recomendaciones.append(f"• Demanda total mínima cubierta: {demanda_total:,.0f} unidades por semana.")
        
        return "\n".join(recomendaciones) if recomendaciones else "No hay recomendaciones disponibles."
    
    def actualizar_recomendaciones(self):
        """Actualiza el cuadro de recomendaciones."""
        try:
            texto = self.generar_recomendaciones()
            if texto:
                self.text_recomendaciones.config(state='normal')  # Habilitar edición temporalmente
                self.text_recomendaciones.delete('1.0', tk.END)
                self.text_recomendaciones.insert('1.0', texto)
                self.text_recomendaciones.config(state='disabled')  # Volver a solo lectura
                # Forzar actualización visual
                self.text_recomendaciones.update_idletasks()
                self.text_recomendaciones.see('1.0')  # Scroll al inicio
            else:
                # Si no hay texto, mostrar mensaje por defecto
                self.text_recomendaciones.config(state='normal')
                self.text_recomendaciones.delete('1.0', tk.END)
                self.text_recomendaciones.insert('1.0', "No hay recomendaciones disponibles.")
                self.text_recomendaciones.config(state='disabled')
        except Exception as e:
            # En caso de error, mostrar mensaje de error
            self.text_recomendaciones.config(state='normal')
            self.text_recomendaciones.delete('1.0', tk.END)
            self.text_recomendaciones.insert('1.0', f"Error al generar recomendaciones: {str(e)}")
            self.text_recomendaciones.config(state='disabled')
    
    def limpiar_resultados(self):
        """Limpia los resultados y permite hacer una nueva optimización"""
        # Limpiar tabla de resultados
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Resetear resultados
        self.resultados = None
        self.ultima_demanda = {}
        self.ultimos_fondos = {}
        
        # Resetear etiquetas
        self.label_resumen.config(text="⏳ Estado: No resuelto")
        self.label_ganancia.config(text="💰 Ganancia Total: $0.00")
        self.text_recomendaciones.config(state='normal')
        self.text_recomendaciones.delete('1.0', tk.END)
        self.text_recomendaciones.insert('1.0', "Ejecuta la optimización para obtener sugerencias.")
        self.text_recomendaciones.config(state='disabled')
        
        messagebox.showinfo("Listo", "Resultados limpiados. Puedes configurar una nueva optimización.")
    
    def exportar_excel(self):
        """Exporta los resultados a Excel"""
        if not self.resultados:
            messagebox.showwarning("Advertencia", "Primero resuelve la optimización")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
        )
        
        if filename:
            if self.optimizador.exportar_a_excel(self.resultados, filename):
                messagebox.showinfo("Éxito", f"Resultados exportados a {filename}")
            else:
                messagebox.showerror("Error", "Error al exportar. Verifica que pandas y openpyxl estén instalados")

