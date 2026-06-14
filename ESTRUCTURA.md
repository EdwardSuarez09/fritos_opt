# 📁 Estructura del Proyecto

```
fritos_opt/
│
├── core/                          # Módulos de lógica de negocio
│   ├── __init__.py
│   ├── json_manager.py            # Gestión de archivos JSON
│   ├── insumos.py                 # Gestión de insumos
│   ├── masas.py                   # Gestión de lotes de masa
│   ├── productos.py               # Gestión de productos
│   ├── inventario.py              # Wrapper unificado
│   ├── costos.py                  # Cálculo de costos
│   └── optimizador.py             # Modelo de optimización (PuLP)
│
├── ui/                            # Módulos de interfaz gráfica
│   ├── __init__.py
│   ├── theme.py                   # Tema moderno (oscuro/claro)
│   ├── main_window.py             # Ventana principal con pestañas
│   ├── insumos_screen.py          # Pantalla de insumos
│   ├── masas_screen.py            # Pantalla de masas
│   ├── rendimiento_screen.py      # Pantalla de rendimiento
│   ├── productos_screen.py        # Pantalla de productos
│   ├── costos_screen.py           # Pantalla de costos
│   └── optimizacion_screen.py     # Pantalla de optimización
│
├── data/                          # Datos persistentes (auto-generado)
│   ├── insumos.json
│   ├── masas.json
│   └── productos.json
│
├── main.py                        # Punto de entrada principal
├── requirements.txt               # Dependencias Python
├── README.md                      # Documentación completa
├── INICIO_RAPIDO.md              # Guía de inicio rápido
└── ESTRUCTURA.md                  # Este archivo

```

## 🔄 Flujo de Datos

1. **Usuario** → Interactúa con la UI
2. **UI** → Llama a los managers del core
3. **Managers** → Gestionan datos en memoria
4. **JSONManager** → Persiste datos en archivos JSON
5. **CalculadorCostos** → Calcula costos automáticamente
6. **Optimizador** → Resuelve modelo de PL

## 📦 Dependencias Principales

- **tkinter/ttk**: Interfaz gráfica (incluido en Python)
- **pulp**: Optimización mediante Programación Lineal
- **pandas/openpyxl**: Exportación a Excel (opcional)

## 🎯 Módulos Clave

### Core
- `json_manager.py`: Maneja persistencia de datos
- `insumos.py`: Clases Insumo e InsumoManager
- `masas.py`: Clases LoteMasa y MasaManager
- `productos.py`: Clases Producto y ProductoManager
- `costos.py`: CalculadorCostos para costos unitarios
- `optimizador.py`: Optimizador con modelo PuLP

### UI
- `main_window.py`: Orquesta todas las pantallas
- Cada `*_screen.py`: Pantalla específica con su lógica

## 🚀 Ejecución

```bash
python main.py
```

El sistema:
1. Crea la carpeta `data/` si no existe
2. Carga datos existentes desde JSON
3. Inicializa la interfaz gráfica
4. Guarda automáticamente al cerrar

