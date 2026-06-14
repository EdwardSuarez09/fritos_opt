"""
Gestor de archivos JSON para persistencia de datos
"""
import json
import os
from pathlib import Path

class JSONManager:
    """Maneja la lectura y escritura de archivos JSON"""
    
    def __init__(self, data_dir=None):
        if data_dir is None:
            # Obtener el directorio base del proyecto
            base_dir = Path(__file__).parent.parent
            data_dir = base_dir / "data"
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_path(self, filename):
        """Obtiene la ruta completa del archivo"""
        return self.data_dir / filename
    
    def load(self, filename, default=None):
        """
        Carga datos desde un archivo JSON
        Args:
            filename: Nombre del archivo (sin extensión .json)
            default: Valor por defecto si el archivo no existe
        Returns:
            Datos cargados o valor por defecto
        """
        filepath = self._get_path(f"{filename}.json")
        if not filepath.exists():
            return default if default is not None else {}
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error al cargar {filename}: {e}")
            return default if default is not None else {}
    
    def save(self, filename, data):
        """
        Guarda datos en un archivo JSON
        Args:
            filename: Nombre del archivo (sin extensión .json)
            data: Datos a guardar
        """
        filepath = self._get_path(f"{filename}.json")
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except IOError as e:
            print(f"Error al guardar {filename}: {e}")
            return False
    
    def delete(self, filename):
        """Elimina un archivo JSON"""
        filepath = self._get_path(f"{filename}.json")
        if filepath.exists():
            filepath.unlink()
            return True
        return False

