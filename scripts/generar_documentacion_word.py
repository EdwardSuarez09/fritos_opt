"""Genera documentacion Word del codigo y estructura del proyecto."""
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "docs" / "DOCUMENTACION_CODIGO_Y_ESTRUCTURA.docx"


def titulo(doc, texto, nivel=1):
    doc.add_heading(texto, level=nivel)


def parrafo(doc, texto, negrita=False):
    p = doc.add_paragraph()
    run = p.add_run(texto)
    if negrita:
        run.bold = True
    run.font.size = Pt(11)
    return p


def pregunta_respuesta(doc, pregunta, respuesta):
    p = doc.add_paragraph()
    rq = p.add_run(f"P: {pregunta}")
    rq.bold = True
    rq.font.size = Pt(11)
    doc.add_paragraph(f"R: {respuesta}")
    doc.add_paragraph()


def tabla_archivos(doc, filas):
    t = doc.add_table(rows=1, cols=3)
    t.style = "Table Grid"
    hdr = t.rows[0].cells
    hdr[0].text = "Archivo / carpeta"
    hdr[1].text = "Ubicacion"
    hdr[2].text = "Para que sirve"
    for nombre, ubic, desc in filas:
        row = t.add_row().cells
        row[0].text = nombre
        row[1].text = ubic
        row[2].text = desc
    doc.add_paragraph()


