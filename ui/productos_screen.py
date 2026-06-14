"""
Pantalla de gestión de productos
"""
import tkinter as tk
from tkinter import ttk, messagebox
from core.productos import Producto, ProductoManager
from core.masas import MasaManager
from core.insumos import InsumoManager

class ProductosScreen:
    """Pantalla para gestionar productos"""
    
    def __init__(self, parent, producto_manager: ProductoManager,
                 masa_manager: MasaManager, insumo_manager: InsumoManager, theme):
        self.producto_manager = producto_manager
        self.masa_manager = masa_manager
        self.insumo_manager = insumo_manager
        self.theme = theme
        
        # Frame principal
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Frame de formulario mejorado
        form_frame = ttk.LabelFrame(main_frame, text="➕ Agregar Producto", padding=15)
        form_frame.pack(fill="x", pady=(0, 15))
        
        # Campos básicos
        ttk.Label(form_frame, text="Nombre:").grid(row=0, column=0, sticky="w", pady=5)
        self.entry_nombre = ttk.Entry(form_frame, width=30)
        self.entry_nombre.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Masa asociada:").grid(row=0, column=2, sticky="w", pady=5)
        self.combo_masa = ttk.Combobox(form_frame, width=25, state="readonly")
        self.combo_masa.grid(row=0, column=3, padx=5, pady=5)
        self.actualizar_combo_masas()
        
        ttk.Label(form_frame, text="Precio de venta:").grid(row=1, column=0, sticky="w", pady=5)
        self.entry_precio = ttk.Entry(form_frame, width=15)
        self.entry_precio.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Demanda estimada/día:").grid(row=1, column=2, sticky="w", pady=5)
        self.entry_demanda = ttk.Entry(form_frame, width=15)
        self.entry_demanda.grid(row=1, column=3, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Categoría:").grid(row=2, column=0, sticky="w", pady=5)
        self.entry_categoria = ttk.Entry(form_frame, width=30)
        self.entry_categoria.grid(row=2, column=1, padx=5, pady=5)
        
        # Frame para insumos extra mejorado
        insumos_frame = ttk.LabelFrame(form_frame, text="🧂 Insumos Extra (Rellenos, Salsas, etc.)", padding=15)
        insumos_frame.grid(row=3, column=0, columnspan=4, sticky="ew", pady=10)
        
        ttk.Label(insumos_frame, text="Insumo:").grid(row=0, column=0, sticky="w")
        self.combo_insumo = ttk.Combobox(insumos_frame, width=30, state="readonly")
        self.combo_insumo.grid(row=0, column=1, padx=5)
        self.actualizar_combo_insumos()
        
        ttk.Label(insumos_frame, text="Porciones usadas:").grid(row=0, column=2, sticky="w", padx=5)
        self.entry_porciones = ttk.Entry(insumos_frame, width=15)
        self.entry_porciones.grid(row=0, column=3, padx=5)
        
        ttk.Button(insumos_frame, text="Agregar", 
                  command=self.agregar_insumo_extra).grid(row=0, column=4, padx=5)
        
        # Lista de insumos extra
        self.insumos_extra = {}  # {insumo_id: porciones}
        self.lista_insumos = tk.Listbox(insumos_frame, height=4)
        self.lista_insumos.grid(row=1, column=0, columnspan=5, sticky="ew", pady=5)
        ttk.Button(insumos_frame, text="Quitar Seleccionado", 
                  command=self.quitar_insumo_extra).grid(row=2, column=0, columnspan=5, pady=5)
        
        # Botones
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=4, column=0, columnspan=4, pady=10)
        
        ttk.Button(btn_frame, text="Agregar Producto", command=self.agregar_producto).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Limpiar", command=self.limpiar_formulario).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Recargar", command=self.recargar_datos).pack(side="left", padx=5)
        
        # Tabla de productos mejorada
        table_frame = ttk.LabelFrame(main_frame, text="🍽️ Productos Registrados", padding=15)
        table_frame.pack(fill="both", expand=True)
        
        columns = ("nombre", "masa", "precio", "demanda", "categoria")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        
        self.tree.heading("nombre", text="📦 Nombre")
        self.tree.heading("masa", text="🥟 Masa")
        self.tree.heading("precio", text="💰 Precio Venta")
        self.tree.heading("demanda", text="📊 Demanda/día")
        self.tree.heading("categoria", text="🏷️ Categoría")
        
        self.tree.column("nombre", width=250, anchor="w")
        self.tree.column("masa", width=180, anchor="w")
        self.tree.column("precio", width=140, anchor="e")
        self.tree.column("demanda", width=140, anchor="e")
        self.tree.column("categoria", width=180, anchor="w")
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Botón eliminar mejorado
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="🗑️ Eliminar Seleccionado", 
                  command=self.eliminar_producto).pack(side="left", padx=5)
        
        self.actualizar_tabla()
    
    def actualizar_combo_masas(self):
        """Actualiza el combo de masas"""
        masas = self.masa_manager.listar()
        valores = ["Ninguna"] + [masa.nombre for masa in masas]
        self.combo_masa["values"] = valores
        if valores:
            self.combo_masa.set(valores[0])
    
    def actualizar_combo_insumos(self):
        """Actualiza el combo de insumos"""
        insumos = self.insumo_manager.listar()
        valores = [f"{insumo.nombre} ({insumo.categoria})" for insumo in insumos]
        self.combo_insumo["values"] = valores
    
    def agregar_insumo_extra(self):
        """Agrega un insumo extra al producto"""
        try:
            seleccion = self.combo_insumo.get()
            if not seleccion:
                messagebox.showwarning("Advertencia", "Selecciona un insumo")
                return
            
            porciones = float(self.entry_porciones.get())
            if porciones <= 0:
                messagebox.showerror("Error", "Las porciones deben ser mayor a 0")
                return
            
            # Obtener ID del insumo
            nombre_insumo = seleccion.split(" (")[0]
            insumos = self.insumo_manager.listar()
            for insumo in insumos:
                if insumo.nombre == nombre_insumo:
                    self.insumos_extra[insumo.id] = porciones
                    self.lista_insumos.insert("end", 
                        f"{insumo.nombre}: {porciones} porciones")
                    self.entry_porciones.delete(0, "end")
                    break
            
        except ValueError:
            messagebox.showerror("Error", "Las porciones deben ser un número válido")
    
    def quitar_insumo_extra(self):
        """Quita un insumo extra"""
        seleccion = self.lista_insumos.curselection()
        if seleccion:
            index = seleccion[0]
            texto = self.lista_insumos.get(index)
            nombre = texto.split(":")[0]
            # Buscar y eliminar
            insumos = self.insumo_manager.listar()
            for insumo in insumos:
                if insumo.nombre == nombre and insumo.id in self.insumos_extra:
                    del self.insumos_extra[insumo.id]
                    break
            self.lista_insumos.delete(index)
    
    def agregar_producto(self):
        """Agrega un nuevo producto"""
        try:
            nombre = self.entry_nombre.get().strip()
            precio = float(self.entry_precio.get())
            demanda = int(self.entry_demanda.get())
            categoria = self.entry_categoria.get().strip()
            
            if not nombre:
                messagebox.showerror("Error", "El nombre es obligatorio")
                return
            
            # Obtener masa_id
            masa_nombre = self.combo_masa.get()
            masa_id = None
            if masa_nombre and masa_nombre != "Ninguna":
                masas = self.masa_manager.listar()
                for masa in masas:
                    if masa.nombre == masa_nombre:
                        masa_id = masa.id
                        break
            
            producto = Producto(
                nombre=nombre,
                masa_id=masa_id,
                insumos_extra=self.insumos_extra.copy(),
                precio_venta=precio,
                demanda_estimada=demanda,
                categoria=categoria
            )
            
            self.producto_manager.agregar(producto)
            self.actualizar_tabla()
            self.limpiar_formulario()
            messagebox.showinfo("Éxito", "Producto agregado correctamente")
            
        except ValueError:
            messagebox.showerror("Error", "Verifica que los valores numéricos sean correctos")
        except Exception as e:
            messagebox.showerror("Error", f"Error al agregar producto: {e}")
    
    def eliminar_producto(self):
        """Elimina el producto seleccionado"""
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Selecciona un producto para eliminar")
            return
        
        item = self.tree.item(seleccion[0])
        nombre = item["values"][0]
        
        productos = self.producto_manager.listar()
        for producto in productos:
            if producto.nombre == nombre:
                if messagebox.askyesno("Confirmar", f"¿Eliminar producto {producto.nombre}?"):
                    self.producto_manager.eliminar(producto.id)
                    self.actualizar_tabla()
                break
    
    def limpiar_formulario(self):
        """Limpia el formulario"""
        self.entry_nombre.delete(0, "end")
        self.entry_precio.delete(0, "end")
        self.entry_demanda.delete(0, "end")
        self.entry_categoria.delete(0, "end")
        self.insumos_extra.clear()
        self.lista_insumos.delete(0, "end")
        self.actualizar_combo_masas()
        self.actualizar_combo_insumos()
    
    def recargar_datos(self):
        """Recarga los datos desde los archivos JSON"""
        self.producto_manager.load()  # Recargar desde JSON
        self.masa_manager.load()  # También recargar masas
        self.insumo_manager.load()  # También recargar insumos
        self.actualizar_combo_masas()  # Actualizar combos
        self.actualizar_combo_insumos()  # Actualizar combos
        self.actualizar_tabla()  # Actualizar la tabla
        messagebox.showinfo("Éxito", "Datos recargados desde los archivos JSON")
    
    def actualizar_tabla(self):
        """Actualiza la tabla de productos"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for producto in self.producto_manager.listar():
            masa_nombre = "Ninguna"
            if producto.masa_id:
                masa = self.masa_manager.obtener(producto.masa_id)
                if masa:
                    masa_nombre = masa.nombre
            
            self.tree.insert("", "end", values=(
                producto.nombre,
                masa_nombre,
                f"${producto.precio_venta:,.2f}",
                producto.demanda_estimada,
                producto.categoria
            ))

