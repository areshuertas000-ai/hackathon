import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest


RUTA_APP = Path(__file__).resolve().parents[1] / "app.py"


class PruebasInterfaz(unittest.TestCase):
    def setUp(self):
        self.app = AppTest.from_file(str(RUTA_APP)).run(timeout=15)

    def verificar_sin_errores(self):
        self.assertEqual(len(self.app.exception), 0)

    def test_pagina_inicio(self):
        self.verificar_sin_errores()
        self.assertEqual(
            self.app.title[0].value,
            "El tutor perfecto para cada estudiante",
        )

    def test_menu_abre_busqueda(self):
        self.app.sidebar.radio[0].set_value("Buscar tutor").run(timeout=15)
        self.verificar_sin_errores()
        self.assertEqual(self.app.title[0].value, "Buscar el mejor tutor")
        etiquetas = [boton.label for boton in self.app.button]
        self.assertIn("Buscar mejor tutor", etiquetas)

    def test_menu_muestra_tutores_precargados(self):
        self.app.sidebar.radio[0].set_value("Ver tutores").run(timeout=15)
        self.verificar_sin_errores()
        self.assertGreaterEqual(len(self.app.dataframe), 1)
        etiquetas = [boton.label for boton in self.app.button]
        self.assertIn("Eliminar tutor", etiquetas)


if __name__ == "__main__":
    unittest.main()
