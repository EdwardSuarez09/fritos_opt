# -*- coding: utf-8 -*-
"""
Bot hibrido de analisis de sensibilidad.
Combina busqueda en fuentes de conocimiento, historial mensual y calculos en vivo.
"""
import re
from difflib import SequenceMatcher, get_close_matches
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from core.sensibilidad import AnalizadorSensibilidad
from core.historial import HistorialMensual
from core.insumos import InsumoManager
from core.productos import ProductoManager
from core.costos import CalculadorCostos

FUENTES_DIR = Path(__file__).resolve().parent.parent / "fuentes"

PALABRAS_VACIAS = {
    "que", "es", "un", "una", "el", "la", "los", "las", "de", "del", "al", "a", "en", "y", "o",
    "para", "por", "con", "sin", "como", "cuando", "cual", "donde", "dime", "sobre", "se", "su",
    "define", "explica", "ejemplo", "resumen", "importancia", "funcion", "relacion", "caracteristica",
    "ventaja", "riesgo", "importa", "funciona", "sirve", "hace", "aplica", "pregunta", "datos",
    "pasa", "si", "sube", "baja", "suben", "bajan", "precio", "precios", "mucho", "mas", "menos",
    "cuanto", "cuanta", "cuantos", "cuantas", "mes", "pasado", "mayo", "vendio", "vendi", "vende",
    "cuesta", "cuestan", "vale", "valen", "tiene", "tienen", "fue", "son", "esta", "estan",
}
UMBRAL_COINCIDENCIA = 0.60

TAGS_DINAMICOS = {
    "HISTORIAL_VARIACION_MAX", "HISTORIAL_TOP_VARIACION", "HISTORIAL_VENTAS_MES",
    "HISTORIAL_UNIDADES_MES", "HISTORIAL_PRODUCTO_TOP", "HISTORIAL_PRODUCTO_PEOR",
    "HISTORIAL_TOP_PRODUCTOS", "HISTORIAL_GASTOS_MES", "HISTORIAL_GANANCIA_MES",
    "HISTORIAL_SEMANA_TOP", "HISTORIAL_SEMANA_GASTO", "HISTORIAL_RESUMEN_MES",
    "ESCENARIO_PESIMISTA", "ESCENARIO_OPTIMISTA",
    "INSUMO_MAS_CARO", "PRODUCTO_MAS_RENTABLE",
}

# Que grafica corresponde a cada tag dinamico (para la UI)
TAG_GRAFICA = {
    "HISTORIAL_VENTAS_MES": "ventas",
    "HISTORIAL_UNIDADES_MES": "ventas",
    "HISTORIAL_GANANCIA_MES": "resumen",
    "HISTORIAL_SEMANA_TOP": "ventas",
    "HISTORIAL_PRODUCTO_TOP": "productos",
    "HISTORIAL_PRODUCTO_PEOR": "productos",
    "HISTORIAL_TOP_PRODUCTOS": "productos",
    "PRODUCTO_MAS_RENTABLE": "productos",
    "HISTORIAL_VARIACION_MAX": "insumos",
    "HISTORIAL_TOP_VARIACION": "insumos",
    "HISTORIAL_GASTOS_MES": "resumen",
    "HISTORIAL_SEMANA_GASTO": "insumos",
    "INSUMO_MAS_CARO": "insumos",
    "HISTORIAL_RESUMEN_MES": "resumen",
    "ESCENARIO_PESIMISTA": "escenarios",
    "ESCENARIO_OPTIMISTA": "escenarios",
}


def formato_cop(valor: float) -> str:
    """Formatea un monto en pesos colombianos (COP). Ej: $3.450.000 COP"""
    negativo = valor < 0
    entero = round(abs(valor))
    texto = f"{entero:,}".replace(",", ".")
    prefijo = "-$" if negativo else "$"
    return f"{prefijo}{texto} COP"


def normalizar(texto: str) -> str:
    texto = texto.lower().strip()
    cambios = str.maketrans("áéíóúüñ", "aeiouun")
    texto = texto.translate(cambios)
    texto = re.sub(r"[^a-z0-9\s]", " ", texto)
    return re.sub(r"\s+", " ", texto).strip()


def palabras_clave(clave: str) -> set:
    return {p for p in clave.split() if p not in PALABRAS_VACIAS and len(p) > 1}


def coincidencia_valida(clave_usuario: str, clave_base: str, score: float) -> bool:
    if score >= 0.92:
        return True
    kw_usuario = palabras_clave(clave_usuario)
    kw_base = palabras_clave(clave_base)
    if not kw_usuario:
        return False
    return bool(kw_usuario & kw_base)


def cargar_fuentes() -> Dict[str, Dict[str, dict]]:
    fuentes = {}
    if not FUENTES_DIR.exists():
        return fuentes

    for ruta in sorted(FUENTES_DIR.glob("*.txt")):
        nombre = ruta.stem.replace("_", " ").title()
        memoria = {}
        for linea in ruta.read_text(encoding="utf-8").splitlines():
            if "?r:" not in linea or linea.strip().startswith("#"):
                continue
            pregunta, respuesta = linea.split("?r:", 1)
            pregunta = pregunta.replace("p:", "", 1).strip()
            respuesta = respuesta.strip().rstrip(".")
            clave = normalizar(pregunta)
            if clave and respuesta:
                memoria[clave] = {"pregunta": pregunta, "respuesta": respuesta}
        fuentes[nombre] = memoria
    return fuentes


