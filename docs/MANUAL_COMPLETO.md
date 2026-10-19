# 📘 Manual Completo del Sistema de Costeo y Optimización para Puesto de Fritos

## 📋 Tabla de Contenidos

1. [Introducción](#introducción)
2. [¿Qué hace este programa?](#qué-hace-este-programa)
3. [Cómo funciona el sistema](#cómo-funciona-el-sistema)
4. [Modelo matemático de optimización](#modelo-matemático-de-optimización)
5. [Cálculo de costos](#cálculo-de-costos)
6. [Análisis de sensibilidad](#análisis-de-sensibilidad)
7. [Guía de uso paso a paso](#guía-de-uso-paso-a-paso)
8. [Ejemplos prácticos](#ejemplos-prácticos)

---

## 🎯 Introducción

Este sistema está diseñado para ayudar a dueños de puestos de fritos a:
- **Calcular costos** de manera automática y precisa
- **Optimizar la producción** para maximizar ganancias
- **Tomar decisiones** basadas en datos reales
- **Analizar escenarios** antes de que ocurran

Todo esto usando **Programación Lineal**, una técnica matemática poderosa que se usa en empresas grandes.

---

## 💡 ¿Qué hace este programa?

### Funcionalidades principales:

1. **📦 Gestión de Insumos**
   - Registra todos los materiales que compras (harina, aceite, rellenos, etc.)
   - Guarda precios y cantidades
   - Organiza por categorías

2. **🥟 Gestión de Masas**
   - Crea lotes de masa (tradicional, yuca, plátano, etc.)
   - Indica qué insumos usas y en qué cantidad
   - Calcula el costo total del lote automáticamente

3. **📊 Rendimiento de Lotes**
   - Define cuántos productos salen de cada lote
   - Ejemplo: "De este lote salen 20 empanadas y 15 papas rellenas"
   - El sistema calcula el costo por unidad

4. **🍽️ Gestión de Productos**
   - Registra tus productos finales (empanadas, arepas, etc.)
   - Asocia masa e insumos extra (rellenos, salsas)
   - Define precio de venta y demanda estimada

5. **💰 Cálculo Automático de Costos**
   - Calcula el costo de cada producto automáticamente
   - Considera masa, rellenos, aceite, empaques
   - Muestra ganancias y márgenes

6. **⚡ Optimización de Producción**
   - Te dice cuánto producir de cada producto cada día
   - Maximiza tus ganancias
   - Respeta tu presupuesto disponible

7. **📊 Análisis de Sensibilidad**
   - Ve qué pasa si cambian los precios de insumos
   - Compara diferentes situaciones (mejor, normal, peor caso)
   - Toma decisiones informadas

---

## 🔄 Cómo funciona el sistema

### Flujo general:

```
1. REGISTRAS INSUMOS
   ↓
2. CREAS LOTES DE MASA
   ↓
3. DEFINES RENDIMIENTO (cuántos productos salen de cada lote)
   ↓
4. REGISTRAS PRODUCTOS (con masa e insumos extra)
   ↓
5. EL SISTEMA CALCULA COSTOS AUTOMÁTICAMENTE
   ↓
6. OPTIMIZAS LA PRODUCCIÓN (el sistema te dice qué producir)
   ↓
7. ANALIZAS ESCENARIOS (qué pasa si cambian los precios)
```

### Ejemplo práctico completo:

**Paso 1: Registrar Insumos**
- Harina: 5 kg a $2,500/kg
- Aceite: 2 L a $3,000/L
- Carne: 1 kg a $8,000/kg

**Paso 2: Crear Lote de Masa**
- Lote "Masa tradicional": 6 kg
- Usa: 5 kg harina, 0.5 L aceite
- Costo del lote: $14,500

**Paso 3: Definir Rendimiento**
- De este lote salen: 20 empanadas
- Costo por empanada (solo masa): $14,500 ÷ 20 = $725

**Paso 4: Registrar Producto**
- "Empanada de carne"
- Usa: masa tradicional + 0.1 kg carne
- Precio de venta: $2,000

**Paso 5: Cálculo Automático**
- Costo masa: $725
- Costo carne: $800 (0.1 kg × $8,000/kg)
- Costo aceite: $300 (estimado)
- Costo empaque: $50 (estimado)
- **Costo total: $1,875**
- **Ganancia: $2,000 - $1,875 = $125**

**Paso 6: Optimización**
- Si tienes $50,000 de presupuesto diario
- Y necesitas producir al menos 10 empanadas
- El sistema te dice: produce 20 empanadas para maximizar ganancias

---

## 🧮 Modelo Matemático de Optimización

### ¿Qué es la Programación Lineal?

La **Programación Lineal** es una técnica matemática que encuentra la **mejor solución** a un problema cuando hay:
- Una **meta** (maximizar ganancias)
- **Restricciones** (presupuesto limitado, demanda mínima)

Es como tener un asistente matemático que prueba millones de combinaciones y encuentra la mejor.

### El modelo matemático del sistema

#### Variables de decisión

**X[i,j]** = Cantidad de producto **i** a producir en el día **j**

Donde:
- **i** = tipo de producto (empanada de carne, papa rellena, etc.)
- **j** = día de la semana (Lunes, Martes, ..., Domingo)

**Ejemplo:**
- X[empanada_carne, lunes] = 15 → Produce 15 empanadas de carne el lunes
- X[papa_rellena, martes] = 10 → Produce 10 papas rellenas el martes

#### Función objetivo (Lo que queremos maximizar)

```
Maximizar Z = Σ Σ X[i,j] × Ganancia[i]
              i j
```

**En palabras simples:**
- Queremos **maximizar** la ganancia total
- Sumamos la ganancia de cada producto producido cada día
- Ganancia[i] = Precio de venta[i] - Costo unitario[i]

**Ejemplo:**
- Empanada de carne: ganancia = $2,000 - $1,875 = $125
- Si produces 10 empanadas: 10 × $125 = $1,250 de ganancia
- Si produces 20 empanadas: 20 × $125 = $2,500 de ganancia

#### Restricción 1: Demanda mínima

```
X[i,j] ≥ D[i,j]  para todo producto i y día j
```

**En palabras simples:**
- Debes producir **al menos** la cantidad mínima requerida
- D[i,j] = demanda mínima del producto i en el día j

**Ejemplo:**
- Necesitas al menos 10 empanadas el lunes
- Entonces: X[empanada_carne, lunes] ≥ 10
- Puedes producir 10, 15, 20... pero no menos de 10

#### Restricción 2: Presupuesto disponible

```
Σ X[i,j] × Costo[i] ≤ Presupuesto[j]  para todo día j
     i
```

**En palabras simples:**
- El costo total de producción de un día no puede exceder el presupuesto
- Sumas el costo de todos los productos producidos ese día
- Ese total debe ser menor o igual al presupuesto disponible

**Ejemplo:**
- Presupuesto del lunes: $50,000
- Costo de empanada: $1,875
- Si produces 20 empanadas: 20 × $1,875 = $37,500 ✅ (está dentro del presupuesto)
- Si produces 30 empanadas: 30 × $1,875 = $56,250 ❌ (excede el presupuesto)

#### Restricción 3: No negatividad

```
X[i,j] ≥ 0  para todo producto i y día j
```

**En palabras simples:**
- No puedes producir cantidades negativas
- Solo puedes producir 0 o más unidades

### Resumen del modelo completo

```
OBJETIVO:
Maximizar Z = Σ Σ X[i,j] × Ganancia[i]
              i j

RESTRICCIONES:
1. X[i,j] ≥ D[i,j]                    (Satisfacer demanda mínima)
2. Σ X[i,j] × Costo[i] ≤ Presupuesto[j]  (Respetar presupuesto)
   i
3. X[i,j] ≥ 0                         (No negatividad)
```

### ¿Cómo se resuelve?

El sistema usa un **solver** (resolvedor) llamado **PuLP** que:
1. Toma todas las restricciones
2. Prueba millones de combinaciones posibles
3. Encuentra la que maximiza la ganancia
4. Te da la solución óptima

**Ejemplo de solución:**
```
Lunes:
- Empanada de carne: 15 unidades
- Papa rellena: 12 unidades
- Arepa: 8 unidades
Ganancia total del lunes: $3,500

Martes:
- Empanada de carne: 18 unidades
- Papa rellena: 10 unidades
- Arepa: 10 unidades
Ganancia total del martes: $4,200

... y así para toda la semana
```

---

## 💰 Cálculo de Costos

### Componentes del costo de un producto

El costo total de un producto se calcula sumando:

#### 1. Costo de Masa Equivalente

```
Costo_Masa = Costo_Total_Lote / Total_Unidades_Producidas
```

**Ejemplo:**
- Lote de masa: $14,500
- Del lote salen: 20 empanadas
- Costo por empanada (masa): $14,500 ÷ 20 = $725

#### 2. Costo de Insumos Extra

```
Costo_Insumos_Extra = Σ (Precio_Insumo[i] × Cantidad_Usada[i])
                       i
```

**Ejemplo:**
- Carne: $8,000/kg, usas 0.1 kg → $800
- Salsa: $2,000/unidad, usas 0.5 unidades → $1,000
- Total insumos extra: $1,800

#### 3. Costo de Aceite

```
Costo_Aceite = Precio_Aceite_Promedio × 0.1
```

**Ejemplo:**
- Aceite promedio: $3,000/L
- Uso estimado: 0.1 L por producto
- Costo aceite: $300

#### 4. Costo de Empaques

```
Costo_Empaque = Precio_Empaque_Promedio
```

**Ejemplo:**
- Empaque promedio: $50
- Costo empaque: $50

### Fórmula completa del costo

```
Costo_Total = Costo_Masa + Costo_Insumos_Extra + Costo_Aceite + Costo_Empaque
```

**Ejemplo completo:**
```
Empanada de carne:
- Costo masa: $725
- Costo carne: $800
- Costo aceite: $300
- Costo empaque: $50
─────────────────────
Costo total: $1,875
```

### Cálculo de ganancia

```
Ganancia = Precio_Venta - Costo_Total
Margen = (Ganancia / Precio_Venta) × 100%
```

**Ejemplo:**
```
Empanada de carne:
- Precio venta: $2,000
- Costo total: $1,875
- Ganancia: $125
- Margen: ($125 / $2,000) × 100% = 6.25%
```

---

## 📊 Análisis de Sensibilidad

### ¿Qué es?

El análisis de sensibilidad te muestra **cómo cambian tus costos y ganancias** cuando cambia el precio de un insumo.

### Cómo funciona

#### Análisis de cambio de precio

1. **Seleccionas un insumo** (ej: harina)
2. **Ingresas un nuevo precio** (ej: $3,000 en lugar de $2,500)
3. **El sistema recalcula** todos los costos que usan ese insumo
4. **Te muestra el impacto** en cada producto

**Ejemplo:**
```
Harina sube de $2,500 a $3,000 (20% más)

Impacto en Empanada de carne:
- Costo original: $1,875
- Costo nuevo: $1,975
- Cambio: +$100 (5.3% más)
- Ganancia original: $125
- Ganancia nueva: $25
- Cambio: -$100 (80% menos)
```

#### Análisis de escenarios

El sistema genera 3 escenarios:

**1. Escenario Optimista**
- Todos los precios bajan X%
- Ver cuánto más ganarías

**2. Escenario Realista**
- Los precios se mantienen
- Situación actual

**3. Escenario Pesimista**
- Todos los precios suben X%
- Ver cuánto menos ganarías

**Ejemplo con 10% de cambio:**
```
Escenario Optimista (precios bajan 10%):
- Costos bajan: $500
- Ganancias suben: $500

Escenario Realista (precios iguales):
- Costos: $0
- Ganancias: $0

Escenario Pesimista (precios suben 10%):
- Costos suben: $500
- Ganancias bajan: $500
```

---

## 📖 Guía de Uso Paso a Paso

### Paso 1: Registrar Insumos

1. Ve a la pestaña **"📦 Insumos"**
2. Completa:
   - **Nombre**: Harina
   - **Cantidad**: 5
   - **Unidad**: kg
   - **Precio por unidad**: 2500
   - **Categoría**: Masa tradicional
3. Haz clic en **"Agregar"**

**Consejo:** Registra todos los insumos que compras regularmente.

### Paso 2: Crear Lote de Masa

1. Ve a la pestaña **"🥟 Masas"**
2. Completa:
   - **Nombre del lote**: Masa tradicional
   - **Cantidad total**: 6
   - **Unidad**: kg
3. Agrega los insumos usados:
   - Selecciona "Harina" y cantidad: 5 kg
   - Selecciona "Aceite" y cantidad: 0.5 L
4. Haz clic en **"Crear Lote"**

**Consejo:** Crea un lote por cada tipo de masa que uses.

### Paso 3: Definir Rendimiento

1. Ve a la pestaña **"📊 Rendimiento"**
2. Selecciona el lote de masa
3. Agrega productos y cantidades:
   - Empanada de carne: 20 unidades
   - Papa rellena: 15 unidades
4. Haz clic en **"Guardar Rendimiento"**

**Consejo:** Sé realista con las cantidades que realmente produces.

### Paso 4: Registrar Productos

1. Ve a la pestaña **"🍽️ Productos"**
2. Completa:
   - **Nombre**: Empanada de carne
   - **Masa asociada**: Masa tradicional
   - **Precio de venta**: 2000
   - **Demanda estimada/día**: 15
3. Agrega insumos extra:
   - Selecciona "Carne" y porciones: 0.1
4. Haz clic en **"Agregar Producto"**

**Consejo:** Registra todos los productos que vendes.

### Paso 5: Ver Costos

1. Ve a la pestaña **"💰 Costos"**
2. El sistema muestra automáticamente:
   - Costo unitario de cada producto
   - Ganancia unitaria
   - Margen de ganancia
3. Haz clic en **"Actualizar Costos"** si haces cambios

**Consejo:** Revisa regularmente para asegurar que tus productos sean rentables.

### Paso 6: Optimizar Producción

1. Ve a la pestaña **"⚡ Optimización"**
2. En **"Demanda Mínima"**:
   - Ingresa cuántas unidades mínimas necesitas de cada producto cada día
3. En **"Disponibilidad Financiera"**:
   - Ingresa cuánto dinero tienes disponible cada día
4. Haz clic en **"Resolver Optimización"**
5. El sistema te muestra:
   - Cuánto producir de cada producto cada día
   - Ganancia total proyectada

**Consejo:** Empieza con valores conservadores y ajusta según resultados.

### Paso 7: Analizar Sensibilidad

1. Ve a la pestaña **"📊 Sensibilidad"**
2. Selecciona un insumo
3. Ingresa un nuevo precio
4. Haz clic en **"Ver Resultado"**
5. El sistema muestra:
   - Cómo afecta a cada producto
   - Cambio en costos y ganancias
   - Recomendaciones

**Consejo:** Úsalo antes de cambiar de proveedor o cuando suban precios.

---

## 💼 Ejemplos Prácticos

### Ejemplo 1: Empanada de Carne

**Datos iniciales:**
- Harina: $2,500/kg
- Aceite: $3,000/L
- Carne: $8,000/kg
- Empaque: $50/unidad

**Lote de masa:**
- 5 kg harina: $12,500
- 0.5 L aceite: $1,500
- Total lote: $14,000
- Rendimiento: 20 empanadas
- Costo masa por empanada: $700

**Producto:**
- Masa: $700
- Carne (0.1 kg): $800
- Aceite (0.1 L): $300
- Empaque: $50
- **Costo total: $1,850**
- Precio venta: $2,000
- **Ganancia: $150 (7.5%)**

### Ejemplo 2: Optimización Semanal

**Restricciones:**
- Presupuesto diario: $50,000
- Demanda mínima: 10 empanadas/día

**Solución óptima:**
```
Lunes:    15 empanadas → Ganancia: $2,250
Martes:   18 empanadas → Ganancia: $2,700
Miércoles: 12 empanadas → Ganancia: $1,800
Jueves:   20 empanadas → Ganancia: $3,000
Viernes:  22 empanadas → Ganancia: $3,300
Sábado:   25 empanadas → Ganancia: $3,750
Domingo:  15 empanadas → Ganancia: $2,250

Ganancia total semanal: $19,050
```

### Ejemplo 3: Análisis de Sensibilidad

**Situación:** Harina sube 20%

**Resultado:**
```
Costo empanada:
- Antes: $1,850
- Después: $1,950
- Cambio: +$100

Ganancia empanada:
- Antes: $150
- Después: $50
- Cambio: -$100 (67% menos)

Recomendación:
⚠️ Este cambio te afecta mucho. Considera:
• Buscar otro proveedor
• Ajustar tus precios de venta
• Usar menos harina
```

---

## 🎓 Conceptos Clave

### ¿Qué es la Programación Lineal?

Es una técnica matemática que encuentra la **mejor solución** cuando:
- Tienes un **objetivo** (maximizar ganancias)
- Tienes **limitaciones** (presupuesto, demanda)
- Las relaciones son **lineales** (proporcionales)

### ¿Por qué funciona?

Porque prueba **todas las combinaciones posibles** y encuentra la que:
- Maximiza la ganancia
- Respeta todas las restricciones
- Es matemáticamente óptima

### ¿Es confiable?

Sí, es la misma técnica que usan empresas grandes como:
- Empresas de logística (optimizar rutas)
- Fábricas (optimizar producción)
- Supermercados (optimizar inventario)

---

## ❓ Preguntas Frecuentes

### ¿Necesito saber matemáticas para usarlo?

**No.** El sistema hace todos los cálculos por ti. Solo necesitas:
- Registrar tus datos (insumos, productos, precios)
- Entender los resultados (que están explicados de forma simple)

### ¿Qué pasa si no tengo medidas exactas?

**No hay problema.** El sistema funciona con proporciones:
- No necesitas saber "exactamente 0.123 kg"
- Puedes usar "1 porción" o "0.1 kg"
- Lo importante es ser consistente

### ¿Puedo tener varios tipos de masa?

**Sí.** Puedes crear:
- Masa tradicional
- Masa de yuca
- Masa de plátano
- Etc.

Cada una con sus propios insumos y rendimientos.

### ¿Qué hago si el resultado dice "No Factible"?

Significa que:
- Tu presupuesto es muy bajo para la demanda
- O la demanda es muy alta para el presupuesto

**Soluciones:**
- Reduce la demanda mínima
- Aumenta el presupuesto
- Revisa los costos de los productos

### ¿Los datos se guardan automáticamente?

**Sí.** Todo se guarda en archivos JSON en la carpeta `data/`:
- `insumos.json`
- `masas.json`
- `productos.json`

---

## 📝 Notas Finales

### Consejos para mejores resultados:

1. **Sé realista** con los datos que ingresas
2. **Actualiza precios** regularmente
3. **Revisa costos** frecuentemente
4. **Usa la optimización** para planificar la semana
5. **Analiza sensibilidad** antes de tomar decisiones importantes

### Recordatorios:

- Los costos se calculan automáticamente
- La optimización maximiza ganancias respetando restricciones
- El análisis de sensibilidad te ayuda a tomar decisiones
- Todos los datos se guardan automáticamente

---

## 📚 Referencias Técnicas

### Modelo de Programación Lineal

**Forma estándar:**
```
Maximizar: cᵀx
Sujeto a:  Ax ≤ b
           x ≥ 0
```

Donde:
- **c** = vector de ganancias
- **x** = vector de variables de decisión (cantidades a producir)
- **A** = matriz de coeficientes (costos)
- **b** = vector de restricciones (presupuestos)

### Solver utilizado

- **PuLP** (Python Linear Programming)
- Solver: **CBC** (Coin-or Branch and Cut)
- Método: **Simplex** o **Branch and Bound**

---

**¡Disfruta optimizando tu negocio! 🍽️**

*Este documento explica todo el funcionamiento del sistema de manera simplificada pero completa. Si tienes dudas, revisa los ejemplos prácticos o experimenta con el programa.*

