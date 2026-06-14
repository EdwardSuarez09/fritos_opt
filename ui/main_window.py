"""
Ventana principal del sistema
"""
import tkinter as tk
from tkinter import ttk
from ui.theme import Theme
from ui.inventario_screen import InventarioScreen
from ui.masas_screen import MasasScreen
from ui.rendimiento_screen import RendimientoScreen
from ui.productos_screen import ProductosScreen
from ui.costos_screen import CostosScreen
from ui.optimizacion_screen import OptimizacionScreen
from ui.sensibilidad_screen import SensibilidadScreen
from ui.sensibilidad_bot_screen import SensibilidadBotScreen
from ui.ventas_screen import VentasScreen
from ui.consumo_screen import ConsumoScreen
from core.inventario import Inventario
from core.costos import CalculadorCostos
from core.optimizador import Optimizador
from core.compras import ComprasManager
from core.ventas import VentasManager

class MainWindow:
    """Ventana principal con pestañas"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("🍽️ Sistema de Costeo y Optimización - Fritos")
        self.root.geometry("1400x900")
        # Centrar ventana (opcional, mejora la experiencia)
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
        # Inicializar managers
        self.inventario = Inventario()
        self.calculador_costos = CalculadorCostos(
            self.inventario.insumos,
            self.inventario.masas,
            self.inventario.productos
        )
        self.optimizador = Optimizador(
            self.inventario.productos,
            self.calculador_costos
        )
        # Gestores de compras y ventas
        self.compras_manager = ComprasManager(self.inventario.insumos)
        self.ventas_manager = VentasManager(self.inventario.productos)
        
        # Aplicar tema
        self.theme = Theme(dark_mode=True)
        self.style = self.theme.apply_theme(root)
        
        # Crear notebook (pestañas)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Crear pantallas
        self.crear_pantallas()
        
        # Configurar evento para actualizar cuando se cambia de pestaña
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
        
        # Configurar cierre
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def crear_pantallas(self):
        """Crea todas las pantallas del sistema"""
        # Pantalla de Inventario (insumos + compras unificados)
        frame_inventario = ttk.Frame(self.notebook)
        self.notebook.add(frame_inventario, text="📦 Inventario")
        self.inventario_screen = InventarioScreen(
            frame_inventario, self.inventario, self.compras_manager, self.theme
        )
        
        # Pantalla de Masas
        frame_masas = ttk.Frame(self.notebook)
        self.notebook.add(frame_masas, text="🥟 Masas")
        self.masas_screen = MasasScreen(
            frame_masas, self.inventario.masas, 
            self.inventario.insumos, self.theme
        )
        
        # Pantalla de Rendimiento
        frame_rendimiento = ttk.Frame(self.notebook)
        self.notebook.add(frame_rendimiento, text="📊 Rendimiento")
        self.rendimiento_screen = RendimientoScreen(
            frame_rendimiento, self.inventario.masas,
            self.inventario.productos, self.inventario.insumos, self.theme
        )
        
        # Pantalla de Productos
        frame_productos = ttk.Frame(self.notebook)
        self.notebook.add(frame_productos, text="🍽️ Productos")
        self.productos_screen = ProductosScreen(
            frame_productos, self.inventario.productos,
            self.inventario.masas, self.inventario.insumos, self.theme
        )
        
        # Pantalla de Costos
        frame_costos = ttk.Frame(self.notebook)
        self.notebook.add(frame_costos, text="💰 Costos")
        self.costos_screen = CostosScreen(
            frame_costos, self.calculador_costos, self.theme
        )

        # Pantalla de Ventas
        frame_ventas = ttk.Frame(self.notebook)
        self.notebook.add(frame_ventas, text="🧾 Ventas")
        self.ventas_screen = VentasScreen(
            frame_ventas, self.ventas_manager,
            self.inventario.productos, self.theme
        )

        # Pantalla de Consumo y Sobrantes
        frame_consumo = ttk.Frame(self.notebook)
        self.notebook.add(frame_consumo, text="📉 Consumo")
        self.consumo_screen = ConsumoScreen(
            frame_consumo, self.inventario,
            self.ventas_manager, self.compras_manager, self.theme
        )
        
        # Pantalla de Optimización
        frame_optimizacion = ttk.Frame(self.notebook)
        self.notebook.add(frame_optimizacion, text="⚡ Optimización")
        self.optimizacion_screen = OptimizacionScreen(
            frame_optimizacion, self.optimizador,
            self.inventario.productos, self.theme
        )
        
        # Pantalla de Análisis de Sensibilidad
        frame_sensibilidad = ttk.Frame(self.notebook)
        self.notebook.add(frame_sensibilidad, text="📊 Sensibilidad")
        self.sensibilidad_screen = SensibilidadScreen(
            frame_sensibilidad, self.inventario,
            self.calculador_costos, self.theme
        )

        # Asistente conversacional de sensibilidad
        frame_bot = ttk.Frame(self.notebook)
        self.notebook.add(frame_bot, text="🤖 Asistente")
        self.sensibilidad_bot_screen = SensibilidadBotScreen(
            frame_bot, self.inventario,
            self.calculador_costos, self.theme,
            self.optimizador
        )
    
    def on_closing(self):
        """Maneja el cierre de la aplicación"""
        # Guardar todos los datos
        self.inventario.insumos.save()
        self.inventario.masas.save()
        self.inventario.productos.save()
        self.root.destroy()
    
    def on_tab_changed(self, event=None):
        """
        Se ejecuta cuando el usuario cambia de pestaña
        
        Actualiza automáticamente los datos de la pantalla seleccionada
        para reflejar cambios realizados en otras pestañas.
        """
        # Obtener el índice de la pestaña seleccionada
        selected_tab = self.notebook.index(self.notebook.select())
        
        # Actualizar la pantalla correspondiente
        if selected_tab == 0:  # Inventario
            self.inventario_screen.actualizar_datos()
        elif selected_tab == 1:  # Masas
            self.masas_screen.actualizar_tabla()
        elif selected_tab == 2:  # Rendimiento
            self.rendimiento_screen.actualizar_datos()
        elif selected_tab == 3:  # Productos
            self.productos_screen.actualizar_tabla()
        elif selected_tab == 4:  # Costos
            self.costos_screen.actualizar_tabla()
        elif selected_tab == 5:  # Ventas
            self.ventas_screen.actualizar_datos()
        elif selected_tab == 6:  # Consumo
            self.consumo_screen.actualizar_datos()
        elif selected_tab == 7:  # Optimización
            self.optimizacion_screen.actualizar_productos()
        elif selected_tab == 8:  # Sensibilidad
            self.sensibilidad_screen.actualizar_datos()
        elif selected_tab == 9:  # Asistente
            self.sensibilidad_bot_screen.actualizar_datos()
    
    def actualizar_pantallas(self):
        """Actualiza todas las pantallas con datos frescos"""
        self.inventario_screen.actualizar_datos()
        self.masas_screen.actualizar_tabla()
        self.rendimiento_screen.actualizar_datos()
        self.productos_screen.actualizar_tabla()
        self.costos_screen.actualizar_tabla()
        self.ventas_screen.actualizar_datos()
        self.consumo_screen.actualizar_datos()
        self.optimizacion_screen.actualizar_productos()
        self.sensibilidad_screen.actualizar_datos()
        self.sensibilidad_bot_screen.actualizar_datos()

