"""
Pantalla de visualización de costos
"""
import tkinter as tk
from tkinter import ttk
from core.costos import CalculadorCostos

class CostosScreen:
    """Pantalla para visualizar costos y ganancias"""
    
    def __init__(self, parent, calculador_costos: CalculadorCostos, theme):
        self.calculador_costos = calculador_costos
        self.theme = theme
        
        # Frame principal
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Frame de información mejorado
        info_frame = ttk.LabelFrame(main_frame, text="ℹ️ Información de Costos", padding=15)
        info_frame.pack(fill="x", pady=(0, 15))
        
        info_text = (
            "Los costos se calculan automáticamente basándose en:\n"
            "  • Costo de masa equivalente\n"
            "  • Costo de rellenos e insumos extra\n"
            "  • Aceite, salsas, empaques y otros"
        )
        self.label_info = ttk.Label(info_frame, 
            text=info_text,
            justify="left",
            font=('Segoe UI', 9))
        self.label_info.pack(anchor="w", padx=5)
        
        # Tabla de costos mejorada
        table_frame = ttk.LabelFrame(main_frame, text="💰 Costos y Ganancias por Producto", padding=15)
        table_frame.pack(fill="both", expand=True)
        
        columns = ("producto", "costo", "precio", "ganancia", "margen")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=18)
        
        self.tree.heading("producto", text="📦 Producto")
        self.tree.heading("costo", text="💵 Costo Unitario")
        self.tree.heading("precio", text="💰 Precio Venta")
        self.tree.heading("ganancia", text="📈 Ganancia Unitaria")
        self.tree.heading("margen", text="📊 Margen %")
        
        self.tree.column("producto", width=280, anchor="w")
        self.tree.column("costo", width=160, anchor="e")
        self.tree.column("precio", width=160, anchor="e")
        self.tree.column("ganancia", width=180, anchor="e")
        self.tree.column("margen", width=140, anchor="e")
        
        # Colorear ganancias mejorado
        if self.theme.dark_mode:
            self.tree.tag_configure("ganancia_positiva", background="#1e4d2e", foreground="#90ee90")
            self.tree.tag_configure("ganancia_negativa", background="#4d1e1e", foreground="#ff6b6b")
            self.tree.tag_configure("ganancia_alta", background="#2d5a3d", foreground="#7fff7f")
        else:
            self.tree.tag_configure("ganancia_positiva", background="#e8f5e9", foreground="#2e7d32")
            self.tree.tag_configure("ganancia_negativa", background="#ffebee", foreground="#c62828")
            self.tree.tag_configure("ganancia_alta", background="#c8e6c9", foreground="#1b5e20")
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Botón actualizar mejorado
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="🔄 Actualizar Costos", 
                  command=self.actualizar_tabla).pack(side="left", padx=5)
        
        self.actualizar_tabla()
    
    def actualizar_tabla(self):
        """Actualiza la tabla de costos"""
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Obtener costos
        costos = self.calculador_costos.obtener_costos_todos_productos()
        
        if not costos:
            self.tree.insert("", "end", values=(
                "No hay productos registrados", "", "", "", ""
            ))
            return
        
        # Agregar a la tabla con mejor formato
        for producto_id, datos in costos.items():
            ganancia = datos["ganancia"]
            margen = datos["margen"]
            
            # Determinar tag según ganancia y margen
            if ganancia < 0:
                tag = "ganancia_negativa"
            elif margen > 30:
                tag = "ganancia_alta"
            else:
                tag = "ganancia_positiva"
            
            # Formato mejorado de números
            costo_str = f"${datos['costo']:,.2f}"
            precio_str = f"${datos['precio_venta']:,.2f}"
            ganancia_str = f"${ganancia:,.2f}"
            margen_str = f"{margen:.1f}%"
            
            # Agregar indicador visual al margen
            if margen > 30:
                margen_str = f"✓ {margen_str}"
            elif margen < 10:
                margen_str = f"⚠ {margen_str}"
            
            self.tree.insert("", "end", values=(
                datos["nombre"],
                costo_str,
                precio_str,
                ganancia_str,
                margen_str
            ), tags=(tag,))

