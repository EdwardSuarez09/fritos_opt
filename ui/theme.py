"""
Tema moderno para la interfaz gráfica
"""
import tkinter as tk
from tkinter import ttk

class Theme:
    """Configuración de tema moderno estilo VSCode mejorado"""
    
    # Colores modo oscuro mejorados
    DARK_BG = "#1a1a1a"
    DARK_FG = "#e0e0e0"
    DARK_SELECT = "#0d7377"
    DARK_ENTRY = "#2a2a2a"
    DARK_FRAME = "#252525"
    DARK_HOVER = "#3a3a3a"
    DARK_BORDER = "#404040"
    DARK_SUCCESS = "#2d8659"
    DARK_WARNING = "#d4a574"
    DARK_ERROR = "#c94a4a"
    DARK_INFO = "#4a9bd4"
    
    # Colores modo claro mejorados
    LIGHT_BG = "#fafafa"
    LIGHT_FG = "#2a2a2a"
    LIGHT_SELECT = "#0d7377"
    LIGHT_ENTRY = "#ffffff"
    LIGHT_FRAME = "#f0f0f0"
    LIGHT_HOVER = "#e8e8e8"
    LIGHT_BORDER = "#d0d0d0"
    LIGHT_SUCCESS = "#2d8659"
    LIGHT_WARNING = "#d4a574"
    LIGHT_ERROR = "#c94a4a"
    LIGHT_INFO = "#4a9bd4"
    
    def __init__(self, dark_mode=True):
        self.dark_mode = dark_mode
        self.bg = self.DARK_BG if dark_mode else self.LIGHT_BG
        self.fg = self.DARK_FG if dark_mode else self.LIGHT_FG
        self.select = self.DARK_SELECT if dark_mode else self.LIGHT_SELECT
        self.entry = self.DARK_ENTRY if dark_mode else self.LIGHT_ENTRY
        self.frame = self.DARK_FRAME if dark_mode else self.LIGHT_FRAME
        self.hover = self.DARK_HOVER if dark_mode else self.LIGHT_HOVER
        self.border = self.DARK_BORDER if dark_mode else self.LIGHT_BORDER
        self.success = self.DARK_SUCCESS if dark_mode else self.LIGHT_SUCCESS
        self.warning = self.DARK_WARNING if dark_mode else self.LIGHT_WARNING
        self.error = self.DARK_ERROR if dark_mode else self.LIGHT_ERROR
        self.info = self.DARK_INFO if dark_mode else self.LIGHT_INFO
    
    def apply_theme(self, root):
        """Aplica el tema a la ventana principal"""
        root.configure(bg=self.bg)
        
        # Configurar estilo ttk
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configurar Notebook (pestañas) - Mejorado
        style.configure('TNotebook', 
                       background=self.bg, 
                       borderwidth=0)
        style.configure('TNotebook.Tab', 
                       background=self.frame,
                       foreground=self.fg,
                       padding=[25, 12],
                       borderwidth=0,
                       font=('Segoe UI', 10))
        style.map('TNotebook.Tab',
                 background=[('selected', self.select)],
                 foreground=[('selected', '#ffffff'),
                           ('!selected', self.fg)],
                 expand=[('selected', [1, 1, 1, 0])])
        
        # Configurar Frame
        style.configure('TFrame', background=self.bg)
        style.configure('TLabelframe', 
                       background=self.frame,
                       foreground=self.fg,
                       borderwidth=1,
                       relief='solid',
                       bordercolor=self.border)
        style.configure('TLabelframe.Label', 
                       background=self.frame, 
                       foreground=self.select,
                       font=('Segoe UI', 10, 'bold'))
        
        # Configurar Label
        style.configure('TLabel', 
                       background=self.bg, 
                       foreground=self.fg,
                       font=('Segoe UI', 9))
        
        # Configurar Entry - Mejorado
        style.configure('TEntry', 
                       fieldbackground=self.entry,
                       foreground=self.fg,
                       borderwidth=1,
                       relief='solid',
                       bordercolor=self.border,
                       padding=5,
                       font=('Segoe UI', 9))
        style.map('TEntry',
                 bordercolor=[('focus', self.select)])
        
        # Configurar Button - Mejorado
        style.configure('TButton',
                       background=self.frame,
                       foreground=self.fg,
                       borderwidth=1,
                       relief='flat',
                       padding=[15, 8],
                       font=('Segoe UI', 9))
        style.map('TButton',
                 background=[('active', self.hover),
                            ('pressed', self.select)],
                 foreground=[('active', '#ffffff'),
                           ('pressed', '#ffffff')],
                 bordercolor=[('active', self.select),
                             ('pressed', self.select)])
        
        # Configurar Treeview - Mejorado
        style.configure('Treeview',
                       background=self.entry,
                       foreground=self.fg,
                       fieldbackground=self.entry,
                       borderwidth=1,
                       rowheight=25,
                       font=('Segoe UI', 9))
        style.configure('Treeview.Heading',
                       background=self.frame,
                       foreground=self.fg,
                       relief='flat',
                       borderwidth=1,
                       font=('Segoe UI', 9, 'bold'))
        style.map('Treeview',
                 background=[('selected', self.select)],
                 foreground=[('selected', '#ffffff')])
        # Alternar colores de filas
        style.map('Treeview',
                 background=[('selected', self.select),
                           ('!selected', self.entry)])
        
        # Configurar Combobox - Mejorado
        style.configure('TCombobox',
                       fieldbackground=self.entry,
                       foreground=self.fg,
                       borderwidth=1,
                       relief='solid',
                       bordercolor=self.border,
                       padding=5,
                       font=('Segoe UI', 9))
        style.map('TCombobox',
                 fieldbackground=[('readonly', self.frame)],
                 bordercolor=[('focus', self.select)])
        
        return style