def generar():
    doc = Document()
    style = doc.styles["Normal"]
    style.font.name = "Calibri"
    style.font.size = Pt(11)

    # Portada
    t = doc.add_paragraph()
    t.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = t.add_run("DOCUMENTACION DEL CODIGO Y ESTRUCTURA\n")
    r.bold = True
    r.font.size = Pt(18)
    r2 = t.add_run("Sistema de Costeo y Optimizacion para Puesto de Fritos\n\n")
    r2.font.size = Pt(14)
    r3 = t.add_run("Explicacion de carpetas, archivos y arquitectura del software\n")
    r3.font.size = Pt(12)
    r3.font.color.rgb = RGBColor(80, 80, 80)
    doc.add_page_break()

    # 1. Introduccion
    titulo(doc, "1. Introduccion")
    parrafo(doc,
        "Este documento describe la estructura completa del proyecto fritos_opt: "
        "por que esta organizado en carpetas, que hace cada archivo y como se "
        "relacionan entre si. El sistema es una aplicacion de escritorio en Python "
        "con interfaz Tkinter que permite gestionar inventario, costos, ventas, "
        "optimizacion de produccion (Programacion Lineal con PuLP), analisis de "
        "sensibilidad y un asistente conversacional con graficas."
    )
    parrafo(doc,
        "La arquitectura sigue el principio de separacion de responsabilidades: "
        "la logica de negocio vive en core/, la interfaz grafica en ui/, los datos "
        "persistentes en data/, y las pruebas automatizadas en tests/. Asi se "
        "facilita el mantenimiento, las pruebas y futuras mejoras sin redisenar "
        "toda la aplicacion."
    )

    # 2. Arquitectura general
    titulo(doc, "2. Arquitectura general del proyecto")
    parrafo(doc, "El flujo principal del sistema es el siguiente:")
    for paso in [
        "El usuario ejecuta main.py, que abre la ventana principal (MainWindow).",
        "MainWindow inicializa Inventario, CalculadorCostos, Optimizador, ComprasManager y VentasManager.",
        "Cada pestana de la interfaz (ui/*_screen.py) muestra datos y captura acciones del usuario.",
        "Las pantallas llaman a las clases de core/ para leer, calcular o guardar informacion.",
        "JSONManager persiste los cambios en archivos JSON dentro de data/.",
        "CalculadorCostos y Optimizador usan los mismos datos para costos y produccion optima.",
        "El asistente (bot_sensibilidad.py) combina historial, calculos y fuentes de texto.",
    ]:
        doc.add_paragraph(paso, style="List Bullet")

    parrafo(doc, "Estructura de carpetas en la raiz del proyecto:", negrita=True)
    tabla_archivos(doc, [
        ("core/", "Raiz", "Logica de negocio: modelos, calculos, persistencia, bot."),
        ("ui/", "Raiz", "Interfaz grafica: ventanas, formularios, graficas, tema visual."),
        ("data/", "Raiz", "Archivos JSON con datos del negocio (insumos, ventas, etc.)."),
        ("tests/", "Raiz", "85 pruebas unitarias que validan modulos principales."),
        ("fuentes/", "Raiz", "Textos de conocimiento para respuestas del asistente."),
        ("docs/", "Raiz", "Manuales y documentacion del proyecto."),
        ("scripts/", "Raiz", "Herramientas de analisis, depuracion y datos de demostracion."),
        (".vscode/", "Raiz", "Configuracion del depurador en Visual Studio Code / Cursor."),
    ])

    # 3. Punto de entrada
    titulo(doc, "3. Punto de entrada y archivos en la raiz")
    tabla_archivos(doc, [
        ("main.py", "Raiz", "Punto de entrada. Crea la ventana Tkinter e inicia MainWindow. Es el archivo que se ejecuta con: python main.py"),
        ("requirements.txt", "Raiz", "Lista de dependencias: pulp (optimizacion), pandas, openpyxl (Excel), matplotlib (graficas)."),
        ("README.md", "Raiz", "Guia de instalacion, uso y estructura para quien clone el repositorio."),
        ("run_tests.py", "Raiz", "Script auxiliar para ejecutar todas las pruebas unitarias."),
        ("__init__.py", "Raiz", "Permite tratar la raiz como paquete Python."),
        (".gitignore", "Raiz", "Indica a Git que archivos generados y entornos virtuales no versionar."),
        ("DOCUMENTACION_CODIGO_Y_ESTRUCTURA.docx", "docs/", "Documentacion complementaria del codigo y la estructura."),
        ("ESTRUCTURA.md", "docs/", "Resumen markdown de la estructura del proyecto."),
        ("MANUAL_COMPLETO.md", "docs/", "Manual detallado de uso del aplicativo."),
        ("INICIO_RAPIDO.md", "docs/", "Guia rapida para poner en marcha el sistema."),
        ("EXPLICACION_OPTIMIZACION.md", "docs/", "Explicacion del modelo matematico de optimizacion."),
        ("EXPLICACION_GANANCIAS.md", "docs/", "Explicacion de como se calculan ganancias y margenes."),
        ("VALORES_FACTIBLES.txt", "data/", "Referencia de valores de demanda y presupuesto factibles para optimizar."),
        ("calcular_presupuesto.py", "scripts/", "Script de apoyo para calcular presupuesto minimo (desarrollo)."),
        ("calcular_presupuesto_total.py", "scripts/", "Script de apoyo para presupuesto semanal total."),
        ("calcular_exacto.py", "scripts/", "Script de apoyo para calculos exactos de costos."),
        ("verificar_factibilidad.py", "scripts/", "Verifica si un escenario de optimizacion es factible."),
        ("analizar_ceros.py", "scripts/", "Analiza productos con costo o ganancia cero (depuracion)."),
        ("debug_costos.py", "scripts/", "Depuracion de costos unitarios."),
        ("test_imports.py", "scripts/", "Verifica que todos los modulos importen correctamente."),
        ("generar_documentacion_word.py", "scripts/", "Genera documentacion complementaria en formato Word."),
        ("seed_historial_operativo.py", "scripts/", "Carga compras.json y ventas.json desde historial_mensual.json (datos de demo)."),
        ("figura_pruebas_unitarias.png", "docs/img/", "Captura de evidencia: 85 pruebas ejecutadas con exito."),
    ])

    # 4. core/
    titulo(doc, "4. Carpeta core/ — Logica de negocio")
    parrafo(doc,
        "Contiene toda la logica que no depende de la interfaz grafica. "
        "Si manana se cambiara Tkinter por una pagina web, estos archivos "
        "se reutilizarian casi sin cambios."
    )
    titulo(doc, "4.1 Persistencia y acceso unificado", 2)
    tabla_archivos(doc, [
        ("json_manager.py", "core/", "Clase JSONManager: lee y escribe archivos en data/*.json. Centraliza la persistencia."),
        ("inventario.py", "core/", "Clase Inventario: agrupa InsumoManager, MasaManager y ProductoManager en un solo punto de acceso."),
    ])
    titulo(doc, "4.2 Gestion de datos del negocio", 2)
    tabla_archivos(doc, [
        ("insumos.py", "core/", "Clases Insumo e InsumoManager. CRUD de materias primas, categorias, stock y precios."),
        ("masas.py", "core/", "Clases LoteMasa y MasaManager. Lotes de masa, insumos usados, costo por unidad equivalente."),
        ("productos.py", "core/", "Clases Producto y ProductoManager. Productos finales, receta (masa + insumos extra), precio de venta."),
        ("compras.py", "core/", "Clases Compra y ComprasManager. Registro de compras de insumos e historial de gastos."),
        ("ventas.py", "core/", "Clases Venta y VentasManager. Registro de ventas, totales e ingresos por producto."),
    ])
    titulo(doc, "4.3 Calculos y analisis", 2)
    tabla_archivos(doc, [
        ("costos.py", "core/", "CalculadorCostos: costo unitario (masa + rellenos + aceite + empaque), ganancia y margen."),
        ("consumo.py", "core/", "ConsumoEstimador: consumo de ingredientes y sobrantes segun ventas y recetas."),
        ("optimizador.py", "core/", "Optimizador con PuLP: maximiza ganancia semanal respetando demanda y presupuesto diario."),
        ("sensibilidad.py", "core/", "AnalizadorSensibilidad: impacto de cambios de precio y escenarios optimista/realista/pesimista."),
        ("historial.py", "core/", "HistorialMensual: consulta datos historicos de mayo (ventas, compras, variacion de precios)."),
    ])
    titulo(doc, "4.4 Asistente conversacional", 2)
    tabla_archivos(doc, [
        ("bot_sensibilidad.py", "core/", "BotSensibilidad: procesa preguntas en lenguaje natural, enruta a historial/costos/simulacion/escenarios y sugiere graficas."),
    ])

    # 5. ui/
    titulo(doc, "5. Carpeta ui/ — Interfaz grafica")
    parrafo(doc,
        "Cada archivo *_screen.py es una pantalla (pestaña) del aplicativo. "
        "Las pantallas no contienen logica de negocio compleja: delegan en core/."
    )
    tabla_archivos(doc, [
        ("main_window.py", "ui/", "Ventana principal con 10 pestanas. Crea managers, conecta pantallas y guarda al cerrar."),
        ("theme.py", "ui/", "Clase Theme: colores, fuentes y estilos ttk (modo oscuro estilo VS Code)."),
        ("inventario_screen.py", "ui/", "Pestana Inventario: registro de compras, catalogo de insumos e historial de compras."),
        ("masas_screen.py", "ui/", "Pestana Masas: crear lotes de masa y ver costo del lote."),
        ("rendimiento_screen.py", "ui/", "Pestana Rendimiento: cuantos productos salen de cada lote (filtrado por masa)."),
        ("productos_screen.py", "ui/", "Pestana Productos: catalogo de productos, recetas y precios de venta."),
        ("costos_screen.py", "ui/", "Pestana Costos: tabla de costo, ganancia y margen por producto."),
        ("ventas_screen.py", "ui/", "Pestana Ventas: registrar ventas, historial y resumen por producto."),
        ("consumo_screen.py", "ui/", "Pestana Consumo: consumo estimado, sobrantes y grafica comparativa."),
        ("optimizacion_screen.py", "ui/", "Pestana Optimizacion: demanda, presupuesto, resolver modelo y exportar Excel."),
        ("sensibilidad_screen.py", "ui/", "Pestana Sensibilidad: cambio de precios y escenarios de analisis."),
        ("sensibilidad_bot_screen.py", "ui/", "Pestana Asistente: chat, respuestas y graficas segun la pregunta."),
        ("charts.py", "ui/", "Funciones matplotlib: graficas de ventas, productos, insumos, escenarios, impacto, sobrantes."),
    ])
    parrafo(doc, "Pestanas en main_window.py (orden):", negrita=True)
    for i, nombre in enumerate([
        "Inventario", "Masas", "Rendimiento", "Productos", "Costos",
        "Ventas", "Consumo", "Optimizacion", "Sensibilidad", "Asistente"
    ], 1):
        doc.add_paragraph(f"{i}. {nombre}", style="List Number")

    # 6. data/
    titulo(doc, "6. Carpeta data/ — Datos persistentes")
    parrafo(doc,
        "Todos los JSON se guardan aqui automaticamente. Si se borra la carpeta, "
        "el sistema la recrea al iniciar, pero se pierden los datos registrados."
    )
    tabla_archivos(doc, [
        ("insumos.json", "data/", "Catalogo de insumos: nombre, stock, precio, unidad, categoria."),
        ("masas.json", "data/", "Lotes de masa: insumos usados, rendimiento por producto, costos."),
        ("productos.json", "data/", "Productos del negocio: masa, insumos extra, precio, demanda."),
        ("compras.json", "data/", "Historial de compras de insumos (generado o registrado en app)."),
        ("ventas.json", "data/", "Historial de ventas de productos."),
        ("historial_mensual.json", "data/", "Datos simulados de mayo: compras semanales, ventas, variacion de precios (para bot)."),
    ])

    # 7. tests/
    titulo(doc, "7. Carpeta tests/ — Pruebas unitarias")
    parrafo(doc, "85 pruebas en total. Ejecutar con: python -m unittest discover -s tests")
    tabla_archivos(doc, [
        ("base.py", "tests/", "BotTestCase: configura bot y analizador compartidos para pruebas."),
        ("test_costos.py", "tests/", "5 pruebas del calculador de costos y margenes."),
        ("test_optimizador.py", "tests/", "4 pruebas del modelo PuLP (factible, demanda, infactible)."),
        ("test_inventario.py", "tests/", "6 pruebas de InsumoManager (agregar, stock, eliminar)."),
        ("test_compras.py", "tests/", "6 pruebas de ComprasManager."),
        ("test_ventas.py", "tests/", "6 pruebas de VentasManager."),
        ("test_consumo.py", "tests/", "5 pruebas de ConsumoEstimador y sobrantes."),
        ("test_sensibilidad.py", "tests/", "6 pruebas de AnalizadorSensibilidad y escenarios."),
        ("test_historial.py", "tests/", "6 pruebas de HistorialMensual."),
        ("test_bot_helpers.py", "tests/", "12 pruebas de funciones auxiliares del bot."),
        ("test_bot_routing.py", "tests/", "15 pruebas de enrutamiento de preguntas."),
        ("test_no_mezcla.py", "tests/", "10 pruebas anti-mezcla (ventas vs insumos, etc.)."),
        ("test_graficas.py", "tests/", "4 pruebas de sugerencia de graficas por pregunta."),
    ])

    # 8. fuentes/
    titulo(doc, "8. Carpeta fuentes/ — Conocimiento del asistente")
    parrafo(doc,
        "Archivos de texto con respuestas predefinidas y plantillas. "
        "El bot busca coincidencias y reemplaza tags dinamicos (HISTORIAL_VENTAS_MES, etc.)."
    )
    tabla_archivos(doc, [
        ("costos.txt", "fuentes/", "Respuestas sobre costos, margenes y rentabilidad."),
        ("ventas.txt", "fuentes/", "Respuestas sobre ventas e historial."),
        ("sensibilidad.txt", "fuentes/", "Conceptos de analisis de sensibilidad."),
        ("consejos.txt", "fuentes/", "Consejos operativos cuando suben precios de insumos."),
    ])

    # 9. Relaciones entre modulos
    titulo(doc, "9. Como se conectan los modulos")
    parrafo(doc, "Cadena de dependencias principales:", negrita=True)
    for item in [
        "InventarioScreen usa InsumoManager + ComprasManager → actualiza insumos.json y compras.json.",
        "VentasScreen usa VentasManager → ventas.json.",
        "CostosScreen usa CalculadorCostos → lee insumos, masas y productos (sin archivo propio).",
        "ConsumoScreen usa ConsumoEstimador + ventas + compras → estima consumo y sobrantes.",
        "OptimizacionScreen usa Optimizador + CalculadorCostos → resuelve modelo PuLP.",
        "SensibilidadScreen usa AnalizadorSensibilidad → simula cambios de precio.",
        "Asistente usa BotSensibilidad + HistorialMensual + fuentes/ + charts.py.",
    ]:
        doc.add_paragraph(item, style="List Bullet")

    titulo(doc, "9.1 Formula de costo unitario (costos.py)", 2)
    parrafo(doc,
        "Costo = costo de masa equivalente + insumos extra del producto + "
        "aceite estimado (0.1 unidad) + empaque promedio. "
        "Ganancia = precio_venta - costo. Margen = ganancia / precio_venta * 100."
    )

    titulo(doc, "9.2 Modelo de optimizacion (optimizador.py)", 2)
    parrafo(doc,
        "Maximizar Z = suma de (cantidad_producida x ganancia_unitaria). "
        "Restricciones: produccion >= demanda minima por dia; "
        "costo de produccion diario <= presupuesto del dia. "
        "Solver: CBC de PuLP."
    )

    # 10. Por que esta organizacion
    titulo(doc, "10. Por que esta organizacion de carpetas")
    razones = [
        ("Separar core/ y ui/", "Permite probar la logica sin abrir ventanas y cambiar la interfaz sin tocar calculos."),
        ("Un JSON por entidad en data/", "Datos legibles, editables y respaldables; no requiere base de datos."),
        ("tests/ independiente", "Validacion automatica de 85 casos; evita regresiones al modificar codigo."),
        ("fuentes/ para el bot", "Conocimiento editable sin reprogramar; facilita ampliar respuestas."),
        ("Scripts en la raiz", "Herramientas de desarrollo y calculo auxiliar; no forman parte del flujo normal del usuario."),
        ("Documentacion .md en raiz", "Manuales para usuario y evaluador; complementan este documento tecnico."),
    ]
    t = doc.add_table(rows=1, cols=2)
    t.style = "Table Grid"
    t.rows[0].cells[0].text = "Decision"
    t.rows[0].cells[1].text = "Razon"
    for dec, raz in razones:
        row = t.add_row().cells
        row[0].text = dec
        row[1].text = raz
    doc.add_paragraph()

    # 11. Repositorio
    titulo(doc, "11. Control de versiones")
    parrafo(doc,
        "Repositorio GitHub: https://github.com/EdwardSuarez09/fritos_opt\n"
        "Control de versiones con Git. Historial de cambios del codigo fuente, "
        "pruebas unitarias y documentacion."
    )

    # 12. Modelo en cascada
    titulo(doc, "12. Modelo en cascada aplicado al proyecto")
    parrafo(doc,
        "El modelo en cascada (waterfall) organiza el desarrollo en fases secuenciales: "
        "cada etapa debe completarse antes de pasar a la siguiente. En este proyecto "
        "se utilizo porque el alcance fue definido desde el inicio (gestion operativa "
        "de un puesto de fritos con costos, optimizacion y sensibilidad) y los "
        "requisitos eran estables para un entregable academico con documentacion, "
        "pruebas y control de versiones."
    )
    parrafo(doc, "Fases del cascada y entregables de este proyecto:", negrita=True)
    fases = [
        ("1. Analisis de requisitos",
         "Definicion del alcance: inventario, compras, ventas, productos, recetas, "
         "costos, consumo, sobrantes, optimizacion con PuLP, sensibilidad, graficas "
         "y asistente. Caso de uso: microempresa de fritos."),
        ("2. Diseno",
         "Arquitectura en capas (core/, ui/, data/, tests/). Diseno de JSON por entidad, "
         "pestanas de la interfaz, modelo matematico de optimizacion y flujo de datos "
         "entre modulos. Documentos: ESTRUCTURA.md, EXPLICACION_OPTIMIZACION.md."),
        ("3. Implementacion",
         "Codigo Python en core/ y ui/. Modulos desarrollados por funcionalidad: "
         "primero insumos/masas/productos, luego costos y optimizador, despues "
         "compras, ventas, consumo, sensibilidad y bot."),
        ("4. Pruebas",
         "85 pruebas unitarias en tests/. Validacion manual de pantallas, datos de "
         "historial_mensual.json, evaluacion de calidad (seccion 10 del informe) y "
         "correccion de errores detectados (mezcla de respuestas del bot, filtros de rendimiento)."),
        ("5. Despliegue / entrega",
         "Aplicacion de escritorio ejecutable con python main.py. Respaldo en GitHub "
         "(fritos_opt). Documentacion, anexos con capturas y manual de usuario."),
        ("6. Mantenimiento (futuro)",
         "Plan de acciones correctivas: mejorar validaciones, accesibilidad, respaldo "
         "manual de JSON y ampliar respuestas del asistente. Estructura modular facilita "
         "cambios sin redisenar todo el sistema."),
    ]
    t = doc.add_table(rows=1, cols=2)
    t.style = "Table Grid"
    t.rows[0].cells[0].text = "Fase cascada"
    t.rows[0].cells[1].text = "Como se aplico en Fritos Opt"
    for fase, ent in fases:
        row = t.add_row().cells
        row[0].text = fase
        row[1].text = ent
    doc.add_paragraph()

    parrafo(doc,
        "Ventaja principal en este contexto: trazabilidad clara entre requisitos, "
        "diseno, codigo, pruebas y documentacion. La gestion de configuracion con Git "
        "registra los cambios de cada fase posterior (ajustes tras pruebas)."
    )

    # 13. Preguntas y respuestas
    titulo(doc, "13. Preguntas frecuentes y respuestas (modelo cascada y proyecto)")
    parrafo(doc,
        "Posibles preguntas de sustentacion, evaluacion o defensa del informe, "
        "con respuestas alineadas al modelo en cascada y al software desarrollado."
    )

    qa_cascada = [
        (
            "Por que eligieron el modelo en cascada y no otro (Scrum, prototipos, etc.)?",
            "Porque el proyecto academico tenia alcance definido desde el inicio y entregables "
            "claros (informe, software, pruebas, anexos). El cascada permitio avanzar de forma "
            "ordenada: primero requisitos y diseno, luego implementacion y pruebas. No se "
            "requeria entregar versiones parciales cada semana a un cliente cambiante; la "
            "microempresa necesita un sistema completo y documentado."
        ),
        (
            "Cuales fueron las fases del cascada en su proyecto?",
            "Analisis de requisitos (alcance del puesto de fritos), diseno (arquitectura core/ui/data), "
            "implementacion (modulos en Python), pruebas (85 pruebas unitarias y validacion manual), "
            "entrega (aplicacion + GitHub + documentacion) y mantenimiento planificado (acciones "
            "correctivas del informe)."
        ),
        (
            "Que entregable corresponde a la fase de analisis?",
            "El documento de alcance y requisitos: modulos de inventario, compras, ventas, productos, "
            "recetas, costos, consumo, sobrantes, optimizacion, sensibilidad, graficas y asistente; "
            "persistencia en JSON; aplicacion de escritorio para la microempresa."
        ),
        (
            "Que entregable corresponde a la fase de diseno?",
            "La estructura de carpetas (core/, ui/, data/, tests/), el diseno de pantallas por pestanas, "
            "el modelo de datos JSON, el modelo matematico de programacion lineal y los diagramas o "
            "descripciones en ESTRUCTURA.md y EXPLICACION_OPTIMIZACION.md."
        ),
        (
            "Como se evidencia la fase de implementacion?",
            "El codigo fuente en el repositorio GitHub (fritos_opt): mas de 50 archivos Python, "
            "10 pestanas funcionales, integracion de PuLP, matplotlib y bot conversacional."
        ),
        (
            "Como se evidencia la fase de pruebas?",
            "Carpeta tests/ con 85 pruebas unitarias que pasan al 100%; evaluacion de calidad "
            "del software (seccion 10); capturas de pantalla en anexos; correcciones documentadas "
            "(por ejemplo, unificacion de inventario, filtro de rendimiento por masa)."
        ),
        (
            "El cascada permite volver atras si hay errores?",
            "Si. Aunque las fases son secuenciales, cuando las pruebas detectaron problemas "
            "(respuestas mezcladas del bot, productos incorrectos en rendimiento), se regreso "
            "a implementacion, se corrigio y se volvio a probar. Eso coincide con la variante "
            "cascada con retroalimentacion entre pruebas e implementacion."
        ),
        (
            "Cual es la principal desventaja del cascada en su proyecto?",
            "Poca flexibilidad para cambiar requisitos a mitad de desarrollo. Si el docente "
            "hubiera pedido un modulo completamente nuevo al final, implicaria revisar diseno "
            "e implementacion. Por eso el alcance se definio completo desde el inicio."
        ),
        (
            "Por que el cascada es adecuado para este tipo de software?",
            "Porque es un sistema de gestion con reglas de negocio claras (costos, recetas, "
            "optimizacion), datos estructurados y una interfaz definida. No es un producto "
            "en exploracion continua; es una solucion acotada para una microempresa."
        ),
        (
            "Como se relaciona el cascada con la gestion de configuracion?",
            "Cada fase genera artefactos versionados: requisitos y diseno en documentos, "
            "codigo en Git, datos en JSON, pruebas en tests/. Git registra cambios tras "
            "ajustes de la fase de pruebas. GitHub (fritos_opt) conserva el respaldo."
        ),
    ]

    titulo(doc, "13.1 Sobre el modelo en cascada", 2)
    for p, r in qa_cascada:
        pregunta_respuesta(doc, p, r)

    qa_proyecto = [
        (
            "Por que separaron core/ y ui/?",
            "Por el diseno en cascada: primero se definio la logica de negocio (core) y "
            "despues la interfaz (ui). Asi se pueden probar costos y optimizacion sin abrir "
            "ventanas, y cambiar la interfaz sin tocar los calculos."
        ),
        (
            "Por que usaron JSON y no una base de datos?",
            "En la fase de diseno se priorizo simplicidad para una microempresa sin servidor: "
            "archivos legibles, faciles de respaldar y acordes al alcance academico. JSONManager "
            "centraliza lectura y escritura en data/."
        ),
        (
            "Como fluyen los datos entre modulos?",
            "Inventario y compras actualizan insumos.json; ventas actualiza ventas.json; "
            "CalculadorCostos lee insumos, masas y productos; Optimizador usa costos y demanda; "
            "ConsumoEstimador usa ventas y recetas; el bot usa historial y calculos en vivo."
        ),
        (
            "Que hace el modulo de optimizacion?",
            "Resuelve un modelo de programacion lineal (PuLP) que maximiza la ganancia semanal "
            "respetando demanda minima por producto/dia y presupuesto diario. Resultado: "
            "cuanto producir de cada producto cada dia."
        ),
        (
            "Que hace el analisis de sensibilidad?",
            "Evalua que pasa si suben o bajan precios de insumos: impacto en costos, ganancias "
            "y escenarios optimista, realista y pesimista. El asistente permite preguntar en "
            "lenguaje natural y ver graficas."
        ),
        (
            "Para que sirven las 85 pruebas unitarias?",
            "Validar automaticamente que cada modulo funciona y que el bot no mezcla respuestas "
            "(ventas vs precios de insumos, simulacion vs consulta simple). Evidencia de la "
            "fase de pruebas del cascada y de la calidad del software."
        ),
        (
            "Que es historial_mensual.json?",
            "Datos simulados de operacion en mayo (compras semanales, ventas por producto, "
            "variacion de precios). Alimenta el asistente y las graficas de historial; "
            "scripts/seed_historial_operativo.py carga compras.json y ventas.json para las pantallas."
        ),
        (
            "Por que unificaron Inventario y Compras en una sola pantalla?",
            "Tras pruebas con usuario, se detecto redundancia. En implementacion se fusionaron "
            "en InventarioScreen: arriba registrar compras, abajo stock e historial. La logica "
            "sigue en core/compras.py y core/insumos.py."
        ),
        (
            "Como ejecuto el sistema?",
            "pip install -r requirements.txt, luego python main.py. Pruebas: "
            "python -m unittest discover -s tests."
        ),
        (
            "Donde esta el codigo fuente?",
            "Repositorio GitHub: https://github.com/EdwardSuarez09/fritos_opt. "
            "Control de versiones con Git; historial de cambios documentado."
        ),
    ]

    titulo(doc, "13.2 Sobre el codigo y la estructura del software", 2)
    for p, r in qa_proyecto:
        pregunta_respuesta(doc, p, r)

    qa_sustentacion = [
        (
            "Que aporta el sistema a la microempresa?",
            "Centraliza inventario, ventas, costos y produccion optima en una sola aplicacion. "
            "El dueno puede ver margenes, simular subidas de precios, estimar sobrantes y "
            "recibir recomendaciones sin conocer programacion lineal."
        ),
        (
            "Que limitaciones tiene la primera version?",
            "Validaciones basicas, sin respaldo automatico de JSON, estimacion aproximada de "
            "sobrantes (no inventario en tiempo real), asistente con respuestas predefinidas "
            "y reglas (no IA generativa). Estas mejoras estan en el plan de acciones correctivas."
        ),
        (
            "Como demuestran que el software cumple el alcance?",
            "Modulos implementados y probados; 85 pruebas OK; capturas en anexo; repositorio "
            "publico; evaluacion de calidad 4,3/5; documentacion tecnica y manual de usuario."
        ),
    ]

    titulo(doc, "13.3 Preguntas de sustentacion ante el docente", 2)
    for p, r in qa_sustentacion:
        pregunta_respuesta(doc, p, r)

    # 14. Ejecucion
    titulo(doc, "14. Como ejecutar el sistema")
    for cmd in [
        "pip install -r requirements.txt",
        "python main.py",
        "python -m unittest discover -s tests",
        "python scripts/seed_historial_operativo.py",
    ]:
        p = doc.add_paragraph()
        run = p.add_run(cmd)
        run.font.name = "Consolas"
        run.font.size = Pt(10)

    doc.save(OUTPUT)
    print(f"Documento generado: {OUTPUT}")


if __name__ == "__main__":
    generar()
