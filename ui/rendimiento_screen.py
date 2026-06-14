"""
Pantalla de gestión de rendimiento de lotes

El RENDIMIENTO indica cuántos productos se pueden producir con un lote de masa.
Por ejemplo, si haces un lote de masa de 6 lb, ese lote puede producir:
- 20 empanadas de carne
- 15 empanadas de pollo
- 10 pasteles

El rendimiento se usa para calcular el costo por unidad equivalente de cada producto,
distribuyendo el costo total del lote entre todos los productos que se pueden hacer.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from core.masas import MasaManager
from core.productos import ProductoManager, Producto
from core.insumos import InsumoManager

class RendimientoScreen:
    """
    Pantalla para gestionar rendimiento de lotes
    
    Esta pantalla permite registrar cuántos productos se pueden hacer con cada
    lote de masa. Esta información es crucial para calcular correctamente los
    costos unitarios de los productos.
    """
    
    def __init__(self, parent, masa_manager: MasaManager,
                 producto_manager: ProductoManager, 
                 insumo_manager: InsumoManager, theme):
        self.masa_manager = masa_manager
        self.producto_manager = producto_manager
        self.insumo_manager = insumo_manager
        self.theme = theme
        
        # Frame principal
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Frame de selección mejorado
        select_frame = ttk.LabelFrame(main_frame, text="🔍 Seleccionar Lote de Masa", padding=15)
        select_frame.pack(fill="x", pady=(0, 15))
        
        ttk.Label(select_frame, text="Lote:").pack(side="left", padx=5)
        self.combo_masa = ttk.Combobox(select_frame, width=40, state="readonly")
        self.combo_masa.pack(side="left", padx=5)
        self.combo_masa.bind("<<ComboboxSelected>>", self.on_masa_selected)
        
        # Frame de rendimiento mejorado
        rendimiento_frame = ttk.LabelFrame(main_frame, text="📊 Rendimiento del Lote", padding=15)
        rendimiento_frame.pack(fill="both", expand=True, pady=(0, 15))
        
        # Lista de productos y cantidades
        self.productos_rendimiento = {}  # {producto_id: cantidad}
        
        ttk.Label(rendimiento_frame, text="Producto:").grid(row=0, column=0, sticky="w", pady=5)
        self.combo_producto = ttk.Combobox(rendimiento_frame, width=30, state="readonly")
        self.combo_producto.grid(row=0, column=1, padx=5, pady=5)
        self.actualizar_combo_productos()
        
        ttk.Label(rendimiento_frame, text="Cantidad producida:").grid(row=0, column=2, sticky="w", pady=5)
        self.entry_cantidad = ttk.Entry(rendimiento_frame, width=15)
        self.entry_cantidad.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Button(rendimiento_frame, text="Agregar", 
                  command=self.agregar_rendimiento).grid(row=0, column=4, padx=5, pady=5)
        
        # Lista de rendimientos mejorada
        self.lista_rendimientos = ttk.Treeview(rendimiento_frame, 
                                               columns=("producto", "cantidad"),
                                               show="headings", height=10)
        self.lista_rendimientos.heading("producto", text="📦 Producto")
        self.lista_rendimientos.heading("cantidad", text="🔢 Cantidad Producida")
        self.lista_rendimientos.column("producto", width=350, anchor="w")
        self.lista_rendimientos.column("cantidad", width=180, anchor="e")
        self.lista_rendimientos.grid(row=1, column=0, columnspan=5, sticky="ew", pady=10)
        
        ttk.Button(rendimiento_frame, text="🗑️ Quitar Seleccionado", 
                  command=self.quitar_rendimiento).grid(row=2, column=0, columnspan=5, pady=8)
        
        # Botones de acción mejorados
        btn_frame_rendimiento = ttk.Frame(rendimiento_frame)
        btn_frame_rendimiento.grid(row=3, column=0, columnspan=5, pady=12)
        
        ttk.Button(btn_frame_rendimiento, text="💾 Guardar Rendimiento", 
                  command=self.guardar_rendimiento).pack(side="left", padx=5)
        ttk.Button(btn_frame_rendimiento, text="🔄 Actualizar", 
                  command=self.actualizar_datos).pack(side="left", padx=5)
        
        # Frame de información mejorado
        info_frame = ttk.LabelFrame(main_frame, text="ℹ️ Información del Lote", padding=15)
        info_frame.pack(fill="x")
        
        self.label_costo = ttk.Label(info_frame, text="💰 Costo del lote: $0.00",
                                     font=('Segoe UI', 10))
        self.label_costo.pack(anchor="w", pady=3)
        
        self.label_costo_unidad = ttk.Label(info_frame, text="📊 Costo por unidad equivalente: $0.00",
                                           font=('Segoe UI', 10))
        self.label_costo_unidad.pack(anchor="w", pady=3)
        
        self.actualizar_datos()
    
    def actualizar_combo_productos(self):
        """
        Actualiza el combo de productos.

        Solo muestra los productos que realmente usan la masa seleccionada
        (producto.masa_id == masa_actual.id). Si no hay lote seleccionado,
        el combo queda vacío para forzar a elegir primero un lote.
        """
        if hasattr(self, "masa_actual") and self.masa_actual:
            productos = [
                p for p in self.producto_manager.listar()
                if p.masa_id == self.masa_actual.id
            ]
        else:
            productos = []
        valores = [producto.nombre for producto in productos]
        self.combo_producto["values"] = valores
        # Mantener selección válida
        if valores:
            if self.combo_producto.get() not in valores:
                self.combo_producto.set(valores[0])
        else:
            self.combo_producto.set("")
    
    def actualizar_combo_masas(self):
        """Actualiza el combo de masas"""
        masas = self.masa_manager.listar()
        valores = [masa.nombre for masa in masas]
        self.combo_masa["values"] = valores
    
    def on_masa_selected(self, event=None):
        """Cuando se selecciona una masa"""
        self.cargar_rendimiento_masa()
        # Filtrar el combo de productos a los que usan esta masa
        self.actualizar_combo_productos()
        self.actualizar_info()
    
    def cargar_rendimiento_masa(self):
        """Carga el rendimiento de la masa seleccionada"""
        nombre_masa = self.combo_masa.get()
        if not nombre_masa:
            return
        
        masas = self.masa_manager.listar()
        for masa in masas:
            if masa.nombre == nombre_masa:
                self.masa_actual = masa
                # Cargar rendimientos existentes
                self.productos_rendimiento = masa.rendimiento.copy()
                self.actualizar_lista_rendimientos()
                break
    
    def agregar_rendimiento(self):
        """Agrega un producto al rendimiento"""
        try:
            nombre_producto = self.combo_producto.get()
            cantidad = int(self.entry_cantidad.get())
            
            if not nombre_producto:
                messagebox.showwarning("Advertencia", "Selecciona un producto")
                return
            
            if cantidad <= 0:
                messagebox.showerror("Error", "La cantidad debe ser mayor a 0")
                return
            
            # Buscar producto
            productos = self.producto_manager.listar()
            for producto in productos:
                if producto.nombre == nombre_producto:
                    # Validar que el producto realmente use esta masa
                    if hasattr(self, "masa_actual") and producto.masa_id != self.masa_actual.id:
                        messagebox.showwarning(
                            "Advertencia",
                            f"'{producto.nombre}' no usa la masa '{self.masa_actual.nombre}'. "
                            "Asigna su rendimiento en el lote que le corresponde."
                        )
                        return
                    self.productos_rendimiento[producto.id] = cantidad
                    self.actualizar_lista_rendimientos()
                    self.entry_cantidad.delete(0, "end")
                    self.actualizar_info()
                    break
            
        except ValueError:
            messagebox.showerror("Error", "La cantidad debe ser un número entero")
    
    def quitar_rendimiento(self):
        """Quita un producto del rendimiento"""
        seleccion = self.lista_rendimientos.selection()
        if seleccion:
            item = self.lista_rendimientos.item(seleccion[0])
            producto_id = item["values"][0]
            if producto_id in self.productos_rendimiento:
                del self.productos_rendimiento[producto_id]
                self.actualizar_lista_rendimientos()
                self.actualizar_info()
    
    def actualizar_lista_rendimientos(self):
        """Actualiza la lista de rendimientos"""
        for item in self.lista_rendimientos.get_children():
            self.lista_rendimientos.delete(item)
        
        for producto_id, cantidad in self.productos_rendimiento.items():
            producto = self.producto_manager.obtener(producto_id)
            if producto:
                self.lista_rendimientos.insert("", "end", 
                    values=(producto_id, f"{producto.nombre}: {cantidad} unidades"))
    
    def guardar_rendimiento(self):
        """
        Guarda el rendimiento en el lote
        
        Guarda la información de cuántos productos se pueden hacer con este
        lote de masa. Esta información se usa para calcular el costo por
        unidad equivalente de cada producto.
        """
        if not hasattr(self, 'masa_actual'):
            messagebox.showwarning("Advertencia", "Selecciona un lote de masa primero")
            return
        
        if not self.productos_rendimiento:
            messagebox.showwarning("Advertencia", "Agrega al menos un producto al rendimiento")
            return
        
        # Actualizar rendimiento del lote
        self.masa_actual.rendimiento = self.productos_rendimiento.copy()
        # Guardar en el manager (esto guarda en JSON)
        self.masa_manager.save()
        messagebox.showinfo("Éxito", "Rendimiento guardado correctamente")
        # Actualizar información mostrada
        self.actualizar_info()
    
    def actualizar_info(self):
        """Actualiza la información del lote"""
        if not hasattr(self, 'masa_actual'):
            self.label_costo.config(text="💰 Costo del lote: $0.00")
            self.label_costo_unidad.config(text="📊 Costo por unidad equivalente: $0.00")
            return
        
        costo_lote = self.masa_actual.calcular_costo(self.insumo_manager)
        costo_unidad = self.masa_actual.costo_por_unidad_equivalente(self.insumo_manager)
        
        self.label_costo.config(text=f"💰 Costo del lote: ${costo_lote:,.2f}")
        self.label_costo_unidad.config(text=f"📊 Costo por unidad equivalente: ${costo_unidad:,.2f}")
    
    def actualizar_datos(self):
        """
        Actualiza todos los datos de la pantalla
        
        Este método recarga los datos desde los archivos JSON y actualiza
        todos los combos y la información mostrada. Útil cuando se hacen
        cambios en otras pantallas (como agregar nuevos lotes de masa).
        """
        # Recargar datos desde JSON
        self.masa_manager.load()
        self.producto_manager.load()
        self.insumo_manager.load()
        
        # Actualizar combos
        self.actualizar_combo_masas()
        self.actualizar_combo_productos()
        
        # Si hay una masa seleccionada, recargarla y actualizar información
        if hasattr(self, 'masa_actual') and self.combo_masa.get():
            # Recargar la masa actual desde el manager
            nombre_masa = self.combo_masa.get()
            masas = self.masa_manager.listar()
            for masa in masas:
                if masa.nombre == nombre_masa:
                    self.masa_actual = masa
                    # Recargar rendimientos existentes
                    self.productos_rendimiento = masa.rendimiento.copy()
                    self.actualizar_lista_rendimientos()
                    break
        
        # Actualizar información del lote
        if hasattr(self, 'masa_actual'):
            self.actualizar_info()

