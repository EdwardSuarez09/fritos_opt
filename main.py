"""
Sistema de Costeo y Optimización para Puesto de Fritos
Punto de entrada principal de la aplicación
"""
import tkinter as tk
import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.main_window import MainWindow

def main():
    """Función principal"""
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()

if __name__ == "__main__":
    main()