class BotSensibilidad:
    """Motor del bot hibrido de sensibilidad"""

    def __init__(
        self,
        insumo_manager: InsumoManager,
        producto_manager: ProductoManager,
        calculador_costos: CalculadorCostos,
        analizador: AnalizadorSensibilidad,
        optimizador=None,
    ):
        self.insumos = insumo_manager
        self.productos = producto_manager
        self.calculador = calculador_costos
        self.analizador = analizador
        self.optimizador = optimizador
        self.historial = HistorialMensual()
        self.historial.set_nombres_insumos(insumo_manager)
        self.historial.set_nombres_productos(producto_manager)
        self.fuentes = cargar_fuentes()

    def total_preguntas(self) -> int:
        return sum(len(m) for m in self.fuentes.values())

    def buscar_en_fuentes(self, pregunta: str) -> Optional[dict]:
        clave = normalizar(pregunta)
        if not clave:
            return None

        mejor = None
        sugerencias = []

        for nombre_fuente, memoria in self.fuentes.items():
            if clave in memoria:
                item = memoria[clave]
                return {
                    "respuesta": item["respuesta"],
                    "fuente": nombre_fuente,
                    "pregunta": item["pregunta"],
                    "score": 1.0,
                    "exacta": True,
                }

            for pregunta_base, item in memoria.items():
                similitud = SequenceMatcher(None, clave, pregunta_base).ratio()
                kw_usuario = palabras_clave(clave)
                kw_base = palabras_clave(pregunta_base)
                cruce = len(kw_usuario & kw_base) / max(len(kw_usuario), 1)
                score = (similitud * 0.70) + (cruce * 0.30)
                if mejor is None or score > mejor["score"]:
                    mejor = {
                        "respuesta": item["respuesta"],
                        "fuente": nombre_fuente,
                        "pregunta": item["pregunta"],
                        "pregunta_base": pregunta_base,
                        "score": score,
                        "exacta": False,
                    }
                sugerencias.append((pregunta_base, item["pregunta"], nombre_fuente))

        if (
            mejor
            and mejor["score"] >= UMBRAL_COINCIDENCIA
            and coincidencia_valida(clave, mejor["pregunta_base"], mejor["score"])
        ):
            mejor.pop("pregunta_base", None)
            return mejor

        claves = [base for base, _original, _fuente in sugerencias]
        cercanas = get_close_matches(clave, claves, n=5, cutoff=0.35)
        if cercanas:
            texto = []
            for cercana in cercanas:
                for base, original, fuente in sugerencias:
                    if base == cercana:
                        texto.append(f"'{original}' ({fuente})")
                        break
            return {"sin_respuesta": True, "sugerencias": texto}

        return {"sin_respuesta": True, "sugerencias": []}

    def _resolver_tag(self, tag: str, pregunta: str) -> Optional[str]:
        meta = self.historial.meta
        mes = meta.get("mes", "el mes")
        anio = meta.get("anio", "")

        if tag == "HISTORIAL_VARIACION_MAX":
            resultado = self.historial.insumo_mas_volatil()
            if not resultado:
                return "No hay datos de variacion de precios en el historial."
            nombre, datos = resultado
            return (
                f"En {mes} {anio}, el insumo que mas subio fue {nombre}: "
                f"paso de {formato_cop(datos['min'])} a {formato_cop(datos['max'])} "
                f"(+{datos['variacion_pct']:.1f}%). Promedio del mes: {formato_cop(datos['promedio'])}."
            )

        if tag == "HISTORIAL_TOP_VARIACION":
            tops = self.historial.insumos_mas_volatiles(3)
            if not tops:
                return "No hay datos de variacion."
            lineas = [f"Insumos que mas variaron en {mes} {anio}:"]
            for i, (nombre, datos) in enumerate(tops, 1):
                lineas.append(
                    f"  {i}. {nombre}: {formato_cop(datos['min'])} -> {formato_cop(datos['max'])} "
                    f"(+{datos['variacion_pct']:.1f}%)"
                )
            return "\n".join(lineas)

        if tag == "HISTORIAL_VENTAS_MES":
            resumen = self.historial.ventas_mes()
            return (
                f"En {mes} {anio} vendiste {resumen.get('total_unidades', 0):,} unidades "
                f"con ingreso bruto de {formato_cop(resumen.get('ingreso_bruto', 0))}. "
                f"Ganancia estimada del mes: {formato_cop(resumen.get('ganancia_estimada', 0))}."
            )

        if tag == "HISTORIAL_UNIDADES_MES":
            resumen = self.historial.ventas_mes()
            return (
                f"En {mes} {anio} vendiste {resumen.get('total_unidades', 0):,} unidades en total "
                f"({meta.get('dias_operacion', 26)} dias de operacion)."
            )

        if tag == "HISTORIAL_PRODUCTO_TOP":
            resultado = self.historial.producto_mas_vendido()
            if not resultado:
                return "No hay datos de ventas por producto."
            nombre, datos = resultado
            return (
                f"El producto mas vendido en {mes} fue {nombre} con "
                f"{datos['unidades_vendidas']:,} unidades "
                f"({formato_cop(datos['ingreso_total'])} de ingreso)."
            )

        if tag == "HISTORIAL_PRODUCTO_PEOR":
            resultado = self.historial.producto_menos_vendido()
            if not resultado:
                return "No hay datos de ventas por producto."
            nombre, datos = resultado
            return (
                f"El producto que menos vendio en {mes} fue {nombre} con "
                f"{datos['unidades_vendidas']:,} unidades "
                f"({formato_cop(datos['ingreso_total'])} de ingreso)."
            )

        if tag == "HISTORIAL_TOP_PRODUCTOS":
            tops = self.historial.top_productos(3)
            if not tops:
                return "No hay datos de ventas."
            lineas = [f"Top 3 productos en {mes} {anio}:"]
            for i, (nombre, datos) in enumerate(tops, 1):
                lineas.append(
                    f"  {i}. {nombre}: {datos['unidades_vendidas']:,} uds, "
                    f"{formato_cop(datos['ingreso_total'])}"
                )
            return "\n".join(lineas)

        if tag == "HISTORIAL_GASTOS_MES":
            total = self.historial.total_gastado_mes()
            resumen = self.historial.ventas_mes()
            return (
                f"En {mes} gastaste {formato_cop(total)} en compras de insumos. "
                f"Ingreso por ventas: {formato_cop(resumen.get('ingreso_bruto', 0))}."
            )

        if tag == "HISTORIAL_GANANCIA_MES":
            resumen = self.historial.ventas_mes()
            ganancia = resumen.get("ganancia_estimada", 0)
            ingreso = resumen.get("ingreso_bruto", 0)
            gasto = self.historial.total_gastado_mes()
            estado = "ganancia" if ganancia >= 0 else "perdida"
            return (
                f"En {mes} {anio}: ingreso {formato_cop(ingreso)}, "
                f"gasto en insumos {formato_cop(gasto)}, "
                f"{estado} estimada de {formato_cop(abs(ganancia))}."
            )

        if tag == "HISTORIAL_SEMANA_TOP":
            resultado = self.historial.semana_mejor_ventas()
            if not resultado:
                return "No hay datos por semana."
            nombre, datos = resultado
            return (
                f"La mejor semana de ventas fue {nombre}: "
                f"{datos.get('unidades', 0):,} unidades, "
                f"ingreso {formato_cop(datos.get('ingreso', 0))}."
            )

        if tag == "HISTORIAL_SEMANA_GASTO":
            resultado = self.historial.semana_mayor_gasto()
            if not resultado:
                return "No hay datos de compras por semana."
            nombre, datos = resultado
            return (
                f"La semana con mayor gasto en insumos fue {nombre}: "
                f"{formato_cop(datos.get('total_gastado', 0))}."
            )

        if tag == "HISTORIAL_RESUMEN_MES":
            resumen = self.historial.ventas_mes()
            top = self.historial.producto_mas_vendido()
            volatil = self.historial.insumo_mas_volatil()
            lineas = [
                f"Resumen de {mes} {anio}:",
                f"  Ventas: {resumen.get('total_unidades', 0):,} unidades, "
                f"{formato_cop(resumen.get('ingreso_bruto', 0))} de ingreso.",
                f"  Gasto en insumos: {formato_cop(self.historial.total_gastado_mes())}.",
                f"  Ganancia estimada: {formato_cop(resumen.get('ganancia_estimada', 0))}.",
            ]
            if top:
                lineas.append(f"  Producto estrella: {top[0]} ({top[1]['unidades_vendidas']:,} uds).")
            if volatil:
                lineas.append(
                    f"  Insumo mas volatil: {volatil[0]} (+{volatil[1]['variacion_pct']:.1f}%)."
                )
            return "\n".join(lineas)

        if tag == "INSUMO_MAS_CARO":
            insumos = sorted(self.insumos.listar(), key=lambda i: i.precio_unidad, reverse=True)
            if not insumos:
                return "No hay insumos registrados."
            top3 = insumos[:3]
            lineas = ["Insumos mas caros actualmente:"]
            for i, ins in enumerate(top3, 1):
                lineas.append(
                    f"  {i}. {ins.nombre}: {formato_cop(ins.precio_unidad)}/{ins.unidad}"
                )
            return "\n".join(lineas)

        if tag == "PRODUCTO_MAS_RENTABLE":
            productos = self.productos.listar()
            if not productos:
                return "No hay productos registrados."
            ranking = []
            for p in productos:
                ganancia = self.calculador.calcular_ganancia_producto(p.id)
                costo = self.calculador.calcular_costo_producto(p.id)
                ranking.append((p.nombre, ganancia, costo, p.precio_venta))
            ranking.sort(key=lambda x: x[1], reverse=True)
            lineas = ["Productos mas rentables (ganancia por unidad):"]
            for i, (nombre, gan, costo, venta) in enumerate(ranking[:3], 1):
                margen = (gan / venta * 100) if venta > 0 else 0
                lineas.append(
                    f"  {i}. {nombre}: ganancia {formato_cop(gan)} "
                    f"(costo {formato_cop(costo)}, venta {formato_cop(venta)}, margen {margen:.0f}%)"
                )
            return "\n".join(lineas)

        if tag in ("ESCENARIO_PESIMISTA", "ESCENARIO_OPTIMISTA"):
            pct = abs(self._extraer_porcentaje(pregunta) or 10.0)
            escenarios = self.analizador.generar_escenarios(pct)
            key = "pesimista" if tag == "ESCENARIO_PESIMISTA" else "optimista"
            esc = escenarios[key]
            res = esc["resultados"]
            impacto_g = res.get("impacto_total_ganancia", 0)
            impacto_c = res.get("impacto_total_costo", 0)
            n_prod = len(res.get("productos_afectados", []))
            resumen = self.historial.ventas_mes()
            unidades_mes = resumen.get("total_unidades", 0)
            impacto_mes = impacto_g * unidades_mes if unidades_mes else 0

            if impacto_g < 0:
                gan_txt = f"bajan {formato_cop(abs(impacto_g))} por unidad"
            elif impacto_g > 0:
                gan_txt = f"suben {formato_cop(impacto_g)} por unidad"
            else:
                gan_txt = "no cambian"
            if impacto_c > 0:
                cost_txt = f"suben {formato_cop(abs(impacto_c))} por unidad"
            elif impacto_c < 0:
                cost_txt = f"bajan {formato_cop(abs(impacto_c))} por unidad"
            else:
                cost_txt = "no cambian"

            texto = (
                f"Escenario {esc['nombre']} ({esc['descripcion']}): "
                f"costos {cost_txt}, ganancias {gan_txt}. "
                f"{n_prod} productos afectados."
            )
            if unidades_mes and impacto_mes != 0:
                dir_m = "perdida" if impacto_mes < 0 else "ganancia"
                texto += (
                    f" Impacto mensual estimado ({unidades_mes:,} uds/mes): "
                    f"{dir_m} de {formato_cop(abs(impacto_mes))}."
                )
            return texto

        return None

    def _encontrar_insumo(self, pregunta: str):
        clave = normalizar(pregunta)
        insumos = self.insumos.listar()
        mejor = None
        mejor_score = 0.0

        for insumo in insumos:
            nombre_norm = normalizar(insumo.nombre)
            id_norm = normalizar(insumo.id.replace("_", " "))
            similitud = SequenceMatcher(None, clave, nombre_norm).ratio()
            kw_preg = palabras_clave(clave)
            kw_ins = palabras_clave(nombre_norm) | palabras_clave(id_norm)
            comunes = kw_preg & kw_ins
            cruce = len(comunes) / max(len(kw_ins), 1)
            score = max(similitud, cruce)
            for palabra in kw_ins:
                if len(palabra) >= 4 and palabra in clave.split():
                    score = max(score, 0.80)
            if insumo.id.replace("_", " ") in clave or nombre_norm in clave:
                score = max(score, 0.85)
            if score > mejor_score:
                mejor_score = score
                mejor = insumo

        if mejor and mejor_score >= 0.35:
            return mejor, mejor_score
        return None, 0.0

    def _encontrar_producto(self, pregunta: str):
        clave = normalizar(pregunta)
        productos = self.productos.listar()
        mejor = None
        mejor_score = 0.0

        for producto in productos:
            nombre_norm = normalizar(producto.nombre)
            id_norm = normalizar(producto.id.replace("_", " "))
            similitud = SequenceMatcher(None, clave, nombre_norm).ratio()
            kw_preg = palabras_clave(clave)
            kw_prod = palabras_clave(nombre_norm) | palabras_clave(id_norm)
            comunes = kw_preg & kw_prod
            cruce = len(comunes) / max(len(kw_prod), 1)
            score = max(similitud, cruce)
            for palabra in kw_prod:
                if len(palabra) >= 4 and palabra in clave.split():
                    score = max(score, 0.80)
            if score > mejor_score:
                mejor_score = score
                mejor = producto

        if mejor and mejor_score >= 0.35:
            return mejor, mejor_score
        return None, 0.0

    def _extraer_porcentaje(self, pregunta: str) -> Optional[float]:
        clave = normalizar(pregunta)
        match = re.search(r"(\d+(?:\.\d+)?)\s*(?:por\s*ciento|pct|%)?", clave)
        if match:
            valor = float(match.group(1))
            if "baja" in clave or "bajan" in clave:
                return -abs(valor)
            return abs(valor)
        return None

    def _calcular_nuevo_precio(self, precio_actual: float, pregunta: str) -> Optional[float]:
        clave = normalizar(pregunta)
        pct = self._extraer_porcentaje(pregunta)

        match_precio = re.search(r"(?:a|en|de|queda|cuesta)\s*(\d+(?:\.\d+)?)", clave)
        if match_precio and any(w in clave for w in ("pasa", "llega", "cuesta", "queda", "precio")):
            return float(match_precio.group(1))

        numeros = re.findall(r"\d+(?:\.\d+)?", clave)
        for num_str in numeros:
            num = float(num_str)
            if num > precio_actual * 0.3 and num < precio_actual * 5:
                if any(w in clave for w in ("pasa", "llega", "cuesta", "queda")):
                    return num

        if pct is not None:
            if pct < 0 or "baja" in clave or "bajan" in clave:
                return precio_actual * (1 - abs(pct) / 100)
            if any(w in clave for w in ("sube", "suben", "aumenta", "subio")):
                return precio_actual * (1 + abs(pct) / 100)

        return None

    def _analizar_cambio_insumo(self, insumo, nuevo_precio: float) -> str:
        resultados = self.analizador.analizar_cambio_precio_insumo(insumo.id, nuevo_precio)
        if not resultados:
            return f"No pude analizar el insumo {insumo.nombre}."

        cambio = resultados["cambio_porcentual_precio"]
        meta = self.historial.meta
        mes = meta.get("mes", "mayo")
        lineas = [
            f"Analisis de {resultados['insumo']}:",
            f"Precio: {formato_cop(resultados['precio_original'])} -> "
            f"{formato_cop(resultados['nuevo_precio'])} "
            f"({'+' if cambio >= 0 else ''}{cambio:.1f}%).",
        ]

        if resultados["productos_afectados"]:
            lineas.append(f"Productos afectados ({len(resultados['productos_afectados'])}):")
            impactos_mes = []
            for producto_id, impacto_g in resultados["impacto_ganancias"].items():
                nombre = impacto_g["nombre"]
                imp = impacto_g["impacto"]
                unidades = self.historial.ventas_producto(producto_id)
                if imp != 0:
                    impactos_mes.append((nombre, imp, unidades, imp * unidades if unidades else 0))
                    dir_g = "baja" if imp < 0 else "sube"
                    lineas.append(
                        f"  - {nombre}: ganancia/unidad {dir_g} {formato_cop(abs(imp))}"
                    )

            if impactos_mes:
                lineas.append("")
                lineas.append(f"Impacto mensual estimado (ventas de {mes}):")
                total_mes = 0
                for nombre, imp, unidades, impacto_mes in sorted(
                    impactos_mes, key=lambda x: abs(x[3]), reverse=True
                )[:5]:
                    if unidades > 0:
                        total_mes += impacto_mes
                        dir_m = "pierdes" if impacto_mes < 0 else "ganas"
                        lineas.append(
                            f"  - {nombre}: {unidades:,} uds x {formato_cop(abs(imp))} = "
                            f"{dir_m} {formato_cop(abs(impacto_mes))}/mes"
                        )
                if total_mes != 0:
                    dir_t = "perdida" if total_mes < 0 else "ganancia"
                    lineas.append(f"  Total estimado: {dir_t} de {formato_cop(abs(total_mes))}/mes.")
        else:
            lineas.append("Ningun producto se ve afectado por este cambio.")

        ig = resultados["impacto_total_ganancia"]
        if ig < -1000:
            lineas.append("Consejo: impacto alto. Sube precio de venta o busca otro proveedor.")
        elif ig < 0:
            lineas.append("Consejo: impacto moderado. Revisa tus margenes.")
        elif ig > 0:
            lineas.append("Consejo: este cambio te beneficia.")

        return "\n".join(lineas)

    def _respuesta_costo_producto(self, producto) -> str:
        costo = self.calculador.calcular_costo_producto(producto.id)
        ganancia = self.calculador.calcular_ganancia_producto(producto.id)
        venta = producto.precio_venta
        margen = (ganancia / venta * 100) if venta > 0 else 0
        ventas_hist = self.historial.ventas_por_producto_nombre(producto.id)
        extra = ""
        if ventas_hist:
            extra = (
                f" En {self.historial.meta.get('mes', 'mayo')} vendiste "
                f"{ventas_hist['unidades_vendidas']:,} unidades "
                f"({formato_cop(ventas_hist['ingreso_total'])})."
            )
        return (
            f"{producto.nombre}: costo {formato_cop(costo)}, "
            f"precio venta {formato_cop(venta)}, "
            f"ganancia {formato_cop(ganancia)} por unidad (margen {margen:.0f}%).{extra}"
        )

    def _respuesta_ventas_producto(self, producto) -> str:
        ventas_hist = self.historial.ventas_por_producto_nombre(producto.id)
        mes = self.historial.meta.get("mes", "mayo")
        anio = self.historial.meta.get("anio", "")
        if not ventas_hist:
            return f"No tengo ventas historicas de {producto.nombre} en {mes}."
        return (
            f"En {mes} {anio}, {producto.nombre}: "
            f"{ventas_hist['unidades_vendidas']:,} unidades vendidas, "
            f"ingreso {formato_cop(ventas_hist['ingreso_total'])} "
            f"(precio promedio {formato_cop(ventas_hist.get('precio_promedio', 0))})."
        )

    def _respuesta_precio_insumo(self, insumo) -> str:
        hist = self.historial.precio_historico_insumo(insumo.id)
        texto = (
            f"{insumo.nombre}: precio actual {formato_cop(insumo.precio_unidad)}/{insumo.unidad}."
        )
        if hist:
            texto += (
                f" En {self.historial.meta.get('mes', 'mayo')}: min {formato_cop(hist['min'])}, "
                f"max {formato_cop(hist['max'])}, promedio {formato_cop(hist['promedio'])} "
                f"(variacion {hist['variacion_pct']:.1f}%)."
            )
        return texto

    def _es_pregunta_cambio_precio(self, pregunta: str) -> bool:
        clave = normalizar(pregunta)
        if any(w in clave for w in ("que pasa", "que pasaria", "simula", "escenario")):
            return True
        cambio = ("sube", "suben", "baja", "bajan", "aumenta", "subio", "llega", "queda")
        if any(w in clave for w in cambio):
            return True
        if ("por ciento" in clave or " pct " in f" {clave} ") and "%" not in pregunta:
            nums = re.findall(r"\d+", clave)
            if nums and any(w in clave for w in cambio + ("precio", "sube", "baja")):
                return True
        if "%" in pregunta and any(w in clave for w in cambio + ("sube", "baja", "precio")):
            return True
        return False

    def _es_pregunta_costo(self, pregunta: str) -> bool:
        clave = normalizar(pregunta)
        if any(w in clave for w in ("empanada", "arepa", "papa", "pastel", "carimanola", "producto")):
            return any(w in clave for w in (
                "cuesta", "cuestan", "costo", "costos", "produce", "producir", "vale hacer",
            ))
        return any(w in clave for w in ("costo", "costos", "produce", "producir", "vale hacer"))

    def _es_pregunta_ganancia(self, pregunta: str) -> bool:
        clave = normalizar(pregunta)
        return any(w in clave for w in (
            "ganancia", "ganancias", "margen", "rentable", "rentabilidad", "utilidad", "gana",
        ))

    def _es_pregunta_ventas_producto(self, pregunta: str) -> bool:
        clave = normalizar(pregunta)
        return any(w in clave for w in (
            "vendi", "vendio", "vendidos", "vendidas", "unidades", "cuantas", "cuantos",
        )) and any(w in clave for w in (
            "empanada", "arepa", "papa", "pastel", "carimanola", "producto",
        ))

    def _pregunta_es_de_ventas(self, clave: str) -> bool:
        return any(w in clave for w in (
            "vendi", "vendio", "vendidos", "vendidas", "ventas", "ingreso", "ingresos",
            "unidades", "estrella", "top", "resumen", "gane", "ganancia del", "utilidad",
        ))

    def _pregunta_menciona_insumo(self, clave: str, insumo) -> bool:
        nombre_norm = normalizar(insumo.nombre)
        kw_ins = palabras_clave(nombre_norm) | palabras_clave(normalizar(insumo.id.replace("_", " ")))
        return bool(palabras_clave(clave) & kw_ins)

    def _responder_simulacion(self, pregunta: str, clave: str) -> Optional[dict]:
        """Simula cambio de precio de un insumo; asume % historico si no se indica"""
        insumo, score = self._encontrar_insumo(pregunta)
        if not insumo:
            return None
        nuevo_precio = self._calcular_nuevo_precio(insumo.precio_unidad, pregunta)
        nota = ""
        if not nuevo_precio and any(w in clave for w in ("sube", "suben", "baja", "bajan", "aumenta", "subio")):
            # Sin cifra explicita: asumir variacion historica de mayo (o 10%)
            hist = self.historial.precio_historico_insumo(insumo.id)
            pct_asumido = hist.get("variacion_pct", 10.0) if hist else 10.0
            if "baja" in clave or "bajan" in clave:
                nuevo_precio = insumo.precio_unidad * (1 - pct_asumido / 100)
                direccion = "baja"
            else:
                nuevo_precio = insumo.precio_unidad * (1 + pct_asumido / 100)
                direccion = "sube"
            nota = (
                f"\nNota: no indicaste cuanto {direccion}, asi que asumi "
                f"{pct_asumido:.1f}% (la variacion de mayo). "
                f"Puedes precisar, ej: 'si {insumo.nombre} {direccion} 20%'."
            )
        if not nuevo_precio or nuevo_precio <= 0:
            return None
        texto = self._analizar_cambio_insumo(insumo, nuevo_precio)
        extra = nota
        if score < 0.92:
            extra += f" (interprete que hablas de '{insumo.nombre}')"
        return {
            "respuesta": texto + extra,
            "tipo": "calculo",
            "exacta": score >= 0.92,
            "score": score,
            "grafica": "impacto",
        }

    def _es_pregunta_produccion(self, clave: str) -> bool:
        if "que debo producir" in clave or "que produzco" in clave:
            return True
        claves_prod = ("producir", "produccion", "fabricar", "preparar", "hacer")
        guia = ("cuanto", "que", "recomienda", "recomiendas", "recomendacion",
                "sugieres", "sugerencia", "deberia", "debo", "conviene", "optimo", "optima")
        tiene_prod = any(w in clave for w in claves_prod)
        return tiene_prod and any(w in clave for w in guia)

    def _recomendar_produccion(self) -> str:
        """
        Recomienda qué producir priorizando rentabilidad y demanda.

        Si hay un optimizador disponible, ejecuta el modelo de programación
        lineal; si no (o si resulta no factible), usa un ranking por ganancia
        unitaria y demanda estimada.
        """
        productos = self.productos.listar()
        if not productos:
            return "No hay productos registrados para recomendar produccion."

        # Intento con el modelo de optimizacion (programacion lineal)
        if self.optimizador is not None:
            try:
                from core.optimizador import DIAS_SEMANA

                demanda = {}
                costo_por_dia = {dia: 0.0 for dia in DIAS_SEMANA}
                for p in productos:
                    minimo = max(int(p.demanda_estimada), 0)
                    costo_unit = self.calculador.calcular_costo_producto(p.id)
                    for dia in DIAS_SEMANA:
                        demanda[(p.id, dia)] = minimo
                        costo_por_dia[dia] += costo_unit * minimo
                # Presupuesto ajustado a la demanda (margen 8% para factibilidad).
                # El modelo no tiene tope maximo de produccion; un presupuesto
                # ceniido evita que "inunde" el producto mas rentable.
                fondos = {dia: costo_por_dia[dia] * 1.08 for dia in DIAS_SEMANA}
                res = self.optimizador.optimizar(demanda, fondos)
                if res.get("estado") == "Optimal":
                    totales = []
                    for prod in res.get("productos", []):
                        total = sum(prod["produccion"].values())
                        if total > 0:
                            totales.append((prod["nombre"], total))
                    totales.sort(key=lambda x: x[1], reverse=True)
                    lineas = [
                        f"  - {nombre}: {int(total)} uds/semana"
                        for nombre, total in totales[:8]
                    ]
                    ganancia = res.get("ganancia_total", 0)
                    return (
                        "Produccion recomendada (modelo de optimizacion, "
                        "maximiza ganancia respetando demanda y presupuesto):\n"
                        + "\n".join(lineas)
                        + f"\nGanancia total estimada: {formato_cop(ganancia)}."
                    )
            except Exception:
                pass  # Cae al ranking por rentabilidad

        # Fallback: ranking por rentabilidad y demanda
        ranking = []
        for p in productos:
            ganancia = self.calculador.calcular_ganancia_producto(p.id)
            ranking.append((p.nombre, ganancia, p.demanda_estimada))
        ranking.sort(key=lambda x: (x[1] * max(x[2], 1)), reverse=True)
        lineas = []
        for nombre, ganancia, demanda in ranking[:8]:
            lineas.append(
                f"  - {nombre}: gana {formato_cop(ganancia)}/u, "
                f"demanda ~{demanda}/dia"
            )
        return (
            "Produccion recomendada (priorizando los mas rentables segun "
            "ganancia por unidad y demanda):\n" + "\n".join(lineas)
            + "\nProduce primero los de arriba; son los que mas aportan a la ganancia."
        )

    def responder(self, pregunta: str) -> dict:
        """Procesa una pregunta y devuelve respuesta estructurada"""
        clave = normalizar(pregunta)

        # Produccion recomendada (optimizacion)
        if self._es_pregunta_produccion(clave):
            return {
                "respuesta": self._recomendar_produccion(),
                "tipo": "produccion",
                "exacta": True,
                "grafica": "productos",
            }

        # Resumen explicito
        if any(w in clave for w in ("resumen", "resumeme", "como estuvo", "como me fue")):
            texto = self._resolver_tag("HISTORIAL_RESUMEN_MES", pregunta)
            return {"respuesta": texto, "tipo": "historial", "exacta": True, "grafica": "resumen"}

        # Escenarios
        if any(w in clave for w in ("peor caso", "pesimista", "suben todos", "suben los precios")):
            texto = self._resolver_tag("ESCENARIO_PESIMISTA", pregunta)
            return {"respuesta": texto, "tipo": "escenario", "exacta": True, "grafica": "escenarios"}

        if any(w in clave for w in ("mejor caso", "optimista", "bajan todos", "bajan los precios")):
            texto = self._resolver_tag("ESCENARIO_OPTIMISTA", pregunta)
            return {"respuesta": texto, "tipo": "escenario", "exacta": True, "grafica": "escenarios"}

        # Costo de producto (antes que insumo si menciona producto)
        producto_pre, p_score_pre = self._encontrar_producto(pregunta)
        if producto_pre and p_score_pre >= 0.50 and self._es_pregunta_costo(pregunta):
            return {
                "respuesta": self._respuesta_costo_producto(producto_pre),
                "tipo": "costo",
                "exacta": True,
                "grafica": "productos",
            }

        # Consulta de precio actual de insumo
        if any(w in clave for w in ("precio", "cuesta", "cuestan", "vale", "valen")):
            insumo_pre, score_pre = self._encontrar_insumo(pregunta)
            if (
                insumo_pre
                and score_pre >= 0.50
                and self._pregunta_menciona_insumo(clave, insumo_pre)
                and not self._es_pregunta_cambio_precio(pregunta)
                and not any(w in clave for w in ("empanada", "arepa", "papa rellena", "pastel", "carimanola"))
            ):
                return {
                    "respuesta": self._respuesta_precio_insumo(insumo_pre),
                    "tipo": "historial",
                    "exacta": True,
                    "grafica": "insumos",
                }

        # Simulacion explicita ("que pasa si...") antes que fuentes,
        # para que no se confunda con consejos parecidos (ej: "que debo hacer si sube la harina")
        if any(w in clave for w in ("que pasa", "que pasaria", "simula")):
            exacto = self.buscar_en_fuentes(pregunta)
            if not (exacto and exacto.get("exacta")):
                sim = self._responder_simulacion(pregunta, clave)
                if sim:
                    return sim

        # Fuentes de conocimiento
        resultado = self.buscar_en_fuentes(pregunta)
        if resultado and not resultado.get("sin_respuesta"):
            respuesta = resultado["respuesta"]
            if respuesta in TAGS_DINAMICOS:
                texto = self._resolver_tag(respuesta, pregunta)
                if texto:
                    return {
                        "respuesta": texto,
                        "tipo": "historial",
                        "exacta": resultado.get("exacta", True),
                        "grafica": TAG_GRAFICA.get(respuesta),
                    }

            texto = respuesta
            if not resultado.get("exacta"):
                pct = round(resultado["score"] * 100)
                texto += f" (parecido a: '{resultado['pregunta']}', {pct}% seguro)"
            return {
                "respuesta": texto,
                "fuente": resultado.get("fuente", ""),
                "tipo": "conocimiento",
                "exacta": resultado.get("exacta", False),
                "score": resultado.get("score", 1.0),
            }

        # Cambio de precio de insumo
        if self._es_pregunta_cambio_precio(pregunta):
            sim = self._responder_simulacion(pregunta, clave)
            if sim:
                return sim

        # Costo, ganancia o ventas de producto especifico (requiere match claro)
        producto, p_score = self._encontrar_producto(pregunta)
        if producto and p_score >= 0.50:
            if self._es_pregunta_ventas_producto(pregunta):
                return {
                    "respuesta": self._respuesta_ventas_producto(producto),
                    "tipo": "historial",
                    "exacta": True,
                    "grafica": "productos",
                }
            if self._es_pregunta_costo(pregunta):
                return {
                    "respuesta": self._respuesta_costo_producto(producto),
                    "tipo": "costo",
                    "exacta": True,
                    "grafica": "productos",
                }
            if self._es_pregunta_ganancia(pregunta) and not any(
                w in clave for w in ("mas rentable", "mejor margen", "top", "cual producto", "que producto")
            ):
                return {
                    "respuesta": self._respuesta_costo_producto(producto),
                    "tipo": "ganancia",
                    "exacta": True,
                    "grafica": "productos",
                }

        # Precio actual o historial de insumo
        insumo, i_score = self._encontrar_insumo(pregunta)
        consulta_precio_insumo = any(
            w in clave for w in ("precio", "cuesta", "cuestan", "vale", "valen", "historial", "subio", "variacion")
        )
        if (
            insumo
            and i_score >= 0.50
            and self._pregunta_menciona_insumo(clave, insumo)
            and consulta_precio_insumo
            and not self._pregunta_es_de_ventas(clave)
            and not self._es_pregunta_cambio_precio(pregunta)
        ):
            return {
                "respuesta": self._respuesta_precio_insumo(insumo),
                "tipo": "historial",
                "exacta": True,
                "grafica": "insumos",
            }

        # Historial insumo mencionado
        if insumo and self._pregunta_menciona_insumo(clave, insumo):
            hist = self.historial.precio_historico_insumo(insumo.id)
            if hist and any(w in clave for w in ("historial", "mayo", "mes", "subio", "variacion")):
                return {
                    "respuesta": self._respuesta_precio_insumo(insumo),
                    "tipo": "historial",
                    "exacta": True,
                    "grafica": "insumos",
                }

        sugerencias = resultado.get("sugerencias", []) if resultado else []
        return {
            "sin_respuesta": True,
            "sugerencias": sugerencias,
            "respuesta": (
                "No entendi esa pregunta. Puedo ayudarte con:\n"
                "  - Ventas y ganancias del mes en COP (ej: cuanto vendi en mayo)\n"
                "  - Costos y rentabilidad (ej: cuanto cuesta la empanada de carne)\n"
                "  - Variacion de precios (ej: que insumo subio mas)\n"
                "  - Simulaciones (ej: que pasa si la harina sube 15%)\n"
                "  - Escenarios (ej: peor caso al 10%)\n"
                "  - Resumen del mes (ej: dame un resumen de mayo)"
            ),
        }
