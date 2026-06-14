"""
Modelo de optimización usando Programación Lineal (PuLP)

Este módulo implementa un modelo de optimización que maximiza las ganancias
de producción semanal usando técnicas de Programación Lineal. El modelo
considera restricciones de demanda mínima y presupuesto diario disponible.
"""
import pulp
from typing import Dict, List, Tuple, Optional
from core.productos import ProductoManager
from core.costos import CalculadorCostos

# Lista de días de la semana para la optimización
DIAS_SEMANA = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

class Optimizador:
    """
    Optimiza la producción usando Programación Lineal
    
    Esta clase resuelve el problema de optimización de producción semanal,
    determinando cuántas unidades de cada producto producir cada día para
    maximizar las ganancias totales, respetando las restricciones de demanda
    y presupuesto disponible.
    """
    
    def __init__(self, producto_manager: ProductoManager, calculador_costos: CalculadorCostos):
        """
        Inicializa el optimizador
        
        Args:
            producto_manager: Gestor de productos del negocio
            calculador_costos: Calculador de costos unitarios de productos
        """
        self.producto_manager = producto_manager
        self.calculador_costos = calculador_costos
    
    def optimizar(self, demanda: Dict[Tuple[str, str], float], 
                  fondos_diarios: Dict[str, float]) -> Dict:
        """
        Resuelve el modelo de optimización de producción semanal
        
        El modelo matemático implementado es:
        - Función objetivo: Maximizar Z = Σ Σ X[i,j] × Ganancia[i]
        - Restricción 1: X[i,j] ≥ D[i,j] (satisfacer demanda mínima)
        - Restricción 2: Σ X[i,j] × Costo[i] ≤ Fondo[j] (respetar presupuesto)
        - Restricción 3: X[i,j] ≥ 0 (no negatividad)
        
        Donde:
        - X[i,j] = cantidad de producto i a producir en día j
        - D[i,j] = demanda mínima del producto i en día j
        - Fondo[j] = presupuesto disponible para el día j
        
        Args:
            demanda: Diccionario con {(producto_id, dia): cantidad_minima}
                    que especifica la demanda mínima de cada producto por día
            fondos_diarios: Diccionario con {dia: fondo_disponible} que indica
                           el presupuesto disponible para cada día de la semana
        
        Returns:
            Diccionario con los resultados de la optimización que incluye:
            - estado: Estado de la solución (Óptimo, No factible, etc.)
            - ganancia_total: Ganancia máxima obtenida
            - produccion: Dict con producción por producto y día
            - costos_totales: Dict con costos totales por producto
            - productos: Lista con información detallada de cada producto
        """
        # Crear el modelo de Programación Lineal
        # pulp.LpMaximize indica que queremos maximizar la función objetivo
        model = pulp.LpProblem("Optimizacion_Fritos", pulp.LpMaximize)
        
        # Variables de decisión: X[i,j] = cantidad de producto i producido en día j
        # Cada variable representa cuántas unidades de un producto específico
        # se deben producir en un día específico
        productos = self.producto_manager.listar()
        variables = {}
        
        # Crear una variable de decisión para cada combinación producto-día
        for producto in productos:
            for dia in DIAS_SEMANA:
                var_name = f"X_{producto.id}_{dia}"
                # lowBound=0 asegura que no se puede producir cantidad negativa
                # cat='Continuous' permite valores decimales (puede cambiarse a 'Integer')
                variables[(producto.id, dia)] = pulp.LpVariable(
                    var_name, lowBound=0, cat='Continuous'
                )
        
        # Función objetivo: Maximizar ganancias totales
        # Z = Σ Σ X[i,j] × (Precio[i] - CostoUnitario[i])
        #    i j
        # Sumamos la ganancia de cada unidad producida de cada producto en cada día
        objetivo = pulp.lpSum([
            variables[(producto.id, dia)] * self.calculador_costos.calcular_ganancia_producto(producto.id)
            for producto in productos
            for dia in DIAS_SEMANA
        ])
        
        # Asignar la función objetivo al modelo
        model += objetivo
        
        # Restricción 1: Demanda mínima por día
        # X[i,j] >= D[i,j] para todo producto i y día j
        # Asegura que se produzca al menos la cantidad mínima requerida
        for (producto_id, dia), demanda_min in demanda.items():
            if (producto_id, dia) in variables:
                model += variables[(producto_id, dia)] >= demanda_min
        
        # Restricción 2: Disponibilidad financiera diaria
        # Σ X[i,j] × CostoUnitario[i] <= Fondo[j] para todo día j
        #    i
        # El costo total de producción de un día no puede exceder el presupuesto disponible
        for dia in DIAS_SEMANA:
            if dia in fondos_diarios:
                # Calcular el costo total de producción para este día
                restriccion_fondo = pulp.lpSum([
                    variables[(producto.id, dia)] * self.calculador_costos.calcular_costo_producto(producto.id)
                    for producto in productos
                ])
                # Agregar la restricción: costo total <= presupuesto disponible
                model += restriccion_fondo <= fondos_diarios[dia]
        
        # Resolver el modelo usando el solver CBC (Coin-or Branch and Cut)
        # msg=0 suprime los mensajes del solver para una salida más limpia
        model.solve(pulp.PULP_CBC_CMD(msg=0))
        
        # Recopilar y estructurar los resultados de la optimización
        resultados = {
            "estado": pulp.LpStatus[model.status],  # Estado: Optimal, Infeasible, Unbounded, etc.
            "ganancia_total": pulp.value(model.objective) if model.status == 1 else 0,  # Valor de la función objetivo
            "produccion": {},  # Producción por producto y día
            "costos_totales": {},  # Costos totales por producto
            "productos": []  # Lista detallada de productos
        }
        
        # Si la solución es óptima (status == 1), extraer los valores de las variables
        if model.status == 1:  # 1 = Optimal
            # Calcular producción por producto y día
            for producto in productos:
                produccion_producto = {}  # Producción de este producto por día
                costo_total_producto = 0  # Costo total de producción de este producto
                
                # Extraer la cantidad a producir de cada día
                for dia in DIAS_SEMANA:
                    var = variables[(producto.id, dia)]
                    # var.varValue contiene el valor óptimo de la variable
                    cantidad = var.varValue if var.varValue else 0
                    produccion_producto[dia] = cantidad
                    # Acumular el costo total de este producto
                    costo_total_producto += cantidad * self.calculador_costos.calcular_costo_producto(producto.id)
                
                # Guardar resultados para este producto
                resultados["produccion"][producto.id] = produccion_producto
                resultados["costos_totales"][producto.id] = costo_total_producto
                
                # Agregar información detallada del producto
                resultados["productos"].append({
                    "id": producto.id,
                    "nombre": producto.nombre,
                    "produccion": produccion_producto,
                    "costo_total": costo_total_producto
                })
        
        return resultados
    
    def exportar_a_excel(self, resultados: Dict, filename: str = "optimizacion_resultados.xlsx"):
        """
        Exporta los resultados de la optimización a un archivo Excel
        
        Crea un archivo Excel con dos hojas:
        - 'Producción': Detalle de producción por producto y día
        - 'Resumen': Resumen general con estado y ganancia total
        
        Args:
            resultados: Diccionario con los resultados de la optimización
            filename: Nombre del archivo Excel a crear (por defecto: optimizacion_resultados.xlsx)
        
        Returns:
            True si la exportación fue exitosa, False en caso contrario
        """
        try:
            import pandas as pd
            
            # Crear DataFrame con producción detallada
            # Cada fila representa la producción de un producto en un día específico
            datos = []
            for producto_info in resultados["productos"]:
                for dia in DIAS_SEMANA:
                    datos.append({
                        "Producto": producto_info["nombre"],
                        "Día": dia,
                        "Cantidad": producto_info["produccion"][dia],
                        "Costo Total": producto_info["costo_total"]
                    })
            
            df = pd.DataFrame(datos)
            
            # Crear archivo Excel con múltiples hojas usando openpyxl como motor
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                # Hoja 1: Producción detallada
                df.to_excel(writer, sheet_name='Producción', index=False)
                
                # Hoja 2: Resumen general
                resumen = pd.DataFrame([{
                    "Estado": resultados["estado"],
                    "Ganancia Total": resultados["ganancia_total"]
                }])
                resumen.to_excel(writer, sheet_name='Resumen', index=False)
            
            return True
        except ImportError:
            # Si pandas u openpyxl no están instalados
            print("pandas y openpyxl son necesarios para exportar a Excel")
            return False
        except Exception as e:
            # Capturar cualquier otro error durante la exportación
            print(f"Error al exportar: {e}")
            return False

