"""
Pantalla de registro de ventas de productos
"""
from datetime import date
import tkinter as tk
from tkinter import ttk, messagebox

from core.ventas import VentasManager
from core.productos import ProductoManager


class VentasScreen:
    """Pantalla para registrar ventas y ver el historial general y por producto"""

    def __init__(self, parent, ventas_manager: VentasManager,
                 producto_manager: ProductoManager, theme):
        self.ventas_manager = ventas_manager
        self.producto_manager = producto_manager
        self.theme = theme

        main_frame = ttk.Frame(parent)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Formulario
        form_frame = ttk.LabelFrame(main_frame, text="🧾 Registrar Venta de Producto", padding=15)
        form_frame.pack(fill="x", pady=(0, 15))

        ttk.Label(form_frame, text="Producto:").grid(row=0, column=0, sticky="w", pady=5)
        self.combo_producto = ttk.Combobox(form_frame, state="readonly", width=28)
        self.combo_producto.grid(row=0, column=1, padx=5, pady=5)
        self.combo_producto.bind("<<ComboboxSelected>>", self._autocompletar_precio)

        ttk.Label(form_frame, text="Cantidad:").grid(row=0, column=2, sticky="w", pady=5)
        self.entry_cantidad = ttk.Entry(form_frame, width=15)
        self.entry_cantidad.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(form_frame, text="Precio unitario:").grid(row=1, column=0, sticky="w", pady=5)
        self.entry_precio = ttk.Entry(form_frame, width=15)
        self.entry_precio.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(form_frame, text="Fecha (YYYY-MM-DD):").grid(row=1, column=2, sticky="w", pady=5)
        self.entry_fecha = ttk.Entry(form_frame, width=15)
        self.entry_fecha.grid(row=1, column=3, padx=5, pady=5)
        self.entry_fecha.insert(0, date.today().isoformat())

        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=2, column=0, columnspan=4, pady=(10, 0))
        ttk.Button(btn_frame, text="Registrar venta", command=self.registrar).pack(side="left", padx=2)
        ttk.Button(btn_frame, text="Limpiar", command=self.limpiar).pack(side="left", padx=2)

        # Contenedor de dos tablas
        tablas = ttk.Frame(main_frame)
        tablas.pack(fill="both", expand=True)

        # Historial general
        hist_frame = ttk.LabelFrame(tablas, text="📋 Historial de Ventas", padding=10)
        hist_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        columns = ("fecha", "producto", "cantidad", "precio", "total")
        self.tree = ttk.Treeview(hist_frame, columns=columns, show="headings", height=14)
        encabezados = {"fecha": "📅 Fecha", "producto": "🍽️ Producto",
                       "cantidad": "🔢 Unid.", "precio": "💵 Precio/U", "total": "💰 Total"}
        anchos = {"fecha": 100, "producto": 170, "cantidad": 70, "precio": 110, "total": 120}
        for col in columns:
            self.tree.heading(col, text=encabezados[col])
            anchor = "w" if col == "producto" else ("center" if col == "fecha" else "e")
            self.tree.column(col, width=anchos[col], anchor=anchor)
        sb1 = ttk.Scrollbar(hist_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb1.set)
        self.tree.pack(side="left", fill="both", expand=True)
        sb1.pack(side="right", fill="y")

        # Resumen por producto
        res_frame = ttk.LabelFrame(tablas, text="📊 Ventas por Producto", padding=10)
        res_frame.pack(side="left", fill="both", expand=True, padx=(5, 0))
        cols2 = ("producto", "unidades", "ingreso")
        self.tree_resumen = ttk.Treeview(res_frame, columns=cols2, show="headings", height=14)
        self.tree_resumen.heading("producto", text="🍽️ Producto")
        self.tree_resumen.heading("unidades", text="🔢 Unidades")
        self.tree_resumen.heading("ingreso", text="💰 Ingreso")
        self.tree_resumen.column("producto", width=170, anchor="w")
        self.tree_resumen.column("unidades", width=90, anchor="e")
        self.tree_resumen.column("ingreso", width=130, anchor="e")
        self.tree_resumen.pack(fill="both", expand=True)

        bottom = ttk.Frame(main_frame)
        bottom.pack(fill="x", pady=10)
        ttk.Button(bottom, text="🗑️ Eliminar venta seleccionada", command=self.eliminar).pack(side="left", padx=5)
        self.lbl_total = ttk.Label(bottom, text="Ingresos: $0 COP | Unidades: 0",
                                   font=("Segoe UI", 10, "bold"))
        self.lbl_total.pack(side="right", padx=5)

        self.actualizar_datos()

    def _cargar_combo_productos(self):
        productos = sorted(self.producto_manager.listar(), key=lambda p: p.nombre)
        self._mapa_productos = {p.nombre: p.id for p in productos}
        self.combo_producto["values"] = list(self._mapa_productos.keys())
        if self._mapa_productos and not self.combo_producto.get():
            self.combo_producto.set(next(iter(self._mapa_productos)))
            self._autocompletar_precio()

    def _autocompletar_precio(self, event=None):
        nombre = self.combo_producto.get()
        pid = getattr(self, "_mapa_productos", {}).get(nombre)
        producto = self.producto_manager.obtener(pid) if pid else None
        if producto:
            self.entry_precio.delete(0, "end")
            self.entry_precio.insert(0, f"{producto.precio_venta:.0f}")

    def registrar(self):
        try:
            nombre = self.combo_producto.get()
            if not nombre:
                messagebox.showerror("Error", "Selecciona un producto")
                return
            pid = self._mapa_productos.get(nombre)
            cantidad = int(float(self.entry_cantidad.get()))
            precio_txt = self.entry_precio.get().strip()
            precio = float(precio_txt) if precio_txt else None
            fecha = self.entry_fecha.get().strip() or date.today().isoformat()

            if cantidad <= 0:
                messagebox.showerror("Error", "La cantidad debe ser positiva")
                return

            venta = self.ventas_manager.registrar(pid, cantidad, precio, fecha)
            if venta is None:
                messagebox.showerror("Error", "El producto no existe")
                return
            self.actualizar_datos()
            self.limpiar()
            messagebox.showinfo("Éxito", "Venta registrada correctamente")
        except ValueError:
            messagebox.showerror("Error", "Cantidad y precio deben ser números válidos")

    def eliminar(self):
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Selecciona una venta para eliminar")
            return
        venta_id = self.tree.item(seleccion[0])["tags"][0]
        if messagebox.askyesno("Confirmar", "¿Eliminar la venta seleccionada?"):
            self.ventas_manager.eliminar(venta_id)
            self.actualizar_datos()

    def limpiar(self):
        self.entry_cantidad.delete(0, "end")
        self.entry_fecha.delete(0, "end")
        self.entry_fecha.insert(0, date.today().isoformat())

    def actualizar_datos(self):
        self._cargar_combo_productos()
        for item in self.tree.get_children():
            self.tree.delete(item)
        for v in self.ventas_manager.listar():
            self.tree.insert("", "end", tags=(v.id,), values=(
                v.fecha, v.nombre, v.cantidad,
                f"${v.precio_unitario:,.0f}", f"${v.total:,.0f}",
            ))

        for item in self.tree_resumen.get_children():
            self.tree_resumen.delete(item)
        resumen = self.ventas_manager.resumen_por_producto()
        for datos in sorted(resumen.values(), key=lambda d: d["ingreso"], reverse=True):
            self.tree_resumen.insert("", "end", values=(
                datos["nombre"], f"{datos['unidades']:,}", f"${datos['ingreso']:,.0f}",
            ))

        self.lbl_total.config(
            text=f"Ingresos: ${self.ventas_manager.total_ingresos():,.0f} COP | "
                 f"Unidades: {self.ventas_manager.total_unidades():,}"
        )
