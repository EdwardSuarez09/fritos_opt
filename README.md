# Sistema de Costeo y Optimización para Puesto de Fritos

Sistema desarrollado en Python para la gestión de costos, inventario, ventas, producción y optimización de un puesto de fritos. Incluye cálculo automático de costos unitarios, optimización mediante Programación Lineal, análisis de sensibilidad y un asistente conversacional básico.

## Características

- Gestión de Inventario: registro de insumos y compras, con actualización de stock.
- Gestión de Masas: creación de lotes de masa con cálculo automático de costos.
- Rendimiento de Lotes: asociación de productos producidos por cada lote, filtrados por masa.
- Gestión de Productos: registro de productos con masa asociada e insumos extra.
- Cálculo Automático de Costos: costos unitarios considerando masa, rellenos, aceite, salsas y empaques.
- Gestión de Ventas: registro de ventas con historial general y por producto.
- Consumo y Sobrantes: estimación del consumo de ingredientes y del sobrante aproximado.
- Optimización de Producción: modelo de Programación Lineal para maximizar ganancias.
- Análisis de Sensibilidad: impacto de cambios de precios y escenarios optimista, realista y pesimista.
- Asistente Conversacional: respuestas sobre costos, ventas, historial y simulaciones, con sugerencia de gráficas.
- Persistencia de Datos: almacenamiento automático en archivos JSON.
- Pruebas Unitarias: batería de 85 pruebas automatizadas que validan los módulos principales.

## Instalación

### Requisitos Previos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

### Pasos de Instalación

1. Clonar el repositorio:

```bash
git clone https://github.com/EdwardSuarez09/Fritanga.git
cd Fritanga
```

2. Instalar dependencias:

```bash
pip install -r requirements.txt
```

Dependencias principales:
- `pulp`: optimización mediante Programación Lineal
- `matplotlib`: generación de gráficas
- `pandas` y `openpyxl`: manejo y exportación de datos a Excel

## Estructura del Proyecto

```
fritos_opt/
├── core/
│   ├── __init__.py
│   ├── json_manager.py
│   ├── insumos.py
│   ├── compras.py
│   ├── ventas.py
│   ├── consumo.py
│   ├── masas.py
│   ├── productos.py
│   ├── inventario.py
│   ├── costos.py
│   ├── optimizador.py
│   ├── sensibilidad.py
│   ├── bot_sensibilidad.py
│   └── historial.py
├── ui/
│   ├── __init__.py
│   ├── theme.py
│   ├── main_window.py
│   ├── inventario_screen.py
│   ├── masas_screen.py
│   ├── rendimiento_screen.py
│   ├── productos_screen.py
│   ├── costos_screen.py
│   ├── ventas_screen.py
│   ├── consumo_screen.py
│   ├── optimizacion_screen.py
│   ├── sensibilidad_screen.py
│   ├── sensibilidad_bot_screen.py
│   └── charts.py
├── data/
│   ├── insumos.json
│   ├── masas.json
│   ├── productos.json
│   └── historial_mensual.json
├── tests/
│   └── (pruebas unitarias de cada módulo)
├── main.py
├── requirements.txt
└── README.md
```

## Uso del Sistema

### Ejecutar la Aplicación

```bash
python main.py
```

### Flujo de Trabajo Recomendado

1. Inventario: registrar insumos y compras; las compras actualizan el stock.
2. Masas: crear lotes de masa; el sistema calcula su costo automáticamente.
3. Rendimiento: indicar cuántos productos salen de cada lote (filtrados por masa).
4. Productos: crear productos, asociar masa e insumos extra y definir precio de venta.
5. Costos: visualizar costos unitarios, ganancias y márgenes por producto.
6. Ventas: registrar ventas y consultar el historial general y por producto.
7. Consumo y Sobrantes: revisar el consumo estimado de ingredientes y los sobrantes.
8. Optimización: definir demanda mínima y presupuesto diario, y resolver el modelo.
9. Análisis de Sensibilidad: evaluar el impacto de cambios de precios y escenarios.
10. Asistente: hacer preguntas sobre costos, ventas, historial y simulaciones.

## Modelo de Optimización

El sistema utiliza Programación Lineal (PuLP) para optimizar la producción:

Función objetivo:

```
Max Z = Σ X[i,j] * (Precio[i] - CostoUnitario[i])
```

Restricciones:
- Demanda mínima: `X[i,j] >= D[i,j]`
- Disponibilidad financiera: `Σ X[i,j] * CostoUnitario[i] <= Fondo[j]`
- No negatividad: `X[i,j] >= 0`

Donde:
- `X[i,j]` = cantidad de producto i producido en el día j
- `D[i,j]` = demanda mínima del producto i en el día j
- `Fondo[j]` = disponibilidad financiera en el día j

## Almacenamiento de Datos

Los datos se guardan automáticamente en archivos JSON dentro de la carpeta `data/`:

- `insumos.json`: insumos registrados y su stock
- `masas.json`: lotes de masa
- `productos.json`: productos del negocio
- `historial_mensual.json`: datos históricos de ventas y compras
- `compras.json` y `ventas.json`: se generan al registrar compras y ventas

## Pruebas

El proyecto incluye 85 pruebas unitarias que validan los módulos de costos, optimización, inventario, compras, ventas, consumo, análisis de sensibilidad, historial y asistente.

Para ejecutarlas:

```bash
python -m unittest discover -s tests
```

## Solución de Problemas

### Error: "No module named 'pulp'" (u otra dependencia)

Instala las dependencias:

```bash
pip install -r requirements.txt
```

### Los datos no se guardan

Verifica que la carpeta `data/` exista y tenga permisos de escritura.

### La optimización no funciona

- Verifica que tengas al menos un producto registrado.
- Asegúrate de que los costos estén calculados correctamente.
- Verifica que la demanda y los fondos sean valores numéricos válidos.

## Notas Importantes

- El sistema funciona con proporciones y porciones, sin necesidad de medidas exactas.
- Los insumos se distribuyen proporcionalmente según el uso.
- Se admiten varios tipos de masa (tradicional, yuca, plátano, etc.).
- Un insumo puede usarse en varios productos sin duplicarse.
- Los costos se recalculan automáticamente.

## Licencia

Proyecto de uso libre para fines educativos.
