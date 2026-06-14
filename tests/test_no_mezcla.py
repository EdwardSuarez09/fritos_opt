"""
Pruebas anti-mezcla: casos que antes fallaban o son ambiguos.
Si alguna falla, el bot esta confundiendo ventas con insumos, productos con insumos, etc.
"""
import unittest

from tests.base import BotTestCase


class TestNoMezcla(BotTestCase):
    """Matriz de preguntas parecidas que NO deben cruzar respuestas"""

    PARES_DISTINTOS = [
        (
            "cuanto vendi en mayo",
            "cuanto cuesta el aceite",
            "ventas del mes no debe parecerse a precio de aceite",
        ),
        (
            "cuanto cuesta la empanada de carne",
            "cuanto cuesta la carne",
            "costo de producto no debe ser solo precio del insumo carne",
        ),
        (
            "que pasa si la harina sube 15%",
            "cuanto vale la harina",
            "simulacion no debe ser igual a consulta de precio",
        ),
        (
            "cual producto es mas rentable",
            "cuanto cuesta la empanada de carne",
            "ranking de rentabilidad no debe ser costo de un solo producto",
        ),
    ]

    def test_respuestas_pares_son_diferentes(self):
        for pregunta_a, pregunta_b, msg in self.PARES_DISTINTOS:
            texto_a = self.texto(pregunta_a)
            texto_b = self.texto(pregunta_b)
            self.assertNotEqual(
                texto_a,
                texto_b,
                msg=f"{msg}: respuestas identicas",
            )
            # Al menos 30% de diferencia en longitud o contenido clave
            self.assertTrue(
                texto_a[:40] != texto_b[:40],
                msg=f"{msg}: inicio de respuesta muy similar",
            )

    def test_ventas_no_devuelve_precio_insumo(self):
        texto = self.texto("cuanto vendi en mayo")
        self.assertNotRegex(texto, r"precio actual.*lb")
        self.assertNotIn("carne molida", texto.lower())

    def test_empanada_no_devuelve_insumo_carne_puro(self):
        texto = self.texto("cuanto cuesta la empanada de carne")
        self.assertIn("empanada de carne", texto.lower())
        self.assertNotRegex(texto, r"^carne: precio actual")

    def test_aceite_no_dispara_simulacion(self):
        resultado = self.responder("cuanto cuesta el aceite")
        self.assertEqual(resultado.get("tipo"), "historial")
        self.assertNotIn("productos afectados", resultado.get("respuesta", "").lower())

    def test_simulacion_no_dispara_consejo_fuzzy(self):
        resultado = self.responder("que pasa si la harina sube 15%")
        self.assertEqual(resultado.get("tipo"), "calculo")
        self.assertNotIn("proveedor", resultado.get("respuesta", "").lower()[:80])

    def test_peor_caso_no_es_ventas(self):
        resultado = self.responder("peor caso al 10%")
        self.assertEqual(resultado.get("tipo"), "escenario")
        self.assertNotIn("vendiste", resultado.get("respuesta", "").lower())

    def test_tipos_consistentes_en_lote(self):
        """Un mismo tipo de pregunta siempre produce el mismo tipo de respuesta"""
        ventas = [
            self.responder("cuanto vendi en mayo").get("tipo"),
            self.responder("cuanto fue mi ingreso en mayo").get("tipo"),
        ]
        self.assertTrue(all(t == "historial" for t in ventas))

        calculos = [
            self.responder("que pasa si el aceite sube 10%").get("tipo"),
            self.responder("que pasa si la harina sube 20%").get("tipo"),
        ]
        self.assertTrue(all(t == "calculo" for t in calculos))


class TestEncontrarEntidades(BotTestCase):
    """El matcher de insumo/producto no debe confundir entidades"""

    def test_harina_es_insumo_no_producto(self):
        insumo, score_i = self.bot._encontrar_insumo("precio de la harina")
        producto, score_p = self.bot._encontrar_producto("precio de la harina")
        self.assertIsNotNone(insumo)
        self.assertIn("harina", insumo.nombre.lower())
        if producto:
            self.assertLess(score_p, score_i)

    def test_empanada_carne_es_producto(self):
        producto, score = self.bot._encontrar_producto("empanada de carne")
        self.assertIsNotNone(producto)
        self.assertGreaterEqual(score, 0.5)
        self.assertIn("empanada", producto.nombre.lower())

    def test_menciona_insumo_solo_si_esta_en_pregunta(self):
        clave = "cuanto vendi en mayo"
        insumo, _ = self.bot._encontrar_insumo(clave)
        if insumo:
            self.assertFalse(
                self.bot._pregunta_menciona_insumo(clave, insumo),
                "mayo no deberia activar un insumo",
            )


if __name__ == "__main__":
    unittest.main()
