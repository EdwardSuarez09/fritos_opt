"""
Pantalla unificada de Inventario

Combina en una sola vista:
- Arriba: registro de compras (suma stock y actualiza precio).
- Abajo: la tabla de insumos que se actualiza en vivo, junto al historial de
  compras. Así "comprar" y "ver el inventario" van de la mano en la misma
  pantalla, evitando confusión entre módulos separados.
"""
from datetime import date
import tkinter as tk
from tkinter import ttk, messagebox

from core.insumos import Insumo, InsumoManager
from core.compras import ComprasManager


class InventarioScreen:
    """Inventario unificado: compra arriba, insumos y compras abajo"""

    def __init__(self, parent, inventario, compras_manager: ComprasManager, theme):
        self.inventario = inventario
        self.insumo_manager: InsumoManager = inventario.insumos
        self.compras_manager = compras_manager
        self.theme = theme

        main_frame = ttk.Frame(parent)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # ---------- ARRIBA: registrar compra ----------
        form_frame = ttk.LabelFrame(
            main_frame, text="🛒 Registrar compra (suma al stock del inventario)", padding=15
        )
        form_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(form_frame, text="Insumo:").grid(row=0, column=0, sticky="w", pady=5)
        self.combo_insumo = ttk.Combobox(form_frame, state="readonly", width=26)
        self.combo_insumo.grid(row=0, column=1, padx=5, pady=5)
        self.combo_insumo.bind("<<ComboboxSelected>>", self._autocompletar_precio)

        ttk.Label(form_frame, text="Cantidad:").grid(row=0, column=2, sticky="w", pady=5)
        self.entry_cantidad = ttk.Entry(form_frame, width=14)
        self.entry_cantidad.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(form_frame, text="Precio por unidad:").grid(row=1, column=0, sticky="w", pady=5)
        self.entry_precio = ttk.Entry(form_frame, width=14)
        self.entry_precio.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(form_frame, text="Fecha (YYYY-MM-DD):").grid(row=1, column=2, sticky="w", pady=5)
        self.entry_fecha = ttk.Entry(form_frame, width=14)
        self.entry_fecha.grid(row=1, column=3, padx=5, pady=5)
        self.entry_fecha.insert(0, date.today().isoformat())

        btns = ttk.Frame(form_frame)
        btns.grid(row=0, column=4, rowspan=2, padx=(15, 5))
        ttk.Button(btns, text="Registrar compra", command=self.registrar_compra).pack(fill="x", pady=2)
        ttk.Button(btns, text="➕ Nuevo insumo", command=self.nuevo_insumo).pack(fill="x", pady=2)

        self.lbl_feedback = ttk.Label(form_frame, text="", font=("Segoe UI", 9, "bold"))
        self.lbl_feedback.grid(row=2, column=0, columnspan=5, sticky="w", pady=(8, 0))

        # ---------- ABAJO: notebook con insumos y compras ----------
        sub_nb = ttk.Notebook(main_frame)
        sub_nb.pack(fill="both", expand=True)

        # Pestaña: insumos en vivo
        tab_insumos = ttk.Frame(sub_nb)
        sub_nb.add(tab_insumos, text="📦 Insumos en inventario")
        cols = ("nombre", "cantidad", "unidad", "precio", "categoria", "costo_total")
        self.tree = ttk.Treeview(tab_insumos, columns=cols, show="headings", height=14)
        encs = {"nombre": "📦 Nombre", "cantidad": "🔢 Stock", "unidad": "📏 Unidad",
                "precio": "💵 Precio/U", "categoria": "🏷️ Categoría", "costo_total": "💰 Valor"}
        anchos = {"nombre": 200, "cantidad": 110, "unidad": 90, "precio": 130,
                  "categoria": 160, "costo_total": 140}
        for c in cols:
            self.tree.heading(c, text=encs[c])
            anchor = "w" if c in ("nombre", "categoria") else ("center" if c == "unidad" else "e")
            self.tree.column(c, width=anchos[c], anchor=anchor)
        sb = ttk.Scrollbar(tab_insumos, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        self.tree.bind("<Double-1>", lambda e: self.editar_insumo())

        acc = ttk.Frame(tab_insumos)
        acc.pack(side="bottom", fill="x")  # placeholder (no usado, botones abajo)

        # Pestaña: historial de compras
        tab_compras = ttk.Frame(sub_nb)
        sub_nb.add(tab_compras, text="🧾 Historial de compras")
        cols2 = ("fecha", "insumo", "cantidad", "unidad", "precio", "total")
        self.tree_compras = ttk.Treeview(tab_compras, columns=cols2, show="headings", height=14)
        encs2 = {"fecha": "📅 Fecha", "insumo": "📦 Insumo", "cantidad": "🔢 Cantidad",
                 "unidad": "📏 Unidad", "precio": "💵 Precio/U", "total": "💰 Total"}
        anchos2 = {"fecha": 110, "insumo": 200, "cantidad": 100, "unidad": 90,
                   "precio": 130, "total": 140}
        for c in cols2:
            self.tree_compras.heading(c, text=encs2[c])
            anchor = "w" if c == "insumo" else ("center" if c in ("fecha", "unidad") else "e")
            self.tree_compras.column(c, width=anchos2[c], anchor=anchor)
        sb2 = ttk.Scrollbar(tab_compras, orient="vertical", command=self.tree_compras.yview)
        self.tree_compras.configure(yscrollcommand=sb2.set)
        self.tree_compras.pack(side="left", fill="both", expand=True)
        sb2.pack(side="right", fill="y")

        # ---------- Barra de acciones ----------
        barra = ttk.Frame(main_frame)
        barra.pack(fill="x", pady=10)
        ttk.Button(barra, text="✏️ Editar insumo", command=self.editar_insumo).pack(side="left", padx=3)
        ttk.Button(barra, text="🗑️ Eliminar insumo", command=self.eliminar_insumo).pack(side="left", padx=3)
        ttk.Button(barra, text="🗑️ Eliminar compra", command=self.eliminar_compra).pack(side="left", padx=3)
        self.lbl_total = ttk.Label(barra, text="Total gastado: $0 COP", font=("Segoe UI", 10, "bold"))
        self.lbl_total.pack(side="right", padx=5)

        self.actualizar_datos()

    # ---------------- Lógica de compras ----------------
    def _cargar_combo(self):
        insumos = sorted(self.insumo_manager.listar(), key=lambda i: i.nombre)
        self._mapa = {i.nombre: i.id for i in insumos}
        seleccion_actual = self.combo_insumo.get()
        self.combo_insumo["values"] = list(self._mapa.keys())
        if seleccion_actual in self._mapa:
            self.combo_insumo.set(seleccion_actual)
        elif self._mapa:
            self.combo_insumo.set(next(iter(self._mapa)))
            self._autocompletar_precio()

    def _autocompletar_precio(self, event=None):
        pid = getattr(self, "_mapa", {}).get(self.combo_insumo.get())
        insumo = self.insumo_manager.obtener(pid) if pid else None
        if insumo:
            self.entry_precio.delete(0, "end")
            self.entry_precio.insert(0, f"{insumo.precio_unidad:.0f}")

    def registrar_compra(self):
        try:
            nombre = self.combo_insumo.get()
            if not nombre:
                messagebox.showerror("Error", "Selecciona un insumo (o crea uno nuevo)")
                return
            insumo_id = self._mapa.get(nombre)
            insumo = self.insumo_manager.obtener(insumo_id)
            stock_antes = insumo.cantidad
            unidad = insumo.unidad
            cantidad = float(self.entry_cantidad.get())
            precio = float(self.entry_precio.get())
            fecha = self.entry_fecha.get().strip() or date.today().isoformat()

            if cantidad <= 0 or precio < 0:
                messagebox.showerror("Error", "Cantidad y precio deben ser positivos")
                return

            self.compras_manager.registrar(insumo_id, cantidad, precio, fecha)
            stock_despues = self.insumo_manager.obtener(insumo_id).cantidad

            self.actualizar_datos()
            self.entry_cantidad.delete(0, "end")
            self.lbl_feedback.config(
                text=f"✅ {nombre}: {stock_antes:g} → {stock_despues:g} {unidad} · "
                     f"precio ${precio:,.0f}",
                foreground=self.theme.success,
            )
            # Resaltar el insumo afectado en la tabla
            self._resaltar(insumo_id)
        except ValueError:
            messagebox.showerror("Error", "Cantidad y precio deben ser números válidos")

    # ---------------- Lógica de catálogo (ficha) ----------------
    def nuevo_insumo(self):
        self._dialogo_insumo(None)

    def editar_insumo(self):
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Selecciona un insumo para editar")
            return
        nombre = self.tree.item(seleccion[0])["values"][0]
        insumo = next((i for i in self.insumo_manager.listar() if i.nombre == nombre), None)
        if insumo:
            self._dialogo_insumo(insumo)

    def _dialogo_insumo(self, insumo):
        """Ventana para crear o editar la ficha de un insumo"""
        es_nuevo = insumo is None
        top = tk.Toplevel(self.tree.winfo_toplevel())
        top.title("Nuevo insumo" if es_nuevo else f"Editar: {insumo.nombre}")
        top.configure(bg=self.theme.bg)
        top.transient(self.tree.winfo_toplevel())
        top.grab_set()

        frm = ttk.Frame(top, padding=15)
        frm.pack(fill="both", expand=True)

        ttk.Label(frm, text="Nombre:").grid(row=0, column=0, sticky="w", pady=5)
        e_nombre = ttk.Entry(frm, width=26)
        e_nombre.grid(row=0, column=1, pady=5, padx=5)

        ttk.Label(frm, text="Stock inicial:").grid(row=1, column=0, sticky="w", pady=5)
        e_stock = ttk.Entry(frm, width=26)
        e_stock.grid(row=1, column=1, pady=5, padx=5)

        ttk.Label(frm, text="Unidad:").grid(row=2, column=0, sticky="w", pady=5)
        c_unidad = ttk.Combobox(frm, values=Insumo.UNIDADES, state="readonly", width=24)
        c_unidad.grid(row=2, column=1, pady=5, padx=5)
        c_unidad.set(Insumo.UNIDADES[0])

        ttk.Label(frm, text="Precio por unidad:").grid(row=3, column=0, sticky="w", pady=5)
        e_precio = ttk.Entry(frm, width=26)
        e_precio.grid(row=3, column=1, pady=5, padx=5)

        ttk.Label(frm, text="Categoría:").grid(row=4, column=0, sticky="w", pady=5)
        c_cat = ttk.Combobox(frm, values=Insumo.CATEGORIAS, state="readonly", width=24)
        c_cat.grid(row=4, column=1, pady=5, padx=5)
        c_cat.set(Insumo.CATEGORIAS[0])

        if not es_nuevo:
            e_nombre.insert(0, insumo.nombre)
            e_stock.insert(0, f"{insumo.cantidad:g}")
            e_precio.insert(0, f"{insumo.precio_unidad:g}")
            if insumo.unidad in Insumo.UNIDADES:
                c_unidad.set(insumo.unidad)
            if insumo.categoria in Insumo.CATEGORIAS:
                c_cat.set(insumo.categoria)

        ttk.Label(
            frm,
            text="El stock se repone con compras. Aquí defines/corriges la ficha.",
            wraplength=320,
        ).grid(row=5, column=0, columnspan=2, sticky="w", pady=(6, 8))

        def guardar():
            try:
                nombre = e_nombre.get().strip()
                if not nombre:
                    messagebox.showerror("Error", "El nombre es obligatorio", parent=top)
                    return
                stock = float(e_stock.get() or 0)
                precio = float(e_precio.get() or 0)
                nuevo = Insumo(nombre, stock, c_unidad.get(), precio, c_cat.get())
                self.insumo_manager.agregar(nuevo)
                self.actualizar_datos()
                top.destroy()
                self.lbl_feedback.config(
                    text=f"✅ Ficha de '{nombre}' guardada",
                    foreground=self.theme.success,
                )
            except ValueError:
                messagebox.showerror("Error", "Stock y precio deben ser números", parent=top)

        bfrm = ttk.Frame(frm)
        bfrm.grid(row=6, column=0, columnspan=2, pady=(4, 0))
        ttk.Button(bfrm, text="Guardar", command=guardar).pack(side="left", padx=3)
        ttk.Button(bfrm, text="Cancelar", command=top.destroy).pack(side="left", padx=3)

    def eliminar_insumo(self):
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Selecciona un insumo para eliminar")
            return
        nombre = self.tree.item(seleccion[0])["values"][0]
        insumo = next((i for i in self.insumo_manager.listar() if i.nombre == nombre), None)
        if insumo and messagebox.askyesno("Confirmar", f"¿Eliminar el insumo '{insumo.nombre}'?"):
            self.insumo_manager.eliminar(insumo.id)
            self.actualizar_datos()

    def eliminar_compra(self):
        seleccion = self.tree_compras.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Selecciona una compra para eliminar")
            return
        compra_id = self.tree_compras.item(seleccion[0])["tags"][0]
        if messagebox.askyesno("Confirmar", "¿Eliminar la compra seleccionada? (no descuenta el stock)"):
            self.compras_manager.eliminar(compra_id)
            self.actualizar_datos()

    # ---------------- Refresco ----------------
    def _resaltar(self, insumo_id):
        for item in self.tree.get_children():
            if self.tree.item(item)["tags"] and self.tree.item(item)["tags"][0] == insumo_id:
                self.tree.selection_set(item)
                self.tree.see(item)
                break

    def actualizar_datos(self):
        self._cargar_combo()

        for item in self.tree.get_children():
            self.tree.delete(item)
        for insumo in self.insumo_manager.listar():
            self.tree.insert("", "end", tags=(insumo.id,), values=(
                insumo.nombre, f"{insumo.cantidad:,.2f}", insumo.unidad,
                f"${insumo.precio_unidad:,.0f}", insumo.categoria,
                f"${insumo.costo_total():,.0f}",
            ))

        for item in self.tree_compras.get_children():
            self.tree_compras.delete(item)
        for c in self.compras_manager.listar():
            self.tree_compras.insert("", "end", tags=(c.id,), values=(
                c.fecha, c.nombre, f"{c.cantidad:,.2f}", c.unidad,
                f"${c.precio_unidad:,.0f}", f"${c.total:,.0f}",
            ))

        self.lbl_total.config(text=f"Total gastado: ${self.compras_manager.total_gastado():,.0f} COP")

    # Compatibilidad con main_window (refresco al cambiar de pestaña)
    def actualizar_tabla(self):
        self.actualizar_datos()
