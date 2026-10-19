# 📊 Cómo se Calculan las Ganancias

## 1. Ganancia por Producto (Unitaria)

**Fórmula:**
```
Ganancia Unitaria = Precio de Venta - Costo Unitario
```

**Ejemplo: Empanada de Pollo**
- Precio de venta: $2,300
- Costo unitario: $1,205.71
- **Ganancia unitaria: $1,094.29**

---

## 2. Ganancia Total en la Optimización

**Fórmula:**
```
Ganancia Total = Σ Σ (Cantidad Producida[i,j] × Ganancia Unitaria[i])
                 i j
```

Donde:
- `i` = producto
- `j` = día de la semana
- Se suma la ganancia de cada unidad producida de cada producto en cada día

**Ejemplo práctico:**
- Empanada de pollo: ganancia unitaria = $1,094.29
- Si produces 10 unidades el lunes: 10 × $1,094.29 = $10,942.90
- Si produces 10 unidades todos los días (7 días): 70 × $1,094.29 = $76,600.30

---

## 3. Cálculo del Costo Unitario

El costo unitario incluye:
1. **Costo de masa** (distribuido entre productos del lote)
2. **Costo de insumos extra** (rellenos, salsas)
3. **Costo de aceite** (estimado: 0.1 unidades × precio aceite)
4. **Costo de empaques** (promedio de empaques disponibles)

---

## 4. Por qué sale "No Factible"

El modelo es **NO FACTIBLE** cuando:
- El presupuesto diario es menor que el costo necesario para cumplir la demanda mínima
- **Ejemplo:**
  - Demanda: 20 unidades/día de "papa rellena"
  - Costo unitario: $1,830.71
  - Costo diario necesario: 20 × $1,830.71 = **$36,614.20**
  - Presupuesto diario: $1,000
  - **Problema:** $1,000 < $36,614.20 → NO FACTIBLE

---

## 5. Valores que SÍ Funcionan

### Opción A: Empanada de Queso (más barata)
- **Producto:** empanada de queso
- **Demanda:** 10 unidades/día
- **Presupuesto:** $25,000/día
- **Costo diario:** 10 × $1,180.71 = $11,807.10
- **Resultado:** ✅ FACTIBLE (presupuesto suficiente)

### Opción B: Empanada de Pollo
- **Producto:** empanada de pollo
- **Demanda:** 8 unidades/día
- **Presupuesto:** $20,000/día
- **Costo diario:** 8 × $1,205.71 = $9,645.68
- **Resultado:** ✅ FACTIBLE

### Opción C: Papa Rellena (si quieres mantener 20 unidades)
- **Producto:** papa rellena
- **Demanda:** 20 unidades/día
- **Presupuesto:** $45,000/día (mínimo)
- **Costo diario:** 20 × $1,830.71 = $36,614.20
- **Resultado:** ✅ FACTIBLE

---

## 6. Fórmula Rápida para Calcular Presupuesto Mínimo

```
Presupuesto Mínimo Diario = (Costo Unitario × Demanda Diaria) × 1.2
```

El 1.2 agrega un 20% de margen de seguridad.

---

## 7. Resumen

- **Ganancia unitaria:** Precio - Costo (por producto)
- **Ganancia total:** Suma de todas las ganancias de todas las unidades producidas
- **El modelo maximiza la ganancia total** respetando:
  - Demanda mínima (debe producir al menos lo solicitado)
  - Presupuesto diario (no puede gastar más del disponible)

