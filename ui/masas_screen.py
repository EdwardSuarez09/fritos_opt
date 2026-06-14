"""
Pantalla de gestión de lotes de masa
"""
import tkinter as tk
from tkinter import ttk, messagebox
from core.masas import LoteMasa, MasaManager
from core.insumos import InsumoManager

class MasasScreen:
    """Pantalla para gestionar lotes de masa"""
    
    def __init__(self, parent, masa_manager: MasaManager, 
                 insumo_manager: InsumoManager, theme):
        self.masa_manager = masa_manager
        self.insumo_manager = insumo_manager
        self.theme = theme
        
        # Frame principal
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Frame de formulario mejorado
        form_frame = ttk.LabelFrame(main_frame, text="🥟 Crear Lote de Masa", padding=15)
        form_frame.pack(fill="x", pady=(0, 15))
        
        # Campos básicos
        ttk.Label(form_frame, text="Nombre del lote:").grid(row=0, column=0, sticky="w", pady=5)
        self.entry_nombre = ttk.Entry(form_frame, width=30)
        self.entry_nombre.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Cantidad total:").grid(row=0, column=2, sticky="w", pady=5)
        self.entry_cantidad = ttk.Entry(form_frame, width=15)
        self.entry_cantidad.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Unidad:").grid(row=1, column=0, sticky="w", pady=5)
        self.combo_unidad = ttk.Combobox(form_frame, values=["kg", "g", "lb"], 
                                         state="readonly", width=12)
        self.combo_unidad.grid(row=1, column=1, padx=5, pady=5)
        self.combo_unidad.set("kg")
        
        # Frame para insumos usados mejorado
        insumos_frame = ttk.LabelFrame(form_frame, text="📦 Insumos Usados", padding=15)
        insumos_frame.grid(row=2, column=0, columnspan=4, sticky="ew", pady=10)
        
        ttk.Label(insumos_frame, text="Insumo:").grid(row=0, column=0, sticky="w")
        self.combo_insumo = ttk.Combobox(insumos_frame, width=30, state="readonly")
        self.combo_insumo.grid(row=0, column=1, padx=5)
        self.actualizar_combo_insumos()
        
        ttk.Label(insumos_frame, text="Cantidad usada:").grid(row=0, column=2, sticky="w", padx=5)
        self.entry_cantidad_insumo = ttk.Entry(insumos_frame, width=15)
        self.entry_cantidad_insumo.grid(row=0, column=3, padx=5)
        
        ttk.Button(insumos_frame, text="Agregar Insumo", 
                  command=self.agregar_insumo_al_lote).grid(row=0, column=4, padx=5)
        
        # Lista de insumos agregados
        self.insumos_agregados = {}  # {insumo_id: cantidad}
        self.lista_insumos = tk.Listbox(insumos_frame, height=5)
        self.lista_insumos.grid(row=1, column=0, columnspan=5, sticky="ew", pady=5)
        ttk.Button(insumos_frame, text="Quitar Seleccionado", 
                  command=self.quitar_insumo).grid(row=2, column=0, columnspan=5, pady=5)
        
        # Botones
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=3, column=0, columnspan=4, pady=10)
        
        ttk.Button(btn_frame, text="Crear Lote", command=self.crear_lote).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Limpiar", command=self.limpiar_formulario).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Recargar", command=self.recargar_datos).pack(side="left", padx=5)
        
        # Tabla de lotes mejorada
        table_frame = ttk.LabelFrame(main_frame, text="📋 Lotes de Masa Registrados", padding=15)
        table_frame.pack(fill="both", expand=True)
        
        columns = ("nombre", "cantidad", "unidad", "insumos", "costo")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        
        self.tree.heading("nombre", text="📦 Nombre")
        self.tree.heading("cantidad", text="🔢 Cantidad Total")
        self.tree.heading("unidad", text="📏 Unidad")
        self.tree.heading("insumos", text="🧂 Insumos Usados")
        self.tree.heading("costo", text="💰 Costo Total")
        
        self.tree.column("nombre", width=220, anchor="w")
        self.tree.column("cantidad", width=140, anchor="e")
        self.tree.column("unidad", width=100, anchor="center")
        self.tree.column("insumos", width=320, anchor="w")
        self.tree.column("costo", width=160, anchor="e")
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Botón eliminar mejorado
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="🗑️ Eliminar Seleccionado", 
                  command=self.eliminar_lote).pack(side="left", padx=5)
        
        self.actualizar_tabla()
    
    def actualizar_combo_insumos(self):
        """Actualiza el combo de insumos disponibles"""
        insumos = self.insumo_manager.listar()
        valores = [f"{insumo.nombre} ({insumo.cantidad} {insumo.unidad})" 
                  for insumo in insumos]
        self.combo_insumo["values"] = valores
    
    def agregar_insumo_al_lote(self):
        """Agrega un insumo a la lista del lote"""
        try:
            seleccion = self.combo_insumo.get()
            if not seleccion:
                messagebox.showwarning("Advertencia", "Selecciona un insumo")
                return
            
            cantidad = float(self.entry_cantidad_insumo.get())
            if cantidad <= 0:
                messagebox.showerror("Error", "La cantidad debe ser mayor a 0")
                return
            
            # Obtener ID del insumo
            nombre_insumo = seleccion.split(" (")[0]
            insumos = self.insumo_manager.listar()
            for insumo in insumos:
                if insumo.nombre == nombre_insumo:
                    self.insumos_agregados[insumo.id] = cantidad
                    self.lista_insumos.insert("end", 
                        f"{insumo.nombre}: {cantidad} {insumo.unidad}")
                    self.entry_cantidad_insumo.delete(0, "end")
                    break
            
        except ValueError:
            messagebox.showerror("Error", "Cantidad debe ser un número válido")
    
    def quitar_insumo(self):
        """Quita un insumo de la lista"""
        seleccion = self.lista_insumos.curselection()
        if seleccion:
            index = seleccion[0]
            texto = self.lista_insumos.get(index)
            # Extraer nombre del insumo
            nombre = texto.split(":")[0]
            # Buscar y eliminar
            insumos = self.insumo_manager.listar()
            for insumo in insumos:
                if insumo.nombre == nombre and insumo.id in self.insumos_agregados:
                    del self.insumos_agregados[insumo.id]
                    break
            self.lista_insumos.delete(index)
    
    def crear_lote(self):
        """Crea un nuevo lote de masa"""
        try:
            nombre = self.entry_nombre.get().strip()
            cantidad = float(self.entry_cantidad.get())
            unidad = self.combo_unidad.get()
            
            if not nombre:
                messagebox.showerror("Error", "El nombre es obligatorio")
                return
            
            if not self.insumos_agregados:
                messagebox.showerror("Error", "Debes agregar al menos un insumo")
                return
            
            lote = LoteMasa(nombre, cantidad, unidad, self.insumos_agregados.copy())
            self.masa_manager.agregar(lote)
            self.actualizar_tabla()
            self.limpiar_formulario()
            messagebox.showinfo("Éxito", "Lote de masa creado correctamente")
            
        except ValueError:
            messagebox.showerror("Error", "La cantidad debe ser un número válido")
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear lote: {e}")
    
    def eliminar_lote(self):
        """Elimina el lote seleccionado"""
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Selecciona un lote para eliminar")
            return
        
        item = self.tree.item(seleccion[0])
        nombre = item["values"][0]
        
        masas = self.masa_manager.listar()
        for masa in masas:
            if masa.nombre == nombre:
                if messagebox.askyesno("Confirmar", f"¿Eliminar lote {masa.nombre}?"):
                    self.masa_manager.eliminar(masa.id)
                    self.actualizar_tabla()
                break
    
    def limpiar_formulario(self):
        """Limpia el formulario"""
        self.entry_nombre.delete(0, "end")
        self.entry_cantidad.delete(0, "end")
        self.combo_unidad.set("kg")
        self.insumos_agregados.clear()
        self.lista_insumos.delete(0, "end")
        self.actualizar_combo_insumos()
    
    def recargar_datos(self):
        """Recarga los datos desde los archivos JSON"""
        self.masa_manager.load()  # Recargar desde JSON
        self.insumo_manager.load()  # También recargar insumos
        self.actualizar_combo_insumos()  # Actualizar combo de insumos
        self.actualizar_tabla()  # Actualizar la tabla
        messagebox.showinfo("Éxito", "Datos recargados desde los archivos JSON")
    
    def actualizar_tabla(self):
        """Actualiza la tabla de lotes"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for masa in self.masa_manager.listar():
            # Obtener nombres de insumos
            nombres_insumos = []
            for insumo_id in masa.insumos_usados.keys():
                insumo = self.insumo_manager.obtener(insumo_id)
                if insumo:
                    nombres_insumos.append(insumo.nombre)
            
            insumos_str = ", ".join(nombres_insumos[:3])
            if len(nombres_insumos) > 3:
                insumos_str += "..."
            
            costo = masa.calcular_costo(self.insumo_manager)
            
            self.tree.insert("", "end", values=(
                masa.nombre,
                f"{masa.cantidad_total:,.2f}",
                masa.unidad,
                insumos_str,
                f"${costo:,.2f}"
            ))

